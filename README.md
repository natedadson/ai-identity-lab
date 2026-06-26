# 🔐 AI-Native Identity Security Research Lab

**Researching the intersection of Artificial Intelligence and Identity & Access Management**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Research](https://img.shields.io/badge/Research-Active-brightgreen.svg)]()

## 🎯 Mission

This lab exists to answer fundamental questions at the intersection of AI and identity security:

- **How can AI reduce access review fatigue while maintaining compliance?**
- **Can machine learning detect risky access before it becomes an incident?**
- **What role groupings naturally emerge from user access patterns?**
- **How can we automatically detect Segregation of Duties violations?**
- **What does an identity graph reveal about privilege escalation paths?**

## 📊 Project Portfolio

All 6 projects are **COMPLETE** with working code, APIs, and web dashboards.

| # | Project | Status | Tech Stack | Key Result |
|---|---------|--------|------------|-------------|
| 1 | **Identity Risk Scoring** | ✅ Complete | Random Forest, FastAPI, scikit-learn | 91.9% risk detection accuracy |
| 2 | **Role Mining Engine** | ✅ Complete | Apriori, mlxtend, pandas | 161 role optimization opportunities |
| 3 | **SOD Detection System** | ✅ Complete | Custom rule engine, fuzzy matching | 100% violation detection rate |
| 4 | **AI Access Review Assistant** | ✅ Complete | Llama 3, Ollama, RAG | Local LLM with 11.5s response |
| 5 | **Identity Graph Analytics** | ✅ Complete | NetworkX, Neo4j, matplotlib | 1,028 nodes, 2,275 relationships |
| 6 | **REST API + Web Dashboard** | ✅ Complete | FastAPI, HTML/JS | Production-ready endpoints |
| 7 | **UEBA Detection** | ✅ Complete | Behavioral baselines, FastAPI, anomaly detection | 706 alerts from 9,062 events |
| 8 | **Fraud Detection** | ✅ Complete | LSTM, Random Forest, NetworkX, FastAPI | Real-time transaction fraud scoring |

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- 8GB RAM minimum
- Ollama (for AI reviewer - optional)

### One-command setup

```bash
git clone https://github.com/natedadson/ai-identity-lab.git
cd ai-identity-lab
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Generate synthetic data

```bash
python datasets/synthetic/generate_identity_data.py
```

### Run the ML Risk Scoring API

```bash
python -m uvicorn 01-identity-risk-scoring.api.app:app --reload --port 8000
```

Then open `http://localhost:8000/docs` for interactive API documentation.

### Run the AI Access Reviewer

```bash
# First, install and start Ollama
brew install ollama
ollama serve &
ollama pull llama3.2:3b

# Then run the reviewer
python 04-ai-access-review-assistant/src/simple_rag.py
```

### Open the Web Dashboard

```bash
open 04-ai-access-review-assistant/ui/simple_web.html
```

### Run the UEBA Detection API

```bash
python 06-ueba-detection/src/ueba_api.py


### Generate Fraud Detection Data

```bash
python 08-fraud-detection/src/generate_transactions.py

## 📁 Project Structure

```
ai-identity-lab/
│
├── 01-identity-risk-scoring/      # ✅ ML Model + REST API
├── 02-role-mining-engine/         # ✅ Role Discovery
├── 03-sod-detection-system/       # ✅ SOD Violation Detection
├── 04-ai-access-review-assistant/ # ✅ LLM + RAG Reviewer
├── 05-identity-graph-analytics/   # ✅ Graph Analytics
├── 06-ueba-detection/             # ✅ User & Entity Behavior Analytics
├── 07-enterprise-integration/ # ✅ Slack/Email/Webhook Integration
├── 08-fraud-detection/ # ✅ AI-Driven Fraud Detection
├── datasets/                      # Synthetic identity data
├── research-papers/               # Academic publications
└── linkedin-articles/             # Technical blog posts
```

## 📈 Key Results

### ML Risk Scoring Model
| Metric | Value |
|--------|-------|
| Accuracy | 91.9% |
| AUC-ROC | 0.96 |
| Precision (Risky) | 0.89 |
| Recall (Risky) | 0.87 |

### Feature Importance Discovered
| Feature | Importance |
|---------|------------|
| Risk level | 29.9% |
| Days since last use | 28.0% |
| Never used | 21.4% |
| Direct grant | 17.9% |

### SOD Detection
- **6 rules** covering Critical/High risks
- **100% detection rate** on test violations
- **0 false positives**

### Identity Graph
- **1,028 nodes** (828 users + 200 entitlements)
- **2,275 relationships**
- **1,432 similar user pairs** discovered

### UEBA Detection
- **100 users** with behavioral baselines
- **9,062 events** analyzed
- **706 alerts** generated (99 critical, 607 high)
- **4 anomaly types**: Unusual hours, locations, apps, rapid access
- **Real-time API** with interactive dashboard


### Add Fraud Detection

```markdown
### Fraud Detection
- **500 users** with behavioral profiles
- **45,000+ transactions** generated
- **Real-time scoring** with FastAPI
- **Money mule detection** via graph networks
- **Multiple fraud patterns**: Large transactions, high-risk locations, structuring

## 🧪 Research Paper

**Title:** *AI-Assisted Access Reviews: A Framework for Reducing Reviewer Fatigue While Maintaining Compliance*

**Status:** Submitted to arXiv (pending)

**Abstract:** Access certifications place a significant burden on business reviewers, with fatigue leading to rubber-stamping and undetected privilege creep. This paper presents a framework for AI-assisted access reviews using Random Forest risk scoring and Llama 3 with RAG. Evaluation on synthetic data of 828 users and 2,265 assignments achieved 91.9% risk detection accuracy and simulated 82.5% review time reduction.

## 🛠️ Technologies

| Category | Technologies |
|----------|--------------|
| **ML & AI** | scikit-learn, Random Forest, Llama 3, Ollama |
| **Backend** | Python, FastAPI, Uvicorn |
| **Data** | Pandas, NumPy, NetworkX, Neo4j |
| **Analytics** | Behavioral baselines, Anomaly detection, UEBA |
| **Frontend** | HTML/CSS, JavaScript |
| **DevOps** | Docker, Git |

## 📚 Documentation

- [API Documentation](http://localhost:8000/docs) - run locally
- [Role Mining Report](02-role-mining-engine/output/implementation_plan.json)
- [SOD Violation Report](03-sod-detection-system/output/sod_violations.json)
- [Graph Analysis](05-identity-graph-analytics/output/graph_report.json)
- [UEBA Alerts](06-ueba-detection/output/alerts.json)


## 📧 Contact

**Nathaniel Dadson**
- LinkedIn: [linkedin.com/in/nathaniel-dadson-0094b0168](https://linkedin.com/in/nathaniel-dadson-0094b0168)
- Email: dadsonnathaniel777@gmail.com
- GitHub: [github.com/natedadson](https://github.com/natedadson)

## 📄 License

MIT License - Free for academic and commercial use with attribution.

---

**8 projects. ~3,000 lines of code. 91.9% accuracy. 706 UEBA alerts. Real-time fraud detection.**

*The future of identity governance is not human or machine. It is human and machine, working together.*

