import json
from pathlib import Path

def find_semantic_overlap():
    db_path = Path("/home/kafka/projects/prompt-vault/db/prompts.json")
    with open(db_path, "r", encoding="utf-8") as f:
        db = json.load(f)

    blocks = db.get("blocks", [])
    inclusions = []
    
    # 1. Check for content inclusion
    for i, b1 in enumerate(blocks):
        c1 = b1.get("content", "").strip()
        if len(c1) < 10: continue # Skip too short fragments
        
        for j, b2 in enumerate(blocks):
            if i == j: continue
            c2 = b2.get("content", "").strip()
            
            if c1 in c2 and c1 != c2:
                inclusions.append({
                    "child": b1["id"],
                    "parent": b2["id"],
                    "content_length_ratio": len(c1) / len(c2)
                })

    # 2. Check for title similarity (simple prefix/suffix match)
    title_matches = []
    for i, b1 in enumerate(blocks):
        t1 = b1.get("title", "")
        for j, b2 in enumerate(blocks):
            if i >= j: continue
            t2 = b2.get("title", "")
            if (t1 in t2 or t2 in t1) and t1 != t2:
                title_matches.append((t1, t2))

    print(f"--- 包含関係 (Inclusion) Found {len(inclusions)} items ---")
    for item in inclusions[:20]: # Show top 20
        print(f"Block '{item['child']}' is included in '{item['parent']}' (Ratio: {item['content_length_ratio']:.2f})")

    print(f"\n--- タイトル類似 (Title Similarity) Found {len(title_matches)} items ---")
    for t1, t2 in title_matches[:20]:
        print(f"'{t1}' <-> '{t2}'")

if __name__ == "__main__":
    find_semantic_overlap()
