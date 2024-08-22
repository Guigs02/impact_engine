from typing import List, Dict, Any
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import textwrap

class DataOutput:
    def bar_plot(self, csv_path: str, columns: List[str], n: int = 10) -> None: 
        df = pd.read_csv(csv_path).drop(columns=columns)
        limited_df = df.nlargest(n, ['citation_count']).sort_values(by=['citation_count'],ascending=True)
        ax = limited_df.plot.barh(x='title', y='citation_count', legend = False)
        plt.title(f'Top {n} Citations')
        wrapped_labels = [textwrap.fill(title, width=35) for title in limited_df['title']]

        # Adjust layout to show full y labels
        plt.tight_layout()
        plt.subplots_adjust(left=0.4)  # Adjust left margin to make space for labels
        ax.set_yticklabels(wrapped_labels, fontsize=9, ha='right')
        plt.show()
    def bubble_plot(self, csv_path: str, top_n: int = 10, col: int = 2) -> None:
            df = pd.read_csv(csv_path).reset_index(drop = True)
            periods = df.columns[2:].tolist()
            limited_df = df.nlargest(top_n, columns=df.columns[col])
            df_out, diffs = self.calculate_period_diff(limited_df, periods)
            plot_data = []
            for i, period in enumerate(periods[:]):
                for j, row in df_out.iterrows():
                    plot_data.append({
                        'recid': row['recid'],
                        'Period': period,
                        'Citations': row[period],
                        'Diff': row[diffs[i]]
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

    def calculate_period_diff(self, df: DataFrame, periods: List)->tuple[DataFrame, DataFrame]:
        diffs = []
        for i in range(len(periods)):
            #diff_col = f'{periods[i]}vs{periods[i+1]}'
            diff_col = f'{periods[i]} (%)'
            df[diff_col] = (df[periods[i]]) / (df[periods[0]])
            #df[diff_col] = (df[periods[i]] - df[periods[i+1]]) / (df[periods[0]] - df[periods[1]])
            diffs.append(diff_col)
    
        df.to_csv("out.csv", index=False)
        return df, diffs


if __name__ == "__main__":
    graph = DataOutput()
    #graph.bar_plot("top200_2020-05-28_2020-08-26.csv",['control_number'])
    graph.bubble_plot("out_cit_evo.csv")
