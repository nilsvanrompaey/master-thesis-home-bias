import os
import shutil
import pandas as pd
import numpy as np
import numpy.linalg as la
from scipy import stats

from .constants import *

def annual_to_monthly_return(data):
    
    data = (data + 1) ** (1 / 12) - 1
    
    return data

def monthly_to_annual_return(data):
    
    data = (data + 1) ** 12 - 1

    return data

def compute_monthly_compounded_excess_return(ds, importer, country="BRAZIL", fed_path="../data/source/FED.xlsx", end_date="2024-10"):
    """
    Computes the monthly compounded excess return for a given country.
    
    Parameters:
    - ds: DataFrame containing country excess returns.
    - importer: Object with an `import_fed` method to import FED data.
    - country: The country to analyze (default: "BRAZIL").
    - fed_path: Path to the FED data file.
    - end_date: The final date for the calculation (default: "2024-10").

    Returns:
    - Monthly compounded excess return as a percentage.
    """

    # Get first valid data point
    first_date = ds.loc[country].first_valid_index()
    res = ds.loc[country, first_date:]

    # Import FED data and compute total inflation
    fed = importer.import_fed(fed_path)
    fed = annual_to_monthly_return(fed)
    tot_inflation = (fed.loc["FEDFUNDS", first_date:end_date] + 1).product()

    # Compute return ratio
    r = res.iloc[-1] / res.iloc[0] / tot_inflation

    # Compute total months
    tot_months = (pd.to_datetime(end_date) - first_date.to_timestamp()).days / 30.4375

    # Compute monthly compounded return
    r_monthly = r ** (1 / tot_months)

    return (r_monthly - 1) * 100
    

def calculate_yearly_returns(ds, start_year=2008):
    """
    Calculate yearly returns from a DataFrame with datetime-indexed columns.

    Parameters:
    - ds (pd.DataFrame): DataFrame where columns represent years (datetime format).
    - start_year (int): The starting year for filtering columns.

    Returns:
    - pd.DataFrame: Yearly return percentages sorted in ascending order.
    """
    # Filter columns to include only those from start_year onwards
    ds = ds.loc[:, ds.columns.year >= start_year]
    
    # Calculate total return
    total_return = ds.iloc[:, -1] / ds.bfill(axis=1).iloc[:, 0]
    
    # Find first and last non-NaN values for each row
    first_non_nan_col = ds.apply(lambda row: row.first_valid_index(), axis=1)
    last_non_nan_col = ds.apply(lambda row: row.last_valid_index(), axis=1)
    
    # Compute the number of years invested
    n_years = (last_non_nan_col - first_non_nan_col).dt.days / 365.24
    
    # Compute yearly return
    yearly_return = total_return ** (1 / n_years)
    
    # Format as percentage and return
    return (yearly_return - 1).sort_values().apply(lambda x: f"{100*x:.2f}%").to_frame()


def calculate_home_bias(cpis, wfe, code):
    """
    Calculate the home bias for a given country.

    Parameters:
    - cpis: Dataset containing investment data.
    - wfe: Dataset containing market capitalization data.
    - code (str): Country code.

    Returns:
    - float: Home bias value.
    """
    country = WFE.CODE_TO_COUNTRY[code]
    
    # Foreign investments into the country
    cpis_to = cpis.get_data(issuers=country, holders="World").sum()
    
    # Domestic investments going abroad
    cpis_from = cpis.get_data(issuers="World", holders=country).sum()
    
    # Total market capitalization of the country
    market_cap = wfe.loc[code, :].sum().squeeze() * 1e6
    
    # Domestic investments (calculated as residual)
    cpis_domestic = market_cap - cpis_to
    
    # Home bias formula
    return cpis_domestic / (cpis_domestic + cpis_from)


def neumann_series(df):
    A = df.to_numpy()
    assert np.linalg.norm(A, ord=2) < 1, "Operator norm greater than 1, series does not converge."
    assert A.shape[0] == A.shape[1], "Matrix is not square."

    I = np.eye(A.shape[0])

    assert np.linalg.det(I - A) != 0, "I - A is singular and thus not invertible."
    S = np.linalg.inv(I - A)

    return pd.DataFrame(S, index=df.index, columns=df.columns)

def create_monthly_duplicates(df, monthly_columns=None, interpolate=False):

    n_years = df.shape[1]-1 if interpolate else df.shape[1] 
    df_monthly = pd.DataFrame(index=df.index)

    for i in range(n_years):
        for j in range(12):
            if interpolate:
                df_monthly[i*12+j] = ( df.iloc[:,i]*(11-j) + df.iloc[:,i+1]*(1+j) ) / 12
            else:
                df_monthly[i*12+j] = df.iloc[:,i]

    df_monthly.columns = monthly_columns if monthly_columns is not None else df_monthly.columns

    return df_monthly


def generate_exponential_decay(initial=1, ratio=0.9, length=60):

    return [initial * (ratio ** i) for i in range(length-1,-1,-1)]

def hausman(fe, re):
    b = fe.params
    B = re.params
    v_b = fe.cov
    v_B = re.cov
    df = b[np.abs(b) < 1e8].size
    chi2 = np.dot((b - B).T, la.inv(v_b - v_B).dot(b - B)) 

    pval = stats.chi2.sf(chi2, df)
    return chi2, df, pval


def copy_files(
        src_dir="C:/Users/nilsv/OneDrive/School/KUL - MME/Home bias/master-thesis-home-bias/output/exp3/results/figures",
        dst_dir="C:/Users/nilsv/OneDrive/School/KUL - MME/Home bias/tex/src/img",
):
    # Ensure destination folder exists
    os.makedirs(dst_dir, exist_ok=True)

    # Recursively walk through source directory
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.lower().endswith(".pdf"):
                src_path = os.path.join(root, file)
                dst_path = os.path.join(dst_dir, file)

                # Handle duplicate filenames by appending a counter
                base, ext = os.path.splitext(file)
                counter = 1
                while os.path.exists(dst_path):
                    dst_path = os.path.join(dst_dir, f"{base}_{counter}{ext}")
                    counter += 1

                shutil.copy2(src_path, dst_path)

    return None