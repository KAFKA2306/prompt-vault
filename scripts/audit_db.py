import argparse
import re
import sys

from _bootstrap import ROOT
from config import CONFIG
from src.db_io import load_json_db

KNOWN_ROLES = {
    "identity",
    "style",
    "layout",
    "outfit",
    "pose",
    "background",
    "lighting",
    "text",
    "situation",
    "pack",
    "research",
    "safety",
    "system",
    "effect",
    "composition",
    "mood",
    "expression",
    "control",
    "avatar",
    "audio",
    "memory",
    "strategy",
    "brand",
    "structure",
    "flow",
    "reply",
    "concept",
    "other",
}

SUSPICIOUS_BROAD_PACK_NAMES = {
    "cute_pack",
    "nice_pack",
    "general_pack",
    "all_pack",
    "default_pack",
    "image_pack",
    "post_pack",
}


def audit_db(strict=False):
    db_path = ROOT / CONFIG["paths"]["db"]
    if not db_path.exists():
        print("Error: db/prompts.json not found")
        sys.exit(1)

    db = load_json_db(db_path)

    templates = db.get("templates", [])
    blocks = db.get("blocks", [])
    block_ids = {b.get("id") for b in blocks if b.get("id")}
    block_by_id = {b.get("id"): b for b in blocks if b.get("id")}

    errors = []
    warnings = []

    # 1. Unknown Block & Empty Template Check
    for t in templates:
        tid = t.get("id")
        t_blocks = t.get("blocks", [])
        kind = t.get("kind")

        if not t_blocks and kind != "generated":
            warnings.append(f"Template '{tid}' has empty blocks list")
        if len(t_blocks) > 8:
            warnings.append(f"Template '{tid}' has too many blocks: {len(t_blocks)}")

        for bid in t_blocks:
            if bid not in block_ids:
                errors.append(f"Template '{tid}' references unknown block: {bid}")

    # 2. Duplicate ID Check
    seen_bids = set()
    for b in blocks:
        bid = b.get("id")
        if not bid:
            continue
        if bid in seen_bids:
            errors.append(f"Duplicate block ID found: {bid}")
        seen_bids.add(bid)

        role = b.get("role")
        if not role:
            errors.append(f"Missing role on block: {bid}")
        elif role not in KNOWN_ROLES:
            warnings.append(f"Unknown role on block '{bid}': {role}")

    # 3. Oversized / Mixed Role Check (Banned Keywords)
    BANNED_KEYWORDS = ["scene"]
    ROLE_KEYWORDS = {
        "pose": [r"pose", r"standing", r"sitting"],
        "outfit": [r"outfit", r"clothing", r"jacket"],
        "background": [r"background", r"room", r"desk"],
        "lighting": [r"light", r"shadow", r"glow"],
        "expression": [r"expression", r"smile", r"face"],
    }

    for b in blocks:
        content = b.get("content", "").lower()
        bid = b.get("id")
        block_role = b.get("role")

        for kw in BANNED_KEYWORDS:
            if re.search(rf"\b{kw}\b", content):
                warnings.append(f"Block '{bid}' contains banned/mixed-role term: {kw}")

        # Multiple Roles detection
        roles = []
        for role, kws in ROLE_KEYWORDS.items():
            if any(re.search(rf"\b{kw}\b", content) for kw in kws):
                roles.append(role)

        if block_role != "pack" and len(roles) >= 3:
            warnings.append(f"Block '{bid}' seems to have multiple roles: {roles}")

        if block_role == "identity" and any(
            token in content
            for token in [
                "morning",
                "gaming",
                "reading",
                "news",
                "cosplay",
                "poker",
                "joinwars",
                "summer",
                "spring",
                "autumn",
                "winter",
            ]
        ):
            warnings.append(f"Block '{bid}' mixes identity with situation terms")
        if block_role == "style" and any(
            token in f"{b.get('title', '')} {content}"
            for token in [
                "identity",
                "persona",
                "self-governance",
                "invariant",
                "identity lock",
                "fixed identity",
                "core identity",
            ]
        ):
            warnings.append(f"Block '{bid}' mixes style with identity naming")

        headings = re.findall(r"^(?:##|###)\s", b.get("content", ""), re.MULTILINE)
        if len(headings) >= 2 and block_role != "pack":
            errors.append(
                f"Block '{bid}' contains multiple headings ({len(headings)}), "
                "which violates the single-responsibility rule (must be split or structured as a template)."
            )

        if re.search(r"\bpanel\s+\d+\b", content):
            errors.append(
                f"Block '{bid}' contains concrete panel markers, "
                "which violates the reusability rule (cannot contain concrete session/panel references)."
            )

        list_items = re.findall(r"^\s*[\*\-]\s", b.get("content", ""), re.MULTILINE)
        if len(list_items) >= 7 and block_role != "pack":
            warnings.append(
                f"Block '{bid}' contains too many list items ({len(list_items)}), "
                "which suggests it might be a packed block that should be split."
            )

    # 4. Pack size check
    for bid, block in block_by_id.items():
        if block.get("role") != "pack":
            continue
        lines = [line for line in block.get("content", "").splitlines() if line.strip()]
        if len(lines) > 10:
            errors.append(f"Pack block '{bid}' has too many lines: {len(lines)}")
        elif len(lines) > 5:
            warnings.append(f"Pack block '{bid}' should be split: {len(lines)} lines")

    # 5. Template / block structure checks
    used_block_ids = {bid for t in templates for bid in t.get("blocks", [])}
    unused_blocks = sorted(bid for bid in block_ids if bid not in used_block_ids)
    if unused_blocks:
        warnings.append(f"Unused blocks: {len(unused_blocks)}")

    for b in blocks:
        bid = b.get("id", "")
        if b.get("role") == "pack" and (
            bid in SUSPICIOUS_BROAD_PACK_NAMES
            or (bid.endswith("_pack") and bid.replace("_pack", "") in SUSPICIOUS_BROAD_PACK_NAMES)
        ):
            warnings.append(f"Suspicious broad pack name: {bid}")

    # 6. Result Reporting
    print("--- DB Audit Report ---")
    print(f"Templates: {len(templates)}, Blocks: {len(blocks)}")

    if errors:
        print("\n[ERRORS]")
        for e in errors:
            print(f"  - {e}")

    if warnings:
        print("\n[WARNINGS]")
        for w in warnings:
            print(f"  - {w}")

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
