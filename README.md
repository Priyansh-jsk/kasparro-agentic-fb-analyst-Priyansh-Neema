# Kasparro Agentic Facebook Analyst

Multi-agent system for autonomous Facebook Ads performance analysis and creative recommendations.

## Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

# Create virtual environment:

_python -m venv mykasparro_                      # Create virtual Environment, give any name I have given mykasparro

# Activate virtual environment:

_mykasparro\Scripts\activate_                    # In windows system

# Install dependencies:

_pip install -r requirements.txt_

## Configuration

python_version: "3.10"

random_seed: 42

confidence_min: 0.6

use_sample_data: false

**Edit `config.yaml` to customize:**

put thresholds:
  low_ctr: 0.014        # CTR threshold for underperformance
  
  low_roas: 2.5         # ROAS threshold
  
  fatigue_days: 14      # Days to detect audience fatigue
  
agents:

  hypothesis_count: 5           # Max hypotheses to generate
  
  top_creative_samples: 10      # Top recommendations to show

## Project Structure

├── data/
│   └── synthetic_fb_ads_undergarments.csv
├── reports/
│   ├── report.md         
│   ├── insights.json
│   └── creatives.json
├── logs/
│   └── analysis_log.json
├── config.yaml
├── requirements.txt
├── run.py
├── planner.py
├── data_agent.py
├── insight_agent.py
├── evaluator.py
├── creative_generator.py
└── test_evaluator.py

<img width="379" height="657" alt="Screenshot (23)" src="https://github.com/user-attachments/assets/c627fc92-7480-48fd-87c9-39b6ba4fabab" />


### Run Analysis

_python run.py_

## Outputs
- reports/report.md
- reports/insights.json
- reports/creatives.json

## Logs
- JSON logs logs\analysis_log.json

## Running Tests

_python test_evaluator.py_
