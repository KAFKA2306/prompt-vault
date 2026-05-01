const db = __DB_JSON__;
const blocks = Object.fromEntries(db.blocks
  .filter((block) => block.visibility !== 'internal')
  .map((block) => [block.id, block]));
const templates = db.templates.filter((template) => template.visibility !== 'internal');
const templateMap = Object.fromEntries(templates.map((template) => [template.id, template]));
const generatorBlockNodes = Object.values(blocks).sort((a, b) => (
  a.category.localeCompare(b.category, 'ja') || a.title.localeCompare(b.title, 'ja')
));
const nodeUsageIndex = Object.fromEntries([...Object.keys(blocks)].map((id) => [id, []]));
const fullCopySuffix = '\n\n---\n# 指示\n画像生成する';
const generatorEmptyText = 'まだ生成されていません。';
const generatorDisabledText = '生成機能は未設定です。';

const kindLabels = {
  stamp: 'スタンプ・素材',
  comic: '漫画・ストーリー',
  reaction: '反応画像・リアクション',
  design_sheet: 'デザインシート・設計資料',
  announcement: '告知・宣伝用バナー',
  social: 'SNS投稿用レイアウト',
  brand: 'ブランドロゴ・意匠',
  system: '自律運用・基盤',
  generated: '生成済み',
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
  search: new URLSearchParams(window.location.search).get('q') || '',
  generatorTemplateId: templates[0]?.id || '',
  generatorBlockIds: [...(templates[0]?.blocks || [])],
  generatorOutput: generatorEmptyText,
  generatorBusy: false,
  generatorEnabled: true,
};

const el = (id) => document.getElementById(id);

const meta = (selector) => document.head.querySelector(selector);

const setMetaContent = (selector, value) => {
  const node = meta(selector);
  if (node) node.setAttribute('content', value);
};

const setSeoCopy = () => {
  const title = 'Prompt Vault | テンプレート一覧から探して全文コピー';
  const description = 'Prompt Vault は、テンプレート一覧から探して詳細表示で全文をコピーできる保管庫です。必要なら指示を足して生成もできます。';

  document.title = title;
  setMetaContent('meta[name="description"]', description);
  setMetaContent('meta[property="og:title"]', title);
  setMetaContent('meta[property="og:description"]', description);
  setMetaContent('meta[name="twitter:title"]', title);
  setMetaContent('meta[name="twitter:description"]', description);
};

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

setSeoCopy();

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

const renderTemplatePrompt = (template) => {
  if (template.generated_prompt) return template.generated_prompt;
  return template.blocks.map((blockId) => renderBlockContent(blocks[blockId])).join('\n\n');
};

const splitBlockIds = (value) => uniqueIds(
  value
    .split(/[\s,]+/)
    .map((item) => item.trim())
    .filter(Boolean),
);

const renderGeneratorTemplateOptions = () => {
  const select = el('generator-template');
  if (!select) return;
  select.innerHTML = templates.map((template) => `
    <option value="${escapeHTML(template.id)}">${escapeHTML(template.title)}</option>
  `).join('');
  select.value = state.generatorTemplateId;
};

const setGeneratorBlockIds = (ids) => {
  state.generatorBlockIds = uniqueIds(ids.filter((id) => blocks[id]));
  renderGeneratorSelectedNodes();
  renderGeneratorNodePicker();
};

const getGeneratorBaseBlockIds = () => templateMap[state.generatorTemplateId]?.blocks || [];

const registerGeneratedTemplate = (template) => {
  if (!template || templateMap[template.id]) return;
  templates.push(template);
  templateMap[template.id] = template;
  registerUsage(template.id, template.blocks || []);
};

const toggleGeneratorBlock = (blockId) => {
  if (!blocks[blockId]) return;
  const current = new Set(state.generatorBlockIds);
  const next = state.generatorBlockIds.filter((id) => id !== blockId);
  if (!current.has(blockId)) next.push(blockId);
  setGeneratorBlockIds(next);
};

const renderGeneratorSelectedNodes = () => {
  const target = el('generator-selected-nodes');
  if (!target) return;
  const ids = state.generatorBlockIds.length
    ? state.generatorBlockIds
    : getGeneratorBaseBlockIds();
  target.innerHTML = ids.length
    ? ids.map((id) => `
      <button
        type="button"
        class="tag tag-button tag-button--remove"
        data-generator-remove-id="${escapeHTML(id)}"
      >
        ${escapeHTML(getNode(id)?.title || id)}
        <span aria-hidden="true">×</span>
      </button>
    `).join('')
    : '<span class="subtle">まだ選ばれていません。</span>';

  target.querySelectorAll('[data-generator-remove-id]').forEach((button) => {
    button.addEventListener('click', () => {
      toggleGeneratorBlock(button.dataset.generatorRemoveId);
    });
  });
};

const renderGeneratorNodePicker = () => {
  const picker = el('generator-node-picker');
  const count = el('generator-node-count');
  if (!picker) return;
  const selected = new Set(state.generatorBlockIds.length
    ? state.generatorBlockIds
    : getGeneratorBaseBlockIds());
  if (count) count.textContent = `${selected.size} selected`;

  picker.innerHTML = generatorBlockNodes.map((node) => {
    const { artifact, source } = findNodeDisplayArtifact(node, 'block', node.id);
    const selectedClass = selected.has(node.id) ? ' is-selected' : '';
    const kind = escapeHTML(node.category || 'ブロック');
    const title = escapeHTML(node.title);
    const nodeId = escapeHTML(node.id);
    const badge = source === 'fallback' ? '<span class="recommend-card__badge">関連画像</span>' : '';

    if (artifact?.path) {
      return `
        <button
          type="button"
          class="recommend-card recommend-card--image generator-node-card${selectedClass}"
          data-node-id="${nodeId}"
          aria-pressed="${selected.has(node.id) ? 'true' : 'false'}"
        >
          ${badge}
          <img src="${escapeHTML(artifact.path)}" alt="${escapeHTML(artifact.title || `${node.title} の関連画像`)}" loading="lazy" />
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
        class="recommend-card recommend-card--text generator-node-card${selectedClass}"
        data-node-id="${nodeId}"
        aria-pressed="${selected.has(node.id) ? 'true' : 'false'}"
      >
        <div class="recommend-card__body">
          <span class="recommend-card__title">${title}</span>
          <span class="recommend-card__meta">${kind}</span>
        </div>
      </button>
    `;
  }).join('');

  picker.querySelectorAll('[data-node-id]').forEach((button) => {
    button.addEventListener('click', () => toggleGeneratorBlock(button.dataset.nodeId));
  });
};

const setGeneratorOutput = (value) => {
  state.generatorOutput = value;
  const output = el('generator-output');
  const copyButton = el('generator-copy');
  if (output) output.textContent = value;
  if (copyButton) copyButton.disabled = !value || value === generatorEmptyText;
};

const setGeneratorStatus = (value) => {
  const status = el('generator-status');
  if (status) status.textContent = value;
};

const setGeneratorEnabled = (enabled) => {
  state.generatorEnabled = enabled;
  const submitButton = el('generator-submit');
  const copyButton = el('generator-copy');
  const select = el('generator-template');
  const instructionField = el('generator-instruction');
  const resetButton = el('generator-reset-template');
  const clearButton = el('generator-clear-nodes');
  const pickerButtons = el('generator-node-picker')?.querySelectorAll('button') || [];

  if (submitButton) submitButton.disabled = !enabled;
  if (copyButton) copyButton.disabled = !enabled || !state.generatorOutput || state.generatorOutput === generatorEmptyText;
  if (select) select.disabled = !enabled;
  if (instructionField) instructionField.disabled = !enabled;
  if (resetButton) resetButton.disabled = !enabled;
  if (clearButton) clearButton.disabled = !enabled;
  pickerButtons.forEach((button) => { button.disabled = !enabled; });

  if (!enabled) {
    setGeneratorOutput(generatorDisabledText);
    setGeneratorStatus('生成バックエンドが未設定です。');
  }
};

renderGeneratorTemplateOptions();
setGeneratorOutput(generatorEmptyText);

fetch('/api/config')
  .then((response) => response.json())
  .then((config) => {
    setGeneratorEnabled(Boolean(config.generation_backend));
  })
  .catch(() => {
    setGeneratorEnabled(false);
  });

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
      const imgAlt = escapeHTML(artifact.title || `${node.title} の関連画像`);
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
    node.generated_prompt || '',
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
    imgEl.hidden = false;
    imgEl.src = artifact.path;
    imgEl.alt = artifact.title || `${node.title} の画像`;
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
    imgEl.hidden = true;
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
      template.generated_prompt,
      template.generated_addition,
      template.generated_instruction,
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

const renderTemplateRail = () => {
  const list = filteredTemplates();
  el('template-count').textContent = `${list.length} templates`;

  el('template-rail').innerHTML = list.map((template) => `
    <button type="button" class="template-card ${template.artifacts?.length ? 'template-card--image' : 'template-card--empty'}" data-template-id="${template.id}">
      ${template.artifacts?.length ? `
        <div class="template-card__thumb">
          <img src="${escapeHTML(template.artifacts[0].path)}" alt="${escapeHTML(template.artifacts[0].title || `${template.title} のサムネイル`)}" loading="lazy" />
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
  renderTemplateRail();
};

const generatePrompt = async () => {
  if (state.generatorBusy) return;

  const templateId = el('generator-template')?.value || state.generatorTemplateId;
  const template = templateMap[templateId];
  const instruction = el('generator-instruction')?.value.trim() || '';
  const blockIds = uniqueIds(state.generatorBlockIds.length ? state.generatorBlockIds : (template?.blocks || []));

  if (!template) {
    setGeneratorStatus('テンプレートを選んでください。');
    return;
  }

  if (!instruction) {
    setGeneratorStatus('指示を入れてください。');
    return;
  }

  state.generatorBusy = true;
  setGeneratorStatus('生成中...');

  const submitButton = el('generator-submit');
  if (submitButton) submitButton.disabled = true;

  try {
    const response = await fetch('/api/prompt-generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        template_id: templateId,
        block_ids: blockIds,
        instruction,
      }),
    });

    const payload = await response.json().catch(() => null);
    if (!response.ok) {
      throw new Error(payload?.message || '生成に失敗しました。');
    }

    if (payload.generated_template) {
      registerGeneratedTemplate(payload.generated_template);
      render();
      el('generator-template').value = payload.generated_template.id;
      state.generatorTemplateId = payload.generated_template.id;
      setGeneratorBlockIds(payload.generated_template.blocks || []);
    }
    setGeneratorOutput(payload.generated_prompt || generatorEmptyText);
    setGeneratorStatus(`生成しました。${payload.request_id}`);
  } catch (error) {
    setGeneratorStatus(error.message || '生成に失敗しました。');
  } finally {
    state.generatorBusy = false;
    if (submitButton) submitButton.disabled = false;
  }
};

el('search').addEventListener('input', (event) => {
  state.search = event.target.value;
  render();
});

el('search').value = state.search;
el('generator-template').addEventListener('change', (event) => {
  state.generatorTemplateId = event.target.value;
  setGeneratorBlockIds(getGeneratorBaseBlockIds());
});

el('generator-reset-template').addEventListener('click', () => {
  setGeneratorBlockIds(getGeneratorBaseBlockIds());
});

el('generator-clear-nodes').addEventListener('click', () => {
  setGeneratorBlockIds([]);
});

el('generator-submit').addEventListener('click', generatePrompt);
el('generator-copy').addEventListener('click', async () => {
  if (!state.generatorOutput || state.generatorOutput === generatorEmptyText) return;
  await navigator.clipboard.writeText(state.generatorOutput);
  setGeneratorStatus('生成結果をコピーしました。');
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
  btn.classList.add('is-copied');
  
  setTimeout(() => { 
    btn.textContent = originalText; 
    btn.classList.remove('is-copied');
  }, 2000);
});

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && el('modal').classList.contains('active')) {
    closeModal();
  }
});

render();
renderGeneratorNodePicker();
renderGeneratorSelectedNodes();
