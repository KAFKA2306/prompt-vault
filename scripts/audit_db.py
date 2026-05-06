import json
import re
import sys
import argparse
from pathlib import Path

def audit_db(strict=False):
    db_path = Path('db/prompts.json')
    if not db_path.exists():
        print("Error: db/prompts.json not found")
        sys.exit(1)

    with open(db_path, 'r', encoding='utf-8') as f:
        db = json.load(f)

    templates = db.get('templates', [])
    blocks = db.get('blocks', [])
    block_ids = {b.get('id') for b in blocks if b.get('id')}
    
    errors = []
    warnings = []

    # 1. Unknown Block & Empty Template Check
    for t in templates:
        tid = t.get('id')
        t_blocks = t.get('blocks', [])
        
        if not t_blocks:
            warnings.append(f"Template '{tid}' has empty blocks list")
        
        for bid in t_blocks:
            if bid not in block_ids:
                errors.append(f"Template '{tid}' references unknown block: {bid}")

    # 2. Duplicate ID Check
    seen_bids = set()
    for b in blocks:
        bid = b.get('id')
        if not bid: continue
        if bid in seen_bids:
            errors.append(f"Duplicate block ID found: {bid}")
        seen_bids.add(bid)

    # 3. Oversized / Mixed Role Check (Banned Keywords)
    BANNED_KEYWORDS = ["scene"]
    ROLE_KEYWORDS = {
        "pose": [r"pose", r"standing", r"sitting"],
        "outfit": [r"outfit", r"clothing", r"jacket"],
        "background": [r"background", r"room", r"desk"],
        "lighting": [r"light", r"shadow", r"glow"],
        "expression": [r"expression", r"smile", r"face"]
    }

    for b in blocks:
        content = b.get('content', '').lower()
        bid = b.get('id')
        
        for kw in BANNED_KEYWORDS:
            if re.search(rf"\b{kw}\b", content):
                warnings.append(f"Block '{bid}' contains banned/mixed-role term: {kw}")

        # Multiple Roles detection
        roles = []
        for role, kws in ROLE_KEYWORDS.items():
            if any(re.search(rf"\b{kw}\b", content) for kw in kws):
                roles.append(role)
        
        if len(roles) >= 3:
            warnings.append(f"Block '{bid}' seems to have multiple roles: {roles}")

    # 4. Result Reporting
    print(f"--- DB Audit Report ---")
    print(f"Templates: {len(templates)}, Blocks: {len(blocks)}")
    
    if errors:
        print("\n[ERRORS]")
        for e in errors: print(f"  - {e}")
    
    if warnings:
        print("\n[WARNINGS]")
        for w in warnings: print(f"  - {w}")

    if errors or (strict and warnings):
        print("\nAudit FAILED.")
        sys.exit(1)
    else:
        print("\nAudit PASSED.")
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="Fail on warnings as well")
    args = parser.parse_args()
    audit_db(strict=args.strict)
