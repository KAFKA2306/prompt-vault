import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from _bootstrap import ROOT
from config import CONFIG
from src.artifact_ops import next_artifact_number, slugify
from src.db_io import load_json_db, save_json_db

DB_PATH = ROOT / CONFIG["paths"]["db"]
ARTIFACTS_PATH = ROOT / CONFIG["paths"]["artifacts"]
ORPHANED_PATH = ROOT / CONFIG["paths"]["orphaned_artifacts"]


def make_generated_prompt(title: str, purpose: str, summary: str, kind: str) -> str:
    asset_type = {
        "design_sheet": "design sheet",
        "sheet": "reference sheet",
        "social": "social post illustration",
    }.get(kind, "illustration")
    return "\n".join(
        [
            "Use case: stylized-concept",
            f"Asset type: {asset_type}",
            f"Primary request: {title}. {purpose} {summary}".strip(),
            "Composition: clean layout, mobile readable, tidy margins",
            "Rendering: polished anime illustration, soft pastel lighting, crisp linework, no clutter",
            "Negative: blurry text, broken hands, extra fingers, warped composition, watermark, low resolution",
        ]
    )


NEW_TEMPLATE_SPECS = {
    "boardgame_001_yokohama_duel": {
        "title": "ボードゲームシリーズ: 001 ヨコハマデュエル",
        "kind": "social",
        "purpose": "ヨコハマデュエルの港町の駆け引きを、レトロな交易感で見せる",
        "summary": "港町の商人、資源、古い地図で、静かな競り合いの空気を出す。",
        "blocks": [
            "master_style",
            "character_kafka",
            "boardgame_social_layout",
            "bg_outfit_retro",
            "bg_scene_retro",
            "clean_quality_rendering",
            "negative_common",
        ],
    },
    "boardgame_003_splendor_marvel": {
        "title": "ボードゲームシリーズ: 003 スプレンダー マーベル",
        "kind": "social",
        "purpose": "スプレンダー マーベルのきらめく競り感を、ヒーロー感のある卓上で見せる",
        "summary": "宝石とヒーローカードを並べて、きらめく競りの空気を出す。",
        "blocks": [
            "master_style",
            "character_kafka",
            "boardgame_social_layout",
            "background_splendor_table",
            "splendor_game_text_pack",
            "clean_quality_rendering",
            "negative_common",
        ],
    },
    "boardgame_011_power_grid": {
        "title": "ボードゲームシリーズ: 011 パワーグリッド",
        "kind": "social",
        "purpose": "パワーグリッドの送電網づくりを、工業的な卓上感で見せる",
        "summary": "送電線、資源、都市のつながりで、運営の緊張感を出す。",
        "blocks": [
            "master_style",
            "character_kafka",
            "boardgame_social_layout",
            "bg_outfit_industrial",
            "bg_scene_industrial",
            "clean_quality_rendering",
            "negative_common",
        ],
    },
    "indoor_plant_watering": {
        "title": "室内の植物に水やり",
        "kind": "social",
        "purpose": "室内の観葉植物に水やりする静かな朝の習慣を、やわらかな生活感で見せる",
        "summary": "窓辺の光、水差し、葉のつやで、落ち着いた部屋の空気を出す。",
        "blocks": [
            "master_style",
            "character_kafka",
            "layout_social_square",
            "morning_pose_plants_kafka",
            "morning_home_outfit_kafka",
            "rendering_soft_standard",
            "negative_common",
        ],
    },
    "boardgame_party_table": {
        "title": "ボードゲームパーティー卓",
        "kind": "social",
        "purpose": "みんなで囲むボードゲーム卓のにぎやかさを、家の遊び場の空気で見せる",
        "summary": "ピザ、玩具、カード、タイルで、遊び場の楽しい散らかり感を出す。",
        "blocks": [
            "master_style",
            "character_kafka",
            "boardgame_social_layout",
            "bg_scene_casual",
            "bg_outfit_sporty",
            "clean_quality_rendering",
            "negative_common",
        ],
    },
    "airport_orchard_travel_scene": {
        "title": "空港の森の旅景",
        "kind": "social",
        "purpose": "空港の森の中を歩く旅の場面を、静かな休息感で見せる",
        "summary": "ガラス屋根、樹木、水辺、旅人で、移動中の休息感を出す。",
        "blocks": [
            "master_style",
            "character_kafka",
            "layout_social_square",
            "rendering_soft_standard",
            "negative_common",
        ],
    },
    "airport_orchard_infographic": {
        "title": "空港の森インフォグラフィック",
        "kind": "design_sheet",
        "purpose": "空港の森の規模と特徴を、見やすい図解で整理する",
        "summary": "樹木数、植栽面積、自然光の構造を、見やすい図版にまとめる。",
        "blocks": [
            "source_research",
            "layout_social_square",
            "rendering",
            "text_japanese_labels",
            "negative_common",
        ],
    },
    "unity_material_sheet": {
        "title": "Kafka Unity材質シート",
        "kind": "design_sheet",
        "purpose": "Kafka の Unity 3D モデル用テクスチャとマテリアルを見やすく整理する",
        "summary": "ベースカラー、法線、ORM、顔、髪、衣装を分かりやすく並べる。",
        "blocks": [
            "character_kafka",
            "layout_character_sheet",
            "rendering_soft_infographic",
            "negative_common",
        ],
    },
    "udonsharp_agent_skill_sheet": {
        "title": "UdonSharp エージェントスキル実例集",
        "kind": "design_sheet",
        "purpose": "UdonSharp の実例と避けるべき構文を、VRChat 実装向けに整理する",
        "summary": "同期、イベント、同期付きカウンターなどの基本例と禁止事項をまとめる。",
        "blocks": [
            "layout_social_square",
            "rendering_soft_infographic",
            "text_japanese_labels",
            "negative_common",
        ],
    },
}


ATTACHMENTS = [
    ("001_yokohama_duel.png", "boardgame_001_yokohama_duel", "ボードゲームシリーズ: 001 ヨコハマデュエル"),
    ("002_fort.png", "boardgame_002_fort", "ボードゲームシリーズ: 002 フォート"),
    ("003_splendor_marvel.png", "boardgame_003_splendor_marvel", "ボードゲームシリーズ: 003 スプレンダー マーベル"),
    (
        "004_little_town_builders.png",
        "boardgame_004_little_town_builders",
        "ボードゲームシリーズ: 004 リトルタウンビルダーズ",
    ),
    ("005_tornado_splash.png", "boardgame_005_tornado_splash", "ボードゲームシリーズ: 005 トーネードスプラッシュ"),
    ("006_fearless.png", "boardgame_006_fearless", "ボードゲームシリーズ: 006 フィアーレス"),
    ("007_slide.png", "boardgame_007_slide", "ボードゲームシリーズ: 007 スライド"),
    ("008_eleven.png", "boardgame_008_eleven", "ボードゲームシリーズ: 008 イレブン"),
    ("009_beasty_bar.png", "boardgame_009_beasty_bar", "ボードゲームシリーズ: 009 ビースティーバー"),
    ("010_bet_on.png", "boardgame_010_bet_on", "ボードゲームシリーズ: 010 ベットオン"),
    ("011_power_grid.png", "boardgame_011_power_grid", "ボードゲームシリーズ: 011 パワーグリッド"),
    ("012_mind_space.png", "boardgame_012_mind_space", "ボードゲームシリーズ: 012 マインドスペース"),
    ("013_gomojin.png", "boardgame_013_gomojin", "ボードゲームシリーズ: 013 ゴモジン"),
    ("014_strike.png", "boardgame_014_strike", "ボードゲームシリーズ: 014 ストライク"),
    ("015_nana.png", "boardgame_015_nana", "ボードゲームシリーズ: 015 ナナ"),
    ("016_ra.png", "boardgame_016_ra", "ボードゲームシリーズ: 016 ラー"),
    ("017_wie_verhext.png", "boardgame_017_wie_verhext", "ボードゲームシリーズ: 017 魔法にかかったみたい"),
    ("018_project_l.png", "boardgame_018_project_l", "ボードゲームシリーズ: 018 プロジェクトL"),
    ("019_teiji_taisha.png", "boardgame_019_teiji_taisha", "ボードゲームシリーズ: 019 定時退社"),
    ("020_sugoroku_kabuuru.png", "boardgame_020_sugoroku_kabuuru", "ボードゲームシリーズ: 020 すごろくかぶーる"),
    ("091_indoor_plant_watering.png", "indoor_plant_watering", "室内の植物に水やり"),
    ("092_boardgame_party_table.png", "boardgame_party_table", "ボードゲームパーティー卓"),
    ("093_cardgame_token_layout.png", "cardgame_post", "カードゲーム投稿"),
    ("094_airport_orchard_travel_scene.png", "airport_orchard_travel_scene", "空港の森の旅景"),
    ("095_airport_orchard_infographic.png", "airport_orchard_infographic", "空港の森インフォグラフィック"),
    ("096_art_direction_desk_review.png", "tweet_backed_prompt_index", "Kafka ツイート根拠プロンプト一覧"),
    ("096_rendering_quality_check.png", "artifact_rendering_quality_check_20260505", "Rendering Quality Check"),
    (
        "097_rendering_quality_check_contrast.png",
        "artifact_rendering_quality_check_20260505",
        "Rendering Quality Check",
    ),
    ("105_tweetsdb_idea_map.png", "tweet_backed_prompt_index", "Kafka ツイート根拠プロンプト一覧"),
    ("106_tweetsdb_generate_map.png", "tweet_backed_prompt_index", "Kafka ツイート根拠プロンプト一覧"),
    ("107_tweetsdb_idea_concrete_map.png", "tweet_backed_prompt_index", "Kafka ツイート根拠プロンプト一覧"),
    ("117_life_portfolio_flowchart.png", "artifact_life_portfolio_overview_20260505", "Life Portfolio Overview"),
    ("12f03b7d-2287-4bf9-abb4-58783d7eee14.png", "character_design_sheet", "キャラデザインシートの実例"),
    ("1cb88245-4419-467c-bee2-a2518705e6b5.png", "unity_material_sheet", "Kafka Unity材質シート"),
    ("35252367-49d9-4f4c-bf9f-42aaf06fd69e.png", "character_design_sheet", "キャラデザインシートの別実例"),
    ("3f6378f3-d746-4062-8639-9ede58bcc12f.png", "character_design_sheet", "キャラデザインシートの追加実例"),
    ("42378e8d-91e6-49b2-8b29-180151dfdcf5.png", "character_design_sheet", "キャラデザインシートの実例"),
    ("6e70ebcd-0be8-460d-92ae-d7cc9aff789e.png", "character_design_sheet", "キャラデザインシートの追加実例"),
    ("8bcd5bf8-1197-4e4e-ad6f-85acc4520429.png", "character_design_sheet", "キャラデザインシートの別実例"),
    ("ChatGPT Image 2026年5月7日 09_08_30.png", "character_design_sheet", "キャラデザインシートの追加実例"),
    ("ChatGPT Image 2026年5月7日 09_28_48.png", "character_design_sheet", "キャラデザインシートの追加実例"),
    ("ChatGPT Image 2026年5月7日 09_36_51.png", "character_design_sheet", "キャラデザインシートの追加実例"),
    ("ChatGPT Image 2026年5月7日 12_01_20.png", "character_design_sheet", "キャラデザインシートの追加実例"),
    ("ChatGPT Image 2026年5月7日 12_09_35.png", "character_design_sheet", "キャラデザインシートの追加実例"),
    ("ChatGPT Image 2026年5月7日 12_12_49.png", "character_design_sheet", "キャラデザインシートの追加実例"),
    ("ChatGPT Image 2026年5月7日 12_29_07.png", "character_design_sheet", "キャラデザインシートの追加実例"),
    ("ChatGPT Image 2026年5月7日 18_17_10.png", "character_design_sheet", "キャラデザインシートの追加実例"),
    ("ChatGPT Image 2026年5月7日 18_19_17.png", "character_design_sheet", "キャラデザインシートの追加実例"),
    ("ChatGPT Image 2026年5月7日 18_34_25.png", "character_design_sheet", "キャラデザインシートの追加実例"),
    ("ChatGPT Image 2026年5月7日 18_38_38.png", "character_design_sheet", "キャラデザインシートの追加実例"),
    ("ChatGPT Image 2026年5月7日 18_41_06.png", "character_design_sheet", "キャラデザインシートの追加実例"),
    ("ChatGPT Image 2026年5月7日 18_43_05.png", "character_design_sheet", "キャラデザインシートの追加実例"),
    ("a16dc618-c503-4c73-b8aa-ca4d5ac5a011.png", "character_design_sheet", "キャラデザインシートの実例"),
    ("d3e3c484-48c9-4648-ab85-e7eeb6d95d14.png", "udonsharp_agent_skill_sheet", "UdonSharp エージェントスキル実例集"),
    ("def62011-c07c-4f5e-8e96-4a050a056a98.png", "bake_off_japan_news", "ベイクオフ・ジャパン紹介ニュースの実例"),
    ("e726d207-4ccd-437b-8a95-afa8e87fc22b.png", "character_design_sheet", "キャラデザインシートの別実例"),
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Reconnect unconnected PNGs into artifacts/ and db/prompts.json.")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show planned changes without moving files or writing DB"
    )
    args = parser.parse_args()

    db = load_json_db(DB_PATH)

    templates = db.setdefault("templates", [])
    template_by_id = {t["id"]: t for t in templates if isinstance(t, dict) and t.get("id")}

    planned_templates = []
    for template_id, spec in NEW_TEMPLATE_SPECS.items():
        if template_id in template_by_id:
            continue
        planned_templates.append(template_id)
        templates.append(
            {
                "id": template_id,
                "title": spec["title"],
                "blocks": spec["blocks"],
                "kind": spec["kind"],
                "purpose": spec["purpose"],
                "summary": spec["summary"],
                "artifacts": [],
                "generated_prompt": make_generated_prompt(
                    spec["title"], spec["purpose"], spec["summary"], spec["kind"]
                ),
                "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            }
        )
        template_by_id[template_id] = templates[-1]

    next_number = next_artifact_number()
    moved = []
    planned_moves = []

    for source_name, template_id, artifact_title in ATTACHMENTS:
        source = ORPHANED_PATH / source_name
        destination = ARTIFACTS_PATH / f"{next_number:03d}_{slugify(Path(source_name).stem)}.png"
        next_number += 1

        template = template_by_id.get(template_id)
        if template is None:
            sys.stderr.write(f"ERROR: missing template for {source_name}: {template_id}\n")
            return 1

        arts = template.setdefault("artifacts", [])
        artifact_path = f"artifacts/{destination.name}"
        if any(a.get("path") == artifact_path for a in arts if isinstance(a, dict)):
            continue

        if source.exists():
            planned_moves.append((source_name, destination.name, template_id))
            if not args.dry_run:
                shutil.move(str(source), str(destination))
        elif args.dry_run:
            planned_moves.append((source_name, destination.name, template_id))
        elif not destination.exists():
            sys.stderr.write(f"ERROR: source not found: {source}\n")
            return 1

        arts.append({"path": artifact_path, "title": artifact_title})
        moved.append(destination.name)

    if args.dry_run:
        print("Dry run: no files were moved and no DB changes were written.")
        if planned_templates:
            print("Would add templates:")
            for template_id in planned_templates:
                print(f"  {template_id}")
        if planned_moves:
            print("Would reconnect:")
            for source_name, destination_name, template_id in planned_moves:
                print(f"  {source_name} -> {destination_name} ({template_id})")
        return 0

    save_json_db(DB_PATH, db)

    subprocess.run([sys.executable, "build.py"], cwd=ROOT, check=True)
    subprocess.run([sys.executable, "scripts/validate_db.py"], cwd=ROOT, check=True)

    print("Reconnected:")
    for name in moved:
        print(f"  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
