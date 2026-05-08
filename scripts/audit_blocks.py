import json
import re
from collections import defaultdict
from pathlib import Path


def audit_blocks():
    db_path = Path(__file__).resolve().parents[1] / "db" / "prompts.json"
    with open(db_path, encoding="utf-8") as f:
        db = json.load(f)

    blocks = db.get("blocks", [])

    # 1. 完全一致の重複 (Exact Duplicates)
    c2i = defaultdict(list)
    for b in blocks:
        content = b.get("content", "")
        norm = re.sub(r"\s+", "", content).lower()
        if norm:
            c2i[norm].append(b)

    exact_duplicates = {n: items for n, items in c2i.items() if len(items) > 1}

    # 2. 包含関係 (Content Inclusion)
    inclusions = []
    for i, b1 in enumerate(blocks):
        c1 = b1.get("content", "").strip()
        if len(c1) < 10:
            continue
        for j, b2 in enumerate(blocks):
            if i == j:
                continue
            c2 = b2.get("content", "").strip()
            if c1 in c2 and c1 != c2:
                inclusions.append((b1["id"], b2["id"]))

    # 3. タイトル類似 (Title Similarity)
    title_matches = []
    for i, b1 in enumerate(blocks):
        t1 = b1.get("title", "")
        for j, b2 in enumerate(blocks):
            if i >= j:
                continue
            t2 = b2.get("title", "")
            if (t1 in t2 or t2 in t1) and t1 != t2:
                title_matches.append((t1, t2))

    # 出力
    print(f"--- 完全一致の重複: {len(exact_duplicates)} 件 ---")
    for norm, items in exact_duplicates.items():
        print(f"IDs: {[i['id'] for i in items]}")

    print(f"\n--- 包含関係 (Inclusion): {len(inclusions)} 件 ---")
    for child, parent in inclusions[:20]:
        print(f"'{child}' is in '{parent}'")

    print(f"\n--- タイトル類似 (Title Similarity): {len(title_matches)} 件 ---")
    for t1, t2 in title_matches[:20]:
        print(f"'{t1}' <-> '{t2}'")


if __name__ == "__main__":
    audit_blocks()
