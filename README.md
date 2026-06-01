# Tidy Data: Long and Wide Format Transformations

Published: yes
Medium: [https://medium.com/@kyle-t-jones/working-with-tidy-data-long-wide-and-everything-in-between-using-python-4b217d9e2f04](https://medium.com/@kyle-t-jones/working-with-tidy-data-long-wide-and-everything-in-between-using-python-4b217d9e2f04)


This project demonstrates data reshaping operations including wide-to-long, long-to-wide, pivot tables, and groupby aggregations.

## Business context

Most data you work with in Python will not start out in a useful form. It will be messy. You'll find headers embedded in rows, multiple variables mashed into one column, or entire datasets that try to represent multiple time periods across many columns. When this happens, the first step is to make the data tidy.

Tidy data follows three rules. Each column is a variable. Each row is an observation. Each table is a single kind of observational unit.

This simple structure makes it easy to filter, summarize, model, and visualize your data. It plays nicely with libraries like `pandas`, `statsmodels`, `scikit-learn`, and `matplotlib`. You don't have to guess where your variables are. You don't have to rewrite your code every time you run a new analysis. Tidy data makes things fast and repeatable.

## Project Structure

```
.
├── README.md           # This file
├── main.py            # Main entry point
├── config.yaml        # Configuration file
├── requirements.txt   # Python dependencies
├── src/               # Core functions
│   ├── core.py        # Data transformation functions
│   └── plotting.py    # Tufte-style plotting utilities
├── tests/             # Unit tests
├── data/              # Data files
└── images/            # Generated plots and figures
```

## Configuration

Edit `config.yaml` to customize:
- Data generation parameters (stores, months, weeks)
- Transformation options (wide_to_long, long_to_wide, pivot_table, groupby)
- Output settings

## Transformations

### Wide to Long (melt)
- Converts columns to rows
- Useful for time series analysis
- Preserves identifier variables

### Long to Wide (pivot)
- Converts rows to columns
- Useful for cross-tabulation
- Creates multi-level column structure

### Pivot Table
- Aggregates data during reshaping
- Supports multiple aggregation functions
- Handles duplicate index/column combinations

### Groupby Aggregation
- Groups data by specified columns
- Applies aggregation functions
- Returns summary statistics

## Caveats

- By default, generates synthetic sales data.
- Pivot operations require unique index/column combinations or aggregation.
- Groupby operations can be memory-intensive for large datasets.

## Disclaimer

Educational/demo code only. Not financial, safety, or engineering advice. Use at your own risk. Verify results independently before any production or operational use.

## License

MIT — see [LICENSE](LICENSE).