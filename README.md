# impact_engine
A command-line tool for analysing the most cited papers in InspireHep, with options to generate CSV files and various plot.  

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Basic Usage](#basic-usage)
  - [Citing Papers](#citing-papers)
  - [Plotting Options](#plotting-options)
- [Arguments](#arguments)
- [License](#license)

## Introduction

The Citation Analysis and Plotting Tool is designed to fetch citation data, generate CSV files, and create visualisations for easy analysis. It supports various plot types and can handle both individual timeframes and series of timeframes. Additionally, users can fetch and display or save papers that cite a specific paper.

## Features

- Generate CSV files for citation data over specific timeframes.
- Create bar plots for top-cited papers within timeframes.
- Create bubble and scatter plots for the combined citation data.
- Fetch and display or save papers that cite a specific paper.
- Flexible command-line interface for customisation.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Guigs02/impact-engine.git
   ```

2. **Navigate to the project directory**:
    ```bash
    cd impact-engine
    ```

3. **Install the required dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Generate a CSV and Scatter Plot

To generate a CSV file containing the most referenced papers among the most cited papers published within a user-defined time period. It then produces a scatter plot to visualise the evolution of these citations over time.

```bash
python3 cli.py --start-date "2020-04-01" --final-plot scatter
```

### Generate intermediate CSV files

To generate intermediate CSV files for the most cited papers published within specific timeframes defined by a start and end date. Each one of these intermediate CSV files corresponds to a different period within the timeframe series:

```bash
python3 cli.py --start-date "2020-04-01" --end-date "2023-04-01" --generate-csvs
```
### Analyse a single timeframe

One can also choose to analyse a single timeframe. The following command would produce a bar plot for the last timeframe within the start and end date range. Afterwards, a scatter plot with the most cited references would be produced.

```bash
python3 cli.py --start-date "2020-04-01" --end-date "2020-06-01" --step-back 2 --process-single-timeframe --generate-csvs --timeframe-plot bar 
```

### Citing Papers

To find and save to a CSV file papers that cite a specific paper (e.g. recid:123456):
```bash
python3 cli.py --recid "123456" --save-citing-papers "citing_papers.csv"
```

### Plotting options

To plot data from an existing CSV file by selecting the appropriate plot type — bar plots for top-cited papers within timeframes, and bubble or scatter plots for combined citation data:

```bash
python3 cli.py --plot-csv "top200_2024-05_2024-06.csv" --timeframe-plot bar
```

## Arguments

- --start-date: Start date for data collection (format: YYYY-MM-DD).
- --end-date: End date for data collection (format: YYYY-MM-DD). Default: current date.
- --step-back: Step back in months for the timeframe. Default: Two months
- --process-single-timeframe: Process only a single timeframe.
- --generate-csvs: Generate CSV files for each timeframe.
- --timeframe-plot: Type of plot to generate for each timeframe's CSV (options: bar, none). Default: none.
- --final-plot: Type of plot to generate for the final combined data (options: bubble, scatter, none). Default: scatter.
- --output-file: Name of the final output CSV file. Default: "final_output.csv".
- --plot-csv: Specify a CSV file to plot instead of generating a new one.
- --recid: Specify the recid of the paper to find citing papers.
- --save-citing-papers: Filename to save citing papers CSV.

## License

Distributed under the MIT License.

