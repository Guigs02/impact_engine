from data_processor import DataProcessor
from plot_strategy import PlotStrategy, BarPlot, BubblePlot
from pandas import DataFrame
import pandas as pd

class DataOutput:
    def __init__(self, data_processor: DataProcessor, plot_strategy: PlotStrategy):
        self.data_processor = data_processor
        self.plot_strategy = plot_strategy
    
    def process_and_plot(self, csv_path: str, *args, **kwargs) -> None:
        df = self.data_processor.load_csv(csv_path)
        df = self.data_processor.filter_columns(df, kwargs.get("columns_to_drop", []))

        if isinstance(self.plot_strategy, BubblePlot):
            periods = df.columns[kwargs.get('col'):].tolist()
            df = self.data_processor.calculate_period_diff(df, periods)
        self.plot_strategy.plot(df, *args, **kwargs)
        
if __name__ == "__main__":
    data_processor = DataProcessor()

    # Bar Plot Example
    bar_plot_strategy = BarPlot()
    data_output_bar = DataOutput(data_processor, bar_plot_strategy)
    data_output_bar.process_and_plot("../top200_2020-05-28_2020-08-26.csv", x_column='title', y_column='citation_count', n=10)

    # Bubble Plot Example
    bubble_plot_strategy = BubblePlot()
    data_output_bubble = DataOutput(data_processor, bubble_plot_strategy)
    data_output_bubble.process_and_plot("../out_cit_evo.csv", col = 1)
