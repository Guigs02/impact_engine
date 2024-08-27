from data_processor import DataProcessor
from plot_strategy import PlotStrategy, BarPlot, BubblePlot, ScatterPlot
from pandas import DataFrame
import pandas as pd
from utils import extract_matching_string, replace_latex_symbols

class DataOutput:
    def __init__(self, data_processor: DataProcessor, plot_strategy: PlotStrategy):
        self.data_processor = data_processor
        self.plot_strategy = plot_strategy
    
    def find_period_start_column(self, df: DataFrame) -> int:
        """
        Automatically find the start index of period columns in the DataFrame.

        Args:
            df (DataFrame): The DataFrame with paper details and periods.

        Returns:
            int: The index where period columns start.
        """
        # Set of known non-period columns
        non_period_columns = {'recid', 'preprint_date','title','recid_url'}

        # Find the first column that is not in the set of non-period columns
        for idx, column in enumerate(df.columns):
            if column not in non_period_columns:
                return idx

        # If all columns are non-period columns, return the length of the columns (no period columns)
        return len(df.columns)
    
    def process_and_plot(self, csv_path: str, *args, **kwargs) -> None:
        df = self.data_processor.load_csv(csv_path)
        df = self.data_processor.filter_columns(df, kwargs.get("columns_to_drop", []))
        # Determine the starting index of period columns dynamically
        period_start_col = self.find_period_start_column(df)

        if isinstance(self.plot_strategy, BubblePlot):
            periods = df.columns[period_start_col:].tolist()
            df = self.data_processor.calculate_period_diff(df, periods)
        elif isinstance(self.plot_strategy, ScatterPlot):
            periods = df.columns[period_start_col:].tolist()
        else:
            df['title'] = df['title'].apply(lambda x: replace_latex_symbols(x) if isinstance(x, str) else x)
        self.plot_strategy.plot(df, *args, **kwargs)
        
if __name__ == "__main__":
    
    data_processor = DataProcessor()

    # Bar Plot Example
    csv_file = "top200_2024-07_2024-08.csv"
    title_date = extract_matching_string(csv_file, r"\d{4}-\d{2}_\d{4}-\d{2}")
    title_date = title_date.replace('_', ' to ')
    bar_plot_strategy = BarPlot(f"Top {title_date}")
    data_output_bar = DataOutput(data_processor, bar_plot_strategy)
    data_output_bar.process_and_plot(csv_file, x_column='title', y_column='citation_count', n=10)

    # Bubble Plot Example
    bubble_plot_strategy = BubblePlot()
    data_output_bubble = DataOutput(data_processor, bubble_plot_strategy)
    data_output_bubble.process_and_plot("final_output.csv")

    # Scatter Plot
    scatter_plot_strategy = ScatterPlot()
    data_output_scatter = DataOutput(data_processor, scatter_plot_strategy)

     # Choose whether to process one timeframe or the entire series of timeframes
    process_single_timeframe_only = False  # Change to True to process only one timeframe
    
    if process_single_timeframe_only:
        data_output_scatter.process_and_plot("out_cit_evo.csv")
    else:
        data_output_scatter.process_and_plot("final_output.csv")
