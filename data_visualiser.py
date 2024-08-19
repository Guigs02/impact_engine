import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import pandas as pd
from pandas import DataFrame
from typing import List, Dict, Any, Union, Set
from utils import wrap_labels

class DataVisualiser:
    """ def to_df(self, data_list: List[str])-> DataFrame:
        df = pd.DataFrame(data_list).value_counts()
        print(f'LENGTH: {len(data_list)}')
        # Limit to top 5 categories
        top_n = 30
        limited_df = df.nlargest(top_n).sort_values(ascending=True)
        print(limited_df)
        limited_df.plot.barh()
        plt.title(f'Top {top_n} Citations')

        # Adjust layout to show full y labels
        plt.tight_layout()
        plt.show(block = False)
        return df """
    def __init__(self, df = None):
        self.df: DataFrame = df
    
    def set_df(self, df: DataFrame)-> None:
         self.df = df
    
    def bubble_plot(self, top_n: int = 10) -> None:
            periods = self.df.columns[1:].tolist()
            self.df = self.df.nlargest(top_n, columns=self.df.columns[1])
            diffs = self.calculate_period_diff(self.df, periods)
            plot_data = []
            for i, period in enumerate(periods[:]):
                for j, row in self.df.iterrows():
                    plot_data.append({
                        'DOI': row['DOI'],
                        'Period': period,
                        'Citations': row[period],
                        'Diff': row[diffs[i]]
                    })

            plot_df = pd.DataFrame(plot_data)

            # Generate a color map
            cmap = cm.get_cmap('tab10')  # You can choose any colormap you like
            colours = {doi: cmap(i) for i, doi in enumerate(self.df['DOI'].unique())}

            plt.figure(figsize=(12, 8))

            for doi in plot_df['DOI'].unique():
                subset = plot_df[plot_df['DOI'] == doi]
                plt.scatter(subset['Period'], subset['Citations'], s=subset['Diff']*500, alpha=0.95, label=doi, color=colours[doi])

            plt.gca().invert_xaxis()
            plt.xlabel('Time Periods')
            plt.ylabel('Number of Citations')
            plt.title('Bubble Chart of Citation Differences')
            wrapped_labels = wrap_labels(subset['Period'], 10)
            plt.xticks(rotation=30, ha='right')
            plt.legend()
            plt.tight_layout()
            plt.show()

    def calculate_period_diff(self, df: DataFrame, periods: List)->DataFrame:
        diffs = []
        for i in range(len(periods)):
            #diff_col = f'{periods[i]}vs{periods[i+1]}'
            diff_col = f'{periods[i]} (%)'
            df[diff_col] = (df[periods[i]]) / (df[periods[0]])
            #df[diff_col] = (df[periods[i]] - df[periods[i+1]]) / (df[periods[0]] - df[periods[1]])
            diffs.append(diff_col)
        self.df = df
        print(self.df)
        return diffs
