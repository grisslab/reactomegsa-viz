# ReactomeGSA-Viz

[![Python Version >= 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**ReactomeGSA-Viz** is a specialized Python tool designed to transform raw JSON results from the [ReactomeGSA](https://reactome.org/gsa) service into professional, interactive HTML reports. 

This package simplifies the interpretation of Gene Set Analysis (GSA) by providing clear summaries for individual datasets and powerful comparative visualizations across multiple datasets.

## Key Features

- **Automated Summaries:** Generates concise overview reports for every dataset analyzed.
- **Comparative Analysis:** Built-in logic to compare enrichment results across different experimental conditions or datasets.
- **Interactive Bubble Plots:** Visualizes pathway enrichment (p-values, fold changes, and pathway size) using interactive charts.
- **Detailed Data Tables:** Searchable and sortable tables for deep dives into specific pathway results.
- **Self-Contained:** All assets are embedded directly into a single HTML file for easy sharing.

## Requirements

The package requires **Python 3.6 or higher**. 

## Installation

Install the package via pip:

```bash
pip install reactomegsa-viz
```

## Usage

Integrate the report generator into your own pipelines:
```python
import json
import gzip
from reactomegsa_viz import HtmlReportGenerator

# 1. Load your ReactomeGSA results
with gzip.open("tests/results.json.gz", "rt") as f:
    data = json.load(f)

# 2. Generate the interactive report
HtmlReportGenerator.create_report(
    json_dict=data, 
    out_html="test_package.html", 
    r_script_token="R_SCRIPT_TOKEN"
)
```