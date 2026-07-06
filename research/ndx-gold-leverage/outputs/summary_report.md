---
type: research_report
domain: Finance
source: FRED/DataHub
created: 2026-07-06
---

# NASDAQ100 2x vs NASDAQ100 + Gold 200% 実データ検証

## 0. 結論

- 検証データ終端: 2026-07-02
- 比較対象2戦略のCAGR最大: **NDX_Gold_200_monthly_USD_standard**
- 比較対象2戦略で最大ドローダウンが浅い戦略: **NDX_Gold_200_daily_USD_standard**
- 回復期間が短い戦略: **NDX_Gold_200_monthly_USD_standard**
- 開始年別の勝者数: `{"NDX_Gold_200_daily_USD_standard": 31, "NDX_2x_USD_standard": 9}`
- 楽天レバナス型の標準費用仮定: **0.86%/年**
- NASDAQ100ゴールドプラス型の標準費用仮定: **0.27%/年**

この検証はFREDのNASDAQ100、USD/JPY、3カ月T-Bill、S&P500系列と、DataHubの月次金価格系列を使った理論モデルです。実ファンドのスワップ、先物ロール、税金、トラッキング差、売買制約は完全再現していません。

**金データ制約**: FREDの旧LBMA Gold PM fixing系列は実行時点でCSV取得がHTTP 404だったため、1986年以降の超長期検証ではDataHub gold monthly price datasetを月次実データとして使用し、NASDAQ100日次カレンダーへ前方補完している。日次金ボラティリティと日次株金相関は過小評価されうる。

## 1. 主要指標

| index | CAGR | annual_vol | max_drawdown | recovery_days | worst_5y_return | monthly_win_rate | yearly_win_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| NDX_1x_USD | 0.142879 | 0.261664 | -0.828972 | 4775 | -0.687423 | 0.606996 | 0.829268 |
| NDX_2x_USD_standard | 0.171957 | 0.523328 | -0.989246 | 4421 | -0.966722 | 0.596708 | 0.756098 |
| NDX_Gold_200_daily_USD_standard | 0.175435 | 0.295725 | -0.835073 | 2023 | -0.604899 | 0.615226 | 0.682927 |
| NDX_Gold_200_monthly_USD_standard | 0.175773 | 0.296886 | -0.83608 | 2003 | -0.605931 | 0.619342 | 0.682927 |
| Gold_1x_USD | 0.0638272 | 0.13728 | -0.471193 | 2345 | -0.353086 | 0.37037 | 0.585366 |

## 2. 必須質問への回答

1. 超長期CAGRで勝ったのは **NDX_Gold_200_monthly_USD_standard**。
2. 最大ドローダウンが小さかったのは **NDX_Gold_200_daily_USD_standard**。
3. 回復期間が短かったのは **NDX_Gold_200_monthly_USD_standard**。
4. 10年ローリングは中央値で見ると、`NDX_2x_USD_standard` が 16.49%、`NDX_Gold_200_daily_USD_standard` が 17.20%。
5. 20年ローリングは中央値で見ると、`NDX_2x_USD_standard` が 9.09%、`NDX_Gold_200_daily_USD_standard` が 15.03%。
6. ITバブル天井開始は `start_year_results.csv` の2000年行を参照。
7. リーマン直前開始は `start_year_results.csv` の2007年行を参照。
8. 2021年末開始は `start_year_results.csv` の2022年行を参照。
9. 金の期待リターン閾値は `theory_checks.csv` の `gold_return_threshold_for_gold_plus_win` を参照。
10. 株金相関の損益分岐は `sensitivity_break_even.csv` と `06_sensitivity_heatmap.png` を参照。
11. 円建て投資家の結果は `metrics_summary.csv` の `JPY` 戦略行で確認。
12. ライフサイクル投資の中核では、CAGRだけでなく最大DD、回復期間、ローリング20年の安定性を優先。
13. 戦術枠では、低ボラ上昇局面ならNASDAQ100日次2倍の優位が出やすい。

## 3. 図表

![累積資産](figures/01_cumulative_wealth_log.png)

![ドローダウン](figures/02_drawdowns.png)

![株金相関](figures/05_stock_gold_rolling_correlation.png)

![感応度](figures/06_sensitivity_heatmap.png)

## 4. データソース

- FRED NASDAQ100: https://fred.stlouisfed.org/series/NASDAQ100
- FRED Gold PM fixing候補（実行時HTTP 404）: https://fred.stlouisfed.org/series/GOLDPMGBD228NLBM
- DataHub Gold monthly fallback: https://datahub.io/core/gold-prices/r/monthly.csv
- FRED USD/JPY: https://fred.stlouisfed.org/series/DEXJPUS
- FRED 3-Month Treasury Bill: https://fred.stlouisfed.org/series/DTB3
- FRED S&P 500: https://fred.stlouisfed.org/series/SP500
- 楽天レバナス公式: https://www.rakuten-toushin.co.jp/fund/nav/rilvns/
- Tracers NASDAQ100ゴールドプラス目論見書: https://www.amova-am.com/api/reports/prospectus?fundcode=645133
- World Gold Council Goldhub: https://www.gold.org/goldhub/data/gold-prices
- LBMA precious metal prices: https://www.lbma.org.uk/prices-and-data/precious-metal-prices

## 5. 重要な制約

- 信託報酬以外の実質コストは標準化した近似。
- 為替ヘッジありケースは、USD/JPY変動を除去し、米短期金利をヘッジコスト近似として控除。
- NASDAQ100+Gold 200%は、純資産100に対してNASDAQ100 100%、Gold 100%の200%エクスポージャーを仮定。
- 月次リバランス版は月初に100%/100%へ戻し、月中のウェイト変動を許容。

## 6. 投資判断表

| index | use_case | favored | evidence |
| --- | --- | --- | --- |
| 0 | CAGR最大化 | NDX+Gold 200% | CAGR 17.20% vs 17.54% |
| 1 | 最大DD抑制 | NDX+Gold 200% | MaxDD -98.92% vs -83.51% |
| 2 | 長期中核 | NDX+Gold 200% | 幾何平均、回復期間、破産回避をCAGRと同時評価 |
| 3 | 戦術枠 | NDX 2x | NASDAQ100が低ボラで上昇する局面に限定 |
| 4 | 開始年分散 | NDX_Gold_200_daily_USD_standard | {"NDX_Gold_200_daily_USD_standard": 31, "NDX_2x_USD_standard": 9} |

## 7. コストシナリオ

| index | strategy | cost_case | CAGR | annual_vol | max_drawdown | recovery_days | worst_5y_return |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | NDX_2x | low_0.77pct | 0.173013 | 0.523328 | -0.989159 | 4418 | -0.966571 |
| 1 | NDX_2x | standard_0.86pct | 0.171957 | 0.523328 | -0.989246 | 4421 | -0.966722 |
| 2 | NDX_2x | high_1.00pct | 0.170318 | 0.523328 | -0.989379 | 4490 | -0.966955 |
| 3 | NDX_Gold_200_daily | low_0.22pct | 0.176023 | 0.295725 | -0.834865 | 2020 | -0.603909 |
| 4 | NDX_Gold_200_daily | standard_0.27pct | 0.175435 | 0.295725 | -0.835073 | 2023 | -0.604899 |
| 5 | NDX_Gold_200_daily | high_0.50pct | 0.172736 | 0.295725 | -0.836028 | 2611 | -0.609422 |
| 6 | NDX_Gold_200_daily | true_cost_0.75pct | 0.169809 | 0.295725 | -0.83706 | 2611 | -0.614279 |
| 7 | NDX_Gold_200_daily | true_cost_1.00pct | 0.166889 | 0.295725 | -0.838085 | 2612 | -0.619076 |
| 8 | NDX_2x_JPY_hedged | standard_plus_rate_diff | 0.136123 | 0.523332 | -0.991673 | 5594 | -0.970667 |
