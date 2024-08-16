import matplotlib.pyplot as plt
import pandas as pd
from pandas import DataFrame
from typing import List, Dict, Any, Union, Set

class DataVisualiser:
    def to_df(self, data_list: List[str])-> DataFrame:
        df = pd.DataFrame(data_list).value_counts()
        print(f'LENGTH: {len(data_list)}')
        # Limit to top 5 categories
        top_n = 15
        limited_df = df.nlargest(top_n).sort_values(ascending=True)
        print(limited_df)
        limited_df.plot.barh()
        plt.title(f'Top {top_n} Citations')

        # Adjust layout to show full y labels
        plt.tight_layout()
        plt.show(block = False)
        return df
