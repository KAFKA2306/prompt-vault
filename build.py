from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "db" / "prompts.json"
DIST_PATH = ROOT / "dist"


def load_prompts() -> list[dict[str, Any]]:
    return json.loads(DB_PATH.read_text(encoding="utf-8"))


def render_static(prompts: list[dict[str, Any]]) -> str:
    prompt_json = json.dumps(prompts, ensure_ascii=False)
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Prompt Vault</title>
  <style>
    :root {{
      --bg: #f6f8ff;
      --panel: rgba(255, 255, 255, 0.72);
      --line: rgba(88, 110, 170, 0.15);
      --line-strong: rgba(88, 110, 170, 0.24);
      --text: #182033;
      --muted: #667087;
      --accent: #6f8cff;
      --accent-2: #b48cff;
      --shadow: 0 30px 80px rgba(77, 95, 146, 0.14);
      --radius: 24px;
      --font: "Noto Sans JP", "Inter", system-ui, sans-serif;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--text);
      font-family: var(--font);
      background:
        radial-gradient(circle at 10% 15%, rgba(134, 216, 255, 0.28), transparent 26%),
        radial-gradient(circle at 85% 18%, rgba(180, 140, 255, 0.2), transparent 24%),
        radial-gradient(circle at 70% 82%, rgba(111, 140, 255, 0.16), transparent 22%),
        linear-gradient(180deg, #f6f8ff, #eef3ff);
      min-height: 100vh;
    }}
    .page {{
      width: min(1440px, 100%);
      margin: 0 auto;
      padding: 28px;
    }}
    .hero {{
      display: grid;
      grid-template-columns: minmax(0, 1.4fr) minmax(280px, 0.8fr);
      gap: 18px;
      margin-bottom: 18px;
    }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      backdrop-filter: blur(16px);
    }}
    .hero-copy {{ padding: 24px; }}
    .eyebrow {{
      display: inline-flex;
      gap: 8px;
      align-items: center;
      padding: 7px 12px;
      border-radius: 999px;
      background: rgba(111, 140, 255, 0.09);
      color: #4561c9;
      border: 1px solid rgba(111, 140, 255, 0.16);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.04em;
    }}
    h1 {{
      margin: 8px 0 12px;
      font-size: clamp(32px, 5vw, 58px);
      line-height: 1.02;
      letter-spacing: -0.04em;
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
      background: rgba(255, 255, 255, 0.76);
      border: 1px solid var(--line);
    }}
    .metric .label {{ font-size: 12px; color: var(--muted); }}
    .metric .value {{
      display: block;
      margin-top: 4px;
      font-size: 28px;
      font-weight: 800;
      letter-spacing: -0.03em;
    }}
    .workspace {{
      display: grid;
      grid-template-columns: minmax(320px, 0.86fr) minmax(0, 1.14fr);
      gap: 18px;
    }}
    .sidebar, .detail {{
      padding: 18px;
    }}
    .head {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 12px;
      margin-bottom: 14px;
    }}
    .head h2, .head h3 {{
      margin: 4px 0 0;
      letter-spacing: -0.02em;
    }}
    .subtle {{ color: var(--muted); font-size: 12px; }}
    .search {{
      width: 100%;
      border: 1px solid var(--line);
      background: rgba(255, 255, 255, 0.9);
      color: var(--text);
      border-radius: 16px;
      padding: 12px 14px;
      font: inherit;
      outline: none;
      margin-bottom: 10px;
    }}
    .search:focus {{
      border-color: rgba(111, 140, 255, 0.38);
      box-shadow: 0 0 0 4px rgba(111, 140, 255, 0.08);
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
      background: rgba(255, 255, 255, 0.82);
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
      transition: transform 0.16s ease, border-color 0.16s ease;
    }}
    .card:hover {{
      transform: translateY(-2px);
      border-color: var(--line-strong);
    }}
    .card.active {{
      border-color: rgba(111, 140, 255, 0.36);
      box-shadow: 0 18px 50px rgba(111, 140, 255, 0.12);
    }}
    .row, .card-top, .card-actions {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
    }}
    .title {{
      font-weight: 800;
      letter-spacing: -0.02em;
      margin: 0;
    }}
    .meta, .preview {{
      color: var(--muted);
      font-size: 12px;
    }}
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
      background: rgba(111, 140, 255, 0.08);
      color: #4960b2;
      border: 1px solid rgba(111, 140, 255, 0.12);
    }}
    .detail {{
      display: grid;
      gap: 14px;
    }}
    .block {{
      padding: 16px;
      background: rgba(255, 255, 255, 0.74);
      border: 1px solid var(--line);
      border-radius: 20px;
    }}
    .blocks {{
      display: grid;
      gap: 10px;
    }}
    pre {{
      margin: 10px 0 0;
      padding: 14px;
      overflow: auto;
      white-space: pre-wrap;
      word-break: break-word;
      background: rgba(245, 248, 255, 0.95);
      border: 1px solid var(--line);
      border-radius: 18px;
      line-height: 1.7;
      font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
      color: #25314c;
    }}
    .buttons {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 12px;
    }}
    .status {{
      color: #51607c;
      font-size: 13px;
      min-height: 18px;
    }}
    .empty {{
      padding: 18px;
      text-align: center;
      color: var(--muted);
      border: 1px dashed rgba(111, 140, 255, 0.22);
      border-radius: 18px;
      background: rgba(255, 255, 255, 0.52);
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
        <p class="lead">ちちぷい寄りの「見せる場」ではなく、用途別の断片を素早くコピーするための保管庫です。全文、本文、ネガティブ、用途メモをすぐ取り出せます。</p>
      </div>
      <aside class="panel hero-side">
        <div class="metric"><span class="label">総数</span><span class="value" id="metric-total">0</span></div>
        <div class="metric"><span class="label">固定</span><span class="value" id="metric-pinned">0</span></div>
        <div class="metric"><span class="label">カテゴリ</span><span class="value" id="metric-categories">0</span></div>
      </aside>
    </section>

    <section class="workspace">
      <aside class="panel sidebar">
        <div class="head">
          <div>
            <div class="subtle">一覧</div>
            <h2>用途を選ぶ</h2>
          </div>
        </div>
        <input id="search" class="search" placeholder="検索: タイトル / 本文 / タグ / メモ" />
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
          <span class="subtle" id="detail-category">-</span>
        </div>

        <div class="block">
          <div class="subtle">用途メモ</div>
          <div id="detail-notes" style="margin-top: 6px; line-height: 1.8;">一覧から選んでください。</div>
        </div>

        <div class="blocks">
          <div class="block">
            <div class="row">
              <div>
                <div class="subtle">本文</div>
                <h3 style="margin: 4px 0 0;">メインプロンプト</h3>
              </div>
              <button class="button" id="copy-main">コピー</button>
            </div>
            <pre id="detail-main"></pre>
          </div>

          <div class="block">
            <div class="row">
              <div>
                <div class="subtle">禁止</div>
                <h3 style="margin: 4px 0 0;">ネガティブ</h3>
              </div>
              <button class="button" id="copy-negative">コピー</button>
            </div>
            <pre id="detail-negative"></pre>
          </div>

          <div class="block">
            <div class="row">
              <div>
                <div class="subtle">全文</div>
                <h3 style="margin: 4px 0 0;">Gemini CLI 用パック</h3>
              </div>
              <button class="button primary" id="copy-full">全文コピー</button>
            </div>
            <pre id="detail-full"></pre>
          </div>
        </div>

        <div class="buttons">
          <button class="button" id="copy-title">タイトルコピー</button>
          <button class="button" id="copy-notes">用途メモコピー</button>
          <button class="button" id="copy-tags">タグコピー</button>
        </div>

        <div class="status" id="status"></div>
      </section>
    </section>
  </main>

  <script>
    const prompts = {prompt_json};
    const state = {{
      prompts,
      selectedId: prompts[0]?.id || null,
      search: '',
      category: 'すべて',
    }};

    const el = (id) => document.getElementById(id);

    const splitTags = (value) =>
      Array.from(new Set(String(value || '').split(/[,\n]/).map((item) => item.trim()).filter(Boolean)));

    const selected = () => state.prompts.find((item) => item.id === state.selectedId) || null;

    const pack = (prompt) => [
      `# ${{prompt.title || '無題'}}`,
      `カテゴリ: ${{prompt.category || '未分類'}}`,
      splitTags(prompt.tags || []).length ? `タグ: ${{splitTags(prompt.tags || []).map((tag) => `#${{tag}}`).join(' ')}}` : 'タグ: なし',
      prompt.notes ? `メモ: ${{prompt.notes}}` : '',
      '',
      '--- メイン ---',
      prompt.prompt_text || '',
      '',
      '--- ネガティブ ---',
      prompt.negative_prompt || '',
    ].filter(Boolean).join('\n');

    const renderMetrics = () => {{
      const categories = new Set(state.prompts.map((item) => item.category));
      el('metric-total').textContent = String(state.prompts.length);
      el('metric-pinned').textContent = String(state.prompts.filter((item) => item.is_pinned).length);
      el('metric-categories').textContent = String(categories.size);
    }};

    const renderFilters = () => {{
      const names = ['すべて', ...Array.from(new Set(state.prompts.map((item) => item.category).filter(Boolean))).sort()];
      el('filters').innerHTML = names.map((name) => `<button class="chip ${{state.category === name ? 'active' : ''}}" data-category="${{name}}">${{name}}</button>`).join('');
      el('filters').querySelectorAll('[data-category]').forEach((button) =>
        button.addEventListener('click', () => {{
          state.category = button.dataset.category;
          render();
        }})
      );
    }};

    const filteredPrompts = () => {{
      const query = state.search.trim().toLowerCase();
      return state.prompts.filter((item) => {{
        const matchesCategory = state.category === 'すべて' || item.category === state.category;
        const haystack = [item.title, item.category, item.prompt_text, item.negative_prompt, item.notes, ...(item.tags || [])].join(' ').toLowerCase();
        const matchesSearch = !query || haystack.includes(query);
        return matchesCategory && matchesSearch;
      }});
    }};

    const renderList = () => {{
      const list = filteredPrompts();
      el('list-meta').textContent = `${{list.length}} 件表示 / ${{state.prompts.length}} 件`;
      el('list').innerHTML = list.map((item) => `
        <article class="panel card ${{item.id === state.selectedId ? 'active' : ''}}" data-id="${{item.id}}">
          <div class="card-top">
            <div>
              <p class="title">${{item.title}}</p>
              <div class="meta">${{item.category}} ・ ${{new Date(item.updated_at).toLocaleDateString('ja-JP')}}</div>
            </div>
            ${{item.is_pinned ? '<span class="tag">固定</span>' : ''}}
          </div>
          <p class="preview">${{item.notes || item.prompt_text}}</p>
          <div class="tagrow">${{(item.tags || []).slice(0, 4).map((tag) => `<span class="tag">#${{tag}}</span>`).join('')}}</div>
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
      const prompt = selected();
      if (!prompt) {{
        el('detail-title').textContent = 'テンプレートを選択';
        el('detail-category').textContent = '-';
        el('detail-notes').textContent = '一覧から選んでください。';
        el('detail-main').textContent = '';
        el('detail-negative').textContent = '';
        el('detail-full').textContent = '';
        return;
      }}

      el('detail-title').textContent = prompt.title;
      el('detail-category').textContent = prompt.category;
      el('detail-notes').textContent = prompt.notes || 'メモなし';
      el('detail-main').textContent = prompt.prompt_text || '';
      el('detail-negative').textContent = prompt.negative_prompt || '';
      el('detail-full').textContent = pack(prompt);
    }};

    const setStatus = (text) => {{
      el('status').textContent = text;
    }};

    const copyText = async (text, label) => {{
      await navigator.clipboard.writeText(text);
      setStatus(`${{label}}をコピーしました`);
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
    el('copy-main').addEventListener('click', () => {{
      const prompt = selected();
      if (!prompt) return;
      copyText(prompt.prompt_text || '', '本文');
    }});
    el('copy-negative').addEventListener('click', () => {{
      const prompt = selected();
      if (!prompt) return;
      copyText(prompt.negative_prompt || '', 'ネガティブ');
    }});
    el('copy-full').addEventListener('click', () => {{
      const prompt = selected();
      if (!prompt) return;
      copyText(pack(prompt), '全文');
    }});
    el('copy-title').addEventListener('click', () => {{
      const prompt = selected();
      if (!prompt) return;
      copyText(prompt.title || '', 'タイトル');
    }});
    el('copy-notes').addEventListener('click', () => {{
      const prompt = selected();
      if (!prompt) return;
      copyText(prompt.notes || '', '用途メモ');
    }});
    el('copy-tags').addEventListener('click', () => {{
      const prompt = selected();
      if (!prompt) return;
      copyText((prompt.tags || []).map((tag) => `#${{tag}}`).join(' '), 'タグ');
    }});

    render();
  </script>
</body>
</html>"""


def main() -> None:
    DIST_PATH.mkdir(parents=True, exist_ok=True)
    (DIST_PATH / "index.html").write_text(render_static(load_prompts()), encoding="utf-8")


if __name__ == "__main__":
    main()

