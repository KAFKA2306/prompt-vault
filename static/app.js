const db = __DB_JSON__;
const blocks = Object.fromEntries(db.blocks.map((block) => [block.id, block]));
const templates = db.templates;
const templateMap = Object.fromEntries(templates.map((template) => [template.id, template]));
const nodeUsageIndex = Object.fromEntries([...Object.keys(blocks)].map((id) => [id, []]));
const fullCopySuffix = '\n\n---\n# 指示\n画像生成する';

const kindLabels = {
  stamp: 'スタンプ・素材',
  comic: '漫画・ストーリー',
  reaction: '反応画像・リアクション',
  design_sheet: 'デザインシート・設計資料',
  announcement: '告知・宣伝用バナー',
  social: 'SNS投稿用レイアウト',
  brand: 'ブランドロゴ・意匠',
  system: '自律運用・基盤',
};

const escapeHTML = (value) => value
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')
  .replaceAll("'", '&#39;');

const state = {
  templates,
  selectedNode: null,
  search: '',
};

const el = (id) => document.getElementById(id);

const getNodeType = (id) => {
  if (templateMap[id]) return 'template';
  if (blocks[id]) return 'block';
  return null;
};

const getNode = (id) => templateMap[id] || blocks[id] || null;

const registerUsage = (templateId, ids) => {
  ids.forEach((id) => {
    if (nodeUsageIndex[id]) nodeUsageIndex[id].push(templateId);
  });
};

templates.forEach((template) => registerUsage(template.id, [...template.blocks, ...(template.uses || [])]));

const renderBlockContent = (block) => [
  `## ${block.title}`,
  `ID: ${block.id}`,
  `カテゴリ: ${block.category}`,
  block.tags?.length ? `タグ: ${block.tags.map((tag) => `#${tag}`).join(' ')}` : '',
  block.aliases?.length ? `別名: ${block.aliases.join(', ')}` : '',
  block.related?.length ? `関連: ${block.related.join(', ')}` : '',
  block.variant_of ? `派生元: ${block.variant_of}` : '',
  block.content,
].filter(Boolean).join('\n');

const renderTemplatePrompt = (template) => template.blocks.map((blockId) => renderBlockContent(blocks[blockId])).join('\n\n');

const kindLabel = (template) => kindLabels[template.kind] || template.kind || 'テンプレート';

const nodeLabel = (node, type) => {
  if (type === 'template') return kindLabel(node);
  return node.category || 'ブロック';
};

const renderStepItems = (steps) => steps.map((step, index) => `
  <div class="step-item">
    <span>${index + 1}</span>
    <p>${escapeHTML(step)}</p>
  </div>
`).join('');

const renderNodeChips = (ids) => ids
  .filter((id, index, list) => id && list.indexOf(id) === index)
  .map((id) => {
    const node = getNode(id);
    const type = getNodeType(id);
    const label = node ? node.title : id;
    return `
      <button
        type="button"
        class="tag tag-button"
        data-node-id="${escapeHTML(id)}"
        data-node-type="${escapeHTML(type || '')}"
      >${escapeHTML(label)}</button>
    `;
  }).join('');

const renderTextChips = (items) => items.map((item) => `<span class="tag">${escapeHTML(item)}</span>`).join('');

const renderRecommendItems = (ids) => ids
  .filter((id, index, list) => id && list.indexOf(id) === index)
  .map((id) => {
    const node = getNode(id);
    const type = getNodeType(id);
    if (!node) return '';

    const artifact = findNodeArtifact(node, type, id);
    const title = escapeHTML(node.title);
    const kind = escapeHTML(nodeLabel(node, type));
    const nodeId = escapeHTML(id);
    const nodeType = escapeHTML(type || '');

    if (artifact?.path) {
      const imgAlt = escapeHTML(artifact.title || node.title);
      return `
        <button
          type="button"
          class="recommend-card recommend-card--image"
          data-node-id="${nodeId}"
          data-node-type="${nodeType}"
        >
          <img src="${escapeHTML(artifact.path)}" alt="${imgAlt}" loading="lazy" />
          <div class="recommend-card__body">
            <span class="recommend-card__title">${title}</span>
            <span class="recommend-card__meta">${kind}</span>
          </div>
        </button>
      `;
    }

    return `
      <button
        type="button"
        class="recommend-card recommend-card--text"
        data-node-id="${nodeId}"
        data-node-type="${nodeType}"
      >
        <div class="recommend-card__body">
          <span class="recommend-card__title">${title}</span>
          <span class="recommend-card__meta">${kind}</span>
        </div>
      </button>
    `;
  }).join('');

const nodeSearchText = (ids) => ids.flatMap((id) => {
  const node = getNode(id);
  if (!node) return [id];
  return [
    node.id,
    node.title,
    node.category,
    ...(node.aliases || []),
    ...(node.tags || []),
    ...(node.related || []),
    node.variant_of || '',
  ];
}).join(' ');

const uniqueIds = (ids) => [...new Set(ids.filter(Boolean))];

const relatedTemplatesFor = (blockId) => nodeUsageIndex[blockId] || [];

const nodeScore = (id) => {
  const node = getNode(id);
  if (!node) return 0;
  if (templateMap[id]) {
    return (node.blocks?.length || 0) + (node.uses?.length || 0) + ((node.artifacts?.length || 0) * 2);
  }
  return (nodeUsageIndex[id]?.length || 0) + (node.related?.length || 0) + (node.variant_of ? 1 : 0) + ((node.artifacts?.length || 0) * 2);
};

const recommendNodeIds = (node, type) => {
  if (type === 'template') {
    const ids = node.blocks.flatMap((blockId) => {
      const block = blocks[blockId];
      if (!block) return [];
      return [
        ...(block.related || []),
        block.variant_of,
      ];
    });
    return uniqueIds(ids)
      .filter((id) => id !== node.id && !node.blocks.includes(id))
      .sort((a, b) => nodeScore(b) - nodeScore(a) || getNode(a).title.localeCompare(getNode(b).title, 'ja'));
  }

  const ids = [
    ...(node.related || []),
    node.variant_of,
    ...uniqueIds((node.related || []).flatMap((relatedId) => relatedTemplatesFor(relatedId))),
    ...relatedTemplatesFor(node.id),
  ];
  return uniqueIds(ids)
    .filter((id) => id !== node.id)
    .sort((a, b) => nodeScore(b) - nodeScore(a) || getNode(a).title.localeCompare(getNode(b).title, 'ja'));
};

const findNodeArtifact = (node, type, nodeId) => {
  if (node.artifacts?.length) return node.artifacts[0];

  const candidates = type === 'template'
    ? uniqueIds(node.blocks.flatMap((blockId) => relatedTemplatesFor(blockId)))
    : uniqueIds([
        ...(node.related || []),
        ...(node.variant_of ? [node.variant_of] : []),
        ...relatedTemplatesFor(nodeId),
      ]);

  for (const candidateId of candidates.sort((a, b) => nodeScore(b) - nodeScore(a))) {
    const candidate = getNode(candidateId);
    if (candidate?.artifacts?.length) {
      return candidate.artifacts[0];
    }
  }

  if (type === 'template') {
    for (const blockId of node.blocks) {
      const block = blocks[blockId];
      if (block?.artifacts?.length) return block.artifacts[0];
    }
  }

  return null;
};

const openNode = (nodeId, preferredType = null) => {
  const type = preferredType || getNodeType(nodeId);
  const node = type === 'template' ? templateMap[nodeId] : blocks[nodeId];
  if (!node) return;

  state.selectedNode = { id: nodeId, type };

  const imgView = document.querySelector('.modal-image-view');
  const imgEl = el('modal-img');
  const artifact = findNodeArtifact(node, type, nodeId);

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

  const isTemplate = type === 'template';
  const primaryIds = isTemplate ? node.blocks : [
    ...(node.related || []),
    ...(node.variant_of ? [node.variant_of] : []),
  ];
  const secondaryIds = isTemplate ? (node.uses || []) : (nodeUsageIndex[nodeId] || []);
  const recommendIds = recommendNodeIds(node, type);

  el('modal-kind').textContent = nodeLabel(node, type);
  el('modal-title').textContent = node.title;
  el('modal-purpose').textContent = isTemplate ? node.purpose : `カテゴリ: ${node.category}`;
  el('modal-copy').textContent = isTemplate ? 'プロンプトをコピー' : 'ブロック本文をコピー';
  el('modal-prompt-title').textContent = isTemplate ? '全文プロンプト' : 'ブロック本文';

  el('modal-primary-title').textContent = isTemplate ? '構成ノード' : '関連ノード';
  el('modal-primary').innerHTML = primaryIds.length ? renderNodeChips(primaryIds) : '';
  el('modal-primary-block').hidden = !primaryIds.length;

  el('modal-secondary-title').textContent = isTemplate ? '再利用ノード' : '使用テンプレート';
  el('modal-secondary').innerHTML = secondaryIds.length ? renderNodeChips(secondaryIds) : '';
  el('modal-secondary-block').hidden = !secondaryIds.length;

  const recommendEl = el('modal-recommend');
  recommendEl.className = 'recommend-grid';
  recommendEl.innerHTML = recommendIds.length ? renderRecommendItems(recommendIds) : '';
  el('modal-recommend-block').hidden = !recommendIds.length;

  el('modal-aliases').innerHTML = node.aliases?.length ? renderTextChips(node.aliases) : '';
  el('modal-aliases-block').hidden = !(node.aliases?.length);

  el('modal-summary').textContent = isTemplate ? (node.summary || '') : '';
  el('modal-summary-block').hidden = !isTemplate || !node.summary;
  el('modal-steps').innerHTML = isTemplate && node.steps?.length ? renderStepItems(node.steps) : '';
  el('modal-steps-block').hidden = !isTemplate || !(node.steps?.length);
  el('modal-notes').textContent = isTemplate ? (node.notes || '') : '';
  el('modal-notes-block').hidden = !isTemplate || !node.notes;
  el('modal-prompt').textContent = isTemplate ? renderTemplatePrompt(node) : renderBlockContent(node);

  el('modal').classList.add('active');
};

const openTemplate = (templateId) => openNode(templateId, 'template');

const filteredTemplates = () => {
  const query = state.search.trim().toLowerCase();
  return state.templates.filter((template) => {
    const haystack = [
      template.id,
      template.title,
      template.purpose,
      template.summary,
      template.notes,
      nodeSearchText(template.blocks || []),
      nodeSearchText(template.uses || []),
      template.aliases?.join(' '),
      template.labels?.join(' '),
      template.kind,
    ].join(' ').toLowerCase();
    return !query || haystack.includes(query);
  });
};

const closeModal = () => {
  el('modal').classList.remove('active');
  state.selectedNode = null;
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
    item.addEventListener('click', () => openTemplate(item.dataset.open));
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
      openTemplate(card.dataset.id);
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
  const nodeButton = e.target.closest?.('[data-node-id]');
  if (nodeButton) {
    openNode(nodeButton.dataset.nodeId, nodeButton.dataset.nodeType || null);
    return;
  }
  if (e.target === el('modal')) closeModal();
});

el('modal-copy').addEventListener('click', async (e) => {
  const selected = state.selectedNode;
  if (!selected) return;
  const node = getNode(selected.id);
  if (!node) return;
  const copyText = selected.type === 'template' ? `${renderTemplatePrompt(node)}${fullCopySuffix}` : renderBlockContent(node);
  await navigator.clipboard.writeText(copyText);
  
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
