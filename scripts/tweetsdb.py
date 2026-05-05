#!/usr/bin/env python3
from __future__ import annotations

import argparse
import itertools
import json
import math
import re
import zipfile
from collections import Counter
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

try:
    from fugashi import Tagger
except Exception:  # pragma: no cover - optional dependency
    Tagger = None


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "db" / "tweetsdb.json"
ARCHIVE_PATH = (
    ROOT / "artifacts" / "twitter-2026-05-02-741b09a4d07b6875e14faaed1104872c99f2c1d9574872876fd3d2342d11756c.zip"
)


AI_PATTERN = re.compile(
    r"(?:\bai\b|生成ai|人工知能|chatgpt|openai|gpt|llm|gemini|claude|copilot|prompt)", re.IGNORECASE
)
IMAGEGEN_PATTERN = re.compile(
    r"(画像生成|aiイラスト|イラスト生成|stable diffusion|stablediffusion|sdxl|sd1\.5|midjourney|dall[- ]?e|comfyui|controlnet|img2img|i2i|t2i|text2image|waifu[- ]?diffusion|automatic1111|webui|novelai|novel ai|lora|vae)",
    re.IGNORECASE,
)
URL_RE = re.compile(r"https?://\S+")
MENTION_RE = re.compile(r"@([A-Za-z0-9_]+)")
TOKEN_RE = re.compile(r"[A-Za-z0-9_]+|[一-龯ぁ-んァ-ヶー]+")

ANALYSIS_VERSION = 2
_TAGGER: Any | None = None

TOPIC_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("vrchat-events", ("集会", "周年", "meetup", "event", "anniversary", "host", "ホスト", "告知", "お知らせ")),
    (
        "vrchat-avatar-mod",
        (
            "modular avatar",
            "expressionsmenu",
            "expressions menu",
            "shape changer",
            "menu item",
            "menu installer",
            "色改変",
            "衣装改変",
            "アバター改変",
            "改変",
            "着せ替え",
        ),
    ),
    (
        "vrchat-worlds",
        (
            "madewithvrchat",
            "world travel",
            "world tour",
            "worlds",
            "ワールド",
            "vket",
            "世界旅行",
            "ワールド巡り",
            "ホームワールド",
        ),
    ),
    ("vrchat-mobile", ("vrchat android", "vrchat mobile", "推奨スマホ", "スマホ", "mocopi")),
    (
        "creator-tools",
        (
            "blender",
            "unity",
            "c#",
            "dll",
            "script",
            "api",
            "workflow",
            "gradio",
            "kohya",
            "sd-scripts",
            "github",
            "template",
            "automation",
        ),
    ),
    ("finance-tax", ("tax", "税", "確定申告", "ふるさと納税", "住民税", "所得税", "税関", "納税", "e-tax", "etax")),
    ("finance-jp", ("boj", "日銀", "nisa", "株", "円", "carry", "投機", "金利", "market")),
    (
        "shopping-gadgets",
        (
            "aliexpress",
            "power bank",
            "charger",
            "amazon",
            "ガジェット",
            "充電器",
            "バッテリー",
            "ロボット掃除機",
            "pico",
            "quest",
            "hmd",
            "スマホ",
        ),
    ),
    (
        "music-listening",
        ("playlist", "music", "音楽", "alexa", "spotify", "sound", "カラオケ", "歌詞", "イヤホン", "ヘッドホン", "BGM"),
    ),
    (
        "travel-real-world",
        (
            "travel",
            "旅行",
            "旅",
            "tokyo",
            "京都",
            "kyoto",
            "北海道",
            "hokkaido",
            "沖縄",
            "okinawa",
            "venice",
            "観光",
            "空港",
            "hotel",
            "flight",
            "tour",
        ),
    ),
    (
        "food-drink",
        (
            "food",
            "ごはん",
            "ご飯",
            "食べる",
            "食べ",
            "料理",
            "coffee",
            "cafe",
            "breakfast",
            "dinner",
            "mogumogu",
            "コーヒー",
            "お茶",
            "夕食",
            "朝食",
            "飲み",
            "飲む",
            "食事",
        ),
    ),
    (
        "sleep-morning",
        (
            "おはよ",
            "おはよう",
            "おはしゃふ",
            "おはかふ",
            "おはツイ",
            "おやすみ",
            "sleep",
            "眠い",
            "寝る",
            "起床",
            "早起き",
            "morning",
            "sleepy",
            "朝活",
        ),
    ),
    ("weather-mood", ("rain", "雨", "weather", "天気", "寒い", "暑い", "花粉", "曇り", "雪", "気温", "台風", "暴風")),
    (
        "art-illustration",
        (
            "illustration",
            "drawing",
            "draw",
            "illustrator",
            "イラスト",
            "お絵かき",
            "描いた",
            "描いて",
            "sketch",
            "絵描き",
            "AIイラスト",
        ),
    ),
    (
        "games",
        ("boardgame", "board game", "麻雀", "マダミス", "trpg", "poker", "dominion", "splendor", "ゲーム", "カード"),
    ),
    ("unity", ("unity", "blender", "c#", "dll", "agent", "skill")),
    ("travel", ("travel", "旅", "tokyo", "京都", "kyoto", "北海道", "hokkaido", "沖縄", "okinawa", "venice", "観光")),
    (
        "food",
        (
            "food",
            "ごはん",
            "ご飯",
            "食べる",
            "食べ",
            "料理",
            "coffee",
            "cafe",
            "breakfast",
            "dinner",
            "mogumogu",
            "コーヒー",
            "お茶",
            "食事",
        ),
    ),
    ("finance", ("finance", "market", "boj", "日銀", "tax", "税", "株", "press")),
    (
        "daily-life",
        ("日常", "生活", "通勤", "騒音", "花粉", "くしゃみ", "家事", "ルーティン", "おでかけ", "疲れ", "体調", "眠気"),
    ),
]

ENTITY_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("ChatGPT", ("chatgpt", "openai", "gpt", "llm", "生成ai", "人工知能")),
    ("VRChat", ("vrchat", "vrc", "udon")),
    ("VRChat Android", ("vrchat android", "vrchat mobile", "android")),
    (
        "Modular Avatar",
        (
            "modular avatar",
            "ma object toggle",
            "ma menu item",
            "ma menu installer",
            "ma shape changer",
            "expressionsmenu",
        ),
    ),
    ("Unity", ("unity",)),
    ("Blender", ("blender",)),
    ("Kafka", ("kafka", "かふか", "しゃふか")),
    ("AliExpress", ("aliexpress",)),
    ("Alexa", ("alexa",)),
    ("BOJ", ("boj", "日銀", "日本銀行")),
    ("NISA", ("nisa",)),
    ("Dominion", ("dominion",)),
    ("Splendor", ("splendor",)),
    ("Poker", ("poker", "ポーカー")),
    ("Mahjong", ("麻雀",)),
    ("TRPG", ("trpg", "マダミス", "マーダーミステリー")),
    ("Kohya", ("kohya", "sd-scripts")),
    ("Wizz Air", ("wizz air",)),
]

TOPIC_ESSENCE_PHRASES: dict[str, str] = {
    "ai": "AI/tool behavior",
    "ai-imagegen": "AI image-generation behavior",
    "art-illustration": "art or illustration behavior",
    "creator-tools": "creator tooling",
    "daily-life": "daily-life observation",
    "finance": "finance or policy commentary",
    "finance-tax": "tax or filing commentary",
    "finance-jp": "Japan-focused finance commentary",
    "food": "food or sensory observation",
    "food-drink": "food or drink observation",
    "games": "game play or game design",
    "music-listening": "music listening habit",
    "shopping-gadgets": "shopping or gadget discovery",
    "sleep-morning": "morning or sleep routine",
    "social": "social interaction",
    "travel": "travel or place observation",
    "travel-real-world": "real-world travel or place observation",
    "unity": "creator tooling",
    "vrchat-avatar-mod": "VRChat avatar modification",
    "vrchat-events": "VRChat event or meetup behavior",
    "vrchat-mobile": "VRChat mobile behavior",
    "vrchat-social": "VRChat social behavior",
    "vrchat-technical": "VRChat technical behavior",
    "vrchat-worlds": "VRChat world exploration",
    "weather-mood": "weather-shaped mood",
    "misc": "general observation",
}

TOPIC_PROMPT_FRAGMENTS: dict[str, str] = {
    "ai": "AI tool surprise",
    "ai-imagegen": "AI image-generation note",
    "art-illustration": "art or illustration note",
    "creator-tools": "creator workflow note",
    "daily-life": "everyday life observation",
    "finance": "market commentary note",
    "finance-tax": "tax or filing note",
    "finance-jp": "Japan finance commentary note",
    "food": "food and sensation note",
    "food-drink": "food or drink note",
    "games": "gameplay observation",
    "music-listening": "music listening note",
    "shopping-gadgets": "shopping discovery note",
    "sleep-morning": "morning routine note",
    "social": "reply or social reaction",
    "travel": "travel mood note",
    "travel-real-world": "real-world travel note",
    "unity": "creator workflow note",
    "vrchat-avatar-mod": "VRChat avatar-mod note",
    "vrchat-events": "VRChat event note",
    "vrchat-mobile": "VRChat mobile note",
    "vrchat-social": "VRChat social note",
    "vrchat-technical": "VRChat technical note",
    "vrchat-worlds": "VRChat world note",
    "weather-mood": "weather mood note",
    "misc": "short personal observation",
}

TOPIC_IMAGEGEN_FRAGMENTS: dict[str, str] = {
    "ai": "a small visual metaphor for an AI tool exceeding expectations",
    "ai-imagegen": "a small visual metaphor for AI image generation",
    "art-illustration": "an illustration studio scene with sketching tools",
    "creator-tools": "a creator desk with tools and iteration notes",
    "daily-life": "an everyday moment with mood and weather",
    "finance": "an infographic-like commentary scene",
    "finance-tax": "a tax or filing paperwork scene",
    "finance-jp": "a Japan finance commentary scene",
    "food": "a sensory scene centered on food or drink",
    "food-drink": "a food or drink scene with tactile detail",
    "games": "a game table or game room with expressive tension",
    "music-listening": "a listening scene with speakers or headphones",
    "shopping-gadgets": "a gadget discovery scene with packaging and small objects",
    "sleep-morning": "a sleepy morning scene with soft light",
    "social": "a small conversational scene",
    "travel": "a place-driven scene with travel atmosphere",
    "travel-real-world": "a real-world travel scene with place atmosphere",
    "unity": "a creator desk with tools and iteration notes",
    "vrchat-avatar-mod": "a VRChat avatar customization desk scene",
    "vrchat-events": "a VRChat gathering scene with people and signage",
    "vrchat-mobile": "a VRChat mobile scene on a phone screen",
    "vrchat-social": "a cozy VRChat social scene",
    "vrchat-technical": "a VRChat setup scene with menus, tools, and logs",
    "vrchat-worlds": "a VRChat world exploration scene",
    "weather-mood": "an everyday weather scene with atmosphere",
    "misc": "a compact scene built from a fleeting daily observation",
}

TOPIC_TRAIT_HINTS: dict[str, tuple[str, ...]] = {
    "ai-imagegen": ("tool-aware",),
    "art-illustration": ("visual",),
    "creator-tools": ("creator-aware", "tool-aware"),
    "finance-tax": ("admin",),
    "finance-jp": ("market-aware",),
    "food-drink": ("sensory",),
    "music-listening": ("sensory",),
    "shopping-gadgets": ("discovery-oriented",),
    "sleep-morning": ("everyday-observation",),
    "travel-real-world": ("place-aware",),
    "vrchat-avatar-mod": ("creator-aware", "tool-aware"),
    "vrchat-events": ("social",),
    "vrchat-mobile": ("tool-aware",),
    "vrchat-social": ("social",),
    "vrchat-technical": ("creator-aware", "tool-aware"),
    "vrchat-worlds": ("place-aware",),
    "weather-mood": ("everyday-observation",),
}

FRUSTRATION_WORDS = ("苦手", "たいへん", "ややこしい", "無理", "こわい", "難しい", "止まる", "止ま", "困る", "issue")
CHEERFUL_WORDS = ("うれしい", "よかった", "楽しい", "好き", "最高", "いいね", "いい", "嬉しい")
SURPRISE_WORDS = ("びっくり", "すごい", "えっ", "まじ", "初期", "止まる気配", "想定外")
PLAYFUL_WORDS = ("w", "笑", "めっちゃ", "かわいい", "かわ", "ww", "！")
REFLECTIVE_WORDS = ("考え", "思う", "観察", "気づき", "気づいた", "なぜ", "理論", "わかる")
SLEEPY_WORDS = ("眠", "寝", "朝", "おやすみ", "sleepy")
PROCESS_WORDS = ("進捗", "作業", "起動", "作った", "できた", "やってる", "build", "まとめ", "メモ")
ANNOUNCE_WORDS = ("お知らせ", "告知", "配信", "開始", "新衣装", "重大告知")
SENSORY_WORDS = ("音", "光", "匂", "にお", "味", "食", "寒", "暑", "雨", "風", "窓", "coffee", "cafe")
TOPIC_SPECIFICITY: dict[str, float] = {
    "ai": 0.68,
    "ai-imagegen": 0.84,
    "art-illustration": 0.76,
    "creator-tools": 0.8,
    "daily-life": 0.46,
    "finance": 0.56,
    "finance-tax": 0.74,
    "finance-jp": 0.82,
    "food": 0.58,
    "food-drink": 0.72,
    "games": 0.66,
    "music-listening": 0.7,
    "shopping-gadgets": 0.73,
    "sleep-morning": 0.84,
    "social": 0.42,
    "travel": 0.58,
    "travel-real-world": 0.76,
    "unity": 0.62,
    "vrchat-avatar-mod": 0.84,
    "vrchat-events": 0.8,
    "vrchat-mobile": 0.72,
    "vrchat-social": 0.66,
    "vrchat-technical": 0.79,
    "vrchat-worlds": 0.78,
    "weather-mood": 0.66,
    "misc": 0.3,
}
VISUAL_REUSE_TOPICS = {"ai-imagegen", "art-illustration", "vrchat-avatar-mod", "vrchat-events", "vrchat-worlds"}
REFERENCE_REUSE_TOPICS = {"finance-jp", "finance-tax", "travel-real-world", "weather-mood", "finance"}
TEXTUAL_REUSE_TOPICS = {
    "creator-tools",
    "sleep-morning",
    "music-listening",
    "daily-life",
    "social",
    "vrchat-social",
    "vrchat-technical",
    "misc",
}
FACTUAL_REUSE_TOPICS = REFERENCE_REUSE_TOPICS | {"vrchat-events", "vrchat-worlds", "vrchat-mobile", "shopping-gadgets"}
VRCHAT_CONTEXT_WORDS = (
    "avatar",
    "world",
    "worlds",
    "udon",
    "sdk",
    "osc",
    "mocopi",
    "quest",
    "hmd",
    "改変",
    "着せ替え",
    "イベント",
    "集会",
    "ダンス",
    "フィットネス",
    "ボドゲ",
    "ボードゲーム",
    "ライブ",
)
VRCHAT_SOCIAL_WORDS = (
    "フレンド",
    "交流",
    "雑談",
    "おしゃべり",
    "会った",
    "会う",
    "遊んだ",
    "遊ぶ",
    "撮影",
    "写真",
    "散歩",
    "飲み",
    "集まり",
    "party",
    "hangout",
    "social",
)
VRCHAT_TECHNICAL_WORDS = (
    "udon",
    "sdk",
    "osc",
    "shader",
    "tracking",
    "tracker",
    "quest",
    "hmd",
    "mocopi",
    "performance",
    "menu",
    "toggle",
    "expression",
    "expressions menu",
    "expressionsmenu",
    "modular avatar",
    "shape changer",
    "build",
    "setup",
    "error",
    "dll",
    "api",
    "code",
)
AI_CONTEXT_WORDS = (
    "image",
    "prompt",
    "gpt",
    "chatgpt",
    "openai",
    "claude",
    "gemini",
    "llm",
    "copilot",
    "api",
    "webui",
    "comfyui",
    "stable diffusion",
    "sdxl",
    "model",
    "generate",
    "生成",
)
FINANCE_MARKET_WORDS = (
    "株",
    "市場",
    "金利",
    "配当",
    "投資",
    "資産",
    "ドル",
    "fomc",
    "boj",
    "日銀",
    "etf",
    "決算",
    "関税",
    "インフレ",
    "景気",
)
TOPIC_SUPERSEDES: dict[str, set[str]] = {
    "ai-imagegen": {"ai"},
    "art-illustration": {"misc"},
    "creator-tools": {"unity"},
    "finance-tax": {"finance"},
    "finance-jp": {"finance"},
    "food-drink": {"food", "daily-life"},
    "shopping-gadgets": {"daily-life"},
    "sleep-morning": {"daily-life"},
    "travel-real-world": {"travel", "daily-life"},
    "vrchat-avatar-mod": {"vrchat-technical", "unity"},
    "vrchat-events": {"vrchat-social", "vrchat-technical", "social"},
    "vrchat-mobile": {"vrchat-technical", "shopping-gadgets"},
    "vrchat-social": {"daily-life"},
    "vrchat-technical": {"vrchat-social"},
    "vrchat-worlds": {"vrchat-social", "vrchat-technical", "travel"},
    "weather-mood": {"daily-life"},
}


def contains_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)


def contains_all(text: str, needles: tuple[str, ...]) -> bool:
    return all(needle in text for needle in needles)


def unique_keep_order(items: list[str]) -> list[str]:
    seen = set()
    ordered = []
    for item in items:
        if item not in seen:
            ordered.append(item)
            seen.add(item)
    return ordered


def has_keyword(keyword: str, analysis: dict[str, Any]) -> bool:
    return keyword_matches_analysis(keyword, analysis)


def has_any_keyword(keywords: tuple[str, ...], analysis: dict[str, Any]) -> bool:
    return any(has_keyword(keyword, analysis) for keyword in keywords)


def has_vrchat_context(analysis: dict[str, Any]) -> bool:
    return has_any_keyword(VRCHAT_CONTEXT_WORDS, analysis)


def has_vrchat_social_context(analysis: dict[str, Any]) -> bool:
    return has_any_keyword(VRCHAT_SOCIAL_WORDS, analysis)


def has_vrchat_technical_context(analysis: dict[str, Any]) -> bool:
    return has_any_keyword(VRCHAT_TECHNICAL_WORDS, analysis)


def has_ai_context(analysis: dict[str, Any]) -> bool:
    return has_any_keyword(AI_CONTEXT_WORDS, analysis)


def has_finance_context(analysis: dict[str, Any]) -> bool:
    return has_any_keyword(FINANCE_MARKET_WORDS, analysis)


def get_analysis_backend() -> str:
    global _TAGGER
    if _TAGGER is None and Tagger is not None:
        try:
            _TAGGER = Tagger()
        except Exception:  # pragma: no cover - optional dependency
            _TAGGER = False
    return "fugashi" if _TAGGER else "regex"


@lru_cache(maxsize=8192)
def analyze_text(text: str) -> dict[str, Any]:
    cleaned = normalize_text(text)
    backend = get_analysis_backend()
    tokens: list[dict[str, str]] = []
    if cleaned and backend == "fugashi" and _TAGGER:
        try:
            for word in _TAGGER(cleaned):
                surface = normalize_text(getattr(word, "surface", "") or "")
                if not surface:
                    continue
                feature = getattr(word, "feature", None)
                lemma = surface
                pos = ""
                if feature is not None:
                    lemma = normalize_text(str(getattr(feature, "lemma", surface) or surface))
                    if lemma == "*" or not lemma:
                        lemma = surface
                    pos = normalize_text(str(getattr(feature, "pos1", "") or getattr(feature, "pos", "") or ""))
                tokens.append({"surface": surface, "lemma": lemma, "pos": pos})
        except Exception:  # pragma: no cover - optional dependency
            tokens = []
            backend = "regex"
    if not tokens:
        backend = "regex"
        tokens = [{"surface": token, "lemma": token.lower(), "pos": ""} for token in TOKEN_RE.findall(cleaned)]
    surfaces = [token["surface"].lower() for token in tokens]
    lemmas = [token["lemma"].lower() for token in tokens]
    return {
        "backend": backend,
        "analysis_version": ANALYSIS_VERSION,
        "normalized_text": cleaned.lower(),
        "surface_text": " ".join(surfaces),
        "lemma_text": " ".join(lemmas),
        "surface_tokens": surfaces,
        "lemma_tokens": lemmas,
        "token_count": len(tokens),
        "lemma_count": len(set(lemmas)),
    }


def keyword_matches_analysis(keyword: str, analysis: dict[str, Any]) -> bool:
    needle = normalize_text(keyword).lower()
    if not needle:
        return False
    if needle in analysis.get("normalized_text", ""):
        return True
    if needle in analysis.get("surface_text", ""):
        return True
    if needle in analysis.get("lemma_text", ""):
        return True
    return needle in set(analysis.get("surface_tokens", [])) or needle in set(analysis.get("lemma_tokens", []))


def analysis_source_label(analysis: dict[str, Any]) -> str:
    return str(analysis.get("backend", "regex"))


def extract_evidence_text(text: str, keywords: list[str], width: int = 140) -> str:
    cleaned = visible_text(text)
    if not cleaned:
        return ""
    lowered = cleaned.lower()
    for keyword in keywords:
        needle = keyword.lower()
        idx = lowered.find(needle)
        if idx >= 0:
            start = max(0, idx - width // 3)
            end = min(len(cleaned), idx + len(keyword) + width // 2)
            return normalize_text(cleaned[start:end])
    return cleaned[:width].rstrip()


def topic_confidence(topic: str, keywords: list[str], kind: str) -> float:
    base = TOPIC_SPECIFICITY.get(topic, 0.5)
    hit_bonus = min(len(keywords), 4) * 0.08
    kind_bonus = 0.0
    if topic in {"social", "misc"} and kind in {"reply", "quote", "retweet"}:
        kind_bonus = 0.08
    if (
        topic in {"ai-imagegen", "vrchat-avatar-mod", "vrchat-events", "vrchat-worlds", "vrchat-technical"}
        and len(keywords) >= 2
    ):
        kind_bonus += 0.06
    return round(max(0.0, min(1.0, base + hit_bonus + kind_bonus)), 3)


def classify_owner_signal(kind: str, self_reference: bool, url_count: int, mention_count: int, topic: list[str]) -> str:
    if kind in {"retweet", "quote"}:
        return "参照"
    if kind == "reply":
        return "他者反応"
    if self_reference:
        return "自分発信"
    if url_count >= 2 or "finance-jp" in topic or "travel-real-world" in topic:
        return "参照"
    if mention_count >= 2:
        return "他者反応"
    return "自分発信"


def classify_reuse_type(record: dict[str, Any]) -> str:
    topic = set(record.get("topic", []))
    kind = record.get("kind", "")
    mood = record.get("mood", "")
    owner_signal = record.get("owner_signal", "自分発信")
    has_media = bool(record.get("has_media"))
    if has_media or topic.intersection(VISUAL_REUSE_TOPICS):
        return "画像"
    if owner_signal == "参照" or kind in {"quote", "retweet"}:
        return "事実参照"
    if kind == "reply" or topic.intersection(TEXTUAL_REUSE_TOPICS) or mood in {"playful", "reflective"}:
        return "文体"
    if mood == "surprised" or kind == "original":
        return "ネタ"
    return "文体"


def classify_observation_mode(record: dict[str, Any]) -> str:
    topic = set(record.get("topic", []))
    if record.get("owner_signal") == "他者反応":
        return "reaction"
    if topic.intersection(VISUAL_REUSE_TOPICS) or record.get("reuse_type") == "画像":
        return "visual"
    if topic.intersection({"travel-real-world", "vrchat-worlds", "vrchat-mobile"}):
        return "place"
    if topic.intersection({"vrchat-social", "vrchat-events"}) and record.get("owner_signal") != "他者反応":
        return "social"
    if topic.intersection({"sleep-morning", "daily-life", "food-drink"}) or record.get("mood") == "sleepy":
        return "routine"
    if topic.intersection(FACTUAL_REUSE_TOPICS) or record.get("reuse_type") == "事実参照":
        return "factual"
    if topic.intersection({"vrchat-technical"}):
        return "tooling"
    if record.get("creator_signal"):
        return "tooling"
    if record.get("sensory_level") in {"medium", "high"}:
        return "sensory"
    return "general"


def build_latent_profile(record: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]:
    topics = record.get("topic", [])
    primary = topics[0] if topics else "misc"
    reuse_type = record.get("reuse_type", "文体")
    prompt_bias = (
        "visual"
        if reuse_type == "画像"
        else "textual"
        if reuse_type == "文体"
        else "factual"
        if reuse_type == "事実参照"
        else "playful"
    )
    return {
        "topic_primary": primary,
        "topic_stack": topics[:4],
        "observation_mode": classify_observation_mode(record),
        "emotion_arc": record.get("mood", "neutral"),
        "speech_role": record.get("owner_signal", "自分発信"),
        "reuse_role": reuse_type,
        "prompt_bias": prompt_bias,
        "topic_confidence": record.get("classification_confidence", 0.0),
        "creator_signal": bool(record.get("creator_signal")),
        "sensory_level": record.get("sensory_level", "low"),
        "self_reference": bool(record.get("self_reference")),
        "analysis_backend": analysis.get("backend", "regex"),
        "analysis_version": analysis.get("analysis_version", ANALYSIS_VERSION),
        "analysis_token_count": analysis.get("token_count", 0),
        "analysis_lemma_count": analysis.get("lemma_count", 0),
    }


def classify_topics(text: str, kind: str, analysis: dict[str, Any] | None = None) -> dict[str, Any]:
    analysis = analysis or analyze_text(text)
    topics: list[str] = []
    topic_evidence: list[dict[str, Any]] = []
    matched_keywords: list[str] = []

    def add_topic(topic: str, keywords: list[str], evidence_label: str | None = None) -> None:
        if topic not in topics:
            topics.append(topic)
        unique_hits = unique_keep_order(keywords)
        matched_keywords.extend(unique_hits)
        topic_evidence.append(
            {
                "topic": topic,
                "matched_keywords": unique_hits,
                "evidence_text": extract_evidence_text(text, unique_hits),
                "confidence": topic_confidence(topic, unique_hits, kind),
                "source": evidence_label or analysis_source_label(analysis),
            }
        )

    ai_hits = [
        kw
        for kw in ("生成ai", "chatgpt", "openai", "gpt", "llm", "gemini", "claude", "copilot", "prompt")
        if keyword_matches_analysis(kw, analysis)
    ]
    if ai_hits:
        add_topic("ai", ai_hits, analysis_source_label(analysis))
    elif has_keyword("ai", analysis) and has_ai_context(analysis):
        add_topic("ai", ["ai"], analysis_source_label(analysis))

    imagegen_hits = []
    if any(
        keyword_matches_analysis(kw, analysis)
        for kw in (
            "画像生成",
            "aiイラスト",
            "イラスト生成",
            "stable diffusion",
            "stablediffusion",
            "sdxl",
            "sd1.5",
            "midjourney",
            "dall-e",
            "comfyui",
            "controlnet",
            "img2img",
            "i2i",
            "t2i",
            "text2image",
            "waifu diffusion",
            "automatic1111",
            "webui",
            "novelai",
            "novel ai",
            "lora",
            "vae",
        )
    ):
        imagegen_hits = [
            kw
            for kw in (
                "画像生成",
                "aiイラスト",
                "イラスト生成",
                "stable diffusion",
                "stablediffusion",
                "sdxl",
                "midjourney",
                "dall-e",
                "comfyui",
                "controlnet",
                "img2img",
                "i2i",
                "t2i",
                "webui",
                "lora",
                "vae",
            )
            if keyword_matches_analysis(kw, analysis)
        ]
        if not imagegen_hits:
            imagegen_hits = ["imagegen"]
        add_topic("ai-imagegen", imagegen_hits, analysis_source_label(analysis))

    for topic, keywords in TOPIC_RULES:
        if topic in {"ai", "ai-imagegen", "social", "finance-tax", "finance", "finance-jp"}:
            continue
        hits = [keyword for keyword in keywords if keyword_matches_analysis(keyword, analysis)]
        if hits:
            add_topic(topic, hits)

    vrchat_anchor_hits = [kw for kw in ("vrchat", "vrc") if keyword_matches_analysis(kw, analysis)]
    if vrchat_anchor_hits and has_vrchat_social_context(analysis):
        social_hits = vrchat_anchor_hits + [kw for kw in VRCHAT_SOCIAL_WORDS if keyword_matches_analysis(kw, analysis)]
        add_topic("vrchat-social", social_hits, analysis_source_label(analysis))

    if vrchat_anchor_hits and has_vrchat_technical_context(analysis):
        technical_hits = vrchat_anchor_hits + [
            kw for kw in VRCHAT_TECHNICAL_WORDS if keyword_matches_analysis(kw, analysis)
        ]
        add_topic("vrchat-technical", technical_hits, analysis_source_label(analysis))

    finance_tax_hits = [
        kw
        for kw in ("tax", "税", "確定申告", "ふるさと納税", "住民税", "所得税", "税関", "納税", "e-tax", "etax")
        if keyword_matches_analysis(kw, analysis)
    ]
    if finance_tax_hits:
        add_topic("finance-tax", finance_tax_hits, analysis_source_label(analysis))

    finance_jp_hits = [
        kw
        for kw in (
            "boj",
            "日銀",
            "nisa",
            "株",
            "carry",
            "投機",
            "金利",
            "market",
            "fomc",
            "etf",
            "投資",
            "資産",
            "配当",
            "決算",
            "関税",
            "インフレ",
            "景気",
        )
        if keyword_matches_analysis(kw, analysis)
    ]
    if finance_jp_hits or (keyword_matches_analysis("円", analysis) and has_finance_context(analysis)):
        add_topic("finance-jp", finance_jp_hits or ["円"], analysis_source_label(analysis))

    finance_hits = [
        kw
        for kw in (
            "finance",
            "market",
            "boj",
            "日銀",
            "nisa",
            "株",
            "円",
            "carry",
            "投機",
            "金利",
            "market",
            "fomc",
            "etf",
            "投資",
            "資産",
            "配当",
            "決算",
            "関税",
            "インフレ",
            "景気",
        )
        if keyword_matches_analysis(kw, analysis)
    ]
    if finance_hits and has_finance_context(analysis):
        add_topic("finance", finance_hits, analysis_source_label(analysis))

    suppressed: set[str] = set()
    for specific_topic in topics:
        suppressed.update(TOPIC_SUPERSEDES.get(specific_topic, set()))
    if suppressed:
        filtered_topics: list[str] = []
        filtered_evidence: list[dict[str, Any]] = []
        for item in topic_evidence:
            if item["topic"] in suppressed:
                continue
            filtered_evidence.append(item)
        for topic in topics:
            if topic not in suppressed:
                filtered_topics.append(topic)
        topics = filtered_topics
        topic_evidence = filtered_evidence
        matched_keywords = unique_keep_order(
            keyword for item in topic_evidence for keyword in item.get("matched_keywords", [])
        )

    matched_keywords = unique_keep_order(matched_keywords)
    classification_confidence = round(max(item["confidence"] for item in topic_evidence), 3) if topic_evidence else 0.0
    return {
        "topics": topics,
        "topic_evidence": topic_evidence,
        "matched_keywords": matched_keywords,
        "classification_confidence": classification_confidence,
    }


def normalize_text(text: str) -> str:
    return " ".join(text.split()).strip()


def text_lc(text: str) -> str:
    return normalize_text(text).lower()


def visible_text(text: str) -> str:
    return normalize_text(URL_RE.sub("", text))


def strip_social_prefix(text: str) -> str:
    return normalize_text(
        re.sub(
            r"^(?:おはかふか〜|おはかふかー|おはかふか|おはかふ！|おはかふ|おはようございます|おはよう|おやすみ〜|おやすみ|ohakafka)\s*",
            "",
            normalize_text(text),
            flags=re.IGNORECASE,
        )
    )


def build_scene_hook(record: dict[str, Any]) -> str:
    text = strip_social_prefix(visible_text(record.get("text", "")))
    text = normalize_text(re.sub(r"#\S+", "", text))
    if not text:
        return ""

    match = re.search(r"^(.+?\s+by\s+[^#\n]+)", text, flags=re.IGNORECASE)
    if match:
        text = match.group(1)
    scene = re.split(r"[。.!！？?\n]", text, maxsplit=1)[0]
    scene = normalize_text(scene)
    if len(scene) < 16 and len(text) > len(scene):
        scene = text[:96]
    return scene[:96]


def parse_created_at(value: str | None) -> tuple[str, str]:
    if not value:
        return "", ""
    dt = datetime.strptime(value, "%a %b %d %H:%M:%S %z %Y").astimezone(UTC)
    return dt.isoformat().replace("+00:00", "Z"), dt.strftime("%Y-%m")


def load_archive_tweets(archive_path: Path) -> list[dict[str, Any]]:
    with zipfile.ZipFile(archive_path) as zf, zf.open("data/tweets.js") as fh:
        text = fh.read().decode("utf-8", errors="replace")
    start = text.find("[")
    end = text.rfind("]")
    if start < 0 or end < start:
        raise ValueError("could not locate JSON array in tweets.js")
    return json.loads(text[start : end + 1])


def extract_urls(tweet: dict[str, Any]) -> list[str]:
    urls = []
    for url in tweet.get("entities", {}).get("urls", []):
        expanded = url.get("expanded_url") or url.get("url")
        if expanded:
            urls.append(expanded)
    return urls


def extract_mentions(tweet: dict[str, Any], text: str) -> list[str]:
    mentions = []
    for mention in tweet.get("entities", {}).get("user_mentions", []):
        screen_name = mention.get("screen_name")
        if screen_name:
            mentions.append(screen_name)
    for handle in MENTION_RE.findall(text):
        if handle not in mentions:
            mentions.append(handle)
    return mentions


def detect_kind(tweet: dict[str, Any], text: str) -> str:
    if text.startswith("RT @") or tweet.get("retweeted_status_id_str") or tweet.get("retweeted_status"):
        return "retweet"
    if tweet.get("quoted_status_id_str") or tweet.get("is_quote_status"):
        return "quote"
    if tweet.get("in_reply_to_status_id_str"):
        return "reply"
    return "original"


def detect_topics(text: str, kind: str) -> list[str]:
    return classify_topics(text, kind)["topics"]


def detect_mood(text: str, kind: str) -> str:
    lc = text_lc(text)
    if any(word in lc for word in FRUSTRATION_WORDS):
        return "frustrated"
    if any(word in lc for word in SLEEPY_WORDS):
        return "sleepy"
    if any(word in lc for word in CHEERFUL_WORDS):
        return "cheerful"
    if any(word in lc for word in SURPRISE_WORDS) or "!" in text or "！" in text:
        return "surprised"
    if any(word in lc for word in REFLECTIVE_WORDS):
        return "reflective"
    if "?" in text or "？" in text or any(word in lc for word in ("なぜ", "どう", "なんで", "what")):
        return "curious"
    if any(word in lc for word in PLAYFUL_WORDS) or kind == "reply":
        return "playful"
    return "neutral"


def detect_function(text: str, kind: str) -> str:
    lc = text_lc(text)
    if kind == "retweet":
        return "RT"
    if kind == "reply":
        return "reply"
    if any(word.lower() in lc for word in ANNOUNCE_WORDS):
        return "announcement"
    if any(word.lower() in lc for word in PROCESS_WORDS):
        return "process_log"
    if "?" in text or "？" in text or lc.endswith("?"):
        return "question"
    if any(word in lc for word in REFLECTIVE_WORDS):
        return "opinion"
    if URL_RE.fullmatch(normalize_text(text)):
        return "note"
    return "observation"


def detect_style(text: str, kind: str, has_media: bool) -> list[str]:
    lc = text_lc(text)
    styles = []
    if len(normalize_text(text)) <= 40:
        styles.append("short")
    if URL_RE.fullmatch(normalize_text(text)) or len(URL_RE.findall(text)) >= 2:
        styles.append("link_only")
    if any(token in lc for token in ("w", "笑", "めっちゃ", "かな", "ねー", "だよ", "だね", "〜")):
        styles.append("casual")
    if any(char.isdigit() for char in text) or any(
        word in lc for word in ("東京", "京都", "北海道", "トランプ", "boj", "unity", "vrchat")
    ):
        styles.append("concrete")
    if AI_PATTERN.search(lc) or any(
        word in lc for word in ("unity", "vrchat", "blender", "api", "code", "dll", "skill", "db")
    ):
        styles.append("technical")
    if kind == "reply":
        styles.append("reply_shaped")
    if has_media:
        styles.append("media_first")
    return styles or ["neutral"]


def detect_self_reference(text: str) -> bool:
    lc = text_lc(text)
    return any(marker in lc for marker in ("かふか", "kafka", "しゃふか"))


def detect_creator_signal(text: str) -> bool:
    lc = text_lc(text)
    return bool(
        AI_PATTERN.search(lc)
        or IMAGEGEN_PATTERN.search(lc)
        or contains_any(
            lc,
            (
                "unity",
                "vrchat",
                "blender",
                "db",
                "api",
                "template",
                "graph",
                "github",
                "code",
                "script",
                "workflow",
                "kohya",
                "sd-scripts",
                "gradio",
                "dll",
            ),
        )
    )


def detect_sensory_level(text: str) -> str:
    lc = text_lc(text)
    score = sum(1 for word in SENSORY_WORDS if word in lc)
    if score >= 3:
        return "high"
    if score >= 1:
        return "medium"
    return "low"


def detect_concreteness(text: str, has_media: bool, urls: int) -> str:
    score = 0
    if has_media:
        score += 1
    if urls:
        score += 1
    if any(char.isdigit() for char in text):
        score += 1
    if any(word in text_lc(text) for word in ("東京", "京都", "北海道", "unity", "vrchat", "boj")) or AI_PATTERN.search(
        text_lc(text)
    ):
        score += 1
    if score >= 3:
        return "high"
    if score >= 1:
        return "medium"
    return "low"


def infer_entities(tweet: dict[str, Any], text: str) -> list[str]:
    lc = text_lc(text)
    entities: list[str] = []
    for entity, keywords in ENTITY_RULES:
        if any(keyword in lc for keyword in keywords):
            entities.append(entity)
    for mention in tweet.get("entities", {}).get("user_mentions", []):
        screen_name = mention.get("screen_name")
        if screen_name and screen_name not in entities:
            entities.append(screen_name)
    for url in extract_urls(tweet):
        host = urlparse(url).netloc
        if host and host not in entities:
            entities.append(host)
    return entities


def build_essence(topic: list[str], function: str, mood: str, creator_signal: bool, kind: str) -> str:
    primary = topic[0] if topic else "misc"
    primary_phrase = TOPIC_ESSENCE_PHRASES.get(
        primary,
        {
            "ai": "AI/tool behavior",
            "misc": "general observation",
        }.get(primary, "general observation"),
    )
    function_phrase = {
        "reply": "reply-shaped reaction",
        "RT": "reshared item",
        "question": "curiosity-driven question",
        "process_log": "process note",
        "announcement": "public update",
        "opinion": "commentary",
        "note": "brief note",
        "observation": "observation",
    }.get(function, "observation")
    mood_phrase = {
        "playful": "light playful tone",
        "curious": "curiosity",
        "reflective": "reflective tone",
        "cheerful": "positive tone",
        "frustrated": "frustration",
        "sleepy": "sleepy tone",
        "surprised": "surprise",
        "neutral": "neutral tone",
    }.get(mood, "neutral tone")
    creator_phrase = "with creator-process signal" if creator_signal else "without creator-process signal"
    if kind == "retweet":
        function_phrase = "reshared item"
    return f"{function_phrase} about {primary_phrase} in a {mood_phrase} {creator_phrase}"


def build_trait_tags(
    topic: list[str], function: str, mood: str, creator_signal: bool, self_reference: bool, kind: str
) -> list[str]:
    tags: list[str] = []
    primary = topic[0] if topic else "misc"
    if kind == "reply":
        tags.append("dialogic")
    if function == "process_log":
        tags.append("process-oriented")
    if mood == "playful":
        tags.append("playful")
    if mood == "reflective":
        tags.append("reflective")
    if mood == "surprised":
        tags.append("surprise-led")
    if creator_signal:
        tags.append("creator-aware")
    if self_reference:
        tags.append("identity-linked")
    if primary in TOPIC_TRAIT_HINTS:
        for hint in TOPIC_TRAIT_HINTS[primary]:
            if hint not in tags:
                tags.append(hint)
    if (
        "ai" in topic
        or "unity" in topic
        or "vrchat-technical" in topic
        or "ai-imagegen" in topic
        or "creator-tools" in topic
        or "vrchat-avatar-mod" in topic
    ) and "tool-aware" not in tags:
        tags.append("tool-aware")
    if (
        "daily-life" in topic or "sleep-morning" in topic or "weather-mood" in topic or "food-drink" in topic
    ) and "everyday-observation" not in tags:
        tags.append("everyday-observation")
    if function in {"observation", "opinion"}:
        tags.append("observational")
    if function == "question":
        tags.append("inquiring")
    return tags[:5] or ["observational"]


def build_prompt_seed(topic: list[str], function: str, mood: str, creator_signal: bool) -> str:
    primary = topic[0] if topic else "misc"
    prompt = TOPIC_PROMPT_FRAGMENTS.get(
        primary,
        {
            "ai": "AI tool surprise",
            "misc": "short personal observation",
        }.get(primary, "short personal observation"),
    )
    if creator_signal and primary not in {
        "ai",
        "unity",
        "vrchat-avatar-mod",
        "vrchat-events",
        "vrchat-mobile",
        "vrchat-social",
        "vrchat-technical",
        "vrchat-worlds",
    }:
        prompt = f"creator-style {prompt}"
    if function == "process_log":
        prompt = f"process note about {prompt}"
    elif function == "question":
        prompt = f"curious prompt hook about {prompt}"
    elif function == "RT":
        prompt = f"reshared commentary about {prompt}"
    if mood == "playful":
        prompt = f"playful {prompt}"
    elif mood == "reflective":
        prompt = f"reflective {prompt}"
    elif mood == "surprised":
        prompt = f"surprised {prompt}"
    return prompt


def build_imagegen_seed(topic: list[str], function: str, mood: str, has_media: bool) -> str:
    primary = topic[0] if topic else "misc"
    visual = TOPIC_IMAGEGEN_FRAGMENTS.get(
        primary,
        {
            "ai": "a small visual metaphor for an AI tool exceeding expectations",
            "misc": "a compact scene built from a fleeting daily observation",
        }.get(primary, "a compact scene built from a fleeting daily observation"),
    )
    if has_media:
        visual = f"{visual}, grounded in a real posted image"
    if function == "reply":
        visual = f"{visual}, framed as a quick reaction"
    elif function == "process_log":
        visual = f"{visual}, showing a work-in-progress board"
    if mood == "sleepy":
        visual = f"{visual}, soft and sleepy"
    elif mood == "frustrated":
        visual = f"{visual}, with a slight tension"
    elif mood == "surprised":
        visual = f"{visual}, with a clear sense of surprise"
    return visual


def compute_importance(favorite_count: int, retweet_count: int, has_media: bool, creator_signal: bool) -> float:
    raw = math.log1p(favorite_count + (retweet_count * 2) + (5 if has_media else 0) + (3 if creator_signal else 0))
    return round(min(1.0, raw / 5.0), 3)


def compute_reuse_score(kind: str, self_reference: bool, creator_signal: bool, has_media: bool, text: str) -> float:
    score = 0.25
    if kind == "original":
        score += 0.2
    if self_reference:
        score += 0.2
    if creator_signal:
        score += 0.15
    if has_media:
        score += 0.1
    if len(normalize_text(text)) <= 80:
        score += 0.1
    if kind == "reply":
        score -= 0.05
    return round(max(0.0, min(1.0, score)), 3)


def build_quality_flags(
    kind: str,
    classification_confidence: float,
    topics: list[str],
    url_count: int,
    text: str,
    owner_signal: str,
) -> list[str]:
    flags: list[str] = []
    visible = visible_text(text)
    if kind in {"reply", "quote", "retweet"}:
        flags.append(kind)
    if len(topics) > 1:
        flags.append("mixed_topic")
    if classification_confidence < 0.55:
        flags.append("low_confidence")
    if url_count and len(visible) <= 20:
        flags.append("link_only")
    if owner_signal == "参照":
        flags.append("reference_oriented")
    if not visible:
        flags.append("empty_visible_text")
    if "misc" in topics or "social" in topics:
        flags.append("broad_topic")
    return unique_keep_order(flags)


def build_record(item: dict[str, Any], source_archive_id: str) -> dict[str, Any]:
    tweet = item.get("tweet", {})
    text = normalize_text(tweet.get("full_text") or tweet.get("text") or "")
    created_at, month = parse_created_at(tweet.get("created_at"))
    kind = detect_kind(tweet, text)
    analysis = analyze_text(text)
    urls = extract_urls(tweet)
    media = tweet.get("extended_entities", {}).get("media", [])
    has_media = bool(media)
    classification = classify_topics(text, kind, analysis)
    topic = classification["topics"]
    mood = detect_mood(text, kind)
    function = detect_function(text, kind)
    style = detect_style(text, kind, has_media)
    self_reference = detect_self_reference(text)
    creator_signal = detect_creator_signal(text)
    sensory_level = detect_sensory_level(text)
    concreteness = detect_concreteness(text, has_media, len(urls))
    entities = infer_entities(tweet, text)
    mentions = extract_mentions(tweet, text)
    reply_to = tweet.get("in_reply_to_status_id_str")
    quote_of = tweet.get("quoted_status_id_str")
    retweet_of = tweet.get("retweeted_status_id_str")
    favorite_count = int(tweet.get("favorite_count") or 0)
    retweet_count = int(tweet.get("retweet_count") or 0)
    owner_signal = classify_owner_signal(kind, self_reference, len(urls), len(mentions), topic)

    record = {
        "id": tweet.get("id_str"),
        "source": "twitter",
        "source_archive_id": source_archive_id,
        "schema_version": 2,
        "created_at": created_at,
        "month": month,
        "text": text,
        "kind": kind,
        "reply_to": reply_to,
        "quote_of": quote_of,
        "retweet_of": retweet_of,
        "has_media": has_media,
        "media_count": len(media),
        "url_count": len(urls),
        "favorite_count": favorite_count,
        "retweet_count": retweet_count,
        "lang": tweet.get("lang") or "",
        "topic": topic,
        "topic_evidence": classification["topic_evidence"],
        "matched_keywords": classification["matched_keywords"],
        "classification_confidence": classification["classification_confidence"],
        "owner_signal": owner_signal,
        "mood": mood,
        "function": function,
        "style": style,
        "self_reference": self_reference,
        "creator_signal": creator_signal,
        "sensory_level": sensory_level,
        "concreteness": concreteness,
        "essence": build_essence(topic, function, mood, creator_signal, kind),
        "trait_tags": build_trait_tags(topic, function, mood, creator_signal, self_reference, kind),
        "prompt_seed": build_prompt_seed(topic, function, mood, creator_signal),
        "imagegen_seed": build_imagegen_seed(topic, function, mood, has_media),
        "entities": entities,
        "mentions": mentions,
        "edges": [],
        "embedding": None,
        "keywords": [],
        "month_bucket": month,
        "importance": compute_importance(favorite_count, retweet_count, has_media, creator_signal),
        "reuse_score": compute_reuse_score(kind, self_reference, creator_signal, has_media, text),
    }
    record["evidence_text"] = (
        classification["topic_evidence"][0]["evidence_text"]
        if classification["topic_evidence"]
        else visible_text(text)[:180]
    )
    record["reuse_type"] = classify_reuse_type(record)
    record["quality_flags"] = build_quality_flags(
        kind, record["classification_confidence"], topic, len(urls), text, owner_signal
    )
    if not record["quality_flags"]:
        record["quality_flags"] = ["clean"]
    record["latent_profile"] = build_latent_profile(record, analysis)

    if reply_to:
        record["edges"].append({"type": "reply_to", "target": reply_to})
    if quote_of:
        record["edges"].append({"type": "quote_of", "target": quote_of})
    if retweet_of:
        record["edges"].append({"type": "retweet_of", "target": retweet_of})
    for topic_name in topic:
        record["edges"].append({"type": "same_topic_as", "target": topic_name})
    record["keywords"] = [
        *topic,
        *record["matched_keywords"],
        *style,
        function,
        mood,
        owner_signal,
        record["reuse_type"],
        record["latent_profile"]["observation_mode"],
    ]
    return record


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    months = Counter(record["month"] for record in records if record.get("month"))
    topics = Counter(topic for record in records for topic in record.get("topic", []))
    moods = Counter(record.get("mood", "") for record in records)
    functions = Counter(record.get("function", "") for record in records)
    kinds = Counter(record.get("kind", "") for record in records)
    owner_signals = Counter(record.get("owner_signal", "") for record in records)
    reuse_types = Counter(record.get("reuse_type", "") for record in records)
    quality_flags = Counter(flag for record in records for flag in record.get("quality_flags", []))
    confidences = [float(record.get("classification_confidence", 0.0)) for record in records]
    latent_modes = Counter(record.get("latent_profile", {}).get("observation_mode", "") for record in records)
    prompt_biases = Counter(record.get("latent_profile", {}).get("prompt_bias", "") for record in records)
    chronological = sorted(records, key=lambda item: item.get("created_at", ""))
    primary_topics = [item.get("topic", ["misc"])[0] if item.get("topic") else "misc" for item in chronological]
    primary_moods = [item.get("mood", "neutral") for item in chronological]
    topic_transitions = Counter(
        f"{a} -> {b}" for a, b in itertools.pairwise(primary_topics) if a and b and a != b
    )
    mood_transitions = Counter(
        f"{a} -> {b}" for a, b in itertools.pairwise(primary_moods) if a and b and a != b
    )
    creators = sum(1 for record in records if record.get("creator_signal"))
    self_refs = sum(1 for record in records if record.get("self_reference"))
    with_media = sum(1 for record in records if record.get("has_media"))
    replies = sum(1 for record in records if record.get("kind") == "reply")
    retweets = sum(1 for record in records if record.get("kind") == "retweet")
    return {
        "counts": {
            "records": len(records),
            "months": len(months),
            "topics": len(topics),
            "creator_signal": creators,
            "self_reference": self_refs,
            "with_media": with_media,
            "replies": replies,
            "retweets": retweets,
        },
        "top_months": months.most_common(12),
        "top_topics": topics.most_common(20),
        "top_moods": moods.most_common(10),
        "top_functions": functions.most_common(10),
        "top_kinds": kinds.most_common(10),
        "owner_signals": owner_signals.most_common(10),
        "reuse_types": reuse_types.most_common(10),
        "quality_flags": quality_flags.most_common(15),
        "latent_modes": latent_modes.most_common(10),
        "prompt_biases": prompt_biases.most_common(10),
        "topic_transitions": topic_transitions.most_common(20),
        "mood_transitions": mood_transitions.most_common(20),
        "confidence": {
            "mean": round(sum(confidences) / len(confidences), 3) if confidences else 0.0,
            "min": round(min(confidences), 3) if confidences else 0.0,
            "max": round(max(confidences), 3) if confidences else 0.0,
            "low_confidence": sum(1 for value in confidences if value < 0.55),
        },
    }


def build_profile(summary: dict[str, Any]) -> dict[str, Any]:
    top_topics = [item[0] for item in summary["top_topics"][:5]]
    top_moods = [item[0] for item in summary["top_moods"][:5]]
    top_functions = [item[0] for item in summary["top_functions"][:5]]
    top_latent_modes = [item[0] for item in summary.get("latent_modes", [])[:5]]
    top_prompt_biases = [item[0] for item in summary.get("prompt_biases", [])[:5]]
    top_traits = []
    if "playful" in top_moods:
        top_traits.append("playful")
    if "surprised" in top_moods:
        top_traits.append("surprise-led")
    if "reply" in top_functions:
        top_traits.append("reply-shaped")
    if "observation" in top_functions:
        top_traits.append("observational")
    if "ai" in top_topics or "unity" in top_topics or "creator-tools" in top_topics or "vrchat-technical" in top_topics:
        top_traits.append("creator-aware")
    if "vrchat-social" in top_topics or "vrchat-events" in top_topics:
        top_traits.append("social")
    top_traits = top_traits[:5] or ["observational"]
    return {
        "essence": "Kafka tweets are short, situational, and identity-stable. They move from a concrete observation to a small emotional reaction, usually with a creator, social, or daily-life angle.",
        "dominant_modes": top_functions,
        "dominant_topics": top_topics,
        "dominant_moods": top_moods,
        "dominant_latent_modes": top_latent_modes,
        "dominant_prompt_biases": top_prompt_biases,
        "dominant_traits": top_traits,
        "prompt_generation_recipe": [
            "Pick one topic, one mood, and one function.",
            "Keep the surface short and concrete.",
            "Add one creator or daily-life detail if available.",
            "Prefer a small reaction over a full explanation.",
            "Use `prompt_seed` as the first draft of the new idea.",
        ],
        "imagegen_recipe": [
            "Turn the tweet into a compact scene with one dominant emotional beat.",
            "Favor everyday objects, creator tools, rooms, weather, drinks, or screens.",
            "Keep the composition simple and readable.",
            "Use the tweet as a visual hook, not as literal text to render.",
        ],
        "retrieval_modes": [
            "topic + mood + function",
            "topic + style + creator_signal",
            "month + reply/original split",
            "self_reference + essence",
        ],
    }


def build_schema() -> dict[str, Any]:
    return {
        "version": 2,
        "layers": [
            {
                "name": "raw",
                "fields": [
                    "id",
                    "source",
                    "source_archive_id",
                    "schema_version",
                    "created_at",
                    "month",
                    "text",
                    "kind",
                    "reply_to",
                    "quote_of",
                    "retweet_of",
                    "has_media",
                    "media_count",
                    "url_count",
                    "favorite_count",
                    "retweet_count",
                    "lang",
                ],
            },
            {
                "name": "fingerprint",
                "fields": [
                    "topic",
                    "topic_evidence",
                    "matched_keywords",
                    "classification_confidence",
                    "owner_signal",
                    "mood",
                    "function",
                    "style",
                    "self_reference",
                    "creator_signal",
                    "sensory_level",
                    "concreteness",
                    "essence",
                    "trait_tags",
                    "prompt_seed",
                    "imagegen_seed",
                ],
            },
            {
                "name": "latent",
                "fields": [
                    "latent_profile",
                ],
            },
            {
                "name": "relations",
                "fields": [
                    "entities",
                    "mentions",
                    "edges",
                ],
            },
            {
                "name": "retrieval",
                "fields": [
                    "embedding",
                    "keywords",
                    "month_bucket",
                    "importance",
                    "reuse_score",
                    "reuse_type",
                    "quality_flags",
                    "evidence_text",
                ],
            },
        ],
    }


def generate_db(archive_path: Path, output_path: Path) -> dict[str, Any]:
    raw_items = load_archive_tweets(archive_path)
    source_archive_id = archive_path.stem
    records = [build_record(item, source_archive_id) for item in raw_items]
    summary = summarize(records)
    profile = build_profile(summary)
    payload = {
        "meta": {
            "name": "tweetsdb",
            "source_archive": str(archive_path),
            "source_archive_id": source_archive_id,
            "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "record_count": len(records),
            "status": "generated",
            "version": 2,
            "schema_version": 2,
        },
        "schema": build_schema(),
        "summary": summary,
        "profile": profile,
        "records": records,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def load_db(path: Path = DB_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def score_record(record: dict[str, Any]) -> float:
    quality_penalty = 0.0
    flags = set(record.get("quality_flags", []))
    if "low_confidence" in flags:
        quality_penalty += 0.14
    if "link_only" in flags:
        quality_penalty += 0.08
    if "mixed_topic" in flags:
        quality_penalty += 0.12
    return round(
        (
            float(record.get("reuse_score", 0.0)) * 0.3
            + float(record.get("importance", 0.0)) * 0.2
            + float(record.get("classification_confidence", 0.0)) * 0.4
            + (0.1 if record.get("creator_signal") else 0.0)
        )
        - quality_penalty,
        3,
    )


def matches(record: dict[str, Any], topic: str | None, mood: str | None, function: str | None) -> bool:
    if topic and topic not in record.get("topic", []):
        return False
    if mood and record.get("mood") != mood:
        return False
    return not (function and record.get("function") != function)


def build_idea(
    db: dict[str, Any], topic: str | None, mood: str | None, function: str | None, limit: int
) -> dict[str, Any]:
    records = db["records"]
    long_records = [record for record in records if len(visible_text(record.get("text", ""))) > 20]
    pool = long_records or records
    filtered = [record for record in pool if matches(record, topic, mood, function)]

    def rank(record: dict[str, Any]) -> tuple[int, float]:
        primary = (record.get("topic") or [""])[0]
        return (1 if topic and primary == topic else 0, score_record(record))

    filtered.sort(key=rank, reverse=True)
    top = filtered[:5] if filtered else sorted(pool, key=score_record, reverse=True)[:5]
    top = top[:limit]
    trait_tags: list[str] = []
    for record in top:
        for tag in record.get("trait_tags", []):
            if tag not in trait_tags:
                trait_tags.append(tag)
    prompt_seed = top[0].get("prompt_seed", "") if top else ""
    imagegen_seed = top[0].get("imagegen_seed", "") if top else ""
    scene_hook = build_scene_hook(top[0]) if top else ""
    if not prompt_seed:
        prompt_seed = "short personal observation"
    if not imagegen_seed:
        imagegen_seed = "a compact scene from an everyday observation"
    if scene_hook and scene_hook not in imagegen_seed:
        imagegen_seed = f"{imagegen_seed} — {scene_hook}"
    return {
        "query": {
            "topic": topic,
            "mood": mood,
            "function": function,
        },
        "profile_hint": db.get("profile", {}).get("dominant_traits", []),
        "seed": {
            "prompt_seed": prompt_seed,
            "imagegen_seed": imagegen_seed,
            "trait_tags": trait_tags[:5],
        },
        "reference_tweets": [
            {
                "id": record.get("id"),
                "month": record.get("month"),
                "kind": record.get("kind"),
                "topic": record.get("topic"),
                "mood": record.get("mood"),
                "function": record.get("function"),
                "prompt_seed": record.get("prompt_seed"),
                "imagegen_seed": record.get("imagegen_seed"),
                "text": record.get("text"),
            }
            for record in top
        ],
        "new_idea": {
            "prompt_direction": f"{mood or 'playful'} {function or 'observation'} about {topic or 'a small personal scene'}",
            "image_direction": imagegen_seed,
        },
    }


def cmd_generate(args: argparse.Namespace) -> int:
    generate_db(args.archive, args.output)
    return 0


def cmd_idea(args: argparse.Namespace) -> int:
    db = load_db(args.db)
    build_idea(db, args.topic, args.mood, args.function, args.limit)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="TweetsDB generator and idea extractor.")
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="Build db/tweetsdb.json from the Twitter archive")
    gen.add_argument("--archive", type=Path, default=ARCHIVE_PATH, help="Path to the Twitter archive zip")
    gen.add_argument("--output", type=Path, default=DB_PATH, help="Output JSON path")
    gen.set_defaults(func=cmd_generate)

    idea = sub.add_parser("idea", help="Extract a Kafka-style prompt/imagegen idea from tweetsdb")
    idea.add_argument("--db", type=Path, default=DB_PATH, help="Path to tweetsdb.json")
    idea.add_argument("--topic", default=None)
    idea.add_argument("--mood", default=None)
    idea.add_argument("--function", default=None)
    idea.add_argument("--limit", type=int, default=3)
    idea.set_defaults(func=cmd_idea)

    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
