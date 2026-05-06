const db = __DB_JSON__;
const blocks = Object.fromEntries(db.blocks.map(b => [b.id, b]));
const templates = db.templates;
const templateMap = Object.fromEntries(templates.map(t => [t.id, t]));

const el = (id) => document.getElementById(id);
const esc = (v) => v ? v.toString().replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m])) : '';

const state = {
  search: '',
  genTpl: templates[0]?.id || '',
  genBids: [...(templates[0]?.blocks || [])],
  localGenerated: JSON.parse(localStorage.getItem('prompt-vault-gen') || '[]')
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
  el('template-count').textContent = `${list.length} templates`;
  el('template-rail').innerHTML = list.map(t => `
    <div class="template-card" onclick="openModal('${t.id}')">
      <div class="template-card__thumb">${t.artifacts?.[0] ? `<img src="${t.artifacts[0].path}" loading="lazy">` : '<div class="template-card__placeholder">画像なし</div>'}</div>
      <div class="template-card__body">
        <div class="template-card__top">
          <span class="template-card__kind">${esc(t.kind)}</span>
        </div>
        <div class="template-card__title">${esc(t.title)}</div>
        <div class="template-card__summary">${esc(t.summary || t.purpose || '')}</div>
      </div>
    </div>
  `).join('');
};

window.openModal = (id) => {
  const all = [...templates, ...state.localGenerated];
  let t = all.find(x => x.id === id);
  if (!t && blocks[id]) {
    t = { id, title: blocks[id].title, kind: blocks[id].category || 'block', purpose: '', generated_prompt: blocks[id].content, blocks: [] };
  }
  if (!t) return;

  state.current = t;
  el('modal-title').textContent = t.title;
  el('modal-kind').textContent = t.kind;
  el('modal-purpose').textContent = t.summary || t.purpose || '';
  el('modal-img').src = t.artifacts?.[0]?.path || '';
  el('modal-img').hidden = !t.artifacts?.[0];
  
  el('modal-artifacts').innerHTML = (t.artifacts || []).map((a, i) => `
    <img src="${a.path}" class="modal-artifact-thumb ${i === 0 ? 'is-active' : ''}" onclick="switchModalImg(this, '${a.path}')" alt="${esc(a.title)}">
  `).join('');
  el('modal-artifacts').hidden = !t.artifacts || t.artifacts.length < 2;

  el('modal-prompt').textContent = t.generated_prompt || (t.blocks || [id]).map(bid => blocks[bid]?.content || bid).join('\n\n');
  
  const chips = (ids) => (ids || []).map(bid => `<button class="tag tag-button" onclick="openNode('${bid}', 'block')">${esc(blocks[bid]?.title || bid)}</button>`).join('');
  el('modal-primary').innerHTML = chips(t.blocks);
  el('modal-primary-block').hidden = !t.blocks || t.blocks.length === 0;

  const targetBids = new Set(t.blocks || []);
  const related = all
    .filter(x => x.id !== t.id && (x.blocks || []).some(bid => targetBids.has(bid)))
    .map(x => ({ ...x, score: (x.blocks || []).filter(bid => targetBids.has(bid)).length }))
    .sort((a, b) => b.score - a.score || (templates.indexOf(b) - templates.indexOf(a)))
    .slice(0, 8);

  el('modal-related').innerHTML = related.map(x => `
    <div class="modal-related-item" onclick="openModal('${x.id}')">
      <img src="${x.artifacts?.[0]?.path || ''}" loading="lazy">
      <div class="modal-related-item__title">${esc(x.title)}</div>
    </div>
  `).join('');
  el('modal-related-block').hidden = related.length === 0;
  
  el('modal').classList.add('active');
  el('modal').scrollTo(0, 0); // Scroll modal to top when opening new template
};

window.switchModalImg = (el, path) => {
  document.querySelectorAll('.modal-artifact-thumb').forEach(t => t.classList.remove('is-active'));
  el.classList.add('is-active');
  document.getElementById('modal-img').src = path;
};

const renderGen = () => {
  el('generator-node-picker').innerHTML = db.blocks.map(b => `
    <button class="recommend-card ${state.genBids.includes(b.id) ? 'is-selected' : ''}" onclick="toggleGenBlock('${b.id}')">
      <div class="recommend-card__body">
        <div class="recommend-card__title">${esc(b.title)}</div>
        <div class="recommend-card__meta">${esc(b.category)}</div>
      </div>
    </button>
  `).join('');
  el('generator-selected-nodes').innerHTML = state.genBids.map(bid => `
    <button class="tag tag-button" onclick="toggleGenBlock('${bid}')">${esc(blocks[bid]?.title || bid)} ×</button>
  `).join('');
  el('generator-node-count').textContent = `${state.genBids.length} selected`;
};

window.toggleGenBlock = (id) => {
  state.genBids = state.genBids.includes(id) ? state.genBids.filter(b => b !== id) : [...state.genBids, id];
  renderGen();
};

window.openNode = (id) => window.openModal(id);

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
  const res = await fetch('/api/prompt-generate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ template_id: state.genTpl, block_ids: state.genBids, instruction: el('generator-instruction').value })
  });
  const data = await res.json();
  el('generator-output').textContent = data.generated_prompt;
  el('generator-status').textContent = `完了: ${data.request_id}`;
  el('generator-copy').disabled = false;
  btn.disabled = false;
  
  saveLocal({
    id: `local_${Date.now()}`,
    title: data.title || 'Generated',
    generated_prompt: data.generated_prompt,
    blocks: state.genBids
  });
};

el('generator-copy').onclick = (e) => {
  navigator.clipboard.writeText(el('generator-output').textContent);
  const old = e.target.textContent;
  e.target.textContent = 'コピー完了！';
  setTimeout(() => e.target.textContent = old, 2000);
};

el('generator-reset-template').onclick = () => {
  state.genBids = [...(templateMap[state.genTpl]?.blocks || [])];
  renderGen();
};

el('generator-clear-nodes').onclick = () => {
  state.genBids = [];
  renderGen();
};

el('modal-close').onclick = () => el('modal').classList.remove('active');
el('modal').onclick = (e) => {
  if (e.target.id === 'modal') el('modal').classList.remove('active');
};
el('modal-copy').onclick = (e) => {
  navigator.clipboard.writeText(el('modal-prompt').textContent);
  const old = e.target.textContent;
  e.target.textContent = 'コピー完了！';
  setTimeout(() => e.target.textContent = old, 2000);
};

el('generator-template').innerHTML = templates.map(t => `<option value="${t.id}">${esc(t.title)}</option>`).join('');
renderRail();
renderGen();
