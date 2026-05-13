"""Tidy data reshaping using Polars and DuckDB.

pd.melt()        → DuckDB UNPIVOT
df.pivot()       → DuckDB PIVOT
pd.pivot_table() → DuckDB PIVOT with aggregate function
groupby().agg()  → DuckDB GROUP BY
"""

import duckdb
import polars as pl
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List


# ── data generation ──────────────────────────────────────────────────────────

def generate_wide_data(
    stores: List[str] = None,
    months: List[str] = None,
) -> pl.DataFrame:
    if stores is None:
        stores = ["A", "B"]
    if months is None:
        months = ["Jan_Sales", "Feb_Sales", "Mar_Sales"]
    data: Dict = {"Store": stores}
    for i, m in enumerate(months):
        data[m] = [100 + i * 10, 90 + i * 10]
    return pl.DataFrame(data)


def generate_weekly_sales_data(
    stores: List[str] = None,
    weeks: int = 3,
) -> pl.DataFrame:
    if stores is None:
        stores = ["North", "South", "East", "West"]
    data: Dict = {"Store": stores}
    for w in range(1, weeks + 1):
        data[f"Week_{w}"] = [300 + w * 10, 250 + w * 5, 400 - w * 5, 375 + w * 3]
    return pl.DataFrame(data)


# ── reshape operations ────────────────────────────────────────────────────────

def wide_to_long(
    df: pl.DataFrame,
    id_col: str,
    month_cols: List[str],
    var_name: str = "Month",
    value_name: str = "Sales",
    strip_suffix: str = "_Sales",
) -> pl.DataFrame:
    """pd.melt() → DuckDB UNPIVOT."""
    on_clause = ", ".join(f'"{c}"' for c in month_cols)
    result = duckdb.sql(f"""
        SELECT
            "{id_col}",
            REPLACE("{var_name}", '{strip_suffix}', '') AS "{var_name}",
            "{value_name}"
        FROM (
            UNPIVOT df
            ON {on_clause}
            INTO NAME "{var_name}" VALUE "{value_name}"
        )
    """).pl()
    return result


def long_to_wide(
    df: pl.DataFrame,
    index: str,
    columns: str,
    values: str,
) -> pl.DataFrame:
    """df.pivot() → DuckDB PIVOT (no aggregation, one value per cell)."""
    return duckdb.sql(f"""
        PIVOT df
        ON "{columns}"
        USING FIRST("{values}")
        GROUP BY "{index}"
    """).pl()


def pivot_table_aggregation(
    df: pl.DataFrame,
    index: str,
    columns: str,
    values: str,
    aggfunc: str = "sum",
) -> pl.DataFrame:
    """pd.pivot_table() → DuckDB PIVOT with aggregate function."""
    sql_fn = {
        "sum": "SUM", "mean": "AVG", "min": "MIN",
        "max": "MAX", "count": "COUNT",
    }.get(aggfunc.lower(), "SUM")

    return duckdb.sql(f"""
        PIVOT df
        ON "{columns}"
        USING {sql_fn}("{values}")
        GROUP BY "{index}"
    """).pl()


def groupby_aggregation(
    df: pl.DataFrame,
    groupby_cols: List[str],
    value_col: str,
    aggfuncs: Dict[str, str],
) -> pl.DataFrame:
    """groupby().agg() → DuckDB GROUP BY with multiple aggregate functions."""
    sql_map = {"sum": "SUM", "mean": "AVG", "min": "MIN", "max": "MAX", "count": "COUNT"}
    agg_exprs = ", ".join(
        f'{sql_map.get(fn.lower(), fn.upper())}("{value_col}") AS "{alias}"'
        for alias, fn in aggfuncs.items()
    )
    group_clause = ", ".join(f'"{c}"' for c in groupby_cols)
    return duckdb.sql(
        f'SELECT {group_clause}, {agg_exprs} FROM df GROUP BY {group_clause}'
    ).pl()


def reshape_weekly_data(df: pl.DataFrame, week_cols: List[str]) -> pl.DataFrame:
    """Wide weekly → long via DuckDB UNPIVOT; Week column cast to int."""
    on_clause = ", ".join(f'"{c}"' for c in week_cols)
    return duckdb.sql(f"""
        SELECT
            "Store",
            CAST(REPLACE("Week", 'Week_', '') AS INTEGER) AS "Week",
            "Sales"
        FROM (
            UNPIVOT df
            ON {on_clause}
            INTO NAME "Week" VALUE "Sales"
        )
        ORDER BY "Store", "Week"
    """).pl()


# ── plots ─────────────────────────────────────────────────────────────────────

def plot_weekly_trend(df: pl.DataFrame, output_path: Path, plot: bool = False):
    if not plot:
        return
    weekly = duckdb.sql(
        'SELECT "Week", SUM("Sales") AS total FROM df GROUP BY "Week" ORDER BY "Week"'
    ).pl()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(weekly["Week"].to_list(), weekly["total"].to_list(),
            marker="o", color="#4A90A4", linewidth=1.2)
    ax.set_xlabel("Week")
    ax.set_ylabel("Total Sales")
    ax.set_title("Weekly Sales Trend")
    plt.tight_layout()
    plt.savefig(output_path, dpi=100, bbox_inches="tight")
    plt.close()


def plot_store_comparison(df: pl.DataFrame, output_path: Path, plot: bool = False):
    if not plot:
        return
    pivot = long_to_wide(df, "Week", "Store", "Sales")
    store_cols = [c for c in pivot.columns if c != "Week"]
    colors = ["#4A90A4", "#D4A574", "#8B6F9E", "#A8C5A0"]
    weeks = pivot["Week"].to_list()
    fig, ax = plt.subplots(figsize=(10, 6))
    for i, store in enumerate(store_cols):
        ax.plot(weeks, pivot[store].to_list(), label=store,
                color=colors[i % len(colors)], linewidth=1.2, marker="o")
    ax.set_xlabel("Week")
    ax.set_ylabel("Sales")
    ax.legend(loc="best")
    plt.tight_layout()
    plt.savefig(output_path, dpi=100, bbox_inches="tight")
    plt.close()
