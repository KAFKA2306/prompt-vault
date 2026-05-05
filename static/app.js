const db = __DB_JSON__;
const blocks = Object.fromEntries(db.blocks.map(b => [b.id, b]));
const templates = db.templates;
const templateMap = Object.fromEntries(templates.map(t => [t.id, t]));

const el = (id) => document.getElementById(id);
const escape = (v) => v.toString().replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));

const state = {
  search: '',
  generatorTemplateId: templates[0]?.id || '',
  generatorBlockIds: [...(templates[0]?.blocks || [])],
  output: 'まだ生成されていません。'
};

const renderRail = () => {
  const q = state.search.toLowerCase();
  const list = templates.filter(t => !q || JSON.stringify(t).toLowerCase().includes(q));
  el('template-count').textContent = `${list.length} templates`;
  el('template-rail').innerHTML = list.map(t => `
    <button class="template-card" onclick="openNode('${t.id}')">
      <div class="template-card__thumb">
        ${t.artifacts?.[0] ? `<img src="${t.artifacts[0].path}" loading="lazy">` : '<span>画像なし</span>'}
      </div>
      <div class="template-card__body">
        <div class="template-card__title">${escape(t.title)}</div>
        <div class="template-card__meta">${escape(t.purpose || t.summary || '')}</div>
      </div>
    </button>
  `).join('') || '<div class="empty">なし</div>';
};

const openNode = (id) => {
  const t = templateMap[id] || blocks[id];
  if (!t) return;
  el('modal-title').textContent = t.title;
  el('modal-prompt').textContent = t.generated_prompt || (t.blocks || []).map(bid => blocks[bid]?.content).join('\n\n');
  el('modal-img').src = t.artifacts?.[0]?.path || '';
  el('modal-img').hidden = !t.artifacts?.[0];
  el('modal').classList.add('active');
};

const generate = async () => {
  const btn = el('generator-submit');
  btn.disabled = true;
  el('generator-status').textContent = '生成中...';
  const res = await fetch('/api/prompt-generate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      template_id: el('generator-template').value,
      instruction: el('generator-instruction').value
    })
  });
  const data = await res.json();
  el('generator-output').textContent = data.generated_prompt;
  el('generator-status').textContent = `生成完了: ${data.request_id}`;
  btn.disabled = false;
};

el('search').oninput = (e) => { state.search = e.target.value; renderRail(); };
el('generator-submit').onclick = generate;
el('modal-close').onclick = () => el('modal').classList.remove('active');
el('modal-copy').onclick = () => {
  navigator.clipboard.writeText(el('modal-prompt').textContent);
  el('modal-copy').textContent = 'コピーしました！';
  setTimeout(() => el('modal-copy').textContent = 'プロンプトをコピー', 2000);
};

el('generator-template').innerHTML = templates.map(t => `<option value="${t.id}">${escape(t.title)}</option>`).join('');
renderRail();
