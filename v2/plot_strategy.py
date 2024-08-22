import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
import textwrap
from typing import List, Dict
import matplotlib.cm as cm

class PlotStrategy:
    def plot(self, df: DataFrame) -> None:
        raise NotImplementedError("Subclasses should implement this method")
    
class BarPlot(PlotStrategy):
    def plot(self, df: DataFrame, x_column: str, y_column: str, n: int = 10) -> None:
        limited_df = df.nlargest(n, [y_column]).sort_values(by=[y_column],ascending=True)
        ax = limited_df.plot.barh(x=x_column, y=y_column, legend = False)
        plt.title(f'Top {n} Citations')
        wrapped_labels = [textwrap.fill(title, width=35) for title in limited_df['title']]

        # Adjust layout to show full y labels
        plt.tight_layout()
        plt.subplots_adjust(left=0.4)  # Adjust left margin to make space for labels
        ax.set_yticklabels(wrapped_labels, fontsize=9, ha='right')
        plt.show()

class BubblePlot(PlotStrategy):
    def plot(self, df: DataFrame, col: int = 1, n: int = 10) -> None:
        cols_period: List = []
        cols_diff: List = []
        date_cols = df.columns[col:].tolist()
        character = '%'
        for c in date_cols:
            if character in c:
                cols_diff.append(c)
            else:
                cols_period.append(c)
        limited_df = df.nlargest(n, columns=df.columns[col])
        plot_data = []
        for i, period in enumerate(cols_period[:]):
            for j, row in limited_df.iterrows():
                plot_data.append({
                    'recid': row['recid'],
                    'Period': period,
                    'Citations': row[period],
                    'Diff': row[cols_diff[i]]
                })

        plot_df = pd.DataFrame(plot_data)

        # Generate a color map
        cmap = cm.get_cmap('tab10')  # You can choose any colormap you like
        colours = {recid: cmap(i) for i, recid in enumerate(limited_df['recid'].unique())}

        plt.figure(figsize=(12, 8))

        for recid in plot_df['recid'].unique():
            subset = plot_df[plot_df['recid'] == recid]
            plt.scatter(subset['Period'], subset['Citations'], s=subset['Diff']*500, alpha=0.95, label=recid, color=colours[recid])

        plt.gca().invert_xaxis()
        plt.xlabel('Time Periods')
        plt.ylabel('Number of Citations')
        plt.title('Bubble Chart of Citation Differences')
        plt.xticks(rotation=30, ha='right')
        plt.legend()
        plt.tight_layout()
        plt.show()