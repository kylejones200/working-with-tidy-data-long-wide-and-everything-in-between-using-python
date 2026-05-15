---
author: "Kyle Jones"
date_published: "May 4, 2025"
date_exported_from_medium: "November 10, 2025"
canonical_link: "https://medium.com/@kyle-t-jones/working-with-tidy-data-long-wide-and-everything-in-between-using-python-4b217d9e2f04"
---

# Working with Tidy Data: Long, Wide, and Everything in Between using Python Most data you work with in Python

will not start out in a useful form. It will be messy. You'll find headers embedded in rows, multiple...

### Working with Tidy Data: Long, Wide, and Everything in Between using Python
Most data you work with in Python will not start out in a useful form. It will be messy. You'll find headers embedded in rows, multiple variables mashed into one column, or entire datasets that try to represent multiple time periods across many columns. When this happens, the first step is to make the data tidy.

Tidy data follows three rules. Each column is a variable. Each row is an observation. Each table is a single kind of observational unit.

This simple structure makes it easy to filter, summarize, model, and visualize your data. It plays nicely with libraries like `pandas`, `statsmodels`, `scikit-learn`, and `matplotlib`. You don't have to guess where your variables are. You don't have to rewrite your code every time you run a new analysis. Tidy data makes things fast and repeatable.

Let's look at a small example. Suppose you receive the following Excel file:


This is *wide* data. It's great for a manager who wants to glance at numbers. But if you want to analyze seasonality or run time series models, this format is painful.

Tidy data transforms it to a *long* format:


Now we can group by month, compare across stores, and apply statistical models --- all with clean and predictable code.

In the sections that follow, we'll move back and forth between wide and long formats, group and summarize, and build habits that keep your data analysis smooth from start to finish.

### Long vs. Wide Formats
To get the most out of tidy data, you need to recognize when you're working with a long or wide format and understand when each one is appropriate.

Wide Format

In a wide format, different variables are spread across multiple columns. This is common in spreadsheets and reports, especially when time is represented across the top row. Take this dataset:


Each quarter is a separate column. It's easy to read for a human, but hard to work with programmatically. For example, calculating the average sales across quarters would require explicitly listing each column name. It also breaks the tidy data rule: the time dimension is spread across column names instead of values.

Long Format

In a long format, all values of the same variable are in one column, and each row is a unique observation.


This format is ideal for most statistical analysis and plotting tools. You can group by quarter, compare products, or feed this directly into a line chart with no additional transformation.

When to Use Each Format

Wide format works best when you need to show a snapshot --- when clarity to a human matters more than flexibility for a computer. Monthly reports, printed summaries, and dashboards often benefit from wide data.

Long format works best when you want to analyze, model, or visualize. It's easier to filter, aggregate, and merge with other datasets. If you're building a dashboard that needs to drill down or animate over time, long format is almost always better.

You should be able to move fluidly between formats. In the next section, we'll walk through how to do that using `pandas`.

### Transforming Between Long and Wide
In real analysis, you'll often get data in the wrong shape. Whether it comes from Excel, SQL, or an API, it might be wide when you need it long --- or long when you need it wide. You can fix that with `pandas` using `melt()`, `pivot()`, and `pivot_table()`.

#### From Wide to Long: `pd.melt()`
`melt()` makes a DataFrame longer by stacking columns into rows. You tell it which columns to keep fixed (`id_vars`) and which columns to turn into rows (`value_vars`).

```python
import pandas as pd


df = pd.DataFrame({
    'Store': ['A', 'B'],
    'Jan_Sales': [100, 90],
    'Feb_Sales': [120, 100],
    'Mar_Sales': [130, 110]
})


long_df = pd.melt(df, id_vars='Store', var_name='Month', value_name='Sales')
```


You might want to clean up the `Month` column afterward:

``` 
long_df['Month'] = long_df['Month'].str.replace('_Sales', '')
```

Now you're ready to group by month, filter by store, or plot a time series.

#### From Long to Wide: `pivot()` and `pivot_table()`
To reshape long data back into wide format, use `pivot()` when you know there are no duplicate entries. You need to specify the index, columns, and values.

``` 
wide_df = long_df.pivot(index='Store', columns='Month', values='Sales').reset_index()
```


If your data has duplicates --- say, multiple sales per store per month --- you'll need `pivot_table()` instead. It lets you specify how to aggregate duplicates:

``` 
pivot_df = long_df.pivot_table(
    index='Store',
    columns='Month',
    values='Sales',
    aggfunc='sum'  # or 'mean', 'max', etc.
).reset_index()
```

This is a safer option in general, especially for real-world data that may contain noise, missing values, or unexpected duplicates.

#### Pitfalls to Avoid
1.  [Duplicate keys: If you pivot without handling duplicates, `pandas` will raise an error. Use `pivot_table()` when in doubt.]
2.  [Multi-indexes: Pivoting creates multi-level column names. Flatten them if needed using: `df.columns = [str(col) for col in df.columns]`]
3.  [Missing values: Pivoting can introduce `NaN`s. You can fill them later with `fillna()` or `dropna()` depending on your needs.]

Next, we'll walk through how to summarize and analyze this reshaped data using `groupby()`.

### Grouping and Summarizing
Once your data is in a tidy format --- typically long --- you'll often want to group it by one or more variables and compute summaries. This is the heart of descriptive analysis: you collapse raw records into patterns you can understand.

#### Basic Grouping: `groupby()`
The `groupby()` function in `pandas` splits your data into groups, lets you run computations on each group, and returns the result.

Let's start with a tidy dataset:

``` 
data = pd.DataFrame({
    'Store': ['A', 'A', 'A', 'B', 'B', 'B'],
    'Month': ['Jan', 'Feb', 'Mar', 'Jan', 'Feb', 'Mar'],
    'Sales': [100, 120, 130, 90, 100, 110]
})
```

If you want the total sales per store:

``` 
data.groupby('Store')['Sales'].sum().reset_index()
```


Or the average per month:

``` 
data.groupby('Month')['Sales'].mean().reset_index()
```


#### Grouping by Multiple Variables
You can group by more than one variable. Here's how to get total sales per store per month:

``` 
data.groupby(['Store', 'Month'])['Sales'].sum().reset_index()
```

This returns a long-format summary that's great for plotting:


#### Multiple Aggregations with `agg()`
You can compute several summaries at once:

``` 
data.groupby('Store')['Sales'].agg(['mean', 'sum', 'std']).reset_index()
```

This gives you a wider summary:


To rename the columns:

``` 
data.groupby('Store')['Sales'].agg(
    avg_sales='mean',
    total_sales='sum',
    volatility='std'
).reset_index()
```

#### Resetting the Index
When you group by a variable, `pandas` uses it as the index by default. That can make plotting and merging harder. Use `.reset_index()` to flatten the output back to a normal DataFrame.

``` 
summary = data.groupby('Store')['Sales'].sum().reset_index()
```

Now `summary` behaves just like any other DataFrame---no hidden index tricks.

### Practical Use Case --- Analyzing Weekly Sales
Let's put all these techniques into action. You've been asked to analyze weekly sales performance for a grocery chain. The raw data arrives in wide format from a CSV file:

``` 
raw = pd.DataFrame({
    'Store': ['North', 'South', 'East', 'West'],
    'Week_1': [300, 250, 400, 375],
    'Week_2': [310, 245, 390, 380],
    'Week_3': [305, 260, 395, 370]
})
```

This format makes comparisons difficult. You can't group by week or easily calculate trends. So we start by reshaping.

#### Step 1: Reshape from Wide to Long
``` 
long = pd.melt(
    raw,
    id_vars='Store',
    var_name='Week',
    value_name='Sales'
)
long['Week'] = long['Week'].str.replace('Week_', '').astype(int)
```

Now the data is tidy:


#### Step 2: Summarize Performance
Let's compute each store's average and total sales:

``` 
summary = long.groupby('Store')['Sales'].agg(
    avg='mean',
    total='sum'
).reset_index()
```

Now we can see store performance over time, not just in a snapshot.

#### Step 3: Compare Trends by Week
What if we want to look at how total company sales change week by week?

``` 
weekly = long.groupby('Week')['Sales'].sum().reset_index()
```

You can plot this with Matplotlib:

```python
import matplotlib.pyplot as plt


plt.plot(weekly['Week'], weekly['Sales'], marker='o')
plt.xlabel('Week')
plt.ylabel('Total Sales')
plt.title('Company Sales Trend by Week')
plt.savefig('weekly_sales.png')
plt.show()
```

This shows whether sales are growing, falling, or staying flat over time.

#### Step 4: Pivot to Compare Stores
Want to compare weekly performance side-by-side?

``` 
pivot = long.pivot(index='Week', columns='Store', values='Sales').reset_index()
```

You can now plot lines for each store:

``` 
for store in pivot.columns[1:]:
    plt.plot(pivot['Week'], pivot[store], label=store)


plt.xlabel('Week')
plt.ylabel('Sales')
plt.title('Store-wise Weekly Sales')
plt.legend()
plt.savefig('store_weekly_sales.png')
plt.show()
```

Now you have a clear visual comparison of how each location performed, week after week.

You took wide data, reshaped it, summarized it, and pivoted it back into useful forms for analysis and plotting. That's the full tidy data cycle in action.

### Wrapping up
Working with tidy data is about discipline. It's about shaping your data so that each variable has its own column, each observation its own row, and each table its own unit of analysis. This might sound simple, but in real business environments, it almost never starts that way.

You learned how to distinguish between long and wide formats. Wide is easy to read but hard to analyze. Long is harder for humans but perfect for code. The real skill is being able to switch back and forth using `pandas` functions like `melt()`, `pivot()`, and `pivot_table()`.

Once your data is tidy, it becomes dramatically easier to group, summarize, and visualize. Using `groupby()` with `agg()` lets you extract trends, rank performance, and build KPIs from raw tables. When combined with reshaping, grouping is one of the most powerful tools in business analytics.

Here are a few rules of thumb to keep in mind:

- Use wide format for reporting and dashboards where space is limited and the audience is human.
- Use long format when you want to model, visualize, or join data with other tables.
- Always reset your index after a groupby if you plan to use the results in other operations or plots.
- Use `pivot_table()` instead of `pivot()` when there's any risk of duplicate combinations in your keys.

Tidy data isn't just about making your job easier. It's about making your work reusable, scalable, and trustworthy. The time you spend reshaping and organizing your data pays off in every line of code that follows.
