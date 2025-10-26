"""
Tests for Evaluator Agent
"""
import unittest
import yaml
import pandas as pd
import numpy as np
from data_agent import DataAgent
from insight_agent import InsightAgent
from evaluator import Evaluator

class TestEvaluator(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        with open('config.yaml', 'r') as f:
            cls.config = yaml.safe_load(f)
        
        cls.data_agent = DataAgent()
        cls.data_agent.load_data()
        
        cls.insight_agent = InsightAgent(cls.data_agent)
        cls.hypotheses = cls.insight_agent.generate_hypotheses()
        
        cls.evaluator = Evaluator(cls.data_agent, cls.config)
    
    def test_evaluator_initialization(self):
        """Test evaluator initializes correctly"""
        self.assertIsNotNone(self.evaluator)
        self.assertEqual(len(self.evaluator.validation_results), 0)
    
    def test_validate_hypothesis(self):
        """Test single hypothesis validation"""
        if len(self.hypotheses) > 0:
            result = self.evaluator.validate_hypothesis(self.hypotheses[0])
            
            # Check result structure
            self.assertIn('hypothesis_id', result)
            self.assertIn('validated', result)
            self.assertIn('confidence', result)
            self.assertIn('method', result)
            self.assertIn('conclusion', result)
            
            # Check data types
            self.assertIsInstance(result['validated'], bool)
            self.assertIsInstance(result['confidence'], float)
            self.assertGreaterEqual(result['confidence'], 0.0)
            self.assertLessEqual(result['confidence'], 1.0)
    
    def test_evaluate_all_hypotheses(self):
        """Test evaluation of all hypotheses"""
        results = self.evaluator.evaluate_all(self.hypotheses)
        
        # Should return same number of results as hypotheses
        self.assertEqual(len(results), len(self.hypotheses))
        
        # Each result should have required fields
        for result in results:
            self.assertIn('validated', result)
            self.assertIn('confidence', result)
    
    def test_get_validated_insights(self):
        """Test filtering of validated insights"""
        self.evaluator.evaluate_all(self.hypotheses)
        validated = self.evaluator.get_validated_insights()
        
        # All returned insights should be validated
        for insight in validated:
            self.assertTrue(insight['validated'])
            self.assertGreaterEqual(insight['confidence'], self.config['confidence_min'])
    
    def test_confidence_threshold(self):
        """Test confidence threshold filtering"""
        self.evaluator.evaluate_all(self.hypotheses)
        validated = self.evaluator.get_validated_insights()
        
        for insight in validated:
            self.assertGreaterEqual(
                insight['confidence'],
                self.config['confidence_min'],
                f"Confidence {insight['confidence']} below threshold {self.config['confidence_min']}"
            )

if __name__ == '__main__':
    print("🧪 Running Evaluator Tests...")
    unittest.main(verbosity=2)
