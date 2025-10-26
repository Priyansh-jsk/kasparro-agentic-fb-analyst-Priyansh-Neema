import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class InsightAgent:
    def __init__(self, data_agent):
        self.data_agent = data_agent
        self.hypotheses = []
        
    def generate_hypotheses(self):
        """Generate data-driven hypotheses about performance"""
        print("\nGenerating hypotheses...")
        
        hypotheses = []
        
        # Hypothesis 1: Time-based decay
        decay_data = self.data_agent.detect_time_decay()
        declining_campaigns = decay_data[decay_data['roas_change_pct'] < -20]
        
        if len(declining_campaigns) > 0:
            hypotheses.append({
                "id": "H1",
                "hypothesis": "Audience fatigue causing ROAS decline",
                "description": f"Found {len(declining_campaigns)} campaigns with >20% ROAS decline over time",
                "evidence": {
                    "campaigns_affected": declining_campaigns['campaign_name'].tolist()[:5],
                    "avg_decline_pct": float(declining_campaigns['roas_change_pct'].mean())
                },
                "priority": "HIGH",
                "validation_method": "time_series_regression"
            })
        
        # Hypothesis 2: Creative type performance
        creative_stats = self.data_agent.analyze_creative_performance()
        best_creative = creative_stats.iloc[0]
        worst_creative = creative_stats.iloc[-1]
        
        hypotheses.append({
            "id": "H2",
            "hypothesis": "Creative type impacts ROAS significantly",
            "description": f"{best_creative['creative_type']} outperforms {worst_creative['creative_type']}",
            "evidence": {
                "best_creative_type": best_creative['creative_type'],
                "best_roas": float(best_creative['roas']),
                "worst_creative_type": worst_creative['creative_type'],
                "worst_roas": float(worst_creative['roas']),
                "roas_difference": float(best_creative['roas'] - worst_creative['roas'])
            },
            "priority": "HIGH",
            "validation_method": "anova_test"
        })
        
        # Hypothesis 3: Platform effectiveness
        platform_stats = self.data_agent.get_platform_comparison()
        if len(platform_stats) > 1:
            platform_stats_sorted = platform_stats.sort_values('roas', ascending=False)
            hypotheses.append({
                "id": "H3",
                "hypothesis": "Platform choice affects ROAS",
                "description": f"{platform_stats_sorted.iloc[0]['platform']} has better ROAS than {platform_stats_sorted.iloc[-1]['platform']}",
                "evidence": {
                    "platforms": platform_stats[['platform', 'roas']].to_dict('records')
                },
                "priority": "MEDIUM",
                "validation_method": "t_test"
            })
        
        # Hypothesis 4: Low CTR correlation with messaging
        segments = self.data_agent.segment_by_performance()
        low_ctr = segments['low_ctr_ads']
        
        if len(low_ctr) > 0:
            low_ctr_messages = low_ctr['creative_message'].value_counts()
            hypotheses.append({
                "id": "H4",
                "hypothesis": "Low CTR linked to specific message patterns",
                "description": f"{len(low_ctr)} ads have CTR below threshold",
                "evidence": {
                    "low_ctr_count": len(low_ctr),
                    "avg_ctr": float(low_ctr['ctr'].mean()),
                    "common_messages": low_ctr_messages.head(3).to_dict()
                },
                "priority": "HIGH",
                "validation_method": "message_analysis"
            })
        
        # Hypothesis 5: Audience type saturation
        df = self.data_agent.df
        audience_performance = df.groupby('audience_type').agg({
            'roas': 'mean',
            'ctr': 'mean',
            'spend': 'sum'
        }).reset_index()
        
        hypotheses.append({
            "id": "H5",
            "hypothesis": "Audience type affects performance differently",
            "description": "Different audience segments show varying engagement levels",
            "evidence": {
                "audience_stats": audience_performance.to_dict('records')
            },
            "priority": "MEDIUM",
            "validation_method": "segmentation_analysis"
        })
        
        self.hypotheses = hypotheses
        print(f"Generated {len(hypotheses)} hypotheses")
        return hypotheses
    
    def prioritize_hypotheses(self):
        """Sort hypotheses by priority and evidence strength"""
        priority_order = {"HIGH": 1, "MEDIUM": 2, "LOW": 3}
        sorted_hypotheses = sorted(self.hypotheses, 
                                   key=lambda x: priority_order.get(x['priority'], 4))
        return sorted_hypotheses
    
    def format_hypothesis_report(self):
        """Format hypotheses for reporting"""
        report = "\n## Generated Hypotheses\n\n"
        
        for h in self.hypotheses:
            report += f"### {h['id']}: {h['hypothesis']}\n"
            report += f"**Priority**: {h['priority']}\n\n"
            report += f"{h['description']}\n\n"
            report += f"**Validation Method**: {h['validation_method']}\n\n"
        
        return report

if __name__ == "__main__":
    from data_agent import DataAgent
    
    data_agent = DataAgent()
    data_agent.load_data()
    
    insight_agent = InsightAgent(data_agent)
    hypotheses = insight_agent.generate_hypotheses()
    
    import json
    print(json.dumps(hypotheses, indent=2))
