# KAFKA RESULTS — Business Outcome

Issue #40 のための `kafka.results.business.v1` baseline contract。

## Inventory boundary

collector は KAFKA2306 の public / non-archived repository を列挙し、各repositoryの Git tree から次だけを business/service declaration として記録する。

- `docs/business/*.md`
- `docs/services/*.md`

READMEのマーケティング文、Issue本文、価格表記、GitHub stars/forks/downloadsは取引実績として解釈しない。tree APIがtruncatedの場合も、存在を推測して補わない。

## Metrics

`orders`, `paid_orders`, `gross_revenue`, `refunds`, `net_revenue`, `new_paying_customers`, `conversion_events`, `qualified_leads` を共通fieldとして持つ。

現時点の中央collectorにはBOOTH、決済、請求、CRM等のrepository-owned machine-readable transaction evidenceが接続されていない。このため値は `null / not_instrumented` とする。商品ページの存在や価格×推定件数から実売上を生成しない。

`gross / net / fee / tax` は同一値として扱わない。currencyも実取引証拠が存在するまで未設定とする。無料利用、download、starを売上へ換算しない。

## Periods

7日、30日、月次のslotを持つが、transaction evidenceがない期間は `not_instrumented` のままにする。0円・0件とは意味が異なる。

## Privacy

個別購入者、氏名、メールアドレス、注文番号、決済情報などのprivate transaction detailを公開snapshotへ含めない。将来adapterを追加する場合も、公開成果台帳へ渡すのはprivacy-safeな集計値とsource-system provenanceだけにする。

## Next evidence adapters

Issue #40をcloseするには、実際に利用している販売/決済/問い合わせsourceから、期間・currency・gross/net等の定義を固定した集計evidenceをrepository-owned schemaとして出力し、中央collectorはそのvalidated evidenceだけを取り込む。接続不能なchannelは `not_connected` / `not_instrumented` のまま保持する。
