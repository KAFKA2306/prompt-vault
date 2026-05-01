const db = __DB_JSON__;
const blocks = Object.fromEntries(db.blocks.map((block) => [block.id, block]));
const templates = db.templates;
const fullCopySuffix = '\n\n---\n# 指示\n画像生成する';

const kindLabels = {
  stamp: 'スタンプ / 切り抜きしやすい完成形',
  comic: '漫画 / 物語を追いやすい完成形',
  reaction: '反応画像 / 一発で伝わる完成形',
  design_sheet: 'デザインシート / 設定資料',
  announcement: '告知 / SNSサムネイル',
};

const kindPalettes = {
  stamp: { accent: '15,118,110', accent2: '37,99,235' },
  comic: { accent: '99,102,241', accent2: '14,165,233' },
  reaction: { accent: '236,72,153', accent2: '249,115,22' },
  design_sheet: { accent: '59,130,246', accent2: '168,85,247' },
  announcement: { accent: '244,114,182', accent2: '249,115,22' },
  default: { accent: '15,118,110', accent2: '37,99,235' },
};

const state = {
  templates,
  selectedId: templates[0]?.id || null,
  search: '',
};

const el = (id) => document.getElementById(id);

const renderBlock = (block) => [
  `## ${block.title}`,
  `ID: ${block.id}`,
  `カテゴリ: ${block.category}`,
  block.tags?.length ? `タグ: ${block.tags.map((tag) => `#${tag}`).join(' ')}` : '',
  block.content,
].filter(Boolean).join('\n');

const renderTemplate = (template) => template.blocks.map((blockId) => renderBlock(blocks[blockId])).join('\n\n');

const renderFullCopyText = (template) => `${renderTemplate(template)}${fullCopySuffix}`;

const kindLabel = (template) => kindLabels[template.kind] || 'テンプレート';

const kindPalette = (template) => kindPalettes[template.kind] || kindPalettes.default;

const renderPreviewSteps = (template) => template.steps?.length
  ? template.steps.map((step, index) => `
      <div class="step-item">
        <span>${index + 1}</span>
        <p>${step}</p>
      </div>
    `).join('')
  : '<div class="empty">手順がありません。</div>';

const renderPreviewBlocks = (template) => template.blocks.map((blockId) => {
  const block = blocks[blockId];
  return `<div class="preview-chip">${block.title}</div>`;
}).join('');

const renderArtifacts = (template) => {
  const artifacts = template.artifacts || [];
  if (!artifacts.length) {
    return '<div class="empty">生成実例はありません。</div>';
  }

  const [primary, ...rest] = artifacts;
  return `
    <div class="artifact-showcase">
      <a class="artifact-hero" href="${primary.path}" target="_blank" rel="noreferrer">
        <div class="artifact-hero__media">
          <img src="${primary.path}" alt="${primary.title}" loading="lazy" />
        </div>
        <div class="artifact-hero__meta">
          <div class="artifact-hero__kicker">生成実例</div>
          <div class="artifact-hero__title">${primary.title}</div>
          <div class="artifact-hero__path">${primary.path}</div>
          <div class="artifact-hero__action">原寸で開く</div>
        </div>
      </a>
      ${rest.length ? `
        <div class="artifact-strip">
          ${rest.map((artifact) => `
            <a class="artifact-thumb" href="${artifact.path}" target="_blank" rel="noreferrer">
              <img src="${artifact.path}" alt="${artifact.title}" loading="lazy" />
              <span>${artifact.title}</span>
            </a>
          `).join('')}
        </div>
      ` : ''}
    </div>
  `;
};

const selected = () => state.templates.find((item) => item.id === state.selectedId) || null;

const filteredTemplates = () => {
  const query = state.search.trim().toLowerCase();
  return state.templates.filter((template) => {
    const haystack = [
      template.title,
      template.purpose,
      template.summary,
      template.notes,
      template.blocks.join(' '),
    ].join(' ').toLowerCase();
    return !query || haystack.includes(query);
  });
};

const renderList = () => {
  const list = filteredTemplates();
  el('list').innerHTML = list.map((template) => `
    <article class="panel card ${template.id === state.selectedId ? 'active' : ''}" data-id="${template.id}">
      <div class="card-badge">${kindLabel(template)}</div>
      <p class="title">${template.title}</p>
      <div class="meta">${template.purpose}</div>
      <p class="preview">${template.summary || template.notes || template.blocks.join(', ')}</p>
      <div class="card-foot">
        <span>${template.blocks.length} blocks</span>
        <span>${template.steps?.length || 0} steps</span>
      </div>
      <div class="buttons" style="margin-top: 10px;">
        <button class="button primary" data-copy-full="${template.id}">全文コピー</button>
      </div>
    </article>
  `).join('');

  el('list').querySelectorAll('[data-id]').forEach((card) =>
    card.addEventListener('click', () => {
      state.selectedId = card.dataset.id;
      renderDetail();
      renderList();
    })
  );

  el('list').querySelectorAll('[data-copy-full]').forEach((button) =>
    button.addEventListener('click', async (event) => {
      event.stopPropagation();
      const template = state.templates.find((item) => item.id === button.dataset.copyFull);
      if (!template) return;
      await navigator.clipboard.writeText(renderFullCopyText(template));
      el('status').textContent = `${template.title}の全文をコピーしました`;
    })
  );

  if (!list.length) {
    el('list').innerHTML = '<div class="empty">一致するテンプレートがありません。</div>';
  }
};

const renderDetail = () => {
  const template = selected();
  if (!template) {
    el('detail-title').textContent = 'テンプレートを選択';
    el('preview-kind').textContent = 'テンプレートを選択';
    el('preview-title').textContent = '上の一覧から1つ選ぶ';
    el('preview-purpose').textContent = 'ここに完成イメージの要点が出ます。';
    el('preview-block-count').textContent = '0';
    el('preview-summary').textContent = '一覧から選んでください。';
    el('preview-steps').innerHTML = '';
    el('preview-blocks').innerHTML = '';
    el('detail-summary').textContent = '一覧から選んでください。';
    el('detail-notes').textContent = '一覧から選んでください。';
    el('artifact-list').innerHTML = '';
    el('block-list').innerHTML = '';
    el('detail-full').textContent = '';
    el('preview-stage').style.removeProperty('--accent');
    el('preview-stage').style.removeProperty('--accent-2');
    return;
  }

  el('detail-title').textContent = template.title;
  el('preview-kind').textContent = kindLabel(template);
  el('preview-title').textContent = template.title;
  el('preview-purpose').textContent = template.purpose;
  el('preview-block-count').textContent = String(template.blocks.length);
  el('preview-summary').textContent = template.summary || template.purpose;
  el('preview-steps').innerHTML = renderPreviewSteps(template);
  el('preview-blocks').innerHTML = renderPreviewBlocks(template);
  el('detail-summary').textContent = template.summary || template.purpose;
  el('detail-notes').textContent = template.notes || 'メモなし';
  el('artifact-list').innerHTML = renderArtifacts(template);
  el('detail-full').textContent = renderTemplate(template);
  const palette = kindPalette(template);
  el('preview-stage').style.setProperty('--accent', palette.accent);
  el('preview-stage').style.setProperty('--accent-2', palette.accent2);
  el('block-list').innerHTML = template.blocks.map((blockId) => {
    const block = blocks[blockId];
    return `
      <div class="block">
        <div class="head" style="margin:0 0 6px 0;">
          <div>
            <div class="subtle">${block.category}</div>
            <h3 style="margin:4px 0 0;">${block.title}</h3>
          </div>
          <button class="button" data-copy="${block.id}">コピー</button>
        </div>
        <pre>${renderBlock(block)}</pre>
      </div>
    `;
  }).join('');

  el('block-list').querySelectorAll('[data-copy]').forEach((button) =>
    button.addEventListener('click', async () => {
      const block = blocks[button.dataset.copy];
      await navigator.clipboard.writeText(renderBlock(block));
      el('status').textContent = `${block.title}をコピーしました`;
    })
  );
};

const copyText = async (text, label) => {
  await navigator.clipboard.writeText(text);
  el('status').textContent = `${label}をコピーしました`;
};

const render = () => {
  renderList();
  renderDetail();
};

el('search').addEventListener('input', (event) => {
  state.search = event.target.value;
  renderList();
});

el('copy-full').addEventListener('click', () => {
  const template = selected();
  if (!template) return;
  copyText(renderFullCopyText(template), '全文');
});

el('copy-title').addEventListener('click', () => {
  const template = selected();
  if (!template) return;
  copyText(template.title, 'タイトル');
});

el('copy-purpose').addEventListener('click', () => {
  const template = selected();
  if (!template) return;
  copyText(template.purpose, '用途');
});

el('copy-blocks').addEventListener('click', () => {
  const template = selected();
  if (!template) return;
  copyText(template.blocks.join(', '), 'ブロックID');
});

render();
