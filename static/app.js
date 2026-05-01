const db = __DB_JSON__;
const blocks = Object.fromEntries(db.blocks.map((block) => [block.id, block]));
const templates = db.templates;

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
      <div class="card-top">
        <div>
          <p class="title">${template.title}</p>
          <div class="meta">${template.purpose}</div>
        </div>
      </div>
      <p class="preview">${template.summary || template.notes || template.blocks.join(', ')}</p>
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
      await navigator.clipboard.writeText(renderTemplate(template));
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
    el('detail-summary').textContent = '一覧から選んでください。';
    el('detail-notes').textContent = '一覧から選んでください。';
    el('block-list').innerHTML = '';
    el('detail-full').textContent = '';
    return;
  }

  el('detail-title').textContent = template.title;
  el('detail-summary').textContent = template.summary || template.purpose;
  el('detail-notes').textContent = template.notes || 'メモなし';
  el('detail-full').textContent = renderTemplate(template);
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
  copyText(renderTemplate(template), '全文');
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
