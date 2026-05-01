from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "db" / "prompts.json"

SEED_PROMPTS: list[dict[str, Any]] = [
    {
        "id": "seed-kafka-style",
        "title": "KAFKA Futuristic Infographic Manga 2026",
        "category": "マスタースタイル",
        "prompt_text": "ultra high quality Japanese infographic manga page, emotional slice-of-life manga, systems thinking visualization, VTuber aesthetics, soft futuristic atmosphere, educational infographic design, psychologically immersive storytelling, pastel blue and lavender palette, clean lineart, elegant typography, large central visual, multiple information panels, clean hierarchy, gentle emotion, human-made, carefully designed, soft indirect lighting, monitor glow, tiny sparkles, transparent UI, cozy intelligent future workstation, same character identity, same visual language, same emotional tone",
        "negative_prompt": "low quality, low resolution, bad anatomy, extra fingers, random English text, broken Japanese, watermark, harsh shadows, oversaturated colors, cheap anime style, generic AI anime, plastic skin, cyberpunk overload, chaotic typography, soulless infographic",
        "notes": "ユーザーのマスター指定。最初の基準プロンプトとして使う。",
        "tags": ["kafka", "infographic", "manga", "vtuber", "pastel"],
        "reference_url": "",
        "is_pinned": True,
        "created_at": "2026-05-01T00:00:00Z",
        "updated_at": "2026-05-01T00:00:00Z",
        "last_used_at": None,
    }
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def ensure_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        return
    DB_PATH.write_text(json.dumps(SEED_PROMPTS, ensure_ascii=False, indent=2), encoding="utf-8")


def load_prompts() -> list[dict[str, Any]]:
    ensure_db()
    return json.loads(DB_PATH.read_text(encoding="utf-8"))


def save_prompts(prompts: list[dict[str, Any]]) -> None:
    tmp_path = DB_PATH.with_suffix(".json.tmp")
    tmp_path.write_text(json.dumps(prompts, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_path.replace(DB_PATH)


def split_tags(raw: Any) -> list[str]:
    if isinstance(raw, list):
        values = [str(item).strip() for item in raw]
    else:
        values = [part.strip() for part in str(raw or "").replace("\n", ",").split(",")]
    return list(dict.fromkeys([value for value in values if value]))


def normalize_record(payload: dict[str, Any], existing: dict[str, Any] | None = None) -> dict[str, Any]:
    base = existing or {}
    created_at = base.get("created_at") or utc_now()
    return {
        "id": base.get("id") or payload.get("id") or uuid.uuid4().hex,
        "title": str(payload.get("title", base.get("title", ""))).strip(),
        "category": str(payload.get("category", base.get("category", "未分類"))).strip() or "未分類",
        "prompt_text": str(payload.get("prompt_text", base.get("prompt_text", ""))).strip(),
        "negative_prompt": str(payload.get("negative_prompt", base.get("negative_prompt", ""))).strip(),
        "notes": str(payload.get("notes", base.get("notes", ""))).strip(),
        "tags": split_tags(payload.get("tags", base.get("tags", []))),
        "reference_url": str(payload.get("reference_url", base.get("reference_url", ""))).strip(),
        "is_pinned": bool(payload.get("is_pinned", base.get("is_pinned", False))),
        "created_at": created_at,
        "updated_at": utc_now(),
        "last_used_at": base.get("last_used_at"),
    }


def sorted_prompts(prompts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        prompts,
        key=lambda item: (
            not bool(item.get("is_pinned")),
            item.get("updated_at", ""),
            item.get("created_at", ""),
        ),
        reverse=False,
    )


def render_html() -> str:
    return """<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Prompt Vault</title>
  <style>
    :root{
      --bg:#f6f8ff;
      --bg-2:#eef3ff;
      --panel:rgba(255,255,255,.72);
      --panel-strong:#ffffff;
      --line:rgba(88,110,170,.15);
      --line-strong:rgba(88,110,170,.24);
      --text:#1a2030;
      --muted:#6a7488;
      --accent:#6f8cff;
      --accent-2:#86d8ff;
      --accent-3:#b48cff;
      --shadow:0 30px 80px rgba(77, 95, 146, .14);
      --radius:24px;
      --radius-sm:16px;
      --font:"Noto Sans JP","Inter",system-ui,sans-serif;
    }
    *{box-sizing:border-box}
    body{
      margin:0;
      color:var(--text);
      font-family:var(--font);
      background:
        radial-gradient(circle at 10% 15%, rgba(134,216,255,.28), transparent 26%),
        radial-gradient(circle at 85% 18%, rgba(180,140,255,.20), transparent 24%),
        radial-gradient(circle at 70% 82%, rgba(111,140,255,.16), transparent 22%),
        linear-gradient(180deg,var(--bg),var(--bg-2));
      min-height:100vh;
    }
    .orbs span{
      position:fixed;
      inset:auto;
      border-radius:999px;
      filter:blur(12px);
      pointer-events:none;
      opacity:.8;
    }
    .orb-a{width:220px;height:220px;left:-60px;top:120px;background:rgba(134,216,255,.18)}
    .orb-b{width:180px;height:180px;right:40px;top:80px;background:rgba(180,140,255,.16)}
    .orb-c{width:240px;height:240px;right:-80px;bottom:20px;background:rgba(111,140,255,.12)}
    .page{
      width:min(1440px,100%);
      margin:0 auto;
      padding:28px;
    }
    .hero,.workspace,.toolbar,.panel,.card,.editor,.bundle,.chip,.button,input,textarea{
      backdrop-filter:blur(16px);
    }
    .hero{
      display:grid;
      grid-template-columns:minmax(0,1.4fr) minmax(320px,.8fr);
      gap:18px;
      align-items:stretch;
      margin-bottom:18px;
    }
    .panel,.hero-block{
      background:var(--panel);
      border:1px solid var(--line);
      border-radius:var(--radius);
      box-shadow:var(--shadow);
    }
    .hero-block{
      padding:24px;
      position:relative;
      overflow:hidden;
    }
    .hero-block h1{
      margin:6px 0 10px;
      font-size:clamp(32px,5vw,58px);
      letter-spacing:-.04em;
      line-height:1.02;
    }
    .eyebrow{
      display:inline-flex;
      gap:8px;
      align-items:center;
      padding:7px 12px;
      border-radius:999px;
      background:rgba(111,140,255,.09);
      color:#4561c9;
      border:1px solid rgba(111,140,255,.16);
      font-size:12px;
      font-weight:700;
      letter-spacing:.04em;
    }
    .lead{
      max-width:64ch;
      color:var(--muted);
      line-height:1.8;
      font-size:15px;
      margin:0;
    }
    .commandbar{
      margin-top:18px;
      padding:14px 16px;
      border-radius:18px;
      background:rgba(255,255,255,.68);
      border:1px solid var(--line);
      display:flex;
      flex-wrap:wrap;
      gap:8px;
      color:#43506a;
      font-size:13px;
    }
    .commandbar code{
      font-family:ui-monospace,SFMono-Regular,Consolas,monospace;
      background:rgba(111,140,255,.1);
      border:1px solid rgba(111,140,255,.12);
      padding:4px 8px;
      border-radius:999px;
      color:#344165;
    }
    .metrics{
      padding:18px;
      display:grid;
      gap:12px;
      align-content:start;
    }
    .metric{
      padding:16px;
      border-radius:20px;
      background:rgba(255,255,255,.76);
      border:1px solid var(--line);
    }
    .metric .label{font-size:12px;color:var(--muted)}
    .metric .value{display:block;font-size:28px;font-weight:800;letter-spacing:-.03em;margin-top:4px}
    .workspace{
      display:grid;
      grid-template-columns:minmax(320px,.92fr) minmax(0,1.08fr);
      gap:18px;
    }
    .sidebar,.editor{
      padding:18px;
    }
    .panel-head{
      display:flex;
      justify-content:space-between;
      align-items:flex-start;
      gap:12px;
      margin-bottom:14px;
    }
    .panel-head h2,.panel-head h3{
      margin:4px 0 0;
      font-size:18px;
      letter-spacing:-.02em;
    }
    .subtle{color:var(--muted);font-size:12px}
    .toolbar{
      display:grid;
      gap:10px;
      margin-bottom:14px;
    }
    input,textarea,select{
      width:100%;
      border:1px solid var(--line);
      background:rgba(255,255,255,.9);
      color:var(--text);
      border-radius:16px;
      padding:12px 14px;
      font:inherit;
      outline:none;
    }
    textarea{resize:vertical;min-height:130px;line-height:1.7}
    input:focus,textarea:focus,select:focus{
      border-color:rgba(111,140,255,.38);
      box-shadow:0 0 0 4px rgba(111,140,255,.08);
    }
    .filters{display:flex;flex-wrap:wrap;gap:8px}
    .chip,.button{
      border-radius:999px;
      border:1px solid var(--line);
      background:rgba(255,255,255,.82);
      padding:9px 12px;
      color:#42506b;
      font-size:13px;
      cursor:pointer;
    }
    .chip.active,.button.primary{
      background:linear-gradient(135deg,var(--accent),var(--accent-3));
      color:#fff;
      border-color:transparent;
    }
    .button.ghost{background:rgba(255,255,255,.6)}
    .button.danger{color:#8c3e58}
    .list{
      display:grid;
      gap:10px;
      max-height:calc(100vh - 420px);
      overflow:auto;
      padding-right:4px;
    }
    .card{
      padding:14px;
      cursor:pointer;
      transition:transform .16s ease, border-color .16s ease;
    }
    .card:hover{transform:translateY(-2px);border-color:var(--line-strong)}
    .card.active{
      border-color:rgba(111,140,255,.36);
      box-shadow:0 18px 50px rgba(111,140,255,.12);
    }
    .card-top,.card-bottom,.row{
      display:flex;
      justify-content:space-between;
      align-items:center;
      gap:10px;
    }
    .card-title{
      font-weight:800;
      letter-spacing:-.02em;
      margin:0;
    }
    .card-meta,.card-preview,.meta{
      color:var(--muted);
      font-size:12px;
    }
    .card-preview{
      margin:10px 0 0;
      line-height:1.7;
      display:-webkit-box;
      -webkit-line-clamp:3;
      -webkit-box-orient:vertical;
      overflow:hidden;
    }
    .tagrow{
      display:flex;
      flex-wrap:wrap;
      gap:6px;
      margin-top:10px;
    }
    .tag{
      font-size:12px;
      padding:5px 9px;
      border-radius:999px;
      background:rgba(111,140,255,.08);
      color:#4960b2;
      border:1px solid rgba(111,140,255,.12);
    }
    .split{
      display:grid;
      grid-template-columns:1fr 1fr;
      gap:12px;
    }
    .editor-grid{
      display:grid;
      gap:12px;
    }
    .actions{
      display:flex;
      flex-wrap:wrap;
      justify-content:space-between;
      gap:10px;
      align-items:center;
      margin:14px 0;
    }
    .actions .group{
      display:flex;
      gap:8px;
      flex-wrap:wrap;
    }
    .bundle{
      margin-top:14px;
      padding:16px;
    }
    pre{
      margin:10px 0 0;
      padding:14px;
      overflow:auto;
      white-space:pre-wrap;
      word-break:break-word;
      background:rgba(245,248,255,.95);
      border:1px solid var(--line);
      border-radius:18px;
      line-height:1.7;
      font-family:ui-monospace,SFMono-Regular,Consolas,monospace;
      color:#25314c;
    }
    .status{
      margin-top:8px;
      color:#51607c;
      font-size:13px;
      min-height:18px;
    }
    .empty{
      padding:18px;
      text-align:center;
      color:var(--muted);
      border:1px dashed rgba(111,140,255,.22);
      border-radius:18px;
      background:rgba(255,255,255,.52);
    }
    @media (max-width: 1100px){
      .hero,.workspace{grid-template-columns:1fr}
      .list{max-height:none}
    }
    @media (max-width: 720px){
      .page{padding:14px}
      .split{grid-template-columns:1fr}
      .actions{flex-direction:column;align-items:stretch}
      .actions .group{width:100%}
      .actions .button{flex:1}
    }
  </style>
</head>
<body>
  <div class="orbs"><span class="orb-a"></span><span class="orb-b"></span><span class="orb-c"></span></div>
  <main class="page">
    <section class="hero">
      <div class="hero-block">
        <div class="eyebrow">ローカル完結 / SQLite不要 / 会員登録なし</div>
        <h1>Prompt Vault</h1>
        <p class="lead">ちちぷいや pixiv のような「作る人向けの置き場」を、いちばん単純な形で実装した管理画面です。検索、固定、複製、コピー、編集だけに絞っています。</p>
        <div class="commandbar">
          <span>Gemini CLI で使う想定:</span>
          <code>new</code><code>edit</code><code>copy</code><code>pin</code><code>search</code><code>export</code>
        </div>
      </div>
      <aside class="panel metrics">
        <div class="metric"><span class="label">総数</span><span class="value" id="metric-total">0</span></div>
        <div class="metric"><span class="label">固定</span><span class="value" id="metric-pinned">0</span></div>
        <div class="metric"><span class="label">タグ種</span><span class="value" id="metric-tags">0</span></div>
        <div class="metric"><span class="label">更新</span><span class="value" id="metric-updated" style="font-size:18px">-</span></div>
      </aside>
    </section>

    <section class="workspace">
      <aside class="panel sidebar">
        <div class="panel-head">
          <div>
            <div class="subtle">一覧</div>
            <h2>プロンプトを探す</h2>
          </div>
          <button class="button ghost" id="reload-btn">再読込</button>
        </div>
        <div class="toolbar">
          <input id="search" placeholder="検索: タイトル / 本文 / タグ / メモ" />
          <div class="filters">
            <button class="chip active" data-filter="all">すべて</button>
            <button class="chip" data-filter="pinned">固定のみ</button>
          </div>
          <div class="filters" id="categories"></div>
        </div>
        <div class="subtle" id="list-meta">-</div>
        <div class="list" id="list"></div>
      </aside>

      <section class="panel editor">
        <div class="panel-head">
          <div>
            <div class="subtle">編集</div>
            <h2 id="editor-title">新規プロンプト</h2>
          </div>
          <button class="button ghost" id="new-btn">新規</button>
        </div>
        <div class="editor-grid">
          <input id="id" type="hidden" />
          <input id="title" placeholder="タイトル" />
          <div class="split">
            <input id="category" placeholder="カテゴリ" />
            <input id="tags" placeholder="タグ, カンマ区切り" />
          </div>
          <input id="reference_url" placeholder="参照URL" />
          <textarea id="prompt_text" placeholder="メインプロンプト"></textarea>
          <textarea id="negative_prompt" placeholder="ネガティブプロンプト"></textarea>
          <textarea id="notes" placeholder="メモ"></textarea>
          <label style="display:flex;align-items:center;gap:8px;color:#51607c;font-size:13px">
            <input id="is_pinned" type="checkbox" style="width:auto" />
            固定表示にする
          </label>
        </div>
        <div class="actions">
          <div class="group">
            <button class="button" id="duplicate-btn">複製</button>
            <button class="button" id="copy-btn">本文コピー</button>
            <button class="button" id="bundle-btn">まとめコピー</button>
          </div>
          <div class="group">
            <button class="button danger" id="delete-btn">削除</button>
            <button class="button primary" id="save-btn">保存</button>
          </div>
        </div>
        <div class="bundle">
          <div class="panel-head" style="margin:0">
            <div>
              <div class="subtle">Gemini CLI 用まとめ</div>
              <h3>貼り付けしやすい1本化テキスト</h3>
            </div>
            <div class="subtle" id="bundle-meta"></div>
          </div>
          <pre id="bundle"></pre>
        </div>
        <div class="status" id="status"></div>
      </section>
    </section>
  </main>
  <script>
    const state = {
      prompts: [],
      selectedId: null,
      search: '',
      filter: 'all',
      category: 'すべて',
    };

    const ids = ['id', 'title', 'category', 'tags', 'reference_url', 'prompt_text', 'negative_prompt', 'notes', 'is_pinned'];

    const el = (id) => document.getElementById(id);

    const readForm = () => ({
      id: el('id').value.trim(),
      title: el('title').value.trim(),
      category: el('category').value.trim(),
      tags: el('tags').value.trim(),
      reference_url: el('reference_url').value.trim(),
      prompt_text: el('prompt_text').value.trim(),
      negative_prompt: el('negative_prompt').value.trim(),
      notes: el('notes').value.trim(),
      is_pinned: el('is_pinned').checked,
    });

    const writeForm = (prompt) => {
      el('id').value = prompt?.id || '';
      el('title').value = prompt?.title || '';
      el('category').value = prompt?.category || '未分類';
      el('tags').value = (prompt?.tags || []).join(', ');
      el('reference_url').value = prompt?.reference_url || '';
      el('prompt_text').value = prompt?.prompt_text || '';
      el('negative_prompt').value = prompt?.negative_prompt || '';
      el('notes').value = prompt?.notes || '';
      el('is_pinned').checked = Boolean(prompt?.is_pinned);
      el('editor-title').textContent = prompt?.title || '新規プロンプト';
      renderBundle();
    };

    const splitTags = (value) => Array.from(new Set(String(value || '').split(/[,\\n]/).map(s => s.trim()).filter(Boolean)));

    const bundleText = (prompt) => {
      const tags = splitTags(prompt.tags || '');
      return [
        `# ${prompt.title || '無題'}`,
        `カテゴリ: ${prompt.category || '未分類'}`,
        tags.length ? `タグ: ${tags.map(tag => `#${tag}`).join(' ')}` : 'タグ: なし',
        prompt.reference_url ? `参照: ${prompt.reference_url}` : '',
        prompt.notes ? `メモ: ${prompt.notes}` : '',
        '',
        '--- メイン ---',
        prompt.prompt_text || '',
        '',
        '--- ネガティブ ---',
        prompt.negative_prompt || '',
      ].filter(Boolean).join('\\n');
    };

    const api = async (path, body) => {
      const response = await fetch(path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      return await response.json();
    };

    const selected = () => state.prompts.find((item) => item.id === state.selectedId) || null;

    const renderMetrics = () => {
      const prompts = state.prompts;
      const tags = new Set(prompts.flatMap((item) => item.tags || []));
      el('metric-total').textContent = String(prompts.length);
      el('metric-pinned').textContent = String(prompts.filter((item) => item.is_pinned).length);
      el('metric-tags').textContent = String(tags.size);
      el('metric-updated').textContent = prompts[0]?.updated_at ? new Date(prompts[0].updated_at).toLocaleString('ja-JP') : '-';
      el('bundle-meta').textContent = `${splitTags(el('tags').value).length} タグ / ${el('prompt_text').value.length} 文字`;
    };

    const renderCategories = () => {
      const categories = ['すべて', ...Array.from(new Set(state.prompts.map((item) => item.category).filter(Boolean))).sort()];
      el('categories').innerHTML = categories.map((name) => `<button class="chip ${state.category === name ? 'active' : ''}" data-category="${name}">${name}</button>`).join('');
      el('categories').querySelectorAll('[data-category]').forEach((button) => {
        button.addEventListener('click', () => {
          state.category = button.dataset.category;
          render();
        });
      });
    };

    const filteredPrompts = () => {
      const q = state.search.trim().toLowerCase();
      return state.prompts.filter((item) => {
        const matchesFilter = state.filter === 'all' || (state.filter === 'pinned' && item.is_pinned);
        const matchesCategory = state.category === 'すべて' || item.category === state.category;
        const haystack = [item.title, item.category, item.prompt_text, item.negative_prompt, item.notes, ...(item.tags || [])].join(' ').toLowerCase();
        const matchesSearch = !q || haystack.includes(q);
        return matchesFilter && matchesCategory && matchesSearch;
      });
    };

    const renderList = () => {
      const list = filteredPrompts();
      el('list-meta').textContent = `${list.length} 件表示 / ${state.prompts.length} 件中`;
      el('list').innerHTML = list.map((item) => `
        <article class="card ${item.id === state.selectedId ? 'active' : ''}" data-id="${item.id}">
          <div class="card-top">
            <div>
              <p class="card-title">${item.title}</p>
              <div class="card-meta">${item.category} ・ ${new Date(item.updated_at).toLocaleDateString('ja-JP')}</div>
            </div>
            ${item.is_pinned ? '<span class="tag">固定</span>' : ''}
          </div>
          <p class="card-preview">${item.prompt_text}</p>
          <div class="tagrow">${(item.tags || []).slice(0, 4).map((tag) => `<span class="tag">#${tag}</span>`).join('')}</div>
        </article>
      `).join('');
      el('list').querySelectorAll('[data-id]').forEach((card) => {
        card.addEventListener('click', () => {
          state.selectedId = card.dataset.id;
          writeForm(selected() || state.prompts[0] || null);
          render();
        });
      });
      if (!list.length) {
        el('list').innerHTML = '<div class="empty">一致するプロンプトがありません。</div>';
      }
    };

    const renderBundle = () => {
      const prompt = readForm();
      el('bundle').textContent = bundleText(prompt);
      renderMetrics();
    };

    const render = () => {
      renderCategories();
      renderMetrics();
      renderList();
      const current = selected() || state.prompts[0] || null;
      if (current && !state.selectedId) {
        state.selectedId = current.id;
      }
      if (current) {
        writeForm(current);
      } else {
        writeForm(null);
      }
    };

    const load = async () => {
      el('status').textContent = '読み込み中...';
      const response = await fetch('/api/prompts');
      const data = await response.json();
      state.prompts = data.prompts || [];
      state.selectedId = state.prompts[0]?.id || null;
      render();
      el('status').textContent = `読み込みました: ${state.prompts.length} 件`;
    };

    const save = async () => {
      const payload = readForm();
      if (!payload.title || !payload.prompt_text) {
        el('status').textContent = 'タイトルと本文は必須です';
        return;
      }
      el('status').textContent = '保存中...';
      const data = await api('/api/prompts', { action: 'upsert', ...payload });
      state.prompts = data.prompts || state.prompts;
      state.selectedId = data.item?.id || payload.id || state.selectedId;
      render();
      el('status').textContent = '保存しました';
    };

    const del = async () => {
      const current = selected();
      if (!current) return;
      if (!confirm(`「${current.title}」を削除しますか？`)) return;
      el('status').textContent = '削除中...';
      const data = await api('/api/prompts', { action: 'delete', id: current.id });
      state.prompts = data.prompts || [];
      state.selectedId = state.prompts[0]?.id || null;
      render();
      el('status').textContent = '削除しました';
    };

    const duplicate = () => {
      const current = selected();
      if (!current) return;
      state.selectedId = null;
      writeForm({
        ...current,
        id: '',
        title: `${current.title} の複製`,
        is_pinned: false,
      });
      el('status').textContent = '複製を編集できます';
    };

    const copyMain = async () => {
      await navigator.clipboard.writeText(el('prompt_text').value.trim());
      el('status').textContent = '本文をコピーしました';
    };

    const copyBundle = async () => {
      await navigator.clipboard.writeText(bundleText(readForm()));
      el('status').textContent = 'まとめをコピーしました';
    };

    document.addEventListener('input', (event) => {
      const target = event.target;
      if (target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement) {
        if (ids.includes(target.id)) {
          renderBundle();
        }
        if (target.id === 'search') {
          state.search = target.value;
          renderList();
        }
      }
    });

    document.addEventListener('click', (event) => {
      const target = event.target;
      if (!(target instanceof HTMLElement)) return;
      if (target.dataset.filter) {
        state.filter = target.dataset.filter;
        document.querySelectorAll('[data-filter]').forEach((button) => button.classList.remove('active'));
        target.classList.add('active');
        renderList();
      }
    });

    el('save-btn').addEventListener('click', save);
    el('delete-btn').addEventListener('click', del);
    el('duplicate-btn').addEventListener('click', duplicate);
    el('copy-btn').addEventListener('click', copyMain);
    el('bundle-btn').addEventListener('click', copyBundle);
    el('new-btn').addEventListener('click', () => {
      state.selectedId = null;
      writeForm({ id: '', title: '', category: '未分類', tags: [], reference_url: '', prompt_text: '', negative_prompt: '', notes: '', is_pinned: false });
      el('status').textContent = '新規作成';
    });
    el('reload-btn').addEventListener('click', load);

    load();
  </script>
</body>
</html>"""


class PromptVaultHandler(BaseHTTPRequestHandler):
    server_version = "PromptVault/1.0"

    def _send(self, code: int, content_type: str, body: bytes) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._send(code, "application/json; charset=utf-8", body)

    def _read_json(self) -> dict[str, Any]:
        size = int(self.headers.get("Content-Length", "0"))
        if size <= 0:
            return {}
        raw = self.rfile.read(size).decode("utf-8")
        return json.loads(raw)

    def do_GET(self) -> None:
        if self.path == "/":
            self._send(HTTPStatus.OK, "text/html; charset=utf-8", render_html().encode("utf-8"))
            return
        if self.path == "/api/prompts":
            prompts = sorted_prompts(load_prompts())
            self._json(HTTPStatus.OK, {"prompts": prompts})
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_HEAD(self) -> None:
        if self.path == "/":
            body = render_html().encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            return
        if self.path == "/api/prompts":
            body = json.dumps({"prompts": sorted_prompts(load_prompts())}, ensure_ascii=False).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if self.path != "/api/prompts":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        payload = self._read_json()
        prompts = load_prompts()
        action = str(payload.get("action", "upsert"))

        if action == "delete":
            prompt_id = str(payload.get("id", ""))
            prompts = [prompt for prompt in prompts if prompt["id"] != prompt_id]
            save_prompts(prompts)
            self._json(HTTPStatus.OK, {"prompts": sorted_prompts(prompts)})
            return

        if action == "touch":
            prompt_id = str(payload.get("id", ""))
            updated: list[dict[str, Any]] = []
            for prompt in prompts:
                if prompt["id"] == prompt_id:
                    prompt = {**prompt, "last_used_at": utc_now(), "updated_at": utc_now()}
                updated.append(prompt)
            save_prompts(updated)
            self._json(HTTPStatus.OK, {"prompts": sorted_prompts(updated)})
            return

        prompt_id = str(payload.get("id", ""))
        existing = next((prompt for prompt in prompts if prompt["id"] == prompt_id), None)
        item = normalize_record(payload, existing)
        if existing:
            prompts = [item if prompt["id"] == prompt_id else prompt for prompt in prompts]
        else:
            prompts = [item, *prompts]
        save_prompts(prompts)
        self._json(HTTPStatus.OK, {"item": item, "prompts": sorted_prompts(prompts)})

    def log_message(self, format: str, *args: Any) -> None:
        return


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8787, type=int)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), PromptVaultHandler)
    print(f"Prompt Vault running on http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
