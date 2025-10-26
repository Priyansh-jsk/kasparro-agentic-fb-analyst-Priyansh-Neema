import re
from datetime import datetime, timedelta

class PlannerAgent:
    def __init__(self):
        self.tasks = []
        self.query = ""
        
    def parse_query(self, user_query):
        """Parse user query into actionable tasks"""
        self.query = user_query.lower()
        print(f"\nPlanning analysis for: '{user_query}'")
        
        tasks = []
        
        # Detect intent patterns
        if any(word in self.query for word in ['drop', 'decline', 'decrease', 'fall']):
            tasks.append({
                'type': 'identify_decline',
                'description': 'Identify ROAS/CTR decline patterns',
                'agents': ['data_agent', 'insight_agent', 'evaluator']
            })
        
        if any(word in self.query for word in ['roas', 'roi', 'return']):
            tasks.append({
                'type': 'analyze_roas',
                'description': 'Analyze ROAS fluctuations and drivers',
                'agents': ['data_agent', 'insight_agent', 'evaluator']
            })
        
        if any(word in self.query for word in ['creative', 'message', 'ad copy', 'ctr']):
            tasks.append({
                'type': 'creative_analysis',
                'description': 'Analyze creative performance and generate recommendations',
                'agents': ['data_agent', 'creative_generator']
            })
        
        if any(word in self.query for word in ['platform', 'facebook', 'instagram']):
            tasks.append({
                'type': 'platform_comparison',
                'description': 'Compare performance across platforms',
                'agents': ['data_agent', 'insight_agent']
            })
        
        if any(word in self.query for word in ['audience', 'targeting', 'segment']):
            tasks.append({
                'type': 'audience_analysis',
                'description': 'Analyze audience segment performance',
                'agents': ['data_agent', 'insight_agent', 'evaluator']
            })
        
        # Extract time window if specified
        time_window = self._extract_time_window(user_query)
        if time_window:
            for task in tasks:
                task['time_window'] = time_window
        
        # If no specific intent, run full analysis
        if not tasks:
            tasks = [{
                'type': 'full_analysis',
                'description': 'Complete performance analysis',
                'agents': ['data_agent', 'insight_agent', 'evaluator', 'creative_generator']
            }]
        
        self.tasks = tasks
        print(f"Planned {len(tasks)} analysis tasks")
        return tasks
    
    def _extract_time_window(self, query):
        """Extract time window from query"""
        patterns = {
            r'last (\d+) days?': lambda m: int(m.group(1)),
            r'past (\d+) days?': lambda m: int(m.group(1)),
            r'last week': lambda m: 7,
            r'past week': lambda m: 7,
            r'last month': lambda m: 30,
            r'past month': lambda m: 30
        }
        
        for pattern, extractor in patterns.items():
            match = re.search(pattern, query.lower())
            if match:
                days = extractor(match)
                return {
                    'days': days,
                    'start_date': (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
                    'end_date': datetime.now().strftime('%Y-%m-%d')
                }
        
        return None
    
    def get_execution_plan(self):
        """Return ordered execution plan"""
        plan = []
        agent_order = ['data_agent', 'insight_agent', 'evaluator', 'creative_generator']
        
        for task in self.tasks:
            required_agents = task['agents']
            ordered_agents = [a for a in agent_order if a in required_agents]
            plan.append({'task': task, 'execution_order': ordered_agents})
        
        return plan
    
    def format_plan_summary(self):
        """Format execution plan as readable summary"""
        summary = "\n## Execution Plan\n\n"
        
        for i, task in enumerate(self.tasks, 1):
            summary += f"{i}. **{task['description']}**\n"
            summary += f"   - Type: {task['type']}\n"
            summary += f"   - Agents: {', '.join(task['agents'])}\n"
            if 'time_window' in task:
                summary += f"   - Time window: {task['time_window']['days']} days\n"
            summary += "\n"
        
        return summary

if __name__ == "__main__":
    planner = PlannerAgent()
    test_queries = [
        "Analyze ROAS drop in last 7 days",
        "Why is CTR declining for our campaigns?",
        "Compare Facebook vs Instagram performance"
    ]
    for query in test_queries:
        tasks = planner.parse_query(query)
        print(planner.format_plan_summary())
