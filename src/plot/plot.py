import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import numpy as np
from data.manager import *
from utils import *
from adjustText import adjust_text

import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import numpy as np
from data.manager import *
from utils import *
from adjustText import adjust_text

def scatter_countries(ax, x, y, codes, x_label=None, y_label=None, title=None, save=None, riskfree=None):
    # Perform OLS regression
    X = sm.add_constant(x)
    model = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 4})
    # model = sm.OLS(y, X).fit()
    y_pred = model.predict(X)
    
    
    # Save regression summary to text file
    if save is not None:
        with open(f"./output/{save}.txt", "w") as f:
            f.write(model.summary().as_text())

    # Plot data
    ax.scatter(x, y, color='blue', s=10, label="Countries")

    # Add data labels
    texts = []
    for i, code in enumerate(codes):
        text = ax.text(x.iloc[i], y.iloc[i], code, fontsize=8)
        texts.append(text)
    adjust_text(texts, ax=ax, force_text=2, arrowprops=dict(arrowstyle="-", color='blue'))

    # Plot regression line
    x_max = x.max()
    y_max = y_pred.iloc[x.argmax()]
    ax.plot([0, x_max], [model.params["const"], y_max], color='red', linewidth=2, linestyle="dotted", label='Regression line')

    if riskfree is not None:
        ax.plot([0, x_max], [riskfree, riskfree + 3 * x_max], color='green', linewidth=2, linestyle="dashed", label='RRA = 3')
        ax.set_ylim(top=y.max() * 1.05)

    ax.set_xlim(left=0)
    ax.legend()
    if x_label is not None:
        ax.set_xlabel(x_label)
    if y_label is not None:
        ax.set_ylabel(y_label)  
    if title is not None:
        ax.set_title(title)

    # if save is not None:
    #     plt.savefig(f"./output/figures/{save}")

    return ax


def plot_returns(ds, fed, period, code, log):

    country = DS.CODE_TO_COUNTRY[code]
    start, end = period
    prices = ds.loc[[code], (ds.columns >= pd.Timestamp(f"{start-1}-12-01")) & (ds.columns <= pd.Timestamp(f"{end+1}-01-01"))].T
    returns = prices.pct_change(axis=0).iloc[1:,:]

    fed_reindexed = fed.reindex(columns=returns.index)
    fed_monthly = annual_to_monthly_return(fed_reindexed)
    riskfree_rate = fed_monthly.loc["FEDFUNDS"]
    
    if not log:
        excess_returns = returns.subtract(riskfree_rate, axis=0)
    else:
        log_returns = np.log(1 + returns)
        log_risk_free = np.log(1 + riskfree_rate)
        log_excess_returns = log_returns.subtract(log_risk_free, axis=0)
        excess_returns = log_excess_returns

    ax = excess_returns.plot(kind="bar", legend=False)
    datetime_index = pd.to_datetime(excess_returns.index)
    ax.set_xticklabels([dt.strftime('%b %Y') for dt in datetime_index])
    ax.xaxis.set_major_locator(plt.MaxNLocator(8))
    plt.title(f"Monthly excess return (USD), {country}, {start}-{end}")
    plt.xlabel("Month")
    plt.ylabel("Excess return")
    text_x = 0.7 * len(excess_returns)  # X position (75% of the way across the graph)
    text_y = 0.9 * excess_returns.values.min()   # Y position (90% of the maximum value)
    mean_val, var_val = (excess_returns.mean().iloc[0], excess_returns.var().iloc[0])
    plt.text(text_x, text_y, 
            f'Mean: {mean_val:.4f}\nVariance: {var_val:.4f}',
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'),
            fontsize=12)

    # Add a horizontal line for the mean
    mean_line = ax.axhline(y=mean_val, color='red', linestyle='--', alpha=0.7, label=f'Mean')
    ax.legend([mean_line], ['Mean'])

    # Show the plot
    plt.tight_layout()
    plt.show()