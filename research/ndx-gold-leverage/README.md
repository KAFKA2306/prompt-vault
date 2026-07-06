# NASDAQ100 2x vs NASDAQ100 + Gold 200%

Reproducible long-horizon test for:

- NASDAQ100 1x
- NASDAQ100 daily 2x
- NASDAQ100 100% + Gold 100% daily rebalance
- NASDAQ100 100% + Gold 100% monthly rebalance
- Gold 1x
- Optional S&P 500 analogues
- USD and JPY investor views

Run:

```bash
python3 research/ndx-gold-leverage/run_analysis.py
```

Primary generated outputs land in `research/ndx-gold-leverage/outputs/`.

## Output Figures

The analysis generates the following PNG figures under `outputs/figures/`.

### Cumulative Wealth

![Cumulative wealth, log scale](outputs/figures/01_cumulative_wealth_log.png)

### Drawdowns

![Drawdowns](outputs/figures/02_drawdowns.png)

### Rolling CAGR

![Rolling 5Y CAGR](outputs/figures/03_rolling_5y_cagr.png)

![Rolling 10Y CAGR](outputs/figures/03_rolling_10y_cagr.png)

![Rolling 15Y CAGR](outputs/figures/03_rolling_15y_cagr.png)

![Rolling 20Y CAGR](outputs/figures/03_rolling_20y_cagr.png)

![Rolling 30Y CAGR](outputs/figures/03_rolling_30y_cagr.png)

### Rolling Max Drawdown

![Rolling 5Y max drawdown](outputs/figures/04_rolling_5y_max_drawdown.png)

![Rolling 10Y max drawdown](outputs/figures/04_rolling_10y_max_drawdown.png)

![Rolling 20Y max drawdown](outputs/figures/04_rolling_20y_max_drawdown.png)

### Stock / Gold Relationship

![NASDAQ100 and gold rolling correlation](outputs/figures/05_stock_gold_rolling_correlation.png)

![Sensitivity heatmap](outputs/figures/06_sensitivity_heatmap.png)
