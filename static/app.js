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
  <div class="recipe-item">
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

    const { artifact, source } = findNodeDisplayArtifact(node, type, id);
    const title = escapeHTML(node.title);
    const kind = escapeHTML(nodeLabel(node, type));
    const nodeId = escapeHTML(id);
    const nodeType = escapeHTML(type || '');

    if (artifact?.path) {
      const imgAlt = escapeHTML(artifact.title || node.title);
      return `
        <button
          type="button"
          class="recommend-card recommend-card--image${source === 'fallback' ? ' is-fallback' : ''}"
          data-node-id="${nodeId}"
          data-node-type="${nodeType}"
          data-fallback="${source === 'fallback' ? 'true' : 'false'}"
        >
          ${source === 'fallback' ? '<span class="recommend-card__badge">関連画像</span>' : ''}
          <img src="${escapeHTML(artifact.path)}" alt="${imgAlt}" loading="lazy" />
          <div class="recommend-card__body">
            <span class="recommend-card__title">${title}</span>
            <span class="recommend-card__meta">${kind}</span>
            ${source === 'fallback' ? '<span class="recommend-card__note">このノードの画像は未登録です</span>' : ''}
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
        data-fallback="false"
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

const findNodeDisplayArtifact = (node, type, nodeId) => {
  if (node.artifacts?.length) {
    return { artifact: node.artifacts[0], source: 'direct' };
  }

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
      return { artifact: candidate.artifacts[0], source: 'fallback', sourceNodeId: candidateId };
    }
  }

  if (type === 'template') {
    for (const blockId of node.blocks) {
      const block = blocks[blockId];
      if (block?.artifacts?.length) {
        return { artifact: block.artifacts[0], source: 'fallback', sourceNodeId: blockId };
      }
    }
  }

  return { artifact: null, source: 'none' };
};

const openNode = (nodeId, preferredType = null) => {
  const type = preferredType || getNodeType(nodeId);
  const node = type === 'template' ? templateMap[nodeId] : blocks[nodeId];
  if (!node) return;

  state.selectedNode = { id: nodeId, type };

  const imgView = document.querySelector('.modal-image-view');
  const imgEl = el('modal-img');
  const displayArtifact = findNodeDisplayArtifact(node, type, nodeId);
  const artifact = displayArtifact.artifact;

  if (artifact && artifact.path) {
    imgEl.style.display = 'block';
    imgEl.src = artifact.path;
    imgEl.alt = artifact.title;
    const noImage = imgView.querySelector('.no-image');
    if (noImage) noImage.remove();
    let imageNote = imgView.querySelector('.image-note');
    if (displayArtifact.source === 'fallback') {
      if (!imageNote) {
        imageNote = document.createElement('div');
        imageNote.className = 'image-note';
        imgView.appendChild(imageNote);
      }
      imageNote.innerHTML = '<span class="image-note__badge">関連画像</span><span class="image-note__text">このノードの画像は未登録です。近い実例を表示しています。</span>';
      imgView.classList.add('is-fallback');
    } else {
      if (imageNote) imageNote.remove();
      imgView.classList.remove('is-fallback');
    }
  } else {
    imgEl.style.display = 'none';
    imgEl.src = '';
    imgView.classList.remove('is-fallback');
    const imageNote = imgView.querySelector('.image-note');
    if (imageNote) imageNote.remove();
    let noImage = imgView.querySelector('.no-image');
    if (!noImage) {
      noImage = document.createElement('div');
      noImage.className = 'no-image subtle';
      noImage.textContent = '画像が未登録です';
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

const renderTemplateRail = () => {
  const list = filteredTemplates();
  el('template-count').textContent = `${list.length} templates`;

  el('template-rail').innerHTML = list.map((template) => `
    <button type="button" class="template-card ${template.artifacts?.length ? 'template-card--image' : 'template-card--empty'}" data-template-id="${template.id}">
      ${template.artifacts?.length ? `
        <div class="template-card__thumb">
          <img src="${escapeHTML(template.artifacts[0].path)}" alt="${escapeHTML(template.artifacts[0].title)}" loading="lazy" />
        </div>
      ` : `
        <div class="template-card__placeholder">
          <span class="template-card__placeholder-label">画像なし</span>
          <span class="template-card__placeholder-meta">ブロックと全文から使います</span>
        </div>
      `}
      <div class="template-card__body">
        <div class="template-card__top">
          <span class="template-card__kind">${escapeHTML(kindLabel(template))}</span>
          <span class="template-card__flag">${template.artifacts?.length ? '画像あり' : '画像なし'}</span>
        </div>
        <div class="template-card__title">${escapeHTML(template.title)}</div>
        <div class="template-card__meta">${escapeHTML(template.purpose || template.summary || '')}</div>
      </div>
    </button>
  `).join('');

  el('template-rail').querySelectorAll('[data-template-id]').forEach((item) => {
    item.addEventListener('click', () => openTemplate(item.dataset.templateId));
  });

  if (!list.length) {
    el('template-rail').innerHTML = '<div class="empty">テンプレートが見つかりません。</div>';
  }
};



const render = () => {
  renderGallery();
  renderTemplateRail();
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
