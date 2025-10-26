"""
Main Run Script - Orchestrates the entire agentic system
"""
import yaml
import json
import sys
import os
from datetime import datetime
import numpy as np
import pandas as pd

# Import all agents
from data_agent import DataAgent
from insight_agent import InsightAgent
from evaluator import Evaluator
from creative_generator import CreativeGenerator
from planner import PlannerAgent

class AgenticFBAnalyst:
    def __init__(self, config_path="config.yaml"):
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize agents
        self.planner = PlannerAgent()
        self.data_agent = DataAgent(config_path)
        self.insight_agent = None
        self.evaluator = None
        self.creative_generator = None
        
        # Results storage
        self.results = {
            'query': '',
            'timestamp': datetime.now().isoformat(),
            'tasks': [],
            'hypotheses': [],
            'validated_insights': [],
            'creative_recommendations': [],
            'summary': {}
        }
        
    def run(self, user_query):
        """Main execution flow"""
        print("=" * 70)
        print("KASPARRO AGENTIC FACEBOOK ANALYST")
        print("=" * 70)
        
        self.results['query'] = user_query
        
        # Step 1: Planning
        tasks = self.planner.parse_query(user_query)
        self.results['tasks'] = tasks
        
        # Step 2: Load and analyze data
        print("\n" + "=" * 70)
        self.data_agent.load_data()
        summary = self.data_agent.get_basic_summary()
        self.results['summary'] = summary
        
        print(f"\nDataset Overview:")
        print(f"   - Date range: {summary['date_range']['start']} to {summary['date_range']['end']}")
        print(f"   - Total spend: ${summary['metrics']['total_spend']:,.2f}")
        print(f"   - Total revenue: ${summary['metrics']['total_revenue']:,.2f}")
        print(f"   - Average ROAS: {summary['metrics']['avg_roas']:.2f}")
        print(f"   - Average CTR: {summary['metrics']['avg_ctr']:.4f}")
        
        # Step 3: Generate insights
        print("\n" + "=" * 70)
        self.insight_agent = InsightAgent(self.data_agent)
        hypotheses = self.insight_agent.generate_hypotheses()
        self.results['hypotheses'] = hypotheses
        
        # Step 4: Validate hypotheses
        print("\n" + "=" * 70)
        self.evaluator = Evaluator(self.data_agent, self.config)
        validation_results = self.evaluator.evaluate_all(hypotheses)
        validated = self.evaluator.get_validated_insights()
        self.results['validated_insights'] = validated
        
        print(f"\n✓ Validated {len(validated)}/{len(hypotheses)} hypotheses")
        
        # Step 5: Generate creative recommendations
        print("\n" + "=" * 70)
        self.creative_generator = CreativeGenerator(self.data_agent, self.config)
        recommendations = self.creative_generator.generate_recommendations()
        self.results['creative_recommendations'] = recommendations
        
        # Step 6: Save outputs
        print("\n" + "=" * 70)
        self._save_outputs()
        
        # Step 7: Generate report
        self._generate_report()
        
        print("\n" + "=" * 70)
        print("ANALYSIS COMPLETE")
        print("=" * 70)
        print(f"\nOutputs saved to:")
        print(f"   - reports/insights.json")
        print(f"   - reports/creatives.json")
        print(f"   - reports/report.md")
        
        return self.results
    
    def _save_outputs(self):
        """Save results to files"""
        
        # Custom JSON encoder to handle numpy and pandas types
        class NumpyEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, np.integer):
                    return int(obj)
                if isinstance(obj, np.floating):
                    return float(obj)
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                if isinstance(obj, np.bool_):
                    return bool(obj)
                if isinstance(obj, pd.Timestamp):
                    return obj.strftime('%Y-%m-%d')
                return super(NumpyEncoder, self).default(obj)
        
        os.makedirs('reports', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # Save insights
        with open('reports/insights.json', 'w', encoding='utf-8') as f:
            json.dump({
                'hypotheses': self.results['hypotheses'],
                'validated_insights': self.results['validated_insights']
            }, f, indent=2, cls=NumpyEncoder)
        
        print("\nSaved insights.json")
        
        # Save creative recommendations
        with open('reports/creatives.json', 'w', encoding='utf-8') as f:
            json.dump(self.results['creative_recommendations'], f, indent=2, cls=NumpyEncoder)
        
        print("💾 Saved creatives.json")
        
        # Save full log
        with open('logs/analysis_log.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, cls=NumpyEncoder)
        
        print("Saved analysis_log.json")
    
    def _generate_report(self):
        """Generate markdown report"""
        report = f"""# Facebook Ads Performance Analysis Report

**Query:** {self.results['query']}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Executive Summary

This analysis examined {self.results['summary']['total_rows']} ad performance records from {self.results['summary']['date_range']['start']} to {self.results['summary']['date_range']['end']}.

**Key Metrics:**
- Total Spend: ${self.results['summary']['metrics']['total_spend']:,.2f}
- Total Revenue: ${self.results['summary']['metrics']['total_revenue']:,.2f}
- Average ROAS: {self.results['summary']['metrics']['avg_roas']:.2f}
- Average CTR: {self.results['summary']['metrics']['avg_ctr']:.4f}

---

## Validated Insights

"""
        # Add validated insights
        if len(self.results['validated_insights']) > 0:
            for i, insight in enumerate(self.results['validated_insights'], 1):
                # Find corresponding hypothesis
                hypo = next((h for h in self.results['hypotheses'] if h['id'] == insight['hypothesis_id']), None)
                if hypo:
                    report += f"### {i}. {hypo['hypothesis']}\n\n"
                    report += f"**Confidence:** {insight['confidence']:.2f}\n\n"
                    report += f"**Conclusion:** {insight['conclusion']}\n\n"
                    report += f"{hypo['description']}\n\n"
        else:
            report += "No insights passed the validation threshold. Consider:\n"
            report += "- Adjusting confidence thresholds in config.yaml\n"
            report += "- Collecting more data for robust statistical testing\n"
            report += "- Reviewing hypothesis generation logic\n\n"
        
        report += "---\n\n"
        
        # Add creative recommendations
        if self.creative_generator:
            report += self.creative_generator.format_recommendations_report()
        
        report += """---

## Recommendations

Based on this analysis:

1. **Refresh Creative for Low-CTR Campaigns**: Implement the suggested message variations for underperforming ads
2. **Reallocate Budget**: Shift spend toward high-performing creative types and platforms
3. **Monitor Audience Fatigue**: Track ROAS trends weekly and refresh creative when decline exceeds 15%
4. **Test New Formats**: Experiment with creative types that show higher engagement

---

## Next Steps

- Implement top 3 creative recommendations within 1 week
- Set up automated monitoring for ROAS decline alerts
- Schedule A/B tests for new message variations
- Review audience targeting for fatigued campaigns

"""
        
        # Write with UTF-8 encoding to handle special characters
        with open('reports/report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("Saved report.md")

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
    else:
        query = "Analyze ROAS fluctuations and recommend creative improvements"
    
    analyst = AgenticFBAnalyst()
    analyst.run(query)

if __name__ == "__main__":
    main()
