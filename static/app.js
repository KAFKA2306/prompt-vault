const db = __DB_JSON__;
const skillsIndex = __SKILLS_JSON__;
const blocks = Object.fromEntries(db.blocks.map(b => [b.id, b]));
const templates = db.templates;
const templateMap = Object.fromEntries(templates.map(t => [t.id, t]));

const el = (id) => document.getElementById(id);
const esc = (v) => v ? v.toString().replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m])) : '';
const artifactType = (path = '') => {
  const ext = path.toString().toLowerCase().split('.').pop();
  if (ext === 'wav') return 'audio';
  if (['png', 'webp', 'jpg', 'jpeg'].includes(ext)) return 'image';
  return 'other';
};

const renderArtifactThumb = (artifact) => {
  if (!artifact) {
    return '<div class="placeholder-box">No Image</div>';
  }
  if (artifactType(artifact.path) === 'audio') {
    return `
      <div class="template-card__thumb template-card__thumb--audio">
        <div class="template-card__thumb-label">AUDIO</div>
        <div class="template-card__thumb-wave" aria-hidden="true"></div>
      </div>
    `;
  }
  return `<img src="${artifact.path}" loading="lazy" alt="${esc(artifact.title)}">`;
};

const renderArtifactThumbRow = (artifact, index) => {
  if (artifactType(artifact.path) === 'audio') {
    return `
      <button type="button" class="modal-artifact-thumb modal-artifact-thumb--audio ${index === 0 ? 'is-active' : ''}" onclick="switchModalArtifact(this, '${artifact.path}')">
        WAV
      </button>
    `;
  }
  return `
    <img src="${artifact.path}" class="modal-artifact-thumb ${index === 0 ? 'is-active' : ''}" onclick="switchModalArtifact(this, '${artifact.path}')" alt="${esc(artifact.title)}">
  `;
};

const state = {
  search: '',
  genTpl: templates[0]?.id || '',
  genBids: [...(templates[0]?.blocks || [])],
  localGenerated: JSON.parse(localStorage.getItem('prompt-vault-gen') || '[]'),
  modalHistory: [],
  currentModalId: null
};

const saveLocal = (item) => {
  state.localGenerated = [item, ...state.localGenerated].slice(0, 50);
  localStorage.setItem('prompt-vault-gen', JSON.stringify(state.localGenerated));
  renderRail();
};

const renderRail = () => {
  const q = state.search.toLowerCase();
  const serverIds = new Set(templates.map(t => t.id));
  const localItems = state.localGenerated
    .filter(g => !serverIds.has(g.id))
    .map(g => ({ ...g, kind: 'generated', purpose: g.purpose || 'LocalStorage' }));
  
  const all = [...templates, ...localItems];
  const list = all.filter(t => !q || JSON.stringify(t).toLowerCase().includes(q));
  
  el('template-rail').innerHTML = list.map(t => {
    const isExample = t.blocks && t.blocks.length === 0;
    return `
      <div class="card template-card ${isExample ? 'is-example' : ''}" onclick="openModal('${t.id}')">
        <div class="template-card__thumb">
          ${renderArtifactThumb(t.artifacts?.[0])}
          ${isExample ? '<div class="example-badge">Example Only</div>' : ''}
        </div>
        <div class="template-card__body">
          <span class="template-card__kind">${esc(t.kind)}</span>
          <div class="template-card__title">${esc(t.title)}</div>
          <div class="template-card__summary">${esc(t.summary || t.purpose || '')}</div>
        </div>
      </div>
    `;
  }).join('');
  
  if (el('template-count')) {
    el('template-count').textContent = `${list.length} items`;
  }
};

const renderSkills = () => {
  const sections = Array.isArray(skillsIndex) ? skillsIndex : [];
  const items = sections.flatMap(section => (section.items || []).map(item => ({ ...item, section: section.title })));
  const rail = el('skills-rail');
  const section = el('skills-section');
  if (!rail || !section) return;

  if (!items.length) {
    section.hidden = true;
    return;
  }

  section.hidden = false;
  rail.innerHTML = items.map(item => `
    <div class="card skill-card">
      <span class="template-card__kind">${esc(item.section || 'skill')}</span>
      <div class="template-card__title">${esc(item.id)}</div>
      <div class="template-card__summary">${esc(item.purpose || '')}</div>
      <div class="skill-card__path">${esc(item.path || '')}</div>
    </div>
  `).join('');
};

window.openModal = (id, saveToHistory = true) => {
  const all = [...templates, ...state.localGenerated];
  let t = all.find(x => x.id === id);
  if (!t && blocks[id]) {
    const usingTpls = templates.filter(x => (x.blocks || []).includes(id));
    t = { 
      id, 
      title: blocks[id].title, 
      kind: blocks[id].category || 'block', 
      purpose: 'このノードを使用しているテンプレート', 
      generated_prompt: blocks[id].content, 
      blocks: [id],
      artifacts: usingTpls[0]?.artifacts || []
    };
  }
  if (!t) return;

  const isExample = t.blocks && t.blocks.length === 0;

  if (saveToHistory && state.currentModalId && state.currentModalId !== id) {
    state.modalHistory.push(state.currentModalId);
  }
  state.currentModalId = id;
  el('modal-back').style.display = state.modalHistory.length > 0 ? 'flex' : 'none';

  el('modal-title').textContent = t.title + (isExample ? ' (Example Only)' : '');
  el('modal-kind').textContent = t.kind;
  el('modal-purpose').textContent = t.summary || t.purpose || '';
  const firstArtifact = t.artifacts?.[0];
  const firstType = artifactType(firstArtifact?.path || '');
  el('modal-img').src = '';
  el('modal-img').alt = esc(t.title);
  el('modal-audio').src = '';
  el('modal-img').style.display = firstType === 'image' ? 'block' : 'none';
  el('modal-audio').style.display = firstType === 'audio' ? 'block' : 'none';
  if (firstArtifact) {
    if (firstType === 'audio') {
      el('modal-audio').src = firstArtifact.path;
    } else {
      el('modal-img').src = firstArtifact.path;
    }
  }
  
  el('modal-artifacts').innerHTML = (t.artifacts || []).map((a, i) => renderArtifactThumbRow(a, i)).join('');

  if (isExample) {
    el('modal-prompt').textContent = '【画像見本のみ】\nこのテンプレートには構成要素（プロンプトの種）が定義されていません。';
    el('modal-copy').style.display = 'none';
    el('modal-primary').innerHTML = '<span class="subtle-label">構成要素なし</span>';
  } else {
    el('modal-prompt').textContent = t.generated_prompt || (t.blocks && t.blocks.length ? t.blocks : [id]).map(bid => blocks[bid]?.content || bid).join('\n\n');
    el('modal-copy').style.display = 'block';
    
    const chips = (ids) => (ids || []).map(bid => `
      <span class="tag is-clickable" onclick="openModal('${bid}')">
        ${esc(blocks[bid]?.title || bid)}
      </span>
    `).join('');
    el('modal-primary').innerHTML = chips(t.blocks);
  }
  
  const targetBids = new Set(t.blocks || []);
  const related = templates
    .filter(x => x.id !== t.id && (x.blocks || []).some(bid => targetBids.has(bid)))
    .slice(0, 20);

  el('modal-related').innerHTML = related.map(x => `
    <div class="modal-related-item" onclick="openModal('${x.id}')">
      ${renderArtifactThumb(x.artifacts?.[0])}
      <div class="subtle-label modal-related-title">${esc(x.title)}</div>
    </div>
  `).join('');
  el('modal-related-block').hidden = related.length === 0;
  
  el('modal').classList.add('active');
  el('modal-content').scrollTo(0, 0);
};

window.modalBack = () => {
  if (state.modalHistory.length > 0) {
    const prevId = state.modalHistory.pop();
    openModal(prevId, false);
  }
};

window.switchModalArtifact = (target, path) => {
  const type = artifactType(path);
  document.querySelectorAll('.modal-artifact-thumb').forEach(img => img.classList.remove('is-active'));
  target.classList.add('is-active');
  el('modal-img').style.display = type === 'image' ? 'block' : 'none';
  el('modal-audio').style.display = type === 'audio' ? 'block' : 'none';
  if (type === 'audio') {
    el('modal-audio').src = path;
    el('modal-audio').play?.();
  } else {
    el('modal-img').src = path;
  }
};

const renderGen = () => {
  el('generator-node-picker').innerHTML = db.blocks.map(b => `
    <button class="tag ${state.genBids.includes(b.id) ? 'active' : ''}" style="border:none; cursor:pointer;" onclick="toggleGenBlock('${b.id}')">
      ${esc(b.title)}
    </button>
  `).join('');
  el('generator-selected-nodes').innerHTML = state.genBids.map(bid => `
    <span class="tag">${esc(blocks[bid]?.title || bid)}</span>
  `).join('');
  el('generator-node-count').textContent = state.genBids.length;
};

window.toggleGenBlock = (id) => {
  state.genBids = state.genBids.includes(id) ? state.genBids.filter(b => b !== id) : [...state.genBids, id];
  renderGen();
};

el('search').oninput = (e) => { state.search = e.target.value; renderRail(); };
el('generator-template').onchange = (e) => {
  state.genTpl = e.target.value;
  state.genBids = [...(templateMap[state.genTpl]?.blocks || [])];
  renderGen();
};

el('generator-submit').onclick = async () => {
  const btn = el('generator-submit');
  btn.disabled = true;
  el('generator-status').textContent = '生成中...';
  try {
    const res = await fetch('/api/prompt-generate', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ template_id: state.genTpl, block_ids: state.genBids, instruction: el('generator-instruction').value })
    });
    if (!res.ok) throw new Error('Generation failed');
    const data = await res.json();
    el('generator-output').textContent = data.generated_prompt;
    el('generator-status').textContent = `完了: ${data.request_id}`;
    el('generator-copy').disabled = false;
    saveLocal({
      id: `local_${Date.now()}`,
      title: data.title || 'Generated',
      generated_prompt: data.generated_prompt,
      blocks: state.genBids
    });
  } catch (e) {
    el('generator-status').textContent = '生成に失敗しました。入力を短くするか、再実行してください。';
  }
  btn.disabled = false;
};

el('generator-copy').onclick = (e) => {
  navigator.clipboard.writeText(el('generator-output').textContent);
  const old = e.target.textContent;
  e.target.textContent = '完了';
  setTimeout(() => e.target.textContent = old, 2000);
};

el('generator-reset-template').onclick = () => {
  state.genBids = [...(templateMap[state.genTpl]?.blocks || [])];
  renderGen();
};

el('modal-close').onclick = () => {
  el('modal').classList.remove('active');
  state.modalHistory = [];
  state.currentModalId = null;
};
el('modal-back').onclick = () => modalBack();
el('modal').onclick = (e) => { 
  if (e.target.id === 'modal') {
    el('modal').classList.remove('active');
    state.modalHistory = [];
    state.currentModalId = null;
  }
};
el('modal-copy').onclick = (e) => {
  navigator.clipboard.writeText(el('modal-prompt').textContent);
  const old = e.target.textContent;
  e.target.textContent = 'コピー完了';
  setTimeout(() => e.target.textContent = old, 2000);
};

el('generator-template').innerHTML = templates
  .filter(t => t.blocks && t.blocks.length > 0)
  .map(t => `<option value="${t.id}">${esc(t.title)}</option>`).join('');
renderRail();
renderSkills();
renderGen();
