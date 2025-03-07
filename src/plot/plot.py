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

def scatter_countries(x, y, codes, x_label, y_label, title, save=None):
    # Perform OLS regression
    X = sm.add_constant(x)
    y = y
    model = sm.OLS(y, X).fit()
    y_pred = model.predict(X)
    
    # Save regression summary to text file
    summary_text = model.summary().as_text()
    if save is not None:
        with open(f"./output/results/{save}.txt", "w") as f:
            f.write(summary_text)

    # Plot data
    plt.figure()
    plt.scatter(x, y, color='blue', s=10, label="Countries")

    # Add data labels
    texts = []
    for i, code in enumerate(codes):
        text = plt.text(x.iloc[i], y.iloc[i], code, fontsize=6)
        texts.append(text)
    adjust_text(texts, force_text=0.25, arrowprops=dict(arrowstyle="->", color='blue'))

    # Plot regression line and do layout
    x_min, x_max = x.min(), x.max()     
    y_min, y_max = y_pred.iloc[x.argmin()], y_pred.iloc[x.argmax()]
    plt.plot([x_min, x_max], [y_min, y_max], color='red', linewidth=2, label='Regression line')
    plt.legend()
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    if save is not None:
        plt.savefig(f"./output/figures/{save}")