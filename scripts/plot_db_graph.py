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
HTML_PATH = OUTPUT_DIR / "db_graph.html"
MD_PATH = OUTPUT_DIR / "db_graph.md"

PRESETS = [
    {
        "name": "overview",
        "mode": "overview",
        "focus": None,
        "kinds": [],
        "categories": [],
        "slug": "overview",
        "title": "Overview",
    },
    {
        "name": "social-templates",
        "mode": "templates",
        "focus": None,
        "kinds": ["social"],
        "categories": [],
        "slug": "templates_social",
        "title": "Templates / social",
    },
    {
        "name": "design-sheet-templates",
        "mode": "templates",
        "focus": None,
        "kinds": ["design_sheet"],
        "categories": [],
        "slug": "templates_design_sheet",
        "title": "Templates / design_sheet",
    },
    {
        "name": "layout-blocks",
        "mode": "blocks",
        "focus": None,
        "kinds": [],
        "categories": ["形式・レイアウト"],
        "slug": "blocks_layout",
        "title": "Blocks / layout",
    },
    {
        "name": "morning-focus",
        "mode": "overview",
        "focus": "morning_tweet_layout",
        "kinds": [],
        "categories": [],
        "slug": "focus_morning_tweet_layout",
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
    focus_template_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    focus_template_ids = focus_template_ids or set()
    result = []
    for template in templates:
        if allowed_kinds and template.get("kind") not in allowed_kinds:
            continue
        if focus_template_ids and template["id"] not in focus_template_ids:
            continue
        result.append(template)
    return ordered_nodes(result)


def filter_blocks(
    blocks: list[dict[str, Any]],
    allowed_categories: set[str],
    focus_block_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    focus_block_ids = focus_block_ids or set()
    result = []
    for block in blocks:
        if allowed_categories and block.get("category") not in allowed_categories:
            continue
        if focus_block_ids and block["id"] not in focus_block_ids:
            continue
        result.append(block)
    return ordered_nodes(result)


def expand_focus(
    focus_id: str | None,
    block_map: dict[str, dict[str, Any]],
    template_map: dict[str, dict[str, Any]],
) -> tuple[set[str], set[str]]:
    if not focus_id:
        return set(), set()

    if focus_id in template_map:
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

    if focus_id in block_map:
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

    return set(), set()


def render_template_composition_diagram(
    templates: list[dict[str, Any]],
    blocks: list[dict[str, Any]],
    block_map: dict[str, dict[str, Any]],
) -> str:

    lines: list[str] = [
        "flowchart LR",
        '  classDef template fill:#dbeafe,stroke:#2563eb,color:#0f172a,stroke-width:1px;',
        '  classDef block fill:#dcfce7,stroke:#059669,color:#0f172a,stroke-width:1px;',
    ]

    lines.append('  subgraph templates["Templates"]')
    lines.append("    direction TB")
    for index, (kind, items) in enumerate(group_nodes(templates, "kind", "template"), start=1):
        lines.append(f'    subgraph {group_id("kind", index)}["{html.escape(kind, quote=True)}"]')
        lines.append("      direction TB")
        for template in ordered_nodes(items):
            lines.append(f'      t_{template["id"]}["{mermaid_label(template["title"], template["id"])}"]:::template')
        lines.append("    end")
    lines.append("  end")

    lines.append('  subgraph blocks["Blocks"]')
    lines.append("    direction TB")
    for index, (category, items) in enumerate(group_nodes(blocks, "category", "ブロック"), start=1):
        lines.append(f'    subgraph {group_id("cat", index)}["{html.escape(category, quote=True)}"]')
        lines.append("      direction TB")
        for block in ordered_nodes(items):
            lines.append(f'      b_{block["id"]}["{mermaid_label(block["title"], block["id"])}"]:::block')
        lines.append("    end")
    lines.append("  end")

    for template in templates:
        template_node = f't_{template["id"]}'
        for block_id in template.get("blocks", []):
            if block_id in block_map:
                lines.append(f"  {template_node} --> b_{block_id}")
        for node_id in template.get("uses", []):
            if node_id in block_map:
                lines.append(f"  {template_node} -.-> b_{node_id}")
            else:
                lines.append(f"  {template_node} -.-> t_{node_id}")

    return "\n".join(lines)


def render_block_relations_diagram(
    blocks: list[dict[str, Any]],
    template_map: dict[str, dict[str, Any]],
    block_map: dict[str, dict[str, Any]],
) -> str:

    lines: list[str] = [
        "flowchart LR",
        '  classDef template fill:#dbeafe,stroke:#2563eb,color:#0f172a,stroke-width:1px;',
        '  classDef block fill:#dcfce7,stroke:#059669,color:#0f172a,stroke-width:1px;',
    ]

    lines.append('  subgraph blocks["Blocks"]')
    lines.append("    direction TB")
    for index, (category, items) in enumerate(group_nodes(blocks, "category", "ブロック"), start=1):
        lines.append(f'    subgraph {group_id("cat", index)}["{html.escape(category, quote=True)}"]')
        lines.append("      direction TB")
        for block in ordered_nodes(items):
            lines.append(f'      b_{block["id"]}["{mermaid_label(block["title"], block["id"])}"]:::block')
        lines.append("    end")
    lines.append("  end")

    template_targets: dict[str, dict[str, Any]] = {}
    for block in blocks:
        for node_id in block.get("related", []):
            if node_id in template_map:
                template_targets[node_id] = template_map[node_id]
        variant_of = block.get("variant_of")
        if variant_of and variant_of in template_map:
            template_targets[variant_of] = template_map[variant_of]

    if template_targets:
        lines.append('  subgraph templates["Referenced Templates"]')
        lines.append("    direction TB")
        for template in ordered_nodes(list(template_targets.values())):
            lines.append(f'      t_{template["id"]}["{mermaid_label(template["title"], template["id"])}"]:::template')
        lines.append("  end")

    related_edges: set[tuple[str, str]] = set()
    for block in blocks:
        block_node = f'b_{block["id"]}'
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


def render_html(sections: list[tuple[str, str]], page_title: str) -> str:
    section_html = []
    for title, mermaid_source in sections:
        section_html.extend(
            [
                "    <section>",
                f"      <h2>{html.escape(title)}</h2>",
                '      <div class="mermaid">',
                mermaid_source,
                "      </div>",
                "    </section>",
            ]
        )

    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="ja">',
            "<head>",
            '  <meta charset="utf-8" />',
            '  <meta name="viewport" content="width=device-width, initial-scale=1" />',
            f"  <title>{html.escape(page_title)}</title>",
            "  <style>",
            "    :root { color-scheme: light; }",
            "    body { margin: 0; background: #f4f1ea; color: #111827; font-family: system-ui, sans-serif; }",
            "    main { max-width: 1800px; margin: 0 auto; padding: 24px; }",
            "    section { margin-bottom: 32px; background: #fff; border: 1px solid #e5e7eb; border-radius: 16px; padding: 20px; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06); }",
            "    h1 { margin: 0 0 12px; font-size: 28px; font-weight: 700; }",
            "    h2 { margin: 0 0 14px; font-size: 18px; font-weight: 600; }",
            "    .meta { margin: 0 0 20px; color: #5b6472; font-size: 13px; }",
            "    .mermaid { overflow: auto; }",
            "  </style>",
            '  <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>',
            "  <script>",
            "    mermaid.initialize({",
            "      startOnLoad: true,",
            "      securityLevel: 'loose',",
            "      theme: 'base',",
            "      flowchart: { curve: 'basis', htmlLabels: true },",
            "      themeVariables: {",
            "        background: '#ffffff',",
            "        primaryColor: '#dbeafe',",
            "        primaryBorderColor: '#2563eb',",
            "        secondaryColor: '#dcfce7',",
            "        secondaryBorderColor: '#059669',",
            "        tertiaryColor: '#f3f4f6',",
            "        fontFamily: 'system-ui, sans-serif',",
            "      },",
            "    });",
            "  </script>",
            "</head>",
            "<body>",
            "  <main>",
            f"    <h1>{html.escape(page_title)}</h1>",
            "    <p class=\"meta\">静的レンダリング出力。`--mode` / `--focus` / `--kind` / `--category` で絞り込み可能。</p>",
            *section_html,
            "  </main>",
            "</body>",
            "</html>",
        ]
    )


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


def render_node_list_html(db: dict[str, Any]) -> str:
    block_rows = "\n".join(
        f"<tr><td>block</td><td><code>{html.escape(block['id'])}</code></td><td>{html.escape(block['title'])}</td><td>{html.escape(block.get('category', ''))}</td></tr>"
        for block in ordered_nodes(db["blocks"])
    )
    template_rows = "\n".join(
        f"<tr><td>template</td><td><code>{html.escape(template['id'])}</code></td><td>{html.escape(template['title'])}</td><td>{html.escape(template.get('kind', ''))}</td></tr>"
        for template in ordered_nodes(db["templates"])
    )
    return "\n".join(
        [
            '<details class="list-block">',
            "  <summary>Node List</summary>",
            '  <table class="list-table">',
            "    <thead><tr><th>Type</th><th>ID</th><th>Title</th><th>Kind / Category</th></tr></thead>",
            "    <tbody>",
            block_rows,
            template_rows,
            "    </tbody>",
            "  </table>",
            "</details>",
        ]
    )


def render_relation_list_html(db: dict[str, Any]) -> str:
    block_map, template_map = build_indexes(db)
    rows = []
    for template in ordered_nodes(db["templates"]):
        for block_id in template.get("blocks", []):
            if block_id in block_map:
                rows.append(f"<tr><td><code>{html.escape(template['id'])}</code></td><td>blocks</td><td><code>{html.escape(block_id)}</code></td></tr>")
        for node_id in template.get("uses", []):
            if node_id in block_map or node_id in template_map:
                rows.append(f"<tr><td><code>{html.escape(template['id'])}</code></td><td>uses</td><td><code>{html.escape(node_id)}</code></td></tr>")
    for block in ordered_nodes(db["blocks"]):
        for node_id in block.get("related", []):
            if node_id in block_map or node_id in template_map:
                rows.append(f"<tr><td><code>{html.escape(block['id'])}</code></td><td>related</td><td><code>{html.escape(node_id)}</code></td></tr>")
        variant_of = block.get("variant_of")
        if variant_of and (variant_of in block_map or variant_of in template_map):
            rows.append(f"<tr><td><code>{html.escape(block['id'])}</code></td><td>variant_of</td><td><code>{html.escape(variant_of)}</code></td></tr>")
    return "\n".join(
        [
            '<details class="list-block">',
            "  <summary>Relation List</summary>",
            '  <table class="list-table">',
            "    <thead><tr><th>From</th><th>Relation</th><th>To</th></tr></thead>",
            "    <tbody>",
            *rows,
            "    </tbody>",
            "  </table>",
            "</details>",
        ]
    )


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


def render_combined_html(db: dict[str, Any]) -> str:
    sections_html = []
    for preset in PRESETS:
        diagram_sections, page_title = render_sections(
            db,
            preset["mode"],
            preset["focus"],
            normalize_values(preset["kinds"]),
            normalize_values(preset["categories"]),
        )
        subsections = []
        for section_title, mermaid_source in diagram_sections:
            subsections.extend(
                [
                    '        <div class="subsection">',
                    f"          <h3>{html.escape(section_title)}</h3>",
                    '          <div class="mermaid">',
                    mermaid_source,
                    "          </div>",
                    "        </div>",
                ]
            )
        sections_html.extend(
            [
                '      <section class="preset">',
                f"        <h2>{html.escape(preset['title'])}</h2>",
                f"        <p class=\"meta\">{html.escape(page_title)}</p>",
                *subsections,
                "      </section>",
            ]
        )

    node_list_html = render_node_list_html(db)
    relation_list_html = render_relation_list_html(db)

    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="ja">',
            "<head>",
            '  <meta charset="utf-8" />',
            '  <meta name="viewport" content="width=device-width, initial-scale=1" />',
            "  <title>Prompt Vault DB Graph</title>",
            "  <style>",
            "    :root { color-scheme: light; }",
            "    body { margin: 0; background: #f4f1ea; color: #111827; font-family: system-ui, sans-serif; }",
            "    main { max-width: 1800px; margin: 0 auto; padding: 24px; }",
            "    header { margin-bottom: 24px; }",
            "    h1 { margin: 0 0 8px; font-size: 28px; font-weight: 700; }",
            "    .intro { margin: 0; color: #5b6472; font-size: 14px; }",
            "    .preset { margin-bottom: 24px; background: #fff; border: 1px solid #e5e7eb; border-radius: 16px; padding: 20px; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06); }",
            "    .preset h2 { margin: 0 0 6px; font-size: 22px; }",
            "    .meta { margin: 0 0 16px; color: #5b6472; font-size: 13px; }",
            "    .subsection { margin-top: 16px; padding-top: 16px; border-top: 1px solid #eef2f7; }",
            "    .subsection h3 { margin: 0 0 12px; font-size: 16px; }",
            "    .list-block { margin-bottom: 20px; background: #fff; border: 1px solid #e5e7eb; border-radius: 16px; padding: 16px 20px; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06); }",
            "    .list-block summary { cursor: pointer; font-weight: 700; font-size: 16px; }",
            "    .list-table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13px; }",
            "    .list-table th, .list-table td { text-align: left; padding: 8px 10px; border-bottom: 1px solid #eef2f7; vertical-align: top; }",
            "    .list-table th { color: #5b6472; font-weight: 600; }",
            "    .mermaid { overflow: auto; }",
            "  </style>",
            '  <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>',
            "  <script>",
            "    mermaid.initialize({",
            "      startOnLoad: true,",
            "      securityLevel: 'loose',",
            "      theme: 'base',",
            "      flowchart: { curve: 'basis', htmlLabels: true },",
            "      themeVariables: {",
            "        background: '#ffffff',",
            "        primaryColor: '#dbeafe',",
            "        primaryBorderColor: '#2563eb',",
            "        secondaryColor: '#dcfce7',",
            "        secondaryBorderColor: '#059669',",
            "        tertiaryColor: '#f3f4f6',",
            "        fontFamily: 'system-ui, sans-serif',",
            "      },",
            "    });",
            "  </script>",
            "</head>",
            "<body>",
            "  <main>",
            "    <header>",
            "      <h1>Prompt Vault DB Graph</h1>",
            "      <p class=\"intro\">複数の静的ビューを1枚に順番配置した版。全体から局所まで、上から読む。</p>",
            "    </header>",
            *sections_html,
            f"    {node_list_html}",
            f"    {relation_list_html}",
            "  </main>",
            "</body>",
            "</html>",
        ]
    )


def clean_generated_outputs(output_dir: Path) -> None:
    for path in output_dir.glob("db_graph_*.md"):
        path.unlink()
    for path in output_dir.glob("db_graph_*.html"):
        path.unlink()
    for path in [output_dir / "db_graph_index.html"]:
        if path.exists():
            path.unlink()


def render_index_html(entries: list[dict[str, str]]) -> str:
    cards = []
    for entry in entries:
        cards.extend(
            [
                '      <a class="card" href="%s">' % html.escape(entry["html"]),
                f'        <div class="card__title">{html.escape(entry["title"])}</div>',
                f'        <div class="card__meta">{html.escape(entry["meta"])}</div>',
                "      </a>",
            ]
        )
    cards_html = "\n".join(cards)
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="ja">',
            "<head>",
            '  <meta charset="utf-8" />',
            '  <meta name="viewport" content="width=device-width, initial-scale=1" />',
            "  <title>Prompt Vault DB Graph Index</title>",
            "  <style>",
            "    body { margin: 0; background: #f4f1ea; color: #111827; font-family: system-ui, sans-serif; }",
            "    main { max-width: 1200px; margin: 0 auto; padding: 24px; }",
            "    h1 { margin: 0 0 8px; font-size: 28px; }",
            "    p { margin: 0 0 20px; color: #5b6472; }",
            "    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; }",
            "    .card { display: block; padding: 18px; border-radius: 16px; background: #fff; border: 1px solid #e5e7eb; text-decoration: none; color: inherit; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06); }",
            "    .card__title { font-size: 16px; font-weight: 700; margin-bottom: 6px; }",
            "    .card__meta { font-size: 13px; color: #5b6472; }",
            "  </style>",
            "</head>",
            "<body>",
            "  <main>",
            "    <h1>Prompt Vault DB Graph</h1>",
            "    <p>静的に生成した図の入口。用途ごとに最初の視点を切り替える。</p>",
            f"    <div class=\"grid\">{cards_html}</div>",
            "  </main>",
            "</body>",
            "</html>",
        ]
    )


def render_preset(
    db: dict[str, Any],
    preset: dict[str, Any],
    output_dir: Path,
) -> tuple[Path, Path]:
    sections, page_title = render_sections(
        db,
        preset["mode"],
        preset["focus"],
        normalize_values(preset["kinds"]),
        normalize_values(preset["categories"]),
    )
    html_path = output_dir / f"db_graph_{preset['slug']}.html"
    md_path = output_dir / f"db_graph_{preset['slug']}.md"
    html_path.write_text(render_html(sections, page_title), encoding="utf-8")
    md_path.write_text(render_markdown(sections), encoding="utf-8")
    return html_path, md_path


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
        help="directory to write db_graph.md and db_graph.html",
    )
    args = parser.parse_args()

    db = load_db()
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    clean_generated_outputs(output_dir)

    if args.kind or args.category or args.focus or args.mode != "overview":
        sections, page_title = render_sections(
            db,
            args.mode,
            args.focus,
            normalize_values(args.kind),
            normalize_values(args.category),
        )
        markdown = render_markdown(sections)
        html_output = render_html(sections, page_title)
    else:
        markdown = render_combined_markdown(db)
        html_output = render_combined_html(db)

    md_path = output_dir / MD_PATH.name
    html_path = output_dir / HTML_PATH.name
    md_path.write_text(markdown, encoding="utf-8")
    html_path.write_text(html_output, encoding="utf-8")
    print(f"wrote {md_path}")
    print(f"wrote {html_path}")


if __name__ == "__main__":
    main()
