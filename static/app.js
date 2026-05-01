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
  social: 'SNS / おはツイ',
  brand: 'ブランド / ロゴと記号',
  system: 'AI-Tuber / 基盤と運用',
};

const state = {
  templates,
  selectedId: null,
  search: '',
};

const el = (id) => document.getElementById(id);

const renderBlockContent = (block) => [
  `## ${block.title}`,
  `ID: ${block.id}`,
  `カテゴリ: ${block.category}`,
  block.tags?.length ? `タグ: ${block.tags.map((tag) => `#${tag}`).join(' ')}` : '',
  block.content,
].filter(Boolean).join('\n');

const renderTemplatePrompt = (template) => template.blocks.map((blockId) => renderBlockContent(blocks[blockId])).join('\n\n');

const renderFullCopyText = (template) => `${renderTemplatePrompt(template)}${fullCopySuffix}`;

const kindLabel = (template) => kindLabels[template.kind] || 'テンプレート';

const filteredTemplates = () => {
  const query = state.search.trim().toLowerCase();
  return state.templates.filter((template) => {
    const haystack = [
      template.title,
      template.purpose,
      template.summary,
      template.notes,
      template.blocks.join(' '),
      template.kind,
    ].join(' ').toLowerCase();
    return !query || haystack.includes(query);
  });
};

const openModal = (templateId) => {
  const template = state.templates.find((t) => t.id === templateId);
  if (!template) return;

  const artifact = template.artifacts?.[0];
  const imgView = document.querySelector('.modal-image-view');
  const imgEl = el('modal-img');

  if (artifact && artifact.path) {
    imgEl.style.display = 'block';
    imgEl.src = artifact.path;
    imgEl.alt = artifact.title;
    const noImage = imgView.querySelector('.no-image');
    if (noImage) noImage.remove();
  } else {
    imgEl.style.display = 'none';
    imgEl.src = '';
    let noImage = imgView.querySelector('.no-image');
    if (!noImage) {
      noImage = document.createElement('div');
      noImage.className = 'no-image subtle';
      noImage.textContent = '画像がありません';
      imgView.appendChild(noImage);
    }
  }
  
  el('modal-kind').textContent = kindLabel(template);
  el('modal-title').textContent = template.title;
  el('modal-purpose').textContent = template.purpose;
  el('modal-prompt').textContent = renderTemplatePrompt(template);
  
  el('modal').classList.add('active');
  state.selectedId = templateId;
};

const closeModal = () => {
  el('modal').classList.remove('active');
  state.selectedId = null;
};

const renderGallery = () => {
  const list = filteredTemplates().filter(t => t.artifacts && t.artifacts.length > 0);
  el('gallery-count').textContent = `${list.length} images`;
  
  el('gallery').innerHTML = list.map((template) => `
    <div class="gallery-item" data-open="${template.id}">
      <img src="${template.artifacts[0].path}" alt="${template.artifacts[0].title}" loading="lazy" />
      <div class="gallery-item__overlay">
        <p class="gallery-item__title">${template.title}</p>
        <p class="subtle" style="color: rgba(255,255,255,.8); font-size: 11px;">${template.purpose}</p>
      </div>
    </div>
  `).join('');

  el('gallery').querySelectorAll('[data-open]').forEach((item) => {
    item.addEventListener('click', () => openModal(item.dataset.open));
  });

  if (!list.length) {
    el('gallery').innerHTML = '<div class="empty">一致する実例がありません。</div>';
  }
};

const renderList = () => {
  const list = filteredTemplates();
  el('list').innerHTML = list.map((template) => `
    <article class="panel card" data-id="${template.id}">
      <div class="card-badge">${kindLabel(template)}</div>
      <p class="title">${template.title}</p>
      <div class="meta">${template.purpose}</div>
      <div class="card-foot">
        <span>${template.blocks.length} blocks</span>
      </div>
    </article>
  `).join('');

  el('list').querySelectorAll('[data-id]').forEach((card) =>
    card.addEventListener('click', () => {
      openModal(card.dataset.id);
    })
  );

  if (!list.length) {
    el('list').innerHTML = '<div class="empty">テンプレートなし</div>';
  }
};

const render = () => {
  renderList();
  renderGallery();
};

el('search').addEventListener('input', (event) => {
  state.search = event.target.value;
  render();
});

el('modal-close').addEventListener('click', closeModal);
el('modal').addEventListener('click', (e) => {
  if (e.target === el('modal')) closeModal();
});

el('modal-copy').addEventListener('click', async (e) => {
  const template = state.templates.find((t) => t.id === state.selectedId);
  if (!template) return;
  await navigator.clipboard.writeText(renderFullCopyText(template));
  
  const btn = e.target;
  const originalText = btn.textContent;
  btn.textContent = 'コピーしました！';
  btn.style.background = '#0f766e'; // accent color
  
  setTimeout(() => { 
    btn.textContent = originalText; 
    btn.style.background = '';
  }, 2000);
});

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && el('modal').classList.contains('active')) {
    closeModal();
  }
});

render();
