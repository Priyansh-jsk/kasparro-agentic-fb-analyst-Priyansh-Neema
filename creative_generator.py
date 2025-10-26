import pandas as pd
import numpy as np
import re
from collections import Counter

class CreativeGenerator:
    def __init__(self, data_agent, config):
        self.data_agent = data_agent
        self.config = config
        self.recommendations = []
        
    def generate_recommendations(self):
        """Generate creative recommendations for low-performing ads"""
        print("\nGenerating creative recommendations...")
        
        segments = self.data_agent.segment_by_performance()
        low_ctr_ads = segments['low_ctr_ads']
        high_ctr_ads = segments['high_ctr_ads']
        
        recommendations = []
        
        # Analyze what works in high-performing ads
        successful_patterns = self._extract_message_patterns(high_ctr_ads)
        
        # Group low-performing ads by campaign/adset
        for (campaign, adset), group in low_ctr_ads.groupby(['campaign_name', 'adset_name']):
            
            if len(group) == 0:
                continue
            
            # Get representative ad from this group
            sample_ad = group.iloc[0]
            
            # Generate recommendations
            new_messages = self._generate_new_messages(
                sample_ad,
                successful_patterns,
                high_ctr_ads
            )
            
            recommendation = {
                'campaign_name': campaign,
                'adset_name': adset,
                'current_performance': {
                    'avg_ctr': float(group['ctr'].mean()),
                    'avg_roas': float(group['roas'].mean()),
                    'spend': float(group['spend'].sum())
                },
                'current_message': sample_ad['creative_message'],
                'current_creative_type': sample_ad['creative_type'],
                'recommendations': new_messages,
                'rationale': self._generate_rationale(sample_ad, successful_patterns)
            }
            
            recommendations.append(recommendation)
        
        # Limit to top N recommendations
        top_n = self.config['agents']['top_creative_samples']
        recommendations = sorted(recommendations, 
                                key=lambda x: x['current_performance']['spend'], 
                                reverse=True)[:top_n]
        
        self.recommendations = recommendations
        print(f"Generated {len(recommendations)} creative recommendations")
        return recommendations
    
    def _extract_message_patterns(self, high_performing_ads):
        """Extract successful patterns from high-performing ads"""
        messages = high_performing_ads['creative_message'].tolist()
        
        # Extract common words and phrases
        all_words = []
        for msg in messages:
            words = re.findall(r'\b\w+\b', msg.lower())
            all_words.extend(words)
        
        word_freq = Counter(all_words)
        
        # Common CTAs and power words
        cta_words = ['try', 'shop', 'discover', 'get', 'buy', 'limited', 'new', 'best']
        power_words = ['free', 'guarantee', 'exclusive', 'premium', 'comfortable', 'essential']
        
        patterns = {
            'top_words': [word for word, count in word_freq.most_common(20)],
            'avg_length': np.mean([len(msg) for msg in messages]),
            'has_cta': sum(any(cta in msg.lower() for cta in cta_words) for msg in messages) / len(messages),
            'has_power_words': sum(any(pw in msg.lower() for pw in power_words) for msg in messages) / len(messages),
            'creative_type_dist': high_performing_ads['creative_type'].value_counts().to_dict()
        }
        
        return patterns
    
    def _generate_new_messages(self, current_ad, patterns, high_ctr_ads):
        """Generate new message suggestions based on successful patterns"""
        
        # Sample high-performing messages from similar creative type
        similar_ads = high_ctr_ads[high_ctr_ads['creative_type'] == current_ad['creative_type']]
        
        if len(similar_ads) == 0:
            similar_ads = high_ctr_ads
        
        # Get top 3 messages
        top_messages = similar_ads.nlargest(3, 'ctr')['creative_message'].tolist()
        
        new_messages = []
        
        # Recommendation 1: Adapt from best performer
        if len(top_messages) > 0:
            new_messages.append({
                'message': top_messages[0],
                'strategy': 'adapt_best_performer',
                'expected_lift': '20-30%'
            })
        
        # Recommendation 2: Add strong CTA
        current_msg = current_ad['creative_message']
        cta_options = [
            "Try now — limited time offer!",
            "Shop the collection today.",
            "Discover your perfect fit.",
            "Get yours before they're gone!"
        ]
        
        new_messages.append({
            'message': f"{current_msg} {cta_options[0]}",
            'strategy': 'add_strong_cta',
            'expected_lift': '10-15%'
        })
        
        # Recommendation 3: Emphasize benefits
        benefit_templates = [
            "Premium comfort meets everyday style — {}",
            "All-day confidence starts here — {}",
            "Engineered for comfort — {}"
        ]
        
        product = "essentials" if "men" in current_msg.lower() else "collection"
        new_messages.append({
            'message': benefit_templates[0].format(product),
            'strategy': 'emphasize_benefits',
            'expected_lift': '15-20%'
        })
        
        return new_messages
    
    def _generate_rationale(self, current_ad, patterns):
        """Generate explanation for recommendations"""
        rationale_points = []
        
        current_length = len(current_ad['creative_message'])
        optimal_length = patterns['avg_length']
        
        if abs(current_length - optimal_length) > 20:
            rationale_points.append(
                f"Adjust message length from {current_length} to ~{int(optimal_length)} characters"
            )
        
        if patterns['has_cta'] > 0.5:
            rationale_points.append("High-performing ads frequently include strong CTAs")
        
        best_creative_type = max(patterns['creative_type_dist'], key=patterns['creative_type_dist'].get)
        if current_ad['creative_type'] != best_creative_type:
            rationale_points.append(f"Consider testing {best_creative_type} format")
        
        return rationale_points
    
    def format_recommendations_report(self):
        """Format recommendations as markdown report"""
        report = "\n## Creative Recommendations\n\n"
        
        for i, rec in enumerate(self.recommendations, 1):
            report += f"### Recommendation {i}: {rec['campaign_name']}\n\n"
            report += f"**Current Performance:**\n"
            report += f"- CTR: {rec['current_performance']['avg_ctr']:.4f}\n"
            report += f"- ROAS: {rec['current_performance']['avg_roas']:.2f}\n"
            report += f"- Spend: ${rec['current_performance']['spend']:.2f}\n\n"
            
            report += f"**Current Message:** {rec['current_message']}\n\n"
            
            report += f"**New Message Ideas:**\n"
            for j, msg in enumerate(rec['recommendations'], 1):
                report += f"{j}. {msg['message']}\n"
                report += f"   - Strategy: {msg['strategy']}\n"
                report += f"   - Expected lift: {msg['expected_lift']}\n\n"
            
            report += f"**Rationale:**\n"
            for point in rec['rationale']:
                report += f"- {point}\n"
            report += "\n---\n\n"
        
        return report

if __name__ == "__main__":
    import yaml
    from data_agent import DataAgent
    
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    data_agent = DataAgent()
    data_agent.load_data()
    
    creative_gen = CreativeGenerator(data_agent, config)
    recommendations = creative_gen.generate_recommendations()
    
    import json
    print(json.dumps(recommendations[:2], indent=2))
