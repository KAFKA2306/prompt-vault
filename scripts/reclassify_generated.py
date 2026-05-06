import json
from pathlib import Path

def reclassify():
    db_path = Path("/home/kafka/projects/prompt-vault/db/prompts.json")
    with open(db_path, "r", encoding="utf-8") as f:
        db = json.load(f)

    # Keyword mapping
    mapping = {
        "stamp": ["スタンプ", "もぐもぐ", "返信ぎゅっ"],
        "social": ["朝", "ごはん", "タイム", "光", "水やり", "読書", "ひととき", "身支度", "ストレッチ", "温泉シャーク", "おはツイ", "カーテン", "勝利", "ドミニオン"],
        "design_sheet": ["比較", "対比", "見比べ", "サンプル", "Portfolio", "Overview", "Reference", "Notes", "Sheet", "Workbench", "Avatar", "VRChat", "Check"],
        "announcement": ["告知", "Guide", "Update", "点検", "分岐案内", "案内"],
        "reaction": ["コメント返し", "返信", "指差し説明"],
        "comic": ["Monogatari", "Comic", "漫画"],
        "news": ["ニュース"],
        "brand": ["Logo", "Icon", "Brand"],
    }

    count = 0
    for t in db.get("templates", []):
        if t.get("kind") == "generated":
            title = t.get("title", "")
            new_kind = None
            
            for kind, keywords in mapping.items():
                if any(k in title for k in keywords):
                    new_kind = kind
                    break
            
            if not new_kind:
                # Default to social if no keyword matches
                new_kind = "social"
            
            t["kind"] = new_kind
            count += 1

    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    
    print(f"Reclassified {count} templates.")

if __name__ == "__main__":
    reclassify()
