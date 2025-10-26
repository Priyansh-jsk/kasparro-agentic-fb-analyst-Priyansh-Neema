import pandas as pd
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression

class Evaluator:
    def __init__(self, data_agent, config):
        self.data_agent = data_agent
        self.config = config
        self.validation_results = []
        
    def validate_hypothesis(self, hypothesis):
        """Validate a single hypothesis using appropriate statistical method"""
        method = hypothesis['validation_method']
        
        if method == 'time_series_regression':
            return self._validate_time_decay(hypothesis)
        elif method == 'anova_test':
            return self._validate_creative_impact(hypothesis)
        elif method == 't_test':
            return self._validate_platform_difference(hypothesis)
        elif method == 'message_analysis':
            return self._validate_message_pattern(hypothesis)
        elif method == 'segmentation_analysis':
            return self._validate_audience_segments(hypothesis)
        else:
            return self._default_validation(hypothesis)
    
    def _validate_time_decay(self, hypothesis):
        """Validate time-based performance decay"""
        df = self.data_agent.df.copy()
        
        results = []
        campaigns = hypothesis['evidence']['campaigns_affected']
        
        for campaign in campaigns[:3]:
            campaign_data = df[df['campaign_name'] == campaign].sort_values('date')
            
            if len(campaign_data) > 5:
                X = np.arange(len(campaign_data)).reshape(-1, 1)
                y = campaign_data['roas'].values
                
                model = LinearRegression()
                model.fit(X, y)
                
                slope = model.coef_[0]
                r_squared = model.score(X, y)
                
                results.append({
                    'campaign': campaign,
                    'slope': float(slope),
                    'r_squared': float(r_squared),
                    'declining': slope < -0.01
                })
        
        declining_count = sum(1 for r in results if r['declining'])
        confidence = declining_count / len(results) if results else 0
        
        return {
            'hypothesis_id': hypothesis['id'],
            'validated': confidence > self.config['confidence_min'],
            'confidence': float(confidence),
            'method': 'linear_regression',
            'details': results,
            'conclusion': f"Time decay detected in {declining_count}/{len(results)} campaigns"
        }
    
    def _validate_creative_impact(self, hypothesis):
        """Validate creative type performance differences using ANOVA"""
        df = self.data_agent.df
        
        creative_groups = [group['roas'].values for name, group in df.groupby('creative_type')]
        
        if len(creative_groups) >= 2:
            f_stat, p_value = stats.f_oneway(*creative_groups)
            
            validated = p_value < 0.05
            confidence = 1 - p_value if validated else 0
        else:
            f_stat, p_value = 0, 1
            validated = False
            confidence = 0
        
        return {
            'hypothesis_id': hypothesis['id'],
            'validated': validated,
            'confidence': float(min(confidence, 1.0)),
            'method': 'anova',
            'details': {
                'f_statistic': float(f_stat),
                'p_value': float(p_value),
                'significance_level': 0.05
            },
            'conclusion': f"Creative type {'significantly' if validated else 'does not significantly'} impact ROAS"
        }
    
    def _validate_platform_difference(self, hypothesis):
        """Validate platform performance differences using t-test"""
        df = self.data_agent.df
        
        platforms = df['platform'].unique()
        
        if len(platforms) == 2:
            group1 = df[df['platform'] == platforms[0]]['roas']
            group2 = df[df['platform'] == platforms[1]]['roas']
            
            t_stat, p_value = stats.ttest_ind(group1, group2)
            
            validated = p_value < 0.05
            confidence = 1 - p_value if validated else 0
        else:
            t_stat, p_value = 0, 1
            validated = False
            confidence = 0
        
        return {
            'hypothesis_id': hypothesis['id'],
            'validated': validated,
            'confidence': float(min(confidence, 1.0)),
            'method': 't_test',
            'details': {
                't_statistic': float(t_stat),
                'p_value': float(p_value)
            },
            'conclusion': f"Platform difference {'is' if validated else 'is not'} statistically significant"
        }
    
    def _validate_message_pattern(self, hypothesis):
        """Validate message patterns correlation with CTR"""
        segments = self.data_agent.segment_by_performance()
        low_ctr = segments['low_ctr_ads']
        high_ctr = segments['high_ctr_ads']
        
        low_ctr_avg_length = low_ctr['creative_message'].str.len().mean()
        high_ctr_avg_length = high_ctr['creative_message'].str.len().mean()
        
        length_diff = abs(low_ctr_avg_length - high_ctr_avg_length)
        
        validated = length_diff > 10
        confidence = min(length_diff / 50, 1.0)
        
        return {
            'hypothesis_id': hypothesis['id'],
            'validated': validated,
            'confidence': float(confidence),
            'method': 'message_analysis',
            'details': {
                'low_ctr_avg_msg_length': float(low_ctr_avg_length),
                'high_ctr_avg_msg_length': float(high_ctr_avg_length),
                'difference': float(length_diff)
            },
            'conclusion': f"Message patterns show {'notable' if validated else 'minimal'} correlation with CTR"
        }
    
    def _validate_audience_segments(self, hypothesis):
        """Validate audience segmentation performance"""
        df = self.data_agent.df
        
        audience_groups = [group['roas'].values for name, group in df.groupby('audience_type')]
        
        if len(audience_groups) >= 2:
            f_stat, p_value = stats.f_oneway(*audience_groups)
            validated = p_value < 0.05
            confidence = 1 - p_value if validated else 0
        else:
            validated = False
            confidence = 0
            p_value = 1
        
        return {
            'hypothesis_id': hypothesis['id'],
            'validated': validated,
            'confidence': float(min(confidence, 1.0)),
            'method': 'anova',
            'details': {
                'audience_count': len(audience_groups),
                'p_value': float(p_value) if len(audience_groups) >= 2 else None
            },
            'conclusion': f"Audience segments show {'significant' if validated else 'no significant'} performance variation"
        }
    
    def _default_validation(self, hypothesis):
        """Default validation for unspecified methods"""
        return {
            'hypothesis_id': hypothesis['id'],
            'validated': False,
            'confidence': 0.0,
            'method': 'none',
            'details': {},
            'conclusion': "Validation method not implemented"
        }
    
    def evaluate_all(self, hypotheses):
        """Evaluate all hypotheses"""
        print("\nEvaluating hypotheses...")
        
        results = []
        for hypothesis in hypotheses:
            result = self.validate_hypothesis(hypothesis)
            results.append(result)
            
            status = "VALIDATED" if result['validated'] else "✗ REJECTED"
            print(f"{status} - {hypothesis['id']}: {hypothesis['hypothesis']} (confidence: {result['confidence']:.2f})")
        
        self.validation_results = results
        return results
    
    def get_validated_insights(self):
        """Return only validated hypotheses"""
        return [r for r in self.validation_results if r['validated']]

if __name__ == "__main__":
    import yaml
    from data_agent import DataAgent
    from insight_agent import InsightAgent
    
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    data_agent = DataAgent()
    data_agent.load_data()
    
    insight_agent = InsightAgent(data_agent)
    hypotheses = insight_agent.generate_hypotheses()
    
    evaluator = Evaluator(data_agent, config)
    results = evaluator.evaluate_all(hypotheses)
