import argparse
from datetime import datetime
import pandas as pd
from data_processor import DataProcessor
from data_output import DataOutput
from plot_strategy import BarPlot, BubblePlot, ScatterPlot
from utils import extract_recid_from_url
from api_interaction import get_period_for_date, process_single_timeframe, process_timeframe_series, get_paper_details, add_paper_details

def create_parser():
    parser = argparse.ArgumentParser(description="Citation Analysis and Plotting Tool")
    
    parser.add_argument("--start-date", type=str, default="2020-04-01", help="Start date for data collection (format: YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, default=datetime.now().strftime('%Y-%m-%d'), help="End date for data collection (format: YYYY-MM-DD)")
    parser.add_argument("--step-back", type=int, default=2, help="Step back in months for the timeframe")
    parser.add_argument("--process-single-timeframe", action='store_true', help="Process only a single timeframe instead of the entire series")
    parser.add_argument("--generate-csvs", action='store_true', help="Generate CSV files for each timeframe")
    parser.add_argument("--timeframe-plot-type", choices=["bar", "none"], default="none", help="Type of plot to generate for each timeframe's CSV (only bar plot is allowed)")
    parser.add_argument("--final-plot-type", choices=["bubble", "scatter", "none"], default="scatter", help="Type of plot to generate for the final combined data")
    parser.add_argument("--output-file", type=str, default="final_output.csv", help="Name of the final output CSV file")
    
    return parser
