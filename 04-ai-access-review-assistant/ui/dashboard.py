"""
Streamlit Dashboard for AI Access Review Assistant
Web interface for the identity risk scoring and AI review systems.
"""

import streamlit as st
import pandas as pd
import requests
import json
import sys
import os

# Page configuration
st.set_page_config(
    page_title="AI Access Review Assistant",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #0066cc;
        text-align: center;
        margin-bottom: 2rem;
    }
    .risk-critical { background-color: #ff4444; color: white; padding: 0.5rem; border-radius: 0.5rem; text-align: center; font-weight: bold; }
    .risk-high { background-color: #ff8800; color: white; padding: 0.5rem; border-radius: 0.5rem; text-align: center; font-weight: bold; }
    .risk-medium { background-color: #ffcc00; color: black; padding: 0.5rem; border-radius: 0.5rem; text-align: center; font-weight: bold; }
    .risk-low { background-color: #00cc44; color: white; padding: 0.5rem; border-radius: 0.5rem; text-align: center; font-weight: bold; }
    .recommend-approve { background-color: #00cc44; color: white; padding: 0.5rem; border-radius: 0.5rem; text-align: center; font-weight: bold; }
    .recommend-review { background-color: #ffcc00; color: black; padding: 0.5rem; border-radius: 0.5rem; text-align: center; font-weight: bold; }
    .recommend-revoke { background-color: #ff4444; color: white; padding: 0.5rem; border-radius: 0.5rem; text-align: center; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header">🔐 AI Access Review Assistant</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/artificial-intelligence.png", width=80)
    st.markdown("### About")
    st.markdown("""
    This AI assistant helps security analysts review access requests.
    
    **Powered by:** Llama 3.2 3B (local), RAG, Random Forest
    """)
    
    st.markdown("---")
    st.markdown("### Quick Stats")
    st.markdown("""
    - 📊 2,265 historical assignments loaded
    - ⚡ ~10 seconds per review
    - 🔒 100% local (no data leaves your computer)
    """)

# Main area - two tabs
tab1, tab2 = st.tabs(["📝 Single Review", "📊 Analytics"])

# Tab 1: Single Review
with tab1:
    st.markdown("### Review a Single Access Request")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 👤 User Information")
        user_id = st.text_input("User ID", value="user_0420")
        department = st.selectbox("Department", ["Finance", "Engineering", "Sales", "HR", "IT", "Executive"])
        role = st.selectbox("Role", [
            "Finance Analyst", "Finance Manager", "Software Engineer", 
            "Senior Engineer", "Sales Rep", "HR Specialist", "Security Analyst"
        ])
        tenure_days = st.slider("Tenure (days)", 0, 2000, 365)
    
    with col2:
        st.markdown("#### 🔑 Entitlement Information")
        entitlement_id = st.text_input("Entitlement ID", value="ent_030")
        risk_level = st.selectbox("Risk Level", ["Low", "Medium", "High", "Critical"])
        is_direct_grant = st.checkbox("Is Direct Grant (not via role)", value=True)
        days_since_last_use = st.number_input("Days Since Last Use (-1 = never used)", -1, 365, -1)
    
    # Check if API is running
    api_available = False
    try:
        requests.get("http://localhost:8000/", timeout=2)
        api_available = True
    except:
        api_available = False
    
    if not api_available:
        st.warning("⚠️ ML API not running. Start it with: python -m uvicorn 01-identity-risk-scoring.api.app:app --reload --port 8000")
    
    # Review button
    if st.button("🤖 Generate AI Recommendation", type="primary", use_container_width=True):
        if not api_available:
            st.error("Please start the ML API first")
        else:
            with st.spinner("🔄 Analyzing access request..."):
                try:
                    # Call ML API
                    response = requests.post(
                        "http://localhost:8000/predict",
                        json={
                            "user_id": user_id,
                            "department": department,
                            "role": role,
                            "tenure_days": tenure_days,
                            "entitlement_id": entitlement_id,
                            "risk_level": risk_level,
                            "is_direct_grant": is_direct_grant,
                            "days_since_last_use": days_since_last_use
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        st.markdown("---")
                        st.markdown("### 📊 AI Decision")
                        
                        col_result1, col_result2, col_result3 = st.columns(3)
                        
                        with col_result1:
                            rec = result.get('recommendation', 'Review')
                            rec_class = f"recommend-{rec.lower()}"
                            st.markdown(f'<div class="{rec_class}">🎯 Recommendation: {rec}</div>', unsafe_allow_html=True)
                        
                        with col_result2:
                            risk = result.get('risk_level', 'Medium')
                            risk_class = f"risk-{risk.lower()}"
                            st.markdown(f'<div class="{risk_class}">⚠️ Risk Level: {risk}</div>', unsafe_allow_html=True)
                        
                        with col_result3:
                            st.metric("Risk Probability", f"{result.get('risk_probability', 0)*100:.1f}%")
                        
                        st.markdown("#### 💡 Reasoning")
                        st.info(result.get('top_factors', ['No reasoning provided'])[0])
                    else:
                        st.error(f"API Error: {response.status_code}")
                        
                except Exception as e:
                    st.error(f"Error: {e}")

# Tab 2: Analytics
with tab2:
    st.markdown("### Model Performance Summary")
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Total Reviews", "2,265", delta="synthetic dataset")
    with col_b:
        st.metric("Avg Response Time", "~2 sec", delta="with ML API")
    with col_c:
        st.metric("Risk Detection Rate", "91%", delta="on test data")
    
    st.markdown("#### Feature Importance (From ML Model)")
    
    importance_data = {
        "Feature": ["Risk Level", "Stale Access", "Unused Access", "Direct Grant", "Tenure"],
        "Importance": [29.9, 28.0, 21.4, 17.9, 2.0]
    }
    st.bar_chart(pd.DataFrame(importance_data).set_index("Feature"))

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.8rem;">
    🔐 AI Access Review Assistant | Powered by ML API + Llama 3.2
    <br>
    <a href="https://github.com/natedadson/ai-identity-lab" target="_blank">GitHub Repository</a>
</div>
""", unsafe_allow_html=True)
