# Kasparro Agentic Facebook Analyst

Multi-agent system for autonomous Facebook Ads performance analysis and creative recommendations.

## Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

bash
# Create virtual environment
python -m venv mykasparro                      # Environment name i name it mykasparro

# Activate virtual environment
mykasparro\Scripts\activate                    # In windows system

# Install dependencies
pip install -r requirements.txt

### Setup Data

Place your CSV file:
bash
mkdir -p data
cp synthetic_fb_ads_undergarments.csv data/


### Run Analysis

python run.py

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


## Configuration

Edit `config.yaml` to customize:

yaml

put thresholds:
  low_ctr: 0.014        # CTR threshold for underperformance
  
  low_roas: 2.5         # ROAS threshold
  
  fatigue_days: 14      # Days to detect audience fatigue
  
agents:

  hypothesis_count: 5           # Max hypotheses to generate
  
  top_creative_samples: 10      # Top recommendations to show


## Running Tests

bash

python test_evaluator.py
