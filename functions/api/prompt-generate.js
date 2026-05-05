export async function onRequestPost(context) {
  const { request, env } = context;
  const apiKey = env.GEMINI_API_KEY;
  const model = env.MODEL_NAME || "gemini-2.0-flash";

  if (!apiKey) {
    return new Response(JSON.stringify({ error: "GEMINI_API_KEY is not set" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }

  const req = await request.json();
  const { template_id, block_ids, instruction } = req;

  // db/prompts.json は公開されているので fetch で取得可能（ただし functions からは自分自身を fetch する必要がある）
  // ここでは簡単のため、クライアントから渡されたデータを使うか、assets から取得する
  // 実際には app.js が DB を持っているので、必要な情報をクライアントから送るのが確実
  // しかし app.py と互換性を持たせるため、ここでは assets から prompts.json を取得することを試みる
  
  const url = new URL(request.url);
  const dbRes = await env.ASSETS.fetch(new URL("/api/db", url.origin));
  const db = await dbRes.json();

  const tpl = db.templates.find(t => t.id === template_id);
  const blocksMap = Object.fromEntries(db.blocks.map(b => [b.id, b]));
  const bids = block_ids || tpl.blocks;
  const src = bids.map(id => blocksMap[id] ? `- ${blocksMap[id].title} (${id}): ${blocksMap[id].content}` : "").filter(Boolean).join("\n");

  const codex = `# Prompt Vault Frontend Codex

あなたは既存ブロックの構造を保ち、必要最小限の差分で更新する編集者です。

## 出力形式 (JSONのみ)

\`\`\`json
{
  "title": "シチュエーションに合わせた短いタイトル",
  "block_updates": { "block_id": "updated content" },
  "addition": "既存ブロックに入らない新しい補足（1フレーズ以内、原則空文字）"
}
\`\`\`

## 編集ルール

1. **既存優先**: 可能な限り既存ブロックを流用する。
2. **最小更新**: ユーザー指示に合わないブロックだけを更新する。
3. **役割維持**: \`master_style\`, \`character\`, \`negative\` などの役割を壊さない。
4. **命名規則**: 「生成版」「テンプレート」等の汎用語や \`/\` を使わず、具体的に短く命名する。

## コンテキスト

テンプレート名: ${tpl?.title || "Unknown"}
指示文: ${instruction}

## 既存ブロック (ID: content)

${src}
`;

  const apiRes = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      contents: [{ parts: [{ text: codex }] }]
    })
  });

  const data = await apiRes.json();
  const raw = data.candidates[0].content.parts[0].text.replace(/```json|```/g, "").trim();
  const out = JSON.parse(raw);

  const gen = [
    ...bids.map(id => out.block_updates?.[id] || blocksMap[id]?.content || ""),
    out.addition || ""
  ].filter(Boolean).join("\n\n");

  const now = new Date().toISOString();
  return new Response(JSON.stringify({
    request_id: now,
    generated_prompt: gen,
    title: out.title
  }), {
    headers: { "Content-Type": "application/json" }
  });
}
