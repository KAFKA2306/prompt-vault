import json
import re
import sys
from pathlib import Path

def guard():
    root = Path(__file__).resolve().parents[3] # up to project root
    db_path = root / 'db' / 'prompts.json'
    
    if not db_path.exists():
        print(json.dumps([{"severity": "critical", "reason": "db/prompts.json not found"}]))
        sys.exit(1)

    with open(db_path, 'r', encoding='utf-8') as f:
        db = json.load(f)

    templates = db.get('templates', [])
    blocks = db.get('blocks', [])
    block_ids = {b.get('id') for b in blocks if b.get('id')}
    
    results = []

    # Keywords for mixed-role and pollution
    ROLE_KEYWORDS = {
        "pose": [r"pose", r"standing", r"sitting", r"gesture"],
        "outfit": [r"outfit", r"clothing", r"jacket", r"wear"],
        "background": [r"background", r"room", r"desk", r"window"],
        "lighting": [r"light", r"shadow", r"glow", r"sunlight"],
        "expression": [r"expression", r"smile", r"face"]
    }
    VISUAL_KEYWORDS = ["光", "感情", "空気感", "衣装", "色", "表情", "背景", "構図", "soft", "cozy", "cinematic"]

    def has_word(text, word):
        if re.search(rf"\b{word}\b", text, re.I): return True
        if word in text and not word.isascii(): return True
        return False

    # 1. Unknown Block & Empty Template
    for t in templates:
        tid = t.get('id')
        t_blocks = t.get('blocks', [])
        
        if not t_blocks:
            results.append({
                "severity": "critical",
                "type": "empty_template",
                "id": tid,
                "title": t.get('title'),
                "reason": "blocks list is empty",
                "suggested_action": "Classify and assign blocks manually or deprecate.",
                "requires_human_review": True
            })
        
        if len(t_blocks) > 10:
            results.append({
                "severity": "warning",
                "type": "bloated_template",
                "id": tid,
                "title": t.get('title'),
                "reason": f"Too many blocks ({len(t_blocks)})",
                "suggested_action": "Consolidate blocks into more atomic or master blocks.",
                "requires_human_review": True
            })

        for bid in t_blocks:
            if bid not in block_ids:
                results.append({
                    "severity": "critical",
                    "type": "unknown_block",
                    "id": tid,
                    "title": t.get('title'),
                    "reason": f"References unknown block ID: {bid}",
                    "suggested_action": "Fix the reference in db/prompts.json.",
                    "requires_human_review": True
                })

        # Summary Pollution
        text_to_check = (t.get('title', '') + " " + t.get('summary', '')).lower()
        for kw in VISUAL_KEYWORDS:
            if has_word(text_to_check, kw):
                results.append({
                    "severity": "warning",
                    "type": "summary_pollution",
                    "id": tid,
                    "title": t.get('title'),
                    "reason": f"Visual keyword '{kw}' found in template meta",
                    "suggested_action": "Move visual descriptors to material blocks.",
                    "requires_human_review": True
                })
                break

    # 2. Duplicate ID
    seen_bids = set()
    for b in blocks:
        bid = b.get('id')
        if not bid: continue
        if bid in seen_bids:
            results.append({
                "severity": "critical",
                "type": "duplicate_id",
                "id": bid,
                "title": b.get('title'),
                "reason": "Duplicate block ID found in database",
                "suggested_action": "Rename or merge duplicate blocks.",
                "requires_human_review": True
            })
        seen_bids.add(bid)

    # 3. Block Audit
    for b in blocks:
        bid = b.get('id')
        content = b.get('content', '')
        
        if len(content) > 200:
            results.append({
                "severity": "warning",
                "type": "oversized_block",
                "id": bid,
                "title": b.get('title'),
                "reason": f"Content length ({len(content)}) exceeds 200 chars",
                "suggested_action": "Split into multiple atomic blocks.",
                "requires_human_review": True
            })

        if bid.lower() in ["scene", "layout", "style"]:
            results.append({
                "severity": "warning",
                "type": "ambiguous_category",
                "id": bid,
                "title": b.get('title'),
                "reason": "Trash-can category ID detected",
                "suggested_action": "Use more specific IDs (e.g., master_style, grid_layout).",
                "requires_human_review": True
            })

        # Mixed Roles
        found_roles = [role for role, kws in ROLE_KEYWORDS.items() if any(has_word(content, kw) for kw in kws)]
        if len(found_roles) >= 3:
            results.append({
                "severity": "warning",
                "type": "mixed_roles",
                "id": bid,
                "title": b.get('title'),
                "reason": f"Multiple roles detected: {found_roles}",
                "suggested_action": "Separate into single-role blocks.",
                "requires_human_review": True
            })

    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    guard()
