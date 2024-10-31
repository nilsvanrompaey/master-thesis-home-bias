import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm

def convert_annual_to_monthly_return(annual_rate):
    monthly_rate = (annual_rate/100 + 1)**(1/12) - 1

    return monthly_rate


if (not "returns_data" in vars()) or (not "riskfree_data" in vars()):
    returns_data = pd.read_excel("data/Datastream.xlsx", 0)
    riskfree_data = pd.read_excel("data/FedFundRate.xlsx", 0)

# Read the data
returns = returns_data
# Extract country names and data
countries = returns.iloc[:,0]
returns = returns.iloc[:,1:].T
# Clean up country names
countries = countries.str.split('-').str[0].to_list()
returns.columns = countries
returns.drop("VIETNAM", axis=1, inplace=True)
returns.drop("VENEZUELA", axis=1, inplace=True)
# Read the row headers as dates
returns.index = pd.to_datetime(returns.index)
# Keep only the last day of each month
returns = returns.loc[returns.index.to_series().groupby(returns.index.to_series().dt.to_period("M")).last()]
returns.index = returns.index.to_period("M")


# Clean fed interest rate
riskfree = riskfree_data
riskfree["DATE"] = pd.to_datetime(riskfree["DATE"])
riskfree = riskfree.set_index("DATE")
riskfree.index = riskfree.index.to_period("M")
riskfree = riskfree.reindex(returns.index)
riskfree["FEDFUNDS"] = convert_annual_to_monthly_return(riskfree["FEDFUNDS"])
print(riskfree)

monthly_returns = returns.ffill().pct_change(fill_method=None)
monthly_excess_returns = monthly_returns.subtract(riskfree["FEDFUNDS"], axis=0)
monthly_excess_returns_pct = monthly_excess_returns*100

mean_monthly_excess_return = monthly_excess_returns.mean()
var_monthly_excess_return = monthly_excess_returns.var()

x = var_monthly_excess_return
y = mean_monthly_excess_return
x = sm.add_constant(x)
model = sm.OLS(y, x).fit()
y_pred = model.predict(x)
print(model.summary())

plt.scatter(var_monthly_excess_return, mean_monthly_excess_return, color='blue', s=10, label="Countries")
y_min = y_pred.min()
x_min = var_monthly_excess_return.loc[y_pred.idxmin()]
y_max = y_pred.max()
x_max = var_monthly_excess_return.loc[y_pred.idxmax()]
plt.plot([x_min, x_max], [y_min, y_max], color='red', linewidth=2, label='Regression line')
plt.legend()
plt.xlabel("Variance of monthly return")
plt.ylabel("Mean monthly return")
plt.title("Mean and variance of monthly excess returns in USD")
plt.show()