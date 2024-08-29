import argparse
from datetime import datetime
import pandas as pd
import os
from beaupy.spinners import *
from data_processor import DataProcessor
from data_output import DataOutput
from plot_strategy import BarPlot, BubblePlot, ScatterPlot
from utils import extract_recid_from_url, obj_to_str, str_to_obj, extract_matching_string
from api_interaction import *

def create_parser():
    parser = argparse.ArgumentParser(description="Citation Analysis and Plotting Tool")
    
    parser.add_argument("--start-date", type=str, default="2020-04-01", help="Start date for data collection (format: YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, default=datetime.now().strftime('%Y-%m-%d'), help="End date for data collection (format: YYYY-MM-DD)")
    parser.add_argument("--step-back", type=int, default=2, help="Step back in months for the timeframe")
    parser.add_argument("--process-single-timeframe", action='store_true', help="Process only a single timeframe instead of the entire series")
    parser.add_argument("--generate-csvs", action='store_true', help="Generate CSV files for each timeframe")
    parser.add_argument("--timeframe-plot", choices=["bar", "none"], default="none", help="Type of plot to generate for each timeframe's CSV (only bar plot is allowed)")
    parser.add_argument("--final-plot", choices=["bubble", "scatter", "none"], default="scatter", help="Type of plot to generate for the final combined data")
    parser.add_argument("--output-file", type=str, default="final_output.csv", help="Name of the final output CSV file")
    parser.add_argument("--plot-csv", type=str, help="Specify a CSV file to plot instead of generating a new one")
    parser.add_argument("--recid", type=str, help="Specify the recid of the paper to find citing papers")
    parser.add_argument("--save-citing-papers", type=str, help="Filename to save citing papers CSV")

    
    return parser

def main(args):
    api_fields = 'recid,preprint_date,titles.title'

    if args.recid:
        citing_papers = get_citing_papers(f"refersto:recid:{args.recid}", api_fields)
        # Convert to DataFrame
        df_citing = pd.DataFrame(citing_papers)
        print(df_citing.head(10))

        if args.save_citing_papers:
            df_citing.to_csv(args.save_citing_papers, index = False)
        return

    
    # If a specific CSV file is provided for plotting, validate its existence
    if args.plot_csv:
        if not os.path.isfile(args.plot_csv):
            print(f"Error: The file '{args.plot_csv}' does not exist. Please provide a valid CSV file.")
            return  # Exit the program gracefully
        
        print(f"Plotting the specified CSV file: {args.plot_csv}")

        data_processor = DataProcessor()
        if args.timeframe_plot== "bar":
            title_date = extract_matching_string(args.plot_csv, r"\d{4}-\d{2}_\d{4}-\d{2}")
            title_date = title_date.replace('_', ' to ')
            plot_strategy = BarPlot(f"Top {title_date}")
            
            data_output = DataOutput(data_processor, plot_strategy)
            data_output.process_and_plot(args.plot_csv, x_column='title', y_column='citation_count', n=10)
        else:
            if args.final_plot == "bubble":
                plot_strategy = BubblePlot()
            else:
                plot_strategy = ScatterPlot()
            data_output = DataOutput(data_processor, plot_strategy)
            data_output.process_and_plot(args.plot_csv)
        
        return  # Exit after plotting the specified CSV file
    
    # If no CSV file is provided, proceed with data processing and plotting
    api_fields = 'titles.title,recid,citation_count,references.record'
    details_fields = 'preprint_date,titles.title'

    start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
    end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
    step_back = args.step_back

    start_period_start, start_period_end = get_period_for_date(end_date, step=step_back)
    start_date_str = obj_to_str(start_period_start)
    end_date_str = obj_to_str(start_period_end)

    spinner = Spinner(DOTS, '[green]Fetching data...[/green]')
    spinner.start()
    
    if args.process_single_timeframe:
        df = process_single_timeframe(api_fields, start_date_str, end_date_str, args.generate_csvs)
    else:
        df = process_timeframe_series(api_fields, start_date, end_date, args.generate_csvs, step=step_back)
    spinner.stop()

    if args.generate_csvs:
        print(f"CSV for the period {start_date_str} to {end_date_str} generated.")
        if args.timeframe_plot == "bar":
            bar_plot_strategy = BarPlot(f"Top {start_date_str} to {end_date_str}")
            data_processor = DataProcessor()
            data_output = DataOutput(data_processor, bar_plot_strategy)
            data_output.process_and_plot(f"top200_{start_date_str}_{end_date_str}.csv", x_column='title', y_column='citation_count', n=10)
        
    # Fetch and include paper details for the first 20 records
    spinner = Spinner(DOTS, '[green]Getting additional information[/green]...')
    spinner.start()
    recid_urls = df['recid_url'].head(20).tolist()
    recids = [extract_recid_from_url(url) for url in recid_urls]
    details_df = get_paper_details(recids, details_fields)
    df = add_paper_details(df, details_df)

    # Save the final DataFrame
    df.to_csv(args.output_file, index=False)
    spinner.stop()
    # Final plot for the combined data (Bubble or Scatter)
    data_processor = DataProcessor()
    
    if args.final_plot == "bubble":
        plot_strategy = BubblePlot()
    else:
        plot_strategy = ScatterPlot()
    
    data_output = DataOutput(data_processor, plot_strategy)
    data_output.process_and_plot(args.output_file)

if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    main(args)
    
