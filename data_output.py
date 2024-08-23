from data_processor import DataProcessor
from plot_strategy import PlotStrategy, BarPlot, BubblePlot, ScatterPlot
from pandas import DataFrame
import pandas as pd
from utils import extract_matching_string, replace_latex_symbols

class DataOutput:
    def __init__(self, data_processor: DataProcessor, plot_strategy: PlotStrategy):
        self.data_processor = data_processor
        self.plot_strategy = plot_strategy
    
    def process_and_plot(self, csv_path: str, *args, **kwargs) -> None:
        df = self.data_processor.load_csv(csv_path)
        print(df)
        df = self.data_processor.filter_columns(df, kwargs.get("columns_to_drop", []))

        if isinstance(self.plot_strategy, BubblePlot):
            periods = df.columns[kwargs.get('col'):].tolist()
            df = self.data_processor.calculate_period_diff(df, periods)
        elif isinstance(self.plot_strategy, ScatterPlot):
            periods = df.columns[kwargs.get('col'):].tolist()
        else:
            df['title'] = df['title'].apply(lambda x: replace_latex_symbols(x) if isinstance(x, str) else x)
        self.plot_strategy.plot(df, *args, **kwargs)
        
if __name__ == "__main__":
    data_processor = DataProcessor()

    # Bar Plot Example
    """ csv_file = "top200_2024-07_2024-08.csv"
    title_date = extract_matching_string(csv_file, r"\d{4}-\d{2}_\d{4}-\d{2}")
    title_date = title_date.replace('_', ' to ')
    bar_plot_strategy = BarPlot(f"Top {title_date}")
    data_output_bar = DataOutput(data_processor, bar_plot_strategy)
    data_output_bar.process_and_plot(csv_file, x_column='title', y_column='citation_count', n=10)

    # Bubble Plot Example
    bubble_plot_strategy = BubblePlot()
    data_output_bubble = DataOutput(data_processor, bubble_plot_strategy)
    data_output_bubble.process_and_plot("out_cit_evo.csv", col = 1) """

    # Scatter Plot Example
    scatter_plot_strategy = ScatterPlot()
    data_output_scatter = DataOutput(data_processor, scatter_plot_strategy)
    data_output_scatter.process_and_plot("out_cit_evo.csv", col = 1)
    data_output_scatter.process_and_plot("out_single_timeframe.csv", col = 1)
