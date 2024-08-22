from typing import List, Dict, Any
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import textwrap

class DataProcessor:
    def load_csv(self, csv_path: str)-> DataFrame:
        """Load CSV file into DataFrame."""
        return pd.read_csv(csv_path)
    
    def filter_columns(self, df: DataFrame, columns_to_drop: List[str])-> DataFrame:
        """Drop specified columns from DataFrame."""
        return df.drop(columns=columns_to_drop)
    
    def nlargest_sorted(self, df: DataFrame, n: int, sort_column: str)->DataFrame:
        """Get n largest values in DataFrame sorted by specified column."""
        return df.nlargest(n, [sort_column]).sort_values(by=[sort_column], ascending=True)
    
    def calculate_period_diff(self, df: DataFrame, periods: List)->tuple[DataFrame, DataFrame]:
        """Calculate percentage difference between periods."""
        diffs = []
        for i in range(len(periods)):
            #diff_col = f'{periods[i]}vs{periods[i+1]}'
            diff_col = f'{periods[i]} (%)'
            df[diff_col] = (df[periods[i]]) / (df[periods[0]])
            #df[diff_col] = (df[periods[i]] - df[periods[i+1]]) / (df[periods[0]] - df[periods[1]])
            diffs.append(diff_col)
        df.to_csv("out.csv", index=False)
        return df