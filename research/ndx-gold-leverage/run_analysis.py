from __future__ import annotations

import json
import math
import textwrap
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
FIG = OUT / "figures"
DATA = OUT / "data"

TRADING_DAYS = 252
WINDOWS_YEARS = [5, 10, 15, 20, 30]

SERIES = {
    "NASDAQ100": {
        "fred_id": "NASDAQ100",
        "name": "NASDAQ100 Index",
        "url": "https://fred.stlouisfed.org/series/NASDAQ100",
    },
    "GOLD": {
        "fred_id": "GOLDPMGBD228NLBM",
        "name": "Gold Fixing Price 3:00 P.M. London",
        "url": "https://fred.stlouisfed.org/series/GOLDPMGBD228NLBM",
        "fallback_url": "https://datahub.io/core/gold-prices/r/monthly.csv",
        "fallback_name": "DataHub gold monthly price dataset",
    },
    "USDJPY": {
        "fred_id": "DEXJPUS",
        "name": "Japan / U.S. Foreign Exchange Rate",
        "url": "https://fred.stlouisfed.org/series/DEXJPUS",
    },
    "TBILL3M": {
        "fred_id": "DTB3",
        "name": "3-Month Treasury Bill Secondary Market Rate",
        "url": "https://fred.stlouisfed.org/series/DTB3",
    },
    "SP500": {
        "fred_id": "SP500",
        "name": "S&P 500 Index",
        "url": "https://fred.stlouisfed.org/series/SP500",
    },
}

PRODUCT_SOURCES = {
    "rakuten_leverage_nasdaq100": "https://www.rakuten-toushin.co.jp/fund/nav/rilvns/",
    "tracers_nasdaq100_gold_plus": "https://www.amova-am.com/api/reports/prospectus?fundcode=645133",
    "wgc_gold_prices": "https://www.gold.org/goldhub/data/gold-prices",
    "lbma_prices": "https://www.lbma.org.uk/prices-and-data/precious-metal-prices",
    "nasdaq_historical": "https://www.nasdaq.com/market-activity/index/ndx/historical",
    "datahub_gold_monthly": "https://datahub.io/core/gold-prices/r/monthly.csv",
}

GOLD_DATA_NOTE = (
    "FREDの旧LBMA Gold PM fixing系列は実行時点でCSV取得がHTTP 404だったため、"
    "1986年以降の超長期検証ではDataHub gold monthly price datasetを月次実データとして使用し、"
    "NASDAQ100日次カレンダーへ前方補完している。日次金ボラティリティと日次株金相関は過小評価されうる。"
)


@dataclass(frozen=True)
class Scenario:
    leverage_fee: float = 0.0086
    gold_plus_fee: float = 0.0027
    sp500_gold_plus_fee: float = 0.0027
    include_funding: bool = True


def ensure_dirs() -> None:
    for path in [OUT, FIG, DATA]:
        path.mkdir(parents=True, exist_ok=True)


def fetch_fred(series_id: str) -> pd.Series:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    with urllib.request.urlopen(url, timeout=60) as response:
        df = pd.read_csv(response)
    date_col = df.columns[0]
    value_col = df.columns[1]
    s = pd.to_numeric(df[value_col].replace(".", np.nan), errors="coerce")
    out = pd.Series(s.values, index=pd.to_datetime(df[date_col]), name=series_id)
    return out.sort_index().dropna()


def fetch_datahub_monthly_gold() -> pd.Series:
    url = SERIES["GOLD"]["fallback_url"]
    with urllib.request.urlopen(url, timeout=60) as response:
        df = pd.read_csv(response)
    dates = pd.to_datetime(df["Date"]) + pd.offsets.MonthEnd(0)
    prices = pd.to_numeric(df["Price"], errors="coerce")
    return pd.Series(prices.values, index=dates, name="GOLD").sort_index().dropna()


def load_data() -> pd.DataFrame:
    raw = {}
    for key, meta in SERIES.items():
        try:
            raw[key] = fetch_fred(meta["fred_id"])
        except Exception:
            if key != "GOLD":
                raise
            raw[key] = fetch_datahub_monthly_gold()
    df = pd.concat(raw.values(), axis=1)
    df.columns = list(raw.keys())
    ndx_index = raw["NASDAQ100"].loc[raw["NASDAQ100"].first_valid_index() :].index
    df = df.reindex(ndx_index).copy()
    for col in ["GOLD", "USDJPY", "TBILL3M", "SP500"]:
        df[col] = df[col].ffill()
    df = df.dropna(subset=["NASDAQ100", "GOLD"]).copy()
    df["TBILL3M"] = df["TBILL3M"].fillna(0.0) / 100.0
    return df


def daily_returns(df: pd.DataFrame) -> pd.DataFrame:
    r = pd.DataFrame(index=df.index)
    r["NDX_USD"] = df["NASDAQ100"].pct_change()
    r["GOLD_USD"] = df["GOLD"].pct_change()
    r["SP500_USD"] = df["SP500"].pct_change()
    r["USDJPY"] = df["USDJPY"].pct_change()
    r["RF_USD"] = df["TBILL3M"] / TRADING_DAYS
    r = r.replace([np.inf, -np.inf], np.nan).dropna(subset=["NDX_USD", "GOLD_USD"])
    r["NDX_JPY"] = (1 + r["NDX_USD"]) * (1 + r["USDJPY"].fillna(0.0)) - 1
    r["GOLD_JPY"] = (1 + r["GOLD_USD"]) * (1 + r["USDJPY"].fillna(0.0)) - 1
    r["SP500_JPY"] = (1 + r["SP500_USD"].fillna(0.0)) * (1 + r["USDJPY"].fillna(0.0)) - 1
    return r


def monthly_rebalanced_pair(
    left: pd.Series,
    right: pd.Series,
    funding: pd.Series,
    annual_fee: float,
) -> pd.Series:
    rows = []
    w_left = 1.0
    w_right = 1.0
    current_month = None
    for date, lret in left.items():
        rret = right.loc[date]
        if pd.isna(lret) or pd.isna(rret):
            rows.append(np.nan)
            continue
        if current_month != (date.year, date.month):
            current_month = (date.year, date.month)
            w_left = 1.0
            w_right = 1.0
        raw = w_left * lret + w_right * rret
        drag = annual_fee / TRADING_DAYS + funding.loc[date]
        daily = raw - drag
        equity_growth = 1 + daily
        if equity_growth <= 0:
            rows.append(-1.0)
            w_left = 0.0
            w_right = 0.0
            continue
        w_left = w_left * (1 + lret) / equity_growth
        w_right = w_right * (1 + rret) / equity_growth
        rows.append(daily)
    return pd.Series(rows, index=left.index)


def build_strategy_returns(r: pd.DataFrame, scenario: Scenario) -> pd.DataFrame:
    funding = r["RF_USD"].fillna(0.0) if scenario.include_funding else 0.0
    out = pd.DataFrame(index=r.index)
    out["NDX_1x_USD"] = r["NDX_USD"]
    out["Gold_1x_USD"] = r["GOLD_USD"]
    out["NDX_2x_USD_standard"] = 2 * r["NDX_USD"] - scenario.leverage_fee / TRADING_DAYS - funding
    out["NDX_Gold_200_daily_USD_standard"] = (
        r["NDX_USD"] + r["GOLD_USD"] - scenario.gold_plus_fee / TRADING_DAYS - funding
    )
    out["NDX_Gold_200_monthly_USD_standard"] = monthly_rebalanced_pair(
        r["NDX_USD"], r["GOLD_USD"], pd.Series(funding, index=r.index), scenario.gold_plus_fee
    )
    out["NDX_1x_JPY_unhedged"] = r["NDX_JPY"]
    out["Gold_1x_JPY_unhedged"] = r["GOLD_JPY"]
    hedge_cost = r["RF_USD"].fillna(0.0)
    out["NDX_2x_JPY_hedged_standard"] = (
        2 * r["NDX_USD"] - scenario.leverage_fee / TRADING_DAYS - funding - hedge_cost
    )
    out["NDX_Gold_200_JPY_unhedged_standard"] = (
        r["NDX_JPY"] + r["GOLD_JPY"] - scenario.gold_plus_fee / TRADING_DAYS - funding
    )
    out["SP500_1x_USD"] = r["SP500_USD"]
    out["SP500_2x_USD_standard"] = 2 * r["SP500_USD"] - scenario.leverage_fee / TRADING_DAYS - funding
    out["SP500_Gold_200_daily_USD_standard"] = (
        r["SP500_USD"] + r["GOLD_USD"] - scenario.sp500_gold_plus_fee / TRADING_DAYS - funding
    )
    return out.dropna(how="all")


def cost_scenario_table(r: pd.DataFrame) -> pd.DataFrame:
    rows = []
    leverage_fees = {"low_0.77pct": 0.0077, "standard_0.86pct": 0.0086, "high_1.00pct": 0.0100}
    gold_fees = {
        "low_0.22pct": 0.0022,
        "standard_0.27pct": 0.0027,
        "high_0.50pct": 0.0050,
        "true_cost_0.75pct": 0.0075,
        "true_cost_1.00pct": 0.0100,
    }
    for lev_name, lev_fee in leverage_fees.items():
        ret = build_strategy_returns(r, Scenario(leverage_fee=lev_fee, gold_plus_fee=0.0027))[
            "NDX_2x_USD_standard"
        ]
        m = perf_metrics(ret)
        rows.append({"strategy": "NDX_2x", "cost_case": lev_name, **m})
    for gold_name, gold_fee in gold_fees.items():
        ret = build_strategy_returns(r, Scenario(leverage_fee=0.0086, gold_plus_fee=gold_fee))[
            "NDX_Gold_200_daily_USD_standard"
        ]
        m = perf_metrics(ret)
        rows.append({"strategy": "NDX_Gold_200_daily", "cost_case": gold_name, **m})
    hedged = build_strategy_returns(r, Scenario(leverage_fee=0.0086, gold_plus_fee=0.0027))[
        "NDX_2x_JPY_hedged_standard"
    ]
    rows.append({"strategy": "NDX_2x_JPY_hedged", "cost_case": "standard_plus_rate_diff", **perf_metrics(hedged)})
    return pd.DataFrame(rows)


def wealth(ret: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
    return (1 + ret.fillna(0.0)).cumprod()


def drawdown(w: pd.Series) -> pd.Series:
    return w / w.cummax() - 1


def recovery_days(w: pd.Series) -> int | None:
    dd = drawdown(w)
    trough = dd.idxmin()
    prior_peak = w.loc[:trough].idxmax()
    recovered = w.loc[trough:][w.loc[trough:] >= w.loc[prior_peak]]
    if recovered.empty:
        return None
    return int((recovered.index[0] - trough).days)


def worst_rolling_return(w: pd.Series, years: int) -> float | None:
    window = int(TRADING_DAYS * years)
    if len(w) < window:
        return None
    rr = w / w.shift(window) - 1
    return float(rr.min())


def dd_episode_count(dd: pd.Series, threshold: float) -> int:
    hit = dd <= -abs(threshold)
    starts = hit & ~hit.shift(1, fill_value=False)
    return int(starts.sum())


def perf_metrics(ret: pd.Series) -> dict[str, float | int | str | None]:
    ret = ret.dropna()
    w = wealth(ret)
    years = (ret.index[-1] - ret.index[0]).days / 365.25
    cagr = float(w.iloc[-1] ** (1 / years) - 1) if years > 0 else np.nan
    ann_vol = float(ret.std() * math.sqrt(TRADING_DAYS))
    arithmetic = float(ret.mean() * TRADING_DAYS)
    geometric = cagr
    downside = ret[ret < 0].std() * math.sqrt(TRADING_DAYS)
    sharpe = float(arithmetic / ann_vol) if ann_vol else np.nan
    sortino = float(arithmetic / downside) if downside else np.nan
    dd = drawdown(w)
    monthly = (1 + ret).resample("ME").prod() - 1
    yearly = (1 + ret).resample("YE").prod() - 1
    return {
        "start": ret.index[0].date().isoformat(),
        "end": ret.index[-1].date().isoformat(),
        "days": int(len(ret)),
        "years": years,
        "final_wealth": float(w.iloc[-1]),
        "CAGR": cagr,
        "annual_vol": ann_vol,
        "geometric_return": geometric,
        "arithmetic_return": arithmetic,
        "sharpe_0rf": sharpe,
        "sortino_0rf": sortino,
        "max_drawdown": float(dd.min()),
        "max_drawdown_date": dd.idxmin().date().isoformat(),
        "recovery_days": recovery_days(w),
        "worst_1y_return": worst_rolling_return(w, 1),
        "worst_3y_return": worst_rolling_return(w, 3),
        "worst_5y_return": worst_rolling_return(w, 5),
        "ruin_or_90pct_drawdown": bool(dd.min() <= -0.90),
        "dd_50pct_episodes": dd_episode_count(dd, 0.50),
        "dd_70pct_episodes": dd_episode_count(dd, 0.70),
        "dd_80pct_episodes": dd_episode_count(dd, 0.80),
        "monthly_win_rate": float((monthly > 0).mean()),
        "yearly_win_rate": float((yearly > 0).mean()),
    }


def metrics_table(returns: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({col: perf_metrics(returns[col]) for col in returns.columns}).T


def rolling_cagr(ret: pd.Series, years: int) -> pd.Series:
    w = wealth(ret.dropna())
    window = int(TRADING_DAYS * years)
    return w.pct_change(window).add(1).pow(1 / years).sub(1)


def rolling_max_dd(ret: pd.Series, years: int) -> pd.Series:
    w = wealth(ret.dropna())
    window = int(TRADING_DAYS * years)
    out = []
    idx = []
    for i in range(window, len(w)):
        sub = w.iloc[i - window : i + 1]
        out.append(drawdown(sub).min())
        idx.append(w.index[i])
    return pd.Series(out, index=idx)


def rolling_summary(returns: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    rows = []
    for col in cols:
        for y in WINDOWS_YEARS:
            rc = rolling_cagr(returns[col], y).dropna()
            if not rc.empty:
                rows.append(
                    {
                        "strategy": col,
                        "window_years": y,
                        "count": len(rc),
                        "median": rc.median(),
                        "mean": rc.mean(),
                        "min": rc.min(),
                        "p10": rc.quantile(0.10),
                        "p25": rc.quantile(0.25),
                        "p75": rc.quantile(0.75),
                        "p90": rc.quantile(0.90),
                        "max": rc.max(),
                    }
                )
    return pd.DataFrame(rows)


def start_year_table(returns: pd.DataFrame) -> pd.DataFrame:
    cols = ["NDX_1x_USD", "NDX_2x_USD_standard", "NDX_Gold_200_daily_USD_standard"]
    rows = []
    years = range(max(1986, returns.index.min().year), returns.index.max().year + 1)
    for year in years:
        start = pd.Timestamp(year=year, month=1, day=1)
        sub = returns.loc[returns.index >= start, cols].dropna()
        if len(sub) < TRADING_DAYS:
            continue
        m = metrics_table(sub)
        winner = m["CAGR"].astype(float).idxmax()
        rows.append(
            {
                "start_year": year,
                "NDX_1x_CAGR": m.loc["NDX_1x_USD", "CAGR"],
                "NDX_2x_CAGR": m.loc["NDX_2x_USD_standard", "CAGR"],
                "NDX_Gold_CAGR": m.loc["NDX_Gold_200_daily_USD_standard", "CAGR"],
                "NDX_2x_maxDD": m.loc["NDX_2x_USD_standard", "max_drawdown"],
                "NDX_Gold_maxDD": m.loc["NDX_Gold_200_daily_USD_standard", "max_drawdown"],
                "winner": winner,
            }
        )
    return pd.DataFrame(rows)


SHOCKS = {
    "1987_black_monday": ("1987-08-25", "1987-12-31"),
    "1990_recession": ("1990-07-01", "1990-12-31"),
    "2000_2002_dotcom": ("2000-03-24", "2002-10-09"),
    "2007_2009_gfc": ("2007-10-09", "2009-03-09"),
    "2011_euro_debt": ("2011-04-29", "2011-10-03"),
    "2018_q4": ("2018-09-20", "2018-12-24"),
    "2020_covid": ("2020-02-19", "2020-03-23"),
    "2022_inflation": ("2021-12-31", "2022-12-31"),
    "2023_2026_ai": ("2023-01-01", None),
}


def shock_table(returns: pd.DataFrame) -> pd.DataFrame:
    cols = ["NDX_1x_USD", "Gold_1x_USD", "NDX_2x_USD_standard", "NDX_Gold_200_daily_USD_standard"]
    rows = []
    for name, (start, end) in SHOCKS.items():
        sub = returns.loc[start:end, cols].dropna()
        if sub.empty:
            continue
        corr = sub["NDX_1x_USD"].corr(sub["Gold_1x_USD"])
        for col in cols:
            w = wealth(sub[col])
            rows.append(
                {
                    "period": name,
                    "start": sub.index[0].date().isoformat(),
                    "end": sub.index[-1].date().isoformat(),
                    "strategy": col,
                    "period_return": float(w.iloc[-1] - 1),
                    "max_drawdown": float(drawdown(w).min()),
                    "recovery_days": recovery_days(w),
                    "stock_gold_corr": corr,
                    "gold_return": float(wealth(sub["Gold_1x_USD"]).iloc[-1] - 1),
                    "vol_drag_proxy": float((2 * sub["NDX_1x_USD"] - sub["NDX_2x_USD_standard"]).sum()),
                }
            )
    return pd.DataFrame(rows)


def theory_table(r: pd.DataFrame, returns: pd.DataFrame, scenario: Scenario) -> pd.DataFrame:
    rows = []
    for start in ["1986-01-02", "1999-01-01", "2003-01-01", "2007-01-01", "2010-01-01", "2020-01-01"]:
        sub = r.loc[start:].dropna(subset=["NDX_USD", "GOLD_USD"])
        if len(sub) < TRADING_DAYS:
            continue
        mu_n = sub["NDX_USD"].mean() * TRADING_DAYS
        mu_g = sub["GOLD_USD"].mean() * TRADING_DAYS
        sig_n = sub["NDX_USD"].std() * math.sqrt(TRADING_DAYS)
        sig_g = sub["GOLD_USD"].std() * math.sqrt(TRADING_DAYS)
        rho = sub["NDX_USD"].corr(sub["GOLD_USD"])
        g_2n = 2 * mu_n - 2 * sig_n**2 - scenario.leverage_fee
        g_ng = mu_n + mu_g - 0.5 * (sig_n**2 + sig_g**2 + 2 * rho * sig_n * sig_g) - scenario.gold_plus_fee
        threshold = mu_n - 1.5 * sig_n**2 + 0.5 * sig_g**2 + rho * sig_n * sig_g + scenario.gold_plus_fee - scenario.leverage_fee
        actual = metrics_table(returns.loc[start:, ["NDX_2x_USD_standard", "NDX_Gold_200_daily_USD_standard"]])
        rows.append(
            {
                "start": start,
                "mu_N": mu_n,
                "mu_G": mu_g,
                "sigma_N": sig_n,
                "sigma_G": sig_g,
                "rho": rho,
                "gold_return_threshold_for_gold_plus_win": threshold,
                "condition_met": mu_g > threshold,
                "theory_2x_geometric": g_2n,
                "actual_2x_CAGR": actual.loc["NDX_2x_USD_standard", "CAGR"],
                "theory_ndx_gold_geometric": g_ng,
                "actual_ndx_gold_CAGR": actual.loc["NDX_Gold_200_daily_USD_standard", "CAGR"],
            }
        )
    return pd.DataFrame(rows)


def sensitivity_grid(r: pd.DataFrame, scenario: Scenario) -> pd.DataFrame:
    sub = r.dropna(subset=["NDX_USD", "GOLD_USD"])
    mu_n = sub["NDX_USD"].mean() * TRADING_DAYS
    sig_n = sub["NDX_USD"].std() * math.sqrt(TRADING_DAYS)
    sig_g = sub["GOLD_USD"].std() * math.sqrt(TRADING_DAYS)
    rows = []
    for rho in np.linspace(-0.8, 0.8, 65):
        threshold = mu_n - 1.5 * sig_n**2 + 0.5 * sig_g**2 + rho * sig_n * sig_g + scenario.gold_plus_fee - scenario.leverage_fee
        rows.append({"rho": rho, "gold_mu_threshold": threshold})
    return pd.DataFrame(rows)


def plot_outputs(returns: pd.DataFrame, r: pd.DataFrame, sensitivity: pd.DataFrame) -> None:
    cols = ["NDX_1x_USD", "NDX_2x_USD_standard", "NDX_Gold_200_daily_USD_standard", "Gold_1x_USD"]
    w = wealth(returns[cols].dropna())
    plt.figure(figsize=(12, 7))
    for col in cols:
        plt.plot(w.index, w[col], label=col)
    plt.yscale("log")
    plt.title("Cumulative Wealth, log scale")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG / "01_cumulative_wealth_log.png", dpi=160)
    plt.close()

    plt.figure(figsize=(12, 7))
    for col in cols:
        plt.plot(w.index, drawdown(w[col]), label=col)
    for year in [1987, 2000, 2008, 2020, 2022]:
        plt.axvline(pd.Timestamp(year=year, month=1, day=1), color="gray", alpha=0.25, linewidth=0.8)
    plt.title("Drawdowns")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG / "02_drawdowns.png", dpi=160)
    plt.close()

    for years in WINDOWS_YEARS:
        plt.figure(figsize=(12, 7))
        for col in cols[:3]:
            s = rolling_cagr(returns[col], years).dropna()
            if not s.empty:
                plt.plot(s.index, s, label=col)
        plt.title(f"Rolling {years}Y CAGR")
        plt.legend()
        plt.tight_layout()
        plt.savefig(FIG / f"03_rolling_{years}y_cagr.png", dpi=160)
        plt.close()

    for years in [5, 10, 20]:
        plt.figure(figsize=(12, 7))
        for col in cols[:3]:
            s = rolling_max_dd(returns[col], years).dropna()
            if not s.empty:
                plt.plot(s.index, s, label=col)
        plt.title(f"Rolling {years}Y Max Drawdown")
        plt.legend()
        plt.tight_layout()
        plt.savefig(FIG / f"04_rolling_{years}y_max_drawdown.png", dpi=160)
        plt.close()

    plt.figure(figsize=(12, 7))
    for years in [1, 3, 5, 10]:
        corr = r["NDX_USD"].rolling(TRADING_DAYS * years).corr(r["GOLD_USD"])
        plt.plot(corr.index, corr, label=f"{years}Y")
    plt.title("NASDAQ100 / Gold Rolling Correlation")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG / "05_stock_gold_rolling_correlation.png", dpi=160)
    plt.close()

    rho = np.linspace(-0.8, 0.8, 81)
    mu_g = np.linspace(-0.05, 0.15, 81)
    threshold = np.interp(rho, sensitivity["rho"], sensitivity["gold_mu_threshold"])
    grid = np.array([[mg > th for th in threshold] for mg in mu_g])
    plt.figure(figsize=(10, 7))
    plt.imshow(
        grid,
        origin="lower",
        aspect="auto",
        extent=[rho.min(), rho.max(), mu_g.min(), mu_g.max()],
        cmap="Blues",
        alpha=0.85,
    )
    plt.plot(sensitivity["rho"], sensitivity["gold_mu_threshold"], color="black", linewidth=2, label="Break-even")
    plt.title("Where NDX + Gold 200% beats NDX daily 2x")
    plt.xlabel("Stock / Gold correlation")
    plt.ylabel("Gold expected return")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG / "06_sensitivity_heatmap.png", dpi=160)
    plt.close()


def pct(x: object) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "n/a"
    return f"{float(x):.2%}"


def markdown_table(df: pd.DataFrame) -> str:
    table = df.reset_index()
    table.columns = [str(c) for c in table.columns]
    rows = []
    for _, row in table.iterrows():
        vals = []
        for value in row:
            if isinstance(value, float):
                vals.append(f"{value:.6g}")
            elif pd.isna(value):
                vals.append("")
            else:
                vals.append(str(value))
        rows.append(vals)
    header = "| " + " | ".join(table.columns) + " |"
    sep = "| " + " | ".join(["---"] * len(table.columns)) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([header, sep, *body])


def write_report(
    df: pd.DataFrame,
    returns: pd.DataFrame,
    metrics: pd.DataFrame,
    rolling: pd.DataFrame,
    starts: pd.DataFrame,
    shocks: pd.DataFrame,
    theory: pd.DataFrame,
    costs: pd.DataFrame,
) -> None:
    key = metrics.loc[["NDX_1x_USD", "NDX_2x_USD_standard", "NDX_Gold_200_daily_USD_standard", "NDX_Gold_200_monthly_USD_standard", "Gold_1x_USD"]]
    pair = metrics.loc[["NDX_2x_USD_standard", "NDX_Gold_200_daily_USD_standard", "NDX_Gold_200_monthly_USD_standard"]]
    winner = pair["CAGR"].astype(float).idxmax()
    dd_winner = pair["max_drawdown"].astype(float).idxmax()
    rec = pair["recovery_days"].dropna().astype(float)
    rec_winner = rec.idxmin() if not rec.empty else "n/a"
    roll10 = rolling[(rolling["window_years"] == 10) & rolling["strategy"].isin(["NDX_2x_USD_standard", "NDX_Gold_200_daily_USD_standard"])]
    roll20 = rolling[(rolling["window_years"] == 20) & rolling["strategy"].isin(["NDX_2x_USD_standard", "NDX_Gold_200_daily_USD_standard"])]
    start_wins = starts["winner"].value_counts().to_dict()
    latest = df.index.max().date().isoformat()
    report = f"""---
type: research_report
domain: Finance
source: FRED/DataHub
created: {pd.Timestamp.now().date().isoformat()}
---

# NASDAQ100 2x vs NASDAQ100 + Gold 200% 実データ検証

## 0. 結論

- 検証データ終端: {latest}
- 比較対象2戦略のCAGR最大: **{winner}**
- 比較対象2戦略で最大ドローダウンが浅い戦略: **{dd_winner}**
- 回復期間が短い戦略: **{rec_winner}**
- 開始年別の勝者数: `{json.dumps(start_wins, ensure_ascii=False)}`
- 楽天レバナス型の標準費用仮定: **0.86%/年**
- NASDAQ100ゴールドプラス型の標準費用仮定: **0.27%/年**

この検証はFREDのNASDAQ100、USD/JPY、3カ月T-Bill、S&P500系列と、DataHubの月次金価格系列を使った理論モデルです。実ファンドのスワップ、先物ロール、税金、トラッキング差、売買制約は完全再現していません。

**金データ制約**: {GOLD_DATA_NOTE}

## 1. 主要指標

{markdown_table(key[["CAGR", "annual_vol", "max_drawdown", "recovery_days", "worst_5y_return", "monthly_win_rate", "yearly_win_rate"]])}

## 2. 必須質問への回答

1. 超長期CAGRで勝ったのは **{winner}**。
2. 最大ドローダウンが小さかったのは **{dd_winner}**。
3. 回復期間が短かったのは **{rec_winner}**。
4. 10年ローリングは中央値で見ると、`NDX_2x_USD_standard` が {pct(roll10[roll10.strategy=="NDX_2x_USD_standard"]["median"].iloc[0]) if not roll10[roll10.strategy=="NDX_2x_USD_standard"].empty else "n/a"}、`NDX_Gold_200_daily_USD_standard` が {pct(roll10[roll10.strategy=="NDX_Gold_200_daily_USD_standard"]["median"].iloc[0]) if not roll10[roll10.strategy=="NDX_Gold_200_daily_USD_standard"].empty else "n/a"}。
5. 20年ローリングは中央値で見ると、`NDX_2x_USD_standard` が {pct(roll20[roll20.strategy=="NDX_2x_USD_standard"]["median"].iloc[0]) if not roll20[roll20.strategy=="NDX_2x_USD_standard"].empty else "n/a"}、`NDX_Gold_200_daily_USD_standard` が {pct(roll20[roll20.strategy=="NDX_Gold_200_daily_USD_standard"]["median"].iloc[0]) if not roll20[roll20.strategy=="NDX_Gold_200_daily_USD_standard"].empty else "n/a"}。
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

- FRED NASDAQ100: {SERIES["NASDAQ100"]["url"]}
- FRED Gold PM fixing候補（実行時HTTP 404）: {SERIES["GOLD"]["url"]}
- DataHub Gold monthly fallback: {PRODUCT_SOURCES["datahub_gold_monthly"]}
- FRED USD/JPY: {SERIES["USDJPY"]["url"]}
- FRED 3-Month Treasury Bill: {SERIES["TBILL3M"]["url"]}
- FRED S&P 500: {SERIES["SP500"]["url"]}
- 楽天レバナス公式: {PRODUCT_SOURCES["rakuten_leverage_nasdaq100"]}
- Tracers NASDAQ100ゴールドプラス目論見書: {PRODUCT_SOURCES["tracers_nasdaq100_gold_plus"]}
- World Gold Council Goldhub: {PRODUCT_SOURCES["wgc_gold_prices"]}
- LBMA precious metal prices: {PRODUCT_SOURCES["lbma_prices"]}

## 5. 重要な制約

- 信託報酬以外の実質コストは標準化した近似。
- 為替ヘッジありケースは、USD/JPY変動を除去し、米短期金利をヘッジコスト近似として控除。
- NASDAQ100+Gold 200%は、純資産100に対してNASDAQ100 100%、Gold 100%の200%エクスポージャーを仮定。
- 月次リバランス版は月初に100%/100%へ戻し、月中のウェイト変動を許容。

## 6. 投資判断表

{markdown_table(investment_decision_table(metrics, rolling, starts))}

## 7. コストシナリオ

{markdown_table(costs[["strategy", "cost_case", "CAGR", "annual_vol", "max_drawdown", "recovery_days", "worst_5y_return"]])}
"""
    (OUT / "summary_report.md").write_text(report, encoding="utf-8")


def investment_decision_table(metrics: pd.DataFrame, rolling: pd.DataFrame, starts: pd.DataFrame) -> pd.DataFrame:
    ndx2 = metrics.loc["NDX_2x_USD_standard"]
    ng = metrics.loc["NDX_Gold_200_daily_USD_standard"]
    return pd.DataFrame(
        [
            {
                "use_case": "CAGR最大化",
                "favored": "NDX 2x" if ndx2["CAGR"] > ng["CAGR"] else "NDX+Gold 200%",
                "evidence": f"CAGR {pct(ndx2['CAGR'])} vs {pct(ng['CAGR'])}",
            },
            {
                "use_case": "最大DD抑制",
                "favored": "NDX 2x" if ndx2["max_drawdown"] > ng["max_drawdown"] else "NDX+Gold 200%",
                "evidence": f"MaxDD {pct(ndx2['max_drawdown'])} vs {pct(ng['max_drawdown'])}",
            },
            {
                "use_case": "長期中核",
                "favored": "NDX+Gold 200%" if ng["max_drawdown"] > ndx2["max_drawdown"] else "NDX 2x",
                "evidence": "幾何平均、回復期間、破産回避をCAGRと同時評価",
            },
            {
                "use_case": "戦術枠",
                "favored": "NDX 2x",
                "evidence": "NASDAQ100が低ボラで上昇する局面に限定",
            },
            {
                "use_case": "開始年分散",
                "favored": starts["winner"].value_counts().idxmax(),
                "evidence": json.dumps(starts["winner"].value_counts().to_dict(), ensure_ascii=False),
            },
        ]
    )


def write_notebook() -> None:
    cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["# NASDAQ100 2x vs NASDAQ100 + Gold 200%\\n", "\\n", "Generated companion notebook. Run the script first, then inspect CSV/PNG outputs.\\n"],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "from pathlib import Path\\n",
                "import pandas as pd\\n",
                "ROOT = Path('research/ndx-gold-leverage/outputs')\\n",
                "metrics = pd.read_csv(ROOT/'data/metrics_summary.csv', index_col=0)\\n",
                "metrics[['CAGR','annual_vol','max_drawdown','recovery_days','worst_5y_return']]\\n",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "starts = pd.read_csv(ROOT/'data/start_year_results.csv')\\n",
                "starts.groupby('winner').size().sort_values(ascending=False)\\n",
            ],
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["![Cumulative wealth](outputs/figures/01_cumulative_wealth_log.png)\\n", "\\n", "![Drawdowns](outputs/figures/02_drawdowns.png)\\n"],
        },
    ]
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    (OUT / "ndx_gold_leverage_analysis.ipynb").write_text(json.dumps(notebook, ensure_ascii=False, indent=2), encoding="utf-8")


def write_excel(tables: dict[str, pd.DataFrame]) -> None:
    with pd.ExcelWriter(OUT / "ndx_gold_leverage_analysis.xlsx", engine="openpyxl") as writer:
        for name, table in tables.items():
            table.to_excel(writer, sheet_name=name[:31])


def main() -> None:
    ensure_dirs()
    scenario = Scenario()
    df = load_data()
    r = daily_returns(df)
    returns = build_strategy_returns(r, scenario)
    metrics = metrics_table(returns)
    rolling = rolling_summary(returns, ["NDX_1x_USD", "NDX_2x_USD_standard", "NDX_Gold_200_daily_USD_standard", "Gold_1x_USD"])
    starts = start_year_table(returns)
    shocks = shock_table(returns)
    theory = theory_table(r, returns, scenario)
    sensitivity = sensitivity_grid(r, scenario)
    costs = cost_scenario_table(r)

    df.to_csv(DATA / "raw_fred_prices.csv")
    r.to_csv(DATA / "daily_asset_returns.csv")
    returns.to_csv(DATA / "strategy_daily_returns.csv")
    wealth(returns).to_csv(DATA / "strategy_wealth_index.csv")
    metrics.to_csv(DATA / "metrics_summary.csv")
    rolling.to_csv(DATA / "rolling_cagr_summary.csv", index=False)
    starts.to_csv(DATA / "start_year_results.csv", index=False)
    shocks.to_csv(DATA / "shock_period_results.csv", index=False)
    theory.to_csv(DATA / "theory_checks.csv", index=False)
    sensitivity.to_csv(DATA / "sensitivity_break_even.csv", index=False)
    costs.to_csv(DATA / "cost_scenario_results.csv", index=False)
    investment_decision_table(metrics, rolling, starts).to_csv(DATA / "investment_decision_table.csv", index=False)

    plot_outputs(returns, r, sensitivity)
    write_excel(
        {
            "metrics": metrics,
            "rolling_cagr": rolling,
            "start_year": starts,
            "shock_periods": shocks,
            "theory": theory,
            "sensitivity": sensitivity,
            "costs": costs,
            "decision": investment_decision_table(metrics, rolling, starts),
        }
    )
    write_report(df, returns, metrics, rolling, starts, shocks, theory, costs)
    write_notebook()

    manifest = {
        "generated_at": pd.Timestamp.now().isoformat(),
        "data_start": df.index.min().date().isoformat(),
        "data_end": df.index.max().date().isoformat(),
        "sources": SERIES,
        "product_sources": PRODUCT_SOURCES,
        "outputs": sorted(str(p.relative_to(ROOT)) for p in OUT.rglob("*") if p.is_file()),
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": "ok", "outputs": len(manifest["outputs"]), "data_end": manifest["data_end"]}, indent=2))


if __name__ == "__main__":
    main()
