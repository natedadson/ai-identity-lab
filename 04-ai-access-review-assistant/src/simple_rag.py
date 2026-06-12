"""
Simple RAG Access Reviewer - Fixed Version
"""

import pandas as pd
import ollama
import json
from difflib import SequenceMatcher

class SimpleAccessReviewer:
    def __init__(self):
        self.examples = []
    
    def load_examples(self, assignments_path):
        df = pd.read_csv(assignments_path)
        self.examples = df.to_dict('records')
        print(f"Loaded {len(self.examples)} examples")
    
    def find_similar(self, user_context, entitlement_desc, top_k=3):
        """Find similar examples using simple text matching."""
        query_text = f"{user_context} {entitlement_desc}"
        
        # Create list of (score, example) tuples
        scored = []
        for ex in self.examples:
            ex_text = f"{ex.get('user_role', '')} {ex.get('entitlement_risk', '')} {ex.get('source', '')}"
            score = SequenceMatcher(None, query_text.lower(), ex_text.lower()).ratio()
            scored.append((score, ex))
        
        # Sort by score (highest first)
        scored.sort(key=lambda x: x[0], reverse=True)
        
        # Return just the examples (not the scores)
        return [ex for score, ex in scored[:top_k]]
    
    def review(self, user_context, entitlement_description):
        print("🔍 Finding similar past assignments...")
        similar = self.find_similar(user_context, entitlement_description)
        print(f"   Found {len(similar)} similar examples")
        
        prompt = f"""You are an identity security analyst at a bank. Review this access request using the principle of least privilege.

USER CONTEXT: {user_context}

REQUESTED ACCESS: {entitlement_description}

SIMILAR PAST ASSIGNMENTS (for reference):
{json.dumps(similar[:2], indent=2, default=str)}

Based on identity security best practices, respond with ONLY valid JSON (no other text):
{{"recommendation": "Approve/Review/Revoke", "risk_level": "Low/Medium/High/Critical", "reasoning": "one sentence explanation"}}"""

        print("🤖 Calling Llama 3 for recommendation...")
        try:
            response = ollama.chat(model='llama3.2:3b', messages=[{'role': 'user', 'content': prompt}])
            
            # Clean the response
            content = response['message']['content']
            # Find JSON in the response
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = content[start:end]
                return json.loads(json_str)
            else:
                return {"recommendation": "Review", "risk_level": "Medium", "reasoning": "Could not parse LLM response"}
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return {"recommendation": "Review", "risk_level": "Medium", "reasoning": "Manual review recommended"}

if __name__ == "__main__":
    print("="*50)
    print("🤖 AI ACCESS REVIEW ASSISTANT")
    print("="*50)
    
    reviewer = SimpleAccessReviewer()
    reviewer.load_examples("datasets/synthetic/assignments.csv")
    
    print("\n📋 Test Case 1: High Risk Request")
    print("-"*40)
    result = reviewer.review(
        "Finance Analyst, department Finance, tenure 2 years, junior level",
        "Create payment requests in Workday - Critical risk entitlement"
    )
    
    print(f"\n📊 RESULT:")
    print(f"   Recommendation: {result.get('recommendation', 'N/A')}")
    print(f"   Risk Level: {result.get('risk_level', 'N/A')}")
    print(f"   Reasoning: {result.get('reasoning', 'N/A')}")
    
    print("\n" + "="*50)
    print("✅ Demo Complete!")
    print("="*50)
