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

## 📁 Project Structure

```
ai-identity-lab/
│
├── 01-identity-risk-scoring/      # ✅ ML Model + REST API
├── 02-role-mining-engine/         # ✅ Role Discovery
├── 03-sod-detection-system/       # ✅ SOD Violation Detection
├── 04-ai-access-review-assistant/ # ✅ LLM + RAG Reviewer
├── 05-identity-graph-analytics/   # ✅ Graph Analytics
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

## 🧪 Research Paper

**Title:** *AI-Assisted Access Reviews: A Framework for Reducing Reviewer Fatigue While Maintaining Compliance*

**Status:** Submitted to arXiv (pending)

**Abstract:** Access certifications place significant burden on business reviewers, with fatigue leading to rubber-stamping and undetected privilege creep. This paper presents a framework for AI-assisted access reviews using Random Forest risk scoring and Llama 3 with RAG. Evaluation on synthetic data of 828 users and 2,265 assignments achieved 91.9% risk detection accuracy and simulated 82.5% review time reduction.

## 🛠️ Technologies

| Category | Technologies |
|----------|--------------|
| **ML & AI** | scikit-learn, Random Forest, Llama 3, Ollama |
| **Backend** | Python, FastAPI, Uvicorn |
| **Data** | Pandas, NumPy, NetworkX, Neo4j |
| **Frontend** | HTML/CSS, JavaScript |
| **DevOps** | Docker, Git |

## 📚 Documentation

- [API Documentation](http://localhost:8000/docs) - run locally
- [Role Mining Report](02-role-mining-engine/output/implementation_plan.json)
- [SOD Violation Report](03-sod-detection-system/output/sod_violations.json)
- [Graph Analysis](05-identity-graph-analytics/output/graph_report.json)


## 📧 Contact

**Nathaniel Dadson**
- LinkedIn: [linkedin.com/in/nathaniel-dadson-0094b0168](https://linkedin.com/in/nathaniel-dadson-0094b0168)
- Email: dadsonnathaniel777@gmail.com
- GitHub: [github.com/natedadson](https://github.com/natedadson)

## 📄 License

MIT License - Free for academic and commercial use with attribution.

---

**6 projects. ~2,000 lines of code. 91.9% accuracy.**

*The future of identity governance is not human or machine. It is human and machine, working together.*
```

---

## Step 2: Replace Your README

Run these commands in your terminal:

```bash
cd ~/ai-identity-lab

# Open README for editing
nano README.md
```

**In nano:**
1. `Ctrl + A` (go to beginning)
2. `Ctrl + K` repeatedly until file is empty
3. Paste the new README (right-click → Paste)
4. `Ctrl + O` (save)
5. `Enter` (confirm)
6. `Ctrl + X` (exit)

## Step 3: Commit and Push

```bash
git add README.md
git commit -m "docs: complete README overhaul

- Marked all 6 projects as COMPLETE
- Added key metrics (91.9% accuracy, 1,028 nodes)
- Added research paper section
- Added technology stack table
- Professional formatting with badges"

git push
```

## Step 4: Verify

Open your browser and go to:
```
https://github.com/natedadson/ai-identity-lab
```

You should see the new professional README with all projects marked complete.

---

**That's it! Your GitHub repository now reflects 6 days of serious work.**
