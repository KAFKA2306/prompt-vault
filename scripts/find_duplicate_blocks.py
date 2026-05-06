import json
import re
from collections import defaultdict
from pathlib import Path

def find_duplicates():
    db_path = Path("db/prompts.json")
    with open(db_path, "r", encoding="utf-8") as f:
        db = json.load(f)

    c2i = defaultdict(list)
    for b in db.get("blocks", []):
        content = b.get("content", "")
        # Normalize: remove all whitespace and lowercase
        norm = re.sub(r"\s+", "", content).lower()
        if norm:
            c2i[norm].append(b)

    duplicates = {n: items for n, items in c2i.items() if len(items) > 1}
    
    if not duplicates:
        print("完全な重複 Block は見つかりませんでした。")
        return

    print(f"{len(duplicates)} 組の重複 Block が見つかりました：\n")
    for norm, items in duplicates.items():
        ids = [i["id"] for i in items]
        titles = [i["title"] for i in items]
        print(f"IDs: {ids}")
        print(f"Titles: {titles}")
        snippet = items[0]["content"][:100].replace("\n", "\\n")
        print(f"Content: {snippet}...\n")

if __name__ == "__main__":
    find_duplicates()
