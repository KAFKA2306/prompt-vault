#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from build import load_db  # noqa: E402

OUTPUT_DIR = ROOT / "docs" / "generated"
MD_PATH = OUTPUT_DIR / "db_graph.md"

PRESETS = [
    {
        "mode": "overview",
        "focus": None,
        "kinds": [],
        "categories": [],
        "title": "Overview",
    },
    {
        "mode": "templates",
        "focus": None,
        "kinds": ["social"],
        "categories": [],
        "title": "Templates / social",
    },
    {
        "mode": "templates",
        "focus": None,
        "kinds": ["design_sheet"],
        "categories": [],
        "title": "Templates / design_sheet",
    },
    {
        "mode": "blocks",
        "focus": None,
        "kinds": [],
        "categories": ["形式・レイアウト"],
        "title": "Blocks / layout",
    },
    {
        "mode": "overview",
        "focus": "morning_tweet_layout",
        "kinds": [],
        "categories": [],
        "title": "Focus / morning_tweet_layout",
    },
]


def mermaid_label(title: str, node_id: str) -> str:
    return f"{html.escape(title, quote=True)}<br/><small>{html.escape(node_id, quote=True)}</small>"


def group_nodes(nodes: list[dict[str, Any]], key_name: str, fallback: str) -> list[tuple[str, list[dict[str, Any]]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for node in nodes:
        grouped[node.get(key_name) or fallback].append(node)
    return sorted(
        grouped.items(),
        key=lambda item: (-len(item[1]), item[0]),
    )


def group_id(prefix: str, index: int) -> str:
    return f"{prefix}_{index:02d}"


def ordered_nodes(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(nodes, key=lambda node: (node.get("title") or "", node["id"]))


def normalize_values(values: list[str] | None) -> set[str]:
    return {value.strip() for value in (values or []) if value and value.strip()}


def build_indexes(db: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    block_map = {block["id"]: block for block in db["blocks"]}
    template_map = {template["id"]: template for template in db["templates"]}
    return block_map, template_map


def filter_templates(
    templates: list[dict[str, Any]],
    allowed_kinds: set[str],
) -> list[dict[str, Any]]:
    result = []
    for template in templates:
        if allowed_kinds and template.get("kind") not in allowed_kinds:
            continue
        result.append(template)
    return ordered_nodes(result)


def filter_blocks(
    blocks: list[dict[str, Any]],
    allowed_categories: set[str],
) -> list[dict[str, Any]]:
    result = []
    for block in blocks:
        if allowed_categories and block.get("category") not in allowed_categories:
            continue
        result.append(block)
    return ordered_nodes(result)


def _expand_template_focus(
    focus_id: str, block_map: dict[str, dict[str, Any]], template_map: dict[str, dict[str, Any]]
) -> tuple[set[str], set[str]]:
    selected_templates = {focus_id}
    selected_blocks = set(template_map[focus_id].get("blocks", []))
    selected_blocks.update(template_map[focus_id].get("uses", []))
    for block_id in list(selected_blocks):
        block = block_map.get(block_id)
        if not block:
            continue
        selected_blocks.update(block.get("related", []))
        variant_of = block.get("variant_of")
        if variant_of and variant_of in block_map:
            selected_blocks.add(variant_of)
    for block_id, block in block_map.items():
        related = set(block.get("related", []))
        variant_of = block.get("variant_of")
        if block_id in selected_blocks or related & selected_blocks or variant_of in selected_templates:
            selected_blocks.add(block_id)
            if variant_of and variant_of in template_map:
                selected_templates.add(variant_of)
            for template in template_map.values():
                if block_id in template.get("blocks", []) or block_id in template.get("uses", []):
                    selected_templates.add(template["id"])
    return selected_templates, selected_blocks


def _expand_block_focus(
    focus_id: str, block_map: dict[str, dict[str, Any]], template_map: dict[str, dict[str, Any]]
) -> tuple[set[str], set[str]]:
    selected_blocks = {focus_id}
    selected_templates = set()
    block = block_map[focus_id]
    selected_blocks.update(block.get("related", []))
    variant_of = block.get("variant_of")
    if variant_of and variant_of in block_map:
        selected_blocks.add(variant_of)
    if variant_of and variant_of in template_map:
        selected_templates.add(variant_of)
    for template in template_map.values():
        template_blocks = set(template.get("blocks", []))
        template_uses = set(template.get("uses", []))
        if focus_id in template_blocks or focus_id in template_uses:
            selected_templates.add(template["id"])
    for block_id in list(selected_blocks):
        block_node = block_map.get(block_id)
        if not block_node:
            continue
        selected_blocks.update(block_node.get("related", []))
        parent = block_node.get("variant_of")
        if parent and parent in block_map:
            selected_blocks.add(parent)
        if parent and parent in template_map:
            selected_templates.add(parent)
    for template in template_map.values():
        if set(template.get("blocks", [])) & selected_blocks or set(template.get("uses", [])) & selected_blocks:
            selected_templates.add(template["id"])
    return selected_templates, selected_blocks


def expand_focus(
    focus_id: str | None,
    block_map: dict[str, dict[str, Any]],
    template_map: dict[str, dict[str, Any]],
) -> tuple[set[str], set[str]]:
    if not focus_id:
        return set(), set()
    if focus_id in template_map:
        return _expand_template_focus(focus_id, block_map, template_map)
    if focus_id in block_map:
        return _expand_block_focus(focus_id, block_map, template_map)
    return set(), set()


def render_template_composition_diagram(
    templates: list[dict[str, Any]],
    blocks: list[dict[str, Any]],
    block_map: dict[str, dict[str, Any]],
) -> str:
    lines: list[str] = [
        "flowchart LR",
        "  classDef template fill:#dbeafe,stroke:#2563eb,color:#0f172a,stroke-width:1px;",
        "  classDef block fill:#dcfce7,stroke:#059669,color:#0f172a,stroke-width:1px;",
    ]

    lines.append('  subgraph templates["Templates"]')
    lines.append("    direction TB")
    for index, (family, items) in enumerate(group_nodes(templates, "family", "template"), start=1):
        lines.append(f'    subgraph {group_id("family", index)}["{html.escape(family, quote=True)}"]')
        lines.append("      direction TB")
        for template in ordered_nodes(items):
            lines.append(f'      t_{template["id"]}["{mermaid_label(template["title"], template["id"])}"]:::template')
        lines.append("    end")
    lines.append("  end")

    lines.append('  subgraph blocks["Blocks"]')
    lines.append("    direction TB")
    for index, (family, items) in enumerate(group_nodes(blocks, "family", "ブロック"), start=1):
        lines.append(f'    subgraph {group_id("fam", index)}["{html.escape(family, quote=True)}"]')
        lines.append("      direction TB")
        for block in ordered_nodes(items):
            lines.append(f'      b_{block["id"]}["{mermaid_label(block["title"], block["id"])}"]:::block')
        lines.append("    end")
    lines.append("  end")

    for template in templates:
        template_node = f"t_{template['id']}"
        for block_id in template.get("blocks", []):
            if block_id in block_map:
                lines.append(f"  {template_node} --> b_{block_id}")
        for node_id in template.get("uses", []):
            if node_id in block_map:
                lines.append(f"  {template_node} -.-> b_{node_id}")
            else:
                lines.append(f"  {template_node} -.-> t_{node_id}")

    return "\n".join(lines)


def _render_block_subgraph(blocks: list[dict[str, Any]]) -> list[str]:
    lines = ['  subgraph blocks["Blocks"]', "    direction TB"]
    for index, (family, items) in enumerate(group_nodes(blocks, "family", "ブロック"), start=1):
        lines.append(f'    subgraph {group_id("fam", index)}["{html.escape(family, quote=True)}"]')
        lines.append("      direction TB")
        for block in ordered_nodes(items):
            lines.append(f'      b_{block["id"]}["{mermaid_label(block["title"], block["id"])}"]:::block')
        lines.append("    end")
    lines.append("  end")
    return lines


def _render_referenced_templates(
    blocks: list[dict[str, Any]], template_map: dict[str, dict[str, Any]]
) -> list[str]:
    template_targets: dict[str, dict[str, Any]] = {}
    for block in blocks:
        for node_id in block.get("related", []):
            if node_id in template_map:
                template_targets[node_id] = template_map[node_id]
        variant_of = block.get("variant_of")
        if variant_of and variant_of in template_map:
            template_targets[variant_of] = template_map[variant_of]

    lines = []
    if template_targets:
        lines.append('  subgraph templates["Referenced Templates"]')
        lines.append("    direction TB")
        for template in ordered_nodes(list(template_targets.values())):
            lines.append(f'      t_{template["id"]}["{mermaid_label(template["title"], template["id"])}"]:::template')
        lines.append("  end")
    return lines


def render_block_relations_diagram(
    blocks: list[dict[str, Any]],
    template_map: dict[str, dict[str, Any]],
    block_map: dict[str, dict[str, Any]],
) -> str:
    lines: list[str] = [
        "flowchart LR",
        "  classDef template fill:#dbeafe,stroke:#2563eb,color:#0f172a,stroke-width:1px;",
        "  classDef block fill:#dcfce7,stroke:#059669,color:#0f172a,stroke-width:1px;",
    ]

    lines.extend(_render_block_subgraph(blocks))
    lines.extend(_render_referenced_templates(blocks, template_map))

    related_edges: set[tuple[str, str]] = set()
    for block in blocks:
        block_node = f"b_{block['id']}"
        variant_of = block.get("variant_of")
        if variant_of:
            if variant_of in block_map:
                lines.append(f"  {block_node} -.-> b_{variant_of}")
            elif variant_of in template_map:
                lines.append(f"  {block_node} -.-> t_{variant_of}")
        for node_id in block.get("related", []):
            if node_id in block_map:
                pair = tuple(sorted((block["id"], node_id)))
                if pair not in related_edges:
                    related_edges.add(pair)
                    lines.append(f"  b_{pair[0]} -.-> b_{pair[1]}")
            elif node_id in template_map:
                lines.append(f"  {block_node} -.-> t_{node_id}")

    return "\n".join(lines)


def wrap_markdown(title: str, mermaid_source: str) -> str:
    return "\n".join(
        [
            f"# {title}",
            "",
            "```mermaid",
            mermaid_source,
            "```",
        ]
    )


def render_sections(
    db: dict[str, Any],
    mode: str,
    focus: str | None,
    allowed_kinds: set[str],
    allowed_categories: set[str],
) -> tuple[list[tuple[str, str]], str]:
    block_map, template_map = build_indexes(db)
    focus_templates, focus_blocks = expand_focus(focus, block_map, template_map)

    templates = db["templates"]
    blocks = db["blocks"]
    if focus_templates:
        templates = [template for template in templates if template["id"] in focus_templates]
    if focus_blocks:
        blocks = [block for block in blocks if block["id"] in focus_blocks]

    templates = filter_templates(templates, allowed_kinds)
    blocks = filter_blocks(blocks, allowed_categories)
    block_map = {block["id"]: block for block in blocks}
    template_map = {template["id"]: template for template in templates}

    sections: list[tuple[str, str]] = []
    if mode in {"overview", "templates"}:
        sections.append(("Template Composition", render_template_composition_diagram(templates, blocks, block_map)))
    if mode in {"overview", "blocks"}:
        sections.append(("Block Relations", render_block_relations_diagram(blocks, template_map, block_map)))

    title_bits = ["Prompt Vault DB Graph"]
    if mode != "overview":
        title_bits.append(mode.title())
    if focus:
        title_bits.append(f"focus:{focus}")
    if allowed_kinds:
        title_bits.append(f"kind:{','.join(sorted(allowed_kinds))}")
    if allowed_categories:
        title_bits.append(f"category:{','.join(sorted(allowed_categories))}")
    return sections, " | ".join(title_bits)


def render_markdown(sections: list[tuple[str, str]]) -> str:
    return "\n\n".join(wrap_markdown(title, mermaid_source) for title, mermaid_source in sections) + "\n"


def render_node_list_markdown(db: dict[str, Any]) -> str:
    lines = [
        "## Node List",
        "",
        "| Type | ID | Title | Kind / Category |",
        "| --- | --- | --- | --- |",
    ]
    for block in ordered_nodes(db["blocks"]):
        lines.append(f"| block | `{block['id']}` | {block['title']} | {block.get('category', '')} |")
    for template in ordered_nodes(db["templates"]):
        lines.append(f"| template | `{template['id']}` | {template['title']} | {template.get('kind', '')} |")
    lines.append("")
    return "\n".join(lines)


def render_relation_list_markdown(db: dict[str, Any]) -> str:
    block_map, template_map = build_indexes(db)
    lines = [
        "## Relation List",
        "",
        "| From | Relation | To |",
        "| --- | --- | --- |",
    ]
    for template in ordered_nodes(db["templates"]):
        for block_id in template.get("blocks", []):
            if block_id in block_map:
                lines.append(f"| `{template['id']}` | blocks | `{block_id}` |")
        for node_id in template.get("uses", []):
            if node_id in block_map or node_id in template_map:
                lines.append(f"| `{template['id']}` | uses | `{node_id}` |")
    for block in ordered_nodes(db["blocks"]):
        for node_id in block.get("related", []):
            if node_id in block_map or node_id in template_map:
                lines.append(f"| `{block['id']}` | related | `{node_id}` |")
        variant_of = block.get("variant_of")
        if variant_of and (variant_of in block_map or variant_of in template_map):
            lines.append(f"| `{block['id']}` | variant_of | `{variant_of}` |")
    lines.append("")
    return "\n".join(lines)


def render_combined_markdown(db: dict[str, Any]) -> str:
    parts = [
        "# Prompt Vault DB Graph",
        "",
        "複数の視点を順番に並べた静的グラフ。まず全体、次に用途別、最後に焦点ビューを見る。",
        "",
    ]
    for preset in PRESETS:
        sections, page_title = render_sections(
            db,
            preset["mode"],
            preset["focus"],
            normalize_values(preset["kinds"]),
            normalize_values(preset["categories"]),
        )
        parts.append(f"## {preset['title']}")
        parts.append(f"- {page_title}")
        parts.append("")
        for section_title, mermaid_source in sections:
            parts.append(f"### {section_title}")
            parts.append("")
            parts.append("```mermaid")
            parts.append(mermaid_source)
            parts.append("```")
            parts.append("")
    parts.append(render_node_list_markdown(db))
    parts.append(render_relation_list_markdown(db))
    return "\n".join(parts).rstrip() + "\n"


def clean_generated_outputs(output_dir: Path) -> None:
    for path in output_dir.glob("db_graph_*.md"):
        path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description="Render the prompt DB graph as Mermaid.")
    parser.add_argument(
        "--mode",
        choices=("overview", "templates", "blocks"),
        default="overview",
        help="which diagram set to render",
    )
    parser.add_argument(
        "--focus",
        type=str,
        default=None,
        help="node id to center the graph around",
    )
    parser.add_argument(
        "--kind",
        action="append",
        default=[],
        help="template kind to include; repeatable",
    )
    parser.add_argument(
        "--category",
        action="append",
        default=[],
        help="block category to include; repeatable",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help="directory to write db_graph.md",
    )
    args = parser.parse_args()

    db = load_db()
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    clean_generated_outputs(output_dir)

    if args.kind or args.category or args.focus or args.mode != "overview":
        sections, _ = render_sections(
            db,
            args.mode,
            args.focus,
            normalize_values(args.kind),
            normalize_values(args.category),
        )
        markdown = render_markdown(sections)
    else:
        markdown = render_combined_markdown(db)

    md_path = output_dir / MD_PATH.name
    md_path.write_text(markdown, encoding="utf-8")


if __name__ == "__main__":
    main()
