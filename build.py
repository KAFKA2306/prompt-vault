from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "db" / "prompts.json"
DIST_PATH = ROOT / "dist"


def load_db() -> dict[str, Any]:
    return json.loads(DB_PATH.read_text(encoding="utf-8"))


def render_block(block: dict[str, Any]) -> str:
    tags = block.get("tags") or []
    tag_text = " ".join(f"#{tag}" for tag in tags)
    return "\n".join(
        part
        for part in [
            f"## {block['title']}",
            f"カテゴリ: {block['category']}",
            f"タグ: {tag_text}" if tag_text else "",
            block["content"],
        ]
        if part
    )


def render_template(template: dict[str, Any], blocks: dict[str, dict[str, Any]]) -> str:
    return "\n\n".join(render_block(blocks[block_id]) for block_id in template["blocks"])


def render_static(db: dict[str, Any]) -> str:
    blocks = {block["id"]: block for block in db["blocks"]}
    templates = db["templates"]
    db_json = json.dumps(db, ensure_ascii=False)
    template_json = json.dumps(
        [
            {
                **template,
                "full_text": render_template(template, blocks),
            }
            for template in templates
        ],
        ensure_ascii=False,
    )
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Prompt Vault</title>
  <style>
    :root {{
      --bg: #f6f8ff;
      --panel: rgba(255,255,255,.76);
      --line: rgba(88,110,170,.15);
      --line-strong: rgba(88,110,170,.24);
      --text: #182033;
      --muted: #667087;
      --accent: #6f8cff;
      --accent-2: #b48cff;
      --shadow: 0 30px 80px rgba(77,95,146,.14);
      --radius: 24px;
      --font: "Noto Sans JP","Inter",system-ui,sans-serif;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--text);
      font-family: var(--font);
      background:
        radial-gradient(circle at 10% 15%, rgba(134,216,255,.28), transparent 26%),
        radial-gradient(circle at 85% 18%, rgba(180,140,255,.20), transparent 24%),
        radial-gradient(circle at 70% 82%, rgba(111,140,255,.16), transparent 22%),
        linear-gradient(180deg, #f6f8ff, #eef3ff);
      min-height: 100vh;
    }}
    .page {{ width: min(1440px,100%); margin: 0 auto; padding: 28px; }}
    .hero, .workspace, .panel, .card, .button, input, textarea, pre {{
      backdrop-filter: blur(16px);
    }}
    .hero {{
      display: grid;
      grid-template-columns: minmax(0,1.4fr) minmax(280px,.8fr);
      gap: 18px;
      margin-bottom: 18px;
    }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
    }}
    .hero-copy {{ padding: 24px; }}
    .eyebrow {{
      display: inline-flex;
      gap: 8px;
      align-items: center;
      padding: 7px 12px;
      border-radius: 999px;
      background: rgba(111,140,255,.09);
      color: #4561c9;
      border: 1px solid rgba(111,140,255,.16);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: .04em;
    }}
    h1 {{
      margin: 8px 0 12px;
      font-size: clamp(32px,5vw,58px);
      line-height: 1.02;
      letter-spacing: -.04em;
    }}
    .lead {{
      max-width: 64ch;
      color: var(--muted);
      line-height: 1.8;
      margin: 0;
      font-size: 15px;
    }}
    .hero-side {{
      padding: 18px;
      display: grid;
      gap: 12px;
      align-content: start;
    }}
    .metric {{
      padding: 16px;
      border-radius: 20px;
      background: rgba(255,255,255,.76);
      border: 1px solid var(--line);
    }}
    .metric .label {{ font-size: 12px; color: var(--muted); }}
    .metric .value {{
      display: block;
      margin-top: 4px;
      font-size: 28px;
      font-weight: 800;
      letter-spacing: -.03em;
    }}
    .workspace {{
      display: grid;
      grid-template-columns: minmax(320px,.86fr) minmax(0,1.14fr);
      gap: 18px;
    }}
    .sidebar, .detail {{ padding: 18px; }}
    .head {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 12px;
      margin-bottom: 14px;
    }}
    .head h2, .head h3 {{ margin: 4px 0 0; letter-spacing: -.02em; }}
    .subtle {{ color: var(--muted); font-size: 12px; }}
    .search {{
      width: 100%;
      border: 1px solid var(--line);
      background: rgba(255,255,255,.9);
      color: var(--text);
      border-radius: 16px;
      padding: 12px 14px;
      font: inherit;
      outline: none;
      margin-bottom: 10px;
    }}
    .search:focus {{
      border-color: rgba(111,140,255,.38);
      box-shadow: 0 0 0 4px rgba(111,140,255,.08);
    }}
    .chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 12px;
    }}
    .chip, .button {{
      border-radius: 999px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,.82);
      padding: 9px 12px;
      color: #42506b;
      font-size: 13px;
      cursor: pointer;
    }}
    .chip.active, .button.primary {{
      background: linear-gradient(135deg, var(--accent), var(--accent-2));
      color: #fff;
      border-color: transparent;
    }}
    .list {{
      display: grid;
      gap: 10px;
      max-height: calc(100vh - 330px);
      overflow: auto;
      padding-right: 4px;
    }}
    .card {{
      padding: 14px;
      cursor: pointer;
      transition: transform .16s ease, border-color .16s ease;
    }}
    .card:hover {{ transform: translateY(-2px); border-color: var(--line-strong); }}
    .card.active {{
      border-color: rgba(111,140,255,.36);
      box-shadow: 0 18px 50px rgba(111,140,255,.12);
    }}
    .title {{ font-weight: 800; letter-spacing: -.02em; margin: 0; }}
    .meta, .preview {{ color: var(--muted); font-size: 12px; }}
    .preview {{
      margin: 10px 0 0;
      line-height: 1.7;
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }}
    .tagrow {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 10px;
    }}
    .tag {{
      font-size: 12px;
      padding: 5px 9px;
      border-radius: 999px;
      background: rgba(111,140,255,.08);
      color: #4960b2;
      border: 1px solid rgba(111,140,255,.12);
    }}
    .detail {{
      display: grid;
      gap: 14px;
    }}
    .block {{
      padding: 16px;
      background: rgba(255,255,255,.74);
      border: 1px solid var(--line);
      border-radius: 20px;
    }}
    .blocks {{ display: grid; gap: 10px; }}
    pre {{
      margin: 10px 0 0;
      padding: 14px;
      overflow: auto;
      white-space: pre-wrap;
      word-break: break-word;
      background: rgba(245,248,255,.95);
      border: 1px solid var(--line);
      border-radius: 18px;
      line-height: 1.7;
      font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
      color: #25314c;
    }}
    .buttons {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }}
    .status {{ color: #51607c; font-size: 13px; min-height: 18px; }}
    .empty {{
      padding: 18px;
      text-align: center;
      color: var(--muted);
      border: 1px dashed rgba(111,140,255,.22);
      border-radius: 18px;
      background: rgba(255,255,255,.52);
    }}
    @media (max-width: 1100px) {{
      .hero, .workspace {{ grid-template-columns: 1fr; }}
      .list {{ max-height: none; }}
    }}
    @media (max-width: 720px) {{
      .page {{ padding: 14px; }}
      .buttons {{ flex-direction: column; }}
      .buttons .button {{ width: 100%; }}
    }}
  </style>
</head>
<body>
  <main class="page">
    <section class="hero">
      <div class="panel hero-copy">
        <div class="eyebrow">用途別テンプレート / ローカルDB / 静的配信</div>
        <h1>Prompt Vault</h1>
        <p class="lead">全文ではなく、用途別のブロックを保存する保管庫です。組み立て済み全文、ブロック単体、タグ、メモをそのままコピーできます。</p>
      </div>
      <aside class="panel hero-side">
        <div class="metric"><span class="label">ブロック数</span><span class="value" id="metric-blocks">0</span></div>
        <div class="metric"><span class="label">テンプレート数</span><span class="value" id="metric-templates">0</span></div>
        <div class="metric"><span class="label">固定</span><span class="value" id="metric-pinned">0</span></div>
      </aside>
    </section>

    <section class="workspace">
      <aside class="panel sidebar">
        <div class="head">
          <div>
            <div class="subtle">テンプレート</div>
            <h2>用途を選ぶ</h2>
          </div>
        </div>
        <input id="search" class="search" placeholder="検索: タイトル / 説明 / ブロックID" />
        <div class="chips" id="filters"></div>
        <div class="subtle" id="list-meta">-</div>
        <div class="list" id="list"></div>
      </aside>

      <section class="panel detail">
        <div class="head">
          <div>
            <div class="subtle">詳細</div>
            <h2 id="detail-title">テンプレートを選択</h2>
          </div>
          <span class="subtle" id="detail-purpose">-</span>
        </div>

        <div class="block">
          <div class="subtle">用途メモ</div>
          <div id="detail-notes" style="margin-top: 6px; line-height: 1.8;">一覧から選んでください。</div>
        </div>

        <div class="blocks" id="block-list"></div>

        <div class="block">
          <div class="head" style="margin:0 0 6px 0;">
            <div>
              <div class="subtle">全文</div>
              <h3 style="margin:4px 0 0;">組み立て済みパック</h3>
            </div>
            <button class="button primary" id="copy-full">全文コピー</button>
          </div>
          <pre id="detail-full"></pre>
        </div>

        <div class="buttons">
          <button class="button" id="copy-title">タイトルコピー</button>
          <button class="button" id="copy-purpose">用途コピー</button>
          <button class="button" id="copy-blocks">ブロックIDコピー</button>
        </div>

        <div class="status" id="status"></div>
      </section>
    </section>
  </main>

  <script>
    const db = {db_json};
    const templates = {template_json};
    const blocks = Object.fromEntries(db.blocks.map((block) => [block.id, block]));
    const state = {{
      templates,
      selectedId: templates[0]?.id || null,
      search: '',
      category: 'すべて',
    }};

    const el = (id) => document.getElementById(id);

    const renderBlock = (block) => [
      `## ${{block.title}}`,
      `ID: ${{block.id}}`,
      `カテゴリ: ${{block.category}}`,
      block.tags?.length ? `タグ: ${{block.tags.map((tag) => `#${{tag}}`).join(' ')}}` : '',
      block.content,
    ].filter(Boolean).join('\\n');

    const renderTemplate = (template) => template.blocks.map((blockId) => renderBlock(blocks[blockId])).join('\\n\\n');

    const selected = () => state.templates.find((item) => item.id === state.selectedId) || null;

    const renderMetrics = () => {{
      el('metric-blocks').textContent = String(db.blocks.length);
      el('metric-templates').textContent = String(state.templates.length);
      el('metric-pinned').textContent = String(state.templates.filter((item) => item.is_pinned).length);
    }};

    const renderFilters = () => {{
      const names = ['すべて', ...Array.from(new Set(state.templates.map((item) => item.purpose))).filter(Boolean)];
      el('filters').innerHTML = names.map((name) => `<button class="chip ${{state.category === name ? 'active' : ''}}" data-category="${{name}}">${{name}}</button>`).join('');
      el('filters').querySelectorAll('[data-category]').forEach((button) =>
        button.addEventListener('click', () => {{
          state.category = button.dataset.category;
          render();
        }})
      );
    }};

    const filteredTemplates = () => {{
      const query = state.search.trim().toLowerCase();
      return state.templates.filter((template) => {{
        const matchesCategory = state.category === 'すべて' || template.purpose === state.category;
        const haystack = [
          template.title,
          template.purpose,
          template.notes,
          template.blocks.join(' '),
        ].join(' ').toLowerCase();
        return matchesCategory && (!query || haystack.includes(query));
      }});
    }};

    const renderList = () => {{
      const list = filteredTemplates();
      el('list-meta').textContent = `${{list.length}} 件表示 / ${{state.templates.length}} 件`;
      el('list').innerHTML = list.map((template) => `
        <article class="panel card ${{template.id === state.selectedId ? 'active' : ''}}" data-id="${{template.id}}">
          <div class="card-top">
            <div>
              <p class="title">${{template.title}}</p>
              <div class="meta">${{template.purpose}}</div>
            </div>
            ${{template.is_pinned ? '<span class="tag">固定</span>' : ''}}
          </div>
          <p class="preview">${{template.notes || template.blocks.join(', ')}}</p>
          <div class="tagrow">${{template.blocks.slice(0, 5).map((blockId) => `<span class="tag">${{blockId}}</span>`).join('')}}</div>
        </article>
      `).join('');
      el('list').querySelectorAll('[data-id]').forEach((card) =>
        card.addEventListener('click', () => {{
          state.selectedId = card.dataset.id;
          renderDetail();
          renderList();
        }})
      );
      if (!list.length) {{
        el('list').innerHTML = '<div class="empty">一致するテンプレートがありません。</div>';
      }}
    }};

    const renderDetail = () => {{
      const template = selected();
      if (!template) {{
        el('detail-title').textContent = 'テンプレートを選択';
        el('detail-purpose').textContent = '-';
        el('detail-notes').textContent = '一覧から選んでください。';
        el('block-list').innerHTML = '';
        el('detail-full').textContent = '';
        return;
      }}

      el('detail-title').textContent = template.title;
      el('detail-purpose').textContent = template.purpose;
      el('detail-notes').textContent = template.notes || 'メモなし';
      el('detail-full').textContent = renderTemplate(template);
      el('block-list').innerHTML = template.blocks.map((blockId) => {{
        const block = blocks[blockId];
        return `
          <div class="block">
            <div class="head" style="margin:0 0 6px 0;">
              <div>
                <div class="subtle">${{block.category}}</div>
                <h3 style="margin:4px 0 0;">${{block.title}}</h3>
              </div>
              <button class="button" data-copy="${{block.id}}">コピー</button>
            </div>
            <pre>${{renderBlock(block)}}</pre>
          </div>
        `;
      }}).join('');
      el('block-list').querySelectorAll('[data-copy]').forEach((button) =>
        button.addEventListener('click', async () => {{
          const block = blocks[button.dataset.copy];
          await navigator.clipboard.writeText(renderBlock(block));
          el('status').textContent = `${{block.title}}をコピーしました`;
        }})
      );
    }};

    const copyText = async (text, label) => {{
      await navigator.clipboard.writeText(text);
      el('status').textContent = `${{label}}をコピーしました`;
    }};

    const render = () => {{
      renderMetrics();
      renderFilters();
      renderList();
      renderDetail();
    }};

    el('search').addEventListener('input', (event) => {{
      state.search = event.target.value;
      renderList();
    }});
    el('copy-full').addEventListener('click', () => {{
      const template = selected();
      if (!template) return;
      copyText(renderTemplate(template), '全文');
    }});
    el('copy-title').addEventListener('click', () => {{
      const template = selected();
      if (!template) return;
      copyText(template.title, 'タイトル');
    }});
    el('copy-purpose').addEventListener('click', () => {{
      const template = selected();
      if (!template) return;
      copyText(template.purpose, '用途');
    }});
    el('copy-blocks').addEventListener('click', () => {{
      const template = selected();
      if (!template) return;
      copyText(template.blocks.join(', '), 'ブロックID');
    }});

    render();
  </script>
</body>
</html>"""


def main() -> None:
    DIST_PATH.mkdir(parents=True, exist_ok=True)
    (DIST_PATH / "index.html").write_text(render_static(load_db()), encoding="utf-8")


if __name__ == "__main__":
    main()
