# Kafka Ideation Evidence

`db/tweetsdb.json` は単なる巨大な補助DBではありません。Kafkaの実ツイートを根拠に、観察対象・感情・話題・文体・creator signal・sensory signal・prompt seed・image-generation seed・latent profileを再利用するための一次証拠です。

## Authorities

- Raw / derived evidence: `db/tweetsdb.json`
- Evidence extraction and legacy idea query: `scripts/tweetsdb.py`
- Compact compiler / retrieval library: `src/ideation.py`
- Compact compiler CLI: `scripts/compile_ideation_profile.py`
- Evidence-backed query CLI: `scripts/ideation.py`
- Build output: `dist/data/ideation_profile.json`

`dist/data/ideation_profile.json` は派生物です。`db/tweetsdb.json` の代替正本ではありません。

## Why both layers exist

raw tweetsdbには各recordの実テキストと、そのrecordから抽出した `topic_evidence`、`matched_keywords`、`mood`、`function`、`essence`、`trait_tags`、`prompt_seed`、`imagegen_seed`、`evidence_text`、`latent_profile` があります。これは「Kafkaは観察的」のような抽象profileだけでは失われる、発想の根拠です。

通常利用で全recordを毎回読む必要はありません。`build.py` はraw tweetsdbからcompact profileを生成し、次を残します。

- aggregate profile / summary
- topic / mood / function / latent mode / reuse type
- topic / mood transition
- 偏りを抑えて選んだ最大120件の実例
- 各実例の実テキスト、essence、traits、prompt/imagegen seeds、latent profile
- source SHA-256

## Query

まずbuildします。

```bash
task build
```

その後、自然なテーマから根拠例を取得できます。

```bash
task ideation -- "バニララテ"
```

または:

```bash
uv run python scripts/ideation.py "画像生成" --limit 5
```

結果は必ず `reference_examples` を返し、それらから `trait_tags`、`prompt_seeds`、`imagegen_seeds` を集約します。抽象profileだけからKafkaらしさを捏造するfallbackは持ちません。

旧engineを直接使う場合:

```bash
uv run python scripts/tweetsdb.py idea --topic food-drink --mood cheerful --limit 3
```

## Delivery contract

CIは次を確認します。

1. `tests.test_ideation_contract` がcompact化とevidence retrievalを検証する
2. `build.py` が実 `db/tweetsdb.json` から `dist/data/ideation_profile.json` を生成できる
3. `scripts/ideation.py` がbuild済みprofileから少なくとも1件の根拠例を返す
4. main deploy後、production URLから `data/ideation_profile.json` を取得できる

## Storage rule

`tweetsdb`をGit current treeから外すこと自体を目的にしません。将来外部storageやReleaseへ移す場合も、以下を満たしてから移行します。

- raw corpusが永続的に取得可能
- content hashで同一性を検証可能
- compact profileを再生成可能
- evidence retrievalのテストが同じ意味で通る
- migration前後で代表例とprofileの再現性を確認する

この条件を満たさずに容量だけを理由にraw evidenceを削除しません。
