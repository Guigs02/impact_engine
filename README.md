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
- [Contributing](#contributing)
- [License](#license)

## Introduction

The Citation Analysis and Plotting Tool is designed to fetch citation data, generate CSV files, and create visualisations for easy analysis. It supports various plot types and can handle both individual timeframes and series of timeframes. Additionally, users can fetch and display or save papers that cite a specific paper.

## Features

- Generate CSV files for citation data over specific timeframes.
- Create bar plots for top-cited papers within timeframes.
- Create bubble and scatter plots for the combined citation data.
- Fetch and display or save papers that cite a specific paper.
- Flexible command-line interface for customization.

## Usage

### Basic Usage

To generate a CSV file containing the most referenced papers among the most cited papers published within a user-defined time period. It then produces a scatter plot to visualise the evolution of these citations over time.

```bash
python3 cli.py --start-date "2020-04-01" --final-plot-type scatter
```
To generate intermediate CSV files for the most cited papers published within specific timeframes defined by a start and end date. Each CSV file corresponds to a different period within the timeframe series.

```bash
python3 cli.py --start-date "2020-04-01" --end-date "2023-04-01" --generate-csvs
```
## Citing Papers

To find and save to a CSV file papers that cite a specific paper (e.g. recid:123456)
```bash
python3 cli.py --recid "123456" --save-citing-papers "citing_papers.csv"
```

## Plotting options


```bash
python3 cli.py --plot-csv "top200_2024-05_2024-06.csv" --timeframe-plot-type bar
```

