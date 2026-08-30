from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

TOKEN_RE = re.compile(r"[A-Za-z0-9_+#.-]+|[一-龯ぁ-んァ-ヶー]{2,}")


def _score_record(record: dict[str, Any]) -> float:
    flags = set(record.get("quality_flags", []))
    penalty = 0.0
    if "low_confidence" in flags:
        penalty += 0.14
    if "link_only" in flags:
        penalty += 0.08
    if "mixed_topic" in flags:
        penalty += 0.12
    return round(
        float(record.get("reuse_score", 0.0)) * 0.30
        + float(record.get("importance", 0.0)) * 0.20
        + float(record.get("classification_confidence", 0.0)) * 0.40
        + (0.10 if record.get("creator_signal") else 0.0)
        - penalty,
        3,
    )


def _compact_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": record.get("id"),
        "created_at": record.get("created_at"),
        "month": record.get("month"),
        "text": record.get("text"),
        "kind": record.get("kind"),
        "topic": record.get("topic", []),
        "mood": record.get("mood"),
        "function": record.get("function"),
        "style": record.get("style", []),
        "owner_signal": record.get("owner_signal"),
        "essence": record.get("essence"),
        "trait_tags": record.get("trait_tags", []),
        "prompt_seed": record.get("prompt_seed"),
        "imagegen_seed": record.get("imagegen_seed"),
        "evidence_text": record.get("evidence_text"),
        "latent_profile": record.get("latent_profile", {}),
        "reuse_type": record.get("reuse_type"),
        "score": _score_record(record),
    }


def _top_records(records: list[dict[str, Any]], predicate, count: int) -> list[dict[str, Any]]:
    return sorted((record for record in records if predicate(record)), key=_score_record, reverse=True)[:count]


def compile_ideation_profile_payload(
    tweetsdb: dict[str, Any],
    *,
    source_sha256: str,
    max_exemplars: int = 120,
) -> dict[str, Any]:
    records = tweetsdb.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("tweetsdb.records must be a non-empty list")

    profile = tweetsdb.get("profile")
    summary = tweetsdb.get("summary")
    schema = tweetsdb.get("schema")
    if not isinstance(profile, dict) or not isinstance(summary, dict) or not isinstance(schema, dict):
        raise ValueError("tweetsdb must contain profile, summary, and schema objects")

    selected: list[dict[str, Any]] = []
    seen: set[str] = set()

    def add(items: list[dict[str, Any]]) -> None:
        for record in items:
            key = str(record.get("id") or "")
            if not key or key in seen:
                continue
            seen.add(key)
            selected.append(record)

    add(sorted(records, key=_score_record, reverse=True)[:32])

    topics = [item[0] for item in summary.get("top_topics", [])[:20] if item]
    moods = [item[0] for item in summary.get("top_moods", [])[:10] if item]
    functions = [item[0] for item in summary.get("top_functions", [])[:10] if item]
    latent_modes = [item[0] for item in summary.get("latent_modes", [])[:10] if item]
    reuse_types = [item[0] for item in summary.get("reuse_types", [])[:10] if item]

    for topic in topics:
        add(_top_records(records, lambda record, topic=topic: topic in record.get("topic", []), 4))
    for mood in moods:
        add(_top_records(records, lambda record, mood=mood: record.get("mood") == mood, 3))
    for function in functions:
        add(_top_records(records, lambda record, function=function: record.get("function") == function, 3))
    for mode in latent_modes:
        add(
            _top_records(
                records,
                lambda record, mode=mode: record.get("latent_profile", {}).get("observation_mode") == mode,
                4,
            )
        )
    for reuse_type in reuse_types:
        add(_top_records(records, lambda record, reuse_type=reuse_type: record.get("reuse_type") == reuse_type, 4))

    selected = selected[:max_exemplars]

    return {
        "meta": {
            "name": "kafka-ideation-profile",
            "version": 1,
            "source": "db/tweetsdb.json",
            "source_sha256": source_sha256,
            "source_record_count": len(records),
            "exemplar_count": len(selected),
        },
        "profile": profile,
        "summary": {
            "counts": summary.get("counts", {}),
            "top_topics": summary.get("top_topics", []),
            "top_moods": summary.get("top_moods", []),
            "top_functions": summary.get("top_functions", []),
            "owner_signals": summary.get("owner_signals", []),
            "reuse_types": summary.get("reuse_types", []),
            "latent_modes": summary.get("latent_modes", []),
            "prompt_biases": summary.get("prompt_biases", []),
            "topic_transitions": summary.get("topic_transitions", []),
            "mood_transitions": summary.get("mood_transitions", []),
            "confidence": summary.get("confidence", {}),
        },
        "facets": {
            "topics": Counter(topic for record in selected for topic in record.get("topic", [])),
            "moods": Counter(str(record.get("mood") or "") for record in selected),
            "functions": Counter(str(record.get("function") or "") for record in selected),
            "latent_modes": Counter(
                str(record.get("latent_profile", {}).get("observation_mode") or "") for record in selected
            ),
            "reuse_types": Counter(str(record.get("reuse_type") or "") for record in selected),
        },
        "exemplars": [_compact_record(record) for record in selected],
    }


def compile_ideation_profile(source: Path, output: Path, *, max_exemplars: int = 120) -> dict[str, Any]:
    raw = source.read_bytes()
    tweetsdb = json.loads(raw)
    payload = compile_ideation_profile_payload(
        tweetsdb,
        source_sha256=hashlib.sha256(raw).hexdigest(),
        max_exemplars=max_exemplars,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def load_ideation_profile(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("meta", {}).get("name") != "kafka-ideation-profile":
        raise ValueError("not a kafka ideation profile")
    exemplars = payload.get("exemplars")
    if not isinstance(exemplars, list) or not exemplars:
        raise ValueError("ideation profile has no exemplars")
    return payload


def _query_tokens(query: str) -> set[str]:
    return {token.lower() for token in TOKEN_RE.findall(query) if len(token) >= 2}


def retrieve_ideation(
    payload: dict[str, Any],
    query: str,
    *,
    topic: str | None = None,
    mood: str | None = None,
    function: str | None = None,
    limit: int = 5,
) -> dict[str, Any]:
    tokens = _query_tokens(query)
    query_lc = query.strip().lower()

    def rank(record: dict[str, Any]) -> float:
        score = float(record.get("score", 0.0))
        topics = record.get("topic", [])
        if topic:
            score += 4.0 if topic in topics else -4.0
        if mood:
            score += 3.0 if record.get("mood") == mood else -3.0
        if function:
            score += 3.0 if record.get("function") == function else -3.0

        fields = [
            record.get("text", ""),
            record.get("essence", ""),
            record.get("prompt_seed", ""),
            record.get("imagegen_seed", ""),
            record.get("evidence_text", ""),
            " ".join(topics),
            " ".join(record.get("trait_tags", [])),
            str(record.get("latent_profile", {}).get("observation_mode", "")),
        ]
        haystack = " ".join(str(value) for value in fields).lower()
        if query_lc and query_lc in haystack:
            score += 5.0
        score += sum(1.0 for token in tokens if token in haystack)
        return score

    ranked = sorted(payload["exemplars"], key=rank, reverse=True)[: max(1, limit)]
    traits: list[str] = []
    prompt_seeds: list[str] = []
    imagegen_seeds: list[str] = []
    for record in ranked:
        for trait in record.get("trait_tags", []):
            if trait not in traits:
                traits.append(trait)
        if record.get("prompt_seed") and record["prompt_seed"] not in prompt_seeds:
            prompt_seeds.append(record["prompt_seed"])
        if record.get("imagegen_seed") and record["imagegen_seed"] not in imagegen_seeds:
            imagegen_seeds.append(record["imagegen_seed"])

    return {
        "query": {
            "text": query,
            "topic": topic,
            "mood": mood,
            "function": function,
        },
        "profile_hint": payload.get("profile", {}).get("dominant_traits", []),
        "recipes": {
            "prompt": payload.get("profile", {}).get("prompt_generation_recipe", []),
            "imagegen": payload.get("profile", {}).get("imagegen_recipe", []),
        },
        "seed": {
            "trait_tags": traits[:8],
            "prompt_seeds": prompt_seeds[:5],
            "imagegen_seeds": imagegen_seeds[:5],
        },
        "reference_examples": ranked,
    }
