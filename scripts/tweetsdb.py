#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import re
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "db" / "tweetsdb.json"
ARCHIVE_PATH = ROOT / "artifacts" / "twitter-2026-05-02-741b09a4d07b6875e14faaed1104872c99f2c1d9574872876fd3d2342d11756c.zip"


AI_PATTERN = re.compile(r"(?:\bai\b|生成ai|人工知能|chatgpt|openai|gpt|llm|prompt|画像生成|image generation)", re.IGNORECASE)
URL_RE = re.compile(r"https?://\S+")
MENTION_RE = re.compile(r"@([A-Za-z0-9_]+)")

TOPIC_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("vrchat-events", ("集会", "周年", "host", "ホスト", "meetup", "event", "anniversary")),
    ("vrchat-avatar-mod", ("modular avatar", "expressionsmenu", "expressions menu", "shape changer", "menu item", "menu installer", "着せ替え", "改変", "toggle")),
    ("vrchat-worlds", ("madewithvrchat", "world travel", "world tour", "worlds", "world", "ワールド", "vket", "世界旅行")),
    ("vrchat-mobile", ("vrchat android", "vrchat mobile", "android", "スマホ")),
    ("ai-imagegen", ("chatgpt", "openai", "gpt", "llm", "生成ai", "画像生成", "image generation", "prompt")),
    ("creator-tools", ("blender", "unity", "c#", "dll", "agent", "skill", "script", "api", "build", "workflow", "gradio", "kohya", "sd-scripts", "github", "docs")),
    ("finance-jp", ("boj", "日銀", "nisa", "株", "円", "per", "carry", "投機", "金利", "market")),
    ("shopping-gadgets", ("aliexpress", "power bank", "charger", "amazon", "ガジェット", "充電", "製品", "item")),
    ("music-listening", ("playlist", "music", "曲", "歌", "alexa", "spotify", "sound")),
    ("travel-real-world", ("travel", "旅", "tokyo", "京都", "kyoto", "北海道", "hokkaido", "沖縄", "okinawa", "venice", "観光", "空港", "hotel", "flight")),
    ("food-drink", ("food", "ごはん", "食べ", "coffee", "cafe", "breakfast", "lunch", "dinner", "mogumogu", "味", "飲")),
    ("sleep-morning", ("おは", "おやすみ", "sleep", "眠", "寝", "朝", "起床", "sleepy")),
    ("weather-mood", ("rain", "雨", "wind", "風", "寒", "暑", "花粉", "window", "天気")),
    ("art-illustration", ("illustration", "drawing", "draw", "illustrator", "イラスト", "絵", "描いて", "sketch")),
    ("games", ("boardgame", "board game", "麻雀", "マダミス", "trpg", "poker", "dominion", "splendor", "ゲーム", "カード")),
    ("vrchat", ("vrchat", "vrc", "udon", "avatar", "world")),
    ("unity", ("unity", "blender", "c#", "dll", "agent", "skill")),
    ("travel", ("travel", "旅", "tokyo", "京都", "kyoto", "北海道", "hokkaido", "沖縄", "okinawa", "venice", "観光")),
    ("food", ("food", "ごはん", "食べ", "coffee", "cafe", "breakfast", "lunch", "dinner", "mogumogu", "食")),
    ("finance", ("finance", "market", "boj", "日銀", "tax", "税", "株", "press")),
    ("daily-life", ("おは", "おやすみ", "sleep", "眠", "朝", "通勤", "騒音", "花粉", "くしゃみ", "window", "rain")),
    ("social", ("@",)),
]

ENTITY_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("ChatGPT", ("chatgpt", "openai", "gpt", "llm", "生成ai", "人工知能")),
    ("VRChat", ("vrchat", "vrc", "udon")),
    ("VRChat Android", ("vrchat android", "vrchat mobile", "android")),
    ("Modular Avatar", ("modular avatar", "ma object toggle", "ma menu item", "ma menu installer", "ma shape changer", "expressionsmenu")),
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
    "vrchat": "VRChat/social world behavior",
    "vrchat-avatar-mod": "VRChat avatar modification",
    "vrchat-events": "VRChat event or meetup behavior",
    "vrchat-mobile": "VRChat mobile behavior",
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
    "vrchat": "VRChat scene note",
    "vrchat-avatar-mod": "VRChat avatar-mod note",
    "vrchat-events": "VRChat event note",
    "vrchat-mobile": "VRChat mobile note",
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
    "vrchat": "a cozy VRChat social scene",
    "vrchat-avatar-mod": "a VRChat avatar customization desk scene",
    "vrchat-events": "a VRChat gathering scene with people and signage",
    "vrchat-mobile": "a VRChat mobile scene on a phone screen",
    "vrchat-worlds": "a VRChat world exploration scene",
    "weather-mood": "an everyday weather scene with atmosphere",
    "misc": "a compact scene built from a fleeting daily observation",
}

TOPIC_TRAIT_HINTS: dict[str, tuple[str, ...]] = {
    "ai-imagegen": ("tool-aware",),
    "art-illustration": ("visual",),
    "creator-tools": ("creator-aware", "tool-aware"),
    "finance-jp": ("market-aware",),
    "food-drink": ("sensory",),
    "music-listening": ("sensory",),
    "shopping-gadgets": ("discovery-oriented",),
    "sleep-morning": ("everyday-observation",),
    "travel-real-world": ("place-aware",),
    "vrchat-avatar-mod": ("creator-aware", "tool-aware"),
    "vrchat-events": ("social",),
    "vrchat-mobile": ("tool-aware",),
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


def normalize_text(text: str) -> str:
    return " ".join(text.split()).strip()


def text_lc(text: str) -> str:
    return normalize_text(text).lower()


def visible_text(text: str) -> str:
    return normalize_text(URL_RE.sub("", text))


def parse_created_at(value: str | None) -> tuple[str, str]:
    if not value:
        return "", ""
    dt = datetime.strptime(value, "%a %b %d %H:%M:%S %z %Y").astimezone(timezone.utc)
    return dt.isoformat().replace("+00:00", "Z"), dt.strftime("%Y-%m")


def load_archive_tweets(archive_path: Path) -> list[dict[str, Any]]:
    with zipfile.ZipFile(archive_path) as zf:
        with zf.open("data/tweets.js") as fh:
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
    lc = text_lc(text)
    topics: list[str] = []
    if AI_PATTERN.search(lc):
        topics.append("ai")
    for topic, keywords in TOPIC_RULES:
        if topic == "ai":
            continue
        if any(keyword in lc for keyword in keywords):
            if topic not in topics:
                topics.append(topic)
    if not topics and kind in {"reply", "quote", "retweet"}:
        topics.append("social")
    if not topics:
        topics.append("misc")
    return topics


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
    if any(char.isdigit() for char in text) or any(word in lc for word in ("東京", "京都", "北海道", "トランプ", "boj", "unity", "vrchat")):
        styles.append("concrete")
    if AI_PATTERN.search(lc) or any(word in lc for word in ("unity", "vrchat", "blender", "api", "code", "dll", "skill", "db")):
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
        or any(keyword in lc for keyword in (
            "unity",
            "vrchat",
            "blender",
            "db",
            "api",
            "skill",
            "template",
            "graph",
            "github",
            "code",
            "tool",
            "build",
        ))
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
    if any(word in text_lc(text) for word in ("東京", "京都", "北海道", "unity", "vrchat", "boj")) or AI_PATTERN.search(text_lc(text)):
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
    primary_phrase = TOPIC_ESSENCE_PHRASES.get(primary, {
        "ai": "AI/tool behavior",
        "misc": "general observation",
    }.get(primary, "general observation"))
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


def build_trait_tags(topic: list[str], function: str, mood: str, creator_signal: bool, self_reference: bool, kind: str) -> list[str]:
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
    if ("ai" in topic or "unity" in topic or "vrchat" in topic or "ai-imagegen" in topic or "creator-tools" in topic or "vrchat-avatar-mod" in topic) and "tool-aware" not in tags:
        tags.append("tool-aware")
    if ("daily-life" in topic or "sleep-morning" in topic or "weather-mood" in topic or "food-drink" in topic) and "everyday-observation" not in tags:
        tags.append("everyday-observation")
    if function in {"observation", "opinion"}:
        tags.append("observational")
    if function == "question":
        tags.append("inquiring")
    return tags[:5] or ["observational"]


def build_prompt_seed(topic: list[str], function: str, mood: str, creator_signal: bool) -> str:
    primary = topic[0] if topic else "misc"
    prompt = TOPIC_PROMPT_FRAGMENTS.get(primary, {
        "ai": "AI tool surprise",
        "misc": "short personal observation",
    }.get(primary, "short personal observation"))
    if creator_signal and primary not in {"ai", "unity", "vrchat"}:
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
    visual = TOPIC_IMAGEGEN_FRAGMENTS.get(primary, {
        "ai": "a small visual metaphor for an AI tool exceeding expectations",
        "misc": "a compact scene built from a fleeting daily observation",
    }.get(primary, "a compact scene built from a fleeting daily observation"))
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


def build_record(item: dict[str, Any]) -> dict[str, Any]:
    tweet = item.get("tweet", {})
    text = normalize_text(tweet.get("full_text") or tweet.get("text") or "")
    created_at, month = parse_created_at(tweet.get("created_at"))
    kind = detect_kind(tweet, text)
    urls = extract_urls(tweet)
    media = tweet.get("extended_entities", {}).get("media", [])
    has_media = bool(media)
    topic = detect_topics(text, kind)
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

    record = {
        "id": tweet.get("id_str"),
        "source": "twitter",
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

    if reply_to:
        record["edges"].append({"type": "reply_to", "target": reply_to})
    if quote_of:
        record["edges"].append({"type": "quote_of", "target": quote_of})
    if retweet_of:
        record["edges"].append({"type": "retweet_of", "target": retweet_of})
    for topic_name in topic:
        record["edges"].append({"type": "same_topic_as", "target": topic_name})
    record["keywords"] = [*topic, *style, function, mood]
    return record


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    months = Counter(record["month"] for record in records if record.get("month"))
    topics = Counter(topic for record in records for topic in record.get("topic", []))
    moods = Counter(record.get("mood", "") for record in records)
    functions = Counter(record.get("function", "") for record in records)
    kinds = Counter(record.get("kind", "") for record in records)
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
    }


def build_profile(summary: dict[str, Any]) -> dict[str, Any]:
    top_topics = [item[0] for item in summary["top_topics"][:5]]
    top_moods = [item[0] for item in summary["top_moods"][:5]]
    top_functions = [item[0] for item in summary["top_functions"][:5]]
    top_traits = []
    if "playful" in top_moods:
        top_traits.append("playful")
    if "surprised" in top_moods:
        top_traits.append("surprise-led")
    if "reply" in top_functions:
        top_traits.append("reply-shaped")
    if "observation" in top_functions:
        top_traits.append("observational")
    if "ai" in top_topics or "unity" in top_topics or "vrchat" in top_topics:
        top_traits.append("creator-aware")
    top_traits = top_traits[:5] or ["observational"]
    return {
        "essence": "Kafka tweets are short, situational, and identity-stable. They move from a concrete observation to a small emotional reaction, usually with a creator or daily-life angle.",
        "dominant_modes": top_functions,
        "dominant_topics": top_topics,
        "dominant_moods": top_moods,
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
        "layers": [
            {
                "name": "raw",
                "fields": [
                    "id",
                    "source",
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
                ],
            },
        ]
    }


def generate_db(archive_path: Path, output_path: Path) -> dict[str, Any]:
    raw_items = load_archive_tweets(archive_path)
    records = [build_record(item) for item in raw_items]
    summary = summarize(records)
    profile = build_profile(summary)
    payload = {
        "meta": {
            "name": "tweetsdb",
            "source_archive": str(archive_path.relative_to(ROOT)),
            "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "record_count": len(records),
            "status": "generated",
            "version": 1,
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
    return (
        float(record.get("reuse_score", 0.0)) * 0.6
        + float(record.get("importance", 0.0)) * 0.3
        + (0.1 if record.get("creator_signal") else 0.0)
    )


def matches(record: dict[str, Any], topic: str | None, mood: str | None, function: str | None) -> bool:
    if topic and topic not in record.get("topic", []):
        return False
    if mood and record.get("mood") != mood:
        return False
    if function and record.get("function") != function:
        return False
    return True


def build_idea(db: dict[str, Any], topic: str | None, mood: str | None, function: str | None, limit: int) -> dict[str, Any]:
    records = db["records"]
    long_records = [record for record in records if len(visible_text(record.get("text", ""))) > 20]
    pool = long_records or records
    filtered = [record for record in pool if matches(record, topic, mood, function)]
    filtered.sort(key=score_record, reverse=True)
    top = filtered[:5] if filtered else sorted(pool, key=score_record, reverse=True)[:5]
    top = top[:limit]
    trait_tags: list[str] = []
    for record in top:
        for tag in record.get("trait_tags", []):
            if tag not in trait_tags:
                trait_tags.append(tag)
    prompt_seed = top[0].get("prompt_seed", "") if top else ""
    imagegen_seed = top[0].get("imagegen_seed", "") if top else ""
    if not prompt_seed:
        prompt_seed = "short personal observation"
    if not imagegen_seed:
        imagegen_seed = "a compact scene from an everyday observation"
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
    payload = generate_db(args.archive, args.output)
    print(f"wrote {args.output} ({payload['meta']['record_count']} records)")
    return 0


def cmd_idea(args: argparse.Namespace) -> int:
    db = load_db(args.db)
    idea = build_idea(db, args.topic, args.mood, args.function, args.limit)
    print(json.dumps(idea, ensure_ascii=False, indent=2))
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
