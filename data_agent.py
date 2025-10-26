import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yaml
import json

class DataAgent:
    def __init__(self, config_path="config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        self.df = None
        self.summary = {}
        
    def load_data(self):
        """Load the Facebook Ads dataset"""
        csv_path = self.config['data']['csv_path']
        print(f"Loading data from {csv_path}...")
        self.df = pd.read_csv(csv_path)
        self.df['date'] = pd.to_datetime(self.df['date'])
        print(f"Loaded {len(self.df)} rows, {len(self.df.columns)} columns")
        return self.df
    
    def get_basic_summary(self):
        """Generate basic statistical summary"""
        if self.df is None:
            self.load_data()
            
        summary = {
            "total_rows": len(self.df),
            "date_range": {
                "start": self.df['date'].min().strftime('%Y-%m-%d'),
                "end": self.df['date'].max().strftime('%Y-%m-%d'),
                "days": (self.df['date'].max() - self.df['date'].min()).days
            },
            "metrics": {
                "total_spend": float(self.df['spend'].sum()),
                "total_revenue": float(self.df['revenue'].sum()),
                "total_impressions": int(self.df['impressions'].sum()),
                "total_clicks": int(self.df['clicks'].sum()),
                "avg_ctr": float(self.df['ctr'].mean()),
                "avg_roas": float(self.df['roas'].mean()),
                "median_roas": float(self.df['roas'].median())
            },
            "campaigns": {
                "unique_campaigns": self.df['campaign_name'].nunique(),
                "unique_adsets": self.df['adset_name'].nunique(),
            },
            "dimensions": {
                "platforms": self.df['platform'].unique().tolist(),
                "countries": self.df['country'].unique().tolist(),
                "creative_types": self.df['creative_type'].unique().tolist(),
                "audience_types": self.df['audience_type'].unique().tolist()
            }
        }
        
        self.summary = summary
        return summary
    
    def get_time_series_data(self, metric='roas', groupby='date'):
        """Get time series aggregation"""
        if self.df is None:
            self.load_data()
            
        ts_data = self.df.groupby(groupby).agg({
            'spend': 'sum',
            'revenue': 'sum',
            'impressions': 'sum',
            'clicks': 'sum',
            'ctr': 'mean',
            'roas': 'mean',
            'purchases': 'sum'
        }).reset_index()
        
        return ts_data
    
    def segment_by_performance(self):
        """Segment ads by performance levels"""
        if self.df is None:
            self.load_data()
        
        low_ctr_threshold = self.config['thresholds']['low_ctr']
        low_roas_threshold = self.config['thresholds']['low_roas']
        
        segments = {
            "low_ctr_ads": self.df[self.df['ctr'] < low_ctr_threshold].copy(),
            "high_ctr_ads": self.df[self.df['ctr'] >= low_ctr_threshold].copy(),
            "low_roas_ads": self.df[self.df['roas'] < low_roas_threshold].copy(),
            "high_roas_ads": self.df[self.df['roas'] >= low_roas_threshold].copy()
        }
        
        return segments
    
    def analyze_creative_performance(self):
        """Analyze performance by creative type and message"""
        if self.df is None:
            self.load_data()
            
        creative_stats = self.df.groupby('creative_type').agg({
            'ctr': 'mean',
            'roas': 'mean',
            'spend': 'sum',
            'revenue': 'sum',
            'clicks': 'sum'
        }).reset_index()
        
        creative_stats['roi'] = (creative_stats['revenue'] / creative_stats['spend']) - 1
        creative_stats = creative_stats.sort_values('roas', ascending=False)
        
        return creative_stats
    
    def detect_time_decay(self, window_days=7):
        """Detect performance decay over time"""
        if self.df is None:
            self.load_data()
            
        df_sorted = self.df.sort_values('date')
        
        df_sorted['roas_rolling'] = df_sorted.groupby('campaign_name')['roas'].transform(
            lambda x: x.rolling(window=window_days, min_periods=1).mean()
        )
        
        decay_analysis = df_sorted.groupby('campaign_name').agg({
            'roas': ['first', 'last', 'mean'],
            'date': ['min', 'max']
        }).reset_index()
        
        decay_analysis.columns = ['campaign_name', 'roas_first', 'roas_last', 'roas_mean', 'date_start', 'date_end']
        decay_analysis['roas_change_pct'] = ((decay_analysis['roas_last'] - decay_analysis['roas_first']) / 
                                              decay_analysis['roas_first'] * 100)
        
        return decay_analysis
    
    def get_platform_comparison(self):
        """Compare performance across platforms"""
        if self.df is None:
            self.load_data()
            
        platform_stats = self.df.groupby('platform').agg({
            'spend': 'sum',
            'revenue': 'sum',
            'ctr': 'mean',
            'roas': 'mean',
            'impressions': 'sum',
            'clicks': 'sum'
        }).reset_index()
        
        return platform_stats

if __name__ == "__main__":
    agent = DataAgent()
    agent.load_data()
    summary = agent.get_basic_summary()
    print("\nData Summary:")
    print(json.dumps(summary, indent=2))
