# 💼 ApexConsult AI — Multi-Agent Business Consulting Team

An autonomous, multi-agent strategic business advisory system powered strictly by **CrewAI**, **Groq LPU Inference**, and **Streamlit Cloud**.

Designed around tier-1 management consulting methodologies (McKinsey / BCG / Bain style), this platform coordinates four specialized autonomous agents to research, formulate, stress-test, and synthesize comprehensive, boardroom-ready Business Strategy Advisory Reports.

---

## 🏛️ Multi-Agent Consulting Architecture

To ensure analytical rigor without circular loops or generic summaries, the team is structured into **4 specialized consulting roles**, each residing in its own dedicated, modular file:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        SEQUENTIAL ADVISORY PIPELINE                    │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 1. Senior Market & Competitive Intelligence Specialist                  │
│    File: agents/researcher.py                                          │
│    Focus: PESTLE trends, TAM/SAM/SOM sizing, competitor gap analysis    │
└────────────────────────────────────────────────────────────────────────┘
                                    │ (Market Intelligence Dossier)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 2. Principal Business & Growth Strategist                              │
│    File: agents/strategist.py                                          │
│    Focus: Value proposition, business model, pricing & defensible moats │
└────────────────────────────────────────────────────────────────────────┘
                                    │ (Strategic Business Blueprint)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 3. Strategic Financial Feasibility & Risk Analyst                      │
│    File: agents/financial_analyst.py                                    │
│    Focus: CAC/LTV, unit economics, CapEx/OpEx, and 4-tier risk matrix  │
└────────────────────────────────────────────────────────────────────────┘
                                    │ (Financial & Risk Audit)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 4. Senior Executive Reviewer & Managing Partner                        │
│    File: agents/reviewer.py                                            │
│    Focus: Quality critique, harmony audit, 30-60-90 day execution plan  │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                 Boardroom-Ready Strategic Advisory Report
```

### Why These 4 Agents?
1. **Researcher (`agents/researcher.py`)**: Ground truth matters. Without market sizing and competitive benchmarking, strategy is guesswork.
2. **Strategist (`agents/strategist.py`)**: Formulates the core commercial architecture, positioning, and go-to-market channels based on the researcher's findings.
3. **Financial Analyst (`agents/financial_analyst.py`)**: Quantifies unit economics (CAC, LTV, payback period, margins) and stress-tests vulnerabilities and downside risks.
4. **Executive Reviewer (`agents/reviewer.py`)**: Resolves discrepancies across agents, eliminates bias, and packages the deliverable into an actionable C-suite presentation with a concrete 30-60-90 day implementation roadmap.

---

## ⚡ Groq LLM Integration (OpenAI-Compatible Method)

The system connects to Groq using the OpenAI-compatible endpoint standard with zero deprecated wrappers:

```python
from crewai import LLM

llm = LLM(
    model="openai/gpt-oss-120b",
    base_url="https://api.groq.com/openai/v1",
    api_key=groq_api_key,
    temperature=0.7,
)
```

The system also includes an endpoint diagnostic tester utilizing the official client method:
```python
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

response = client.responses.create(
    input="Explain the importance of fast language models",
    model="openai/gpt-oss-120b",
)
print(response.output_text)
```

---

## 📂 Project Directory Structure

```
bagent/
├── .streamlit/
│   ├── config.toml               # Streamlit theme & UI styling
│   └── secrets.toml.example      # Example secrets template
├── agents/                       # Separate, modular agent definitions
│   ├── __init__.py               # Exports agent factory methods
│   ├── researcher.py             # Agent 1: Market Intelligence Specialist
│   ├── strategist.py             # Agent 2: Business & Growth Strategist
│   ├── financial_analyst.py      # Agent 3: Financial & Risk Analyst
│   └── reviewer.py               # Agent 4: Executive Reviewer & QA Partner
├── tasks/                        # Consulting tasks & dependencies
│   ├── __init__.py               # Exports tasks factory method
│   └── consulting_tasks.py       # Sequential task definitions & context passing
├── config.py                     # Groq LLM setup, secrets resolution & health check
├── crew.py                       # CrewAI assembly & pipeline execution
├── app.py                        # Modern Streamlit Cloud user interface
├── requirements.txt              # Pinned, tested production dependencies
└── .gitignore                    # Protects secrets, cache, and virtual environments
```

---

## 🚀 Deployment: Code ➔ GitHub ➔ Streamlit Cloud

Follow this direct flow to deploy your application to Streamlit Cloud without needing local setup:

### Step 1: Push Code to GitHub

1. Initialize git and commit the code (the `.gitignore` is already configured to keep your secrets private):
   ```bash
   git init
   git add .
   git commit -m "feat: initial commit of multi-agent business consulting team"
   ```

2. Create a new repository on [GitHub](https://github.com/new) (e.g. `business-consulting-crew`).

3. Link and push your code:
   ```bash
   git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPOSITORY>.git
   git branch -M main
   git push -u origin main
   ```

---

### Step 2: Deploy on Streamlit Cloud

1. Log in to [Streamlit Community Cloud](https://share.streamlit.io).
2. Click **"Create app"** (or **"New app"**).
3. Select your GitHub repository (`<YOUR_USERNAME>/<YOUR_REPOSITORY>`), branch (`main`), and set the main file path to:
   ```
   app.py
   ```
4. Click **"Advanced settings..."** before deploying.

---

### Step 3: Configure Streamlit Secrets

In the **Secrets** text box of your Streamlit Cloud app settings, paste your Groq API Key:

```toml
GROQ_API_KEY = "gsk_your_actual_groq_api_key_here"
```

*(Optional: You can also specify an override model)*
```toml
DEFAULT_MODEL = "openai/gpt-oss-120b"
```

5. Click **"Save"** and then **"Deploy!"**.
6. Streamlit Cloud will automatically install `requirements.txt` and launch your live consulting studio.

> **Note**: Even if you haven't set up secrets yet, the app includes a secure sidebar key input so you can test it immediately in your browser.

---

## 💻 Optional: Local Development / Testing

If you ever wish to test locally:

```bash
# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .streamlit/secrets.toml
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml and add your GROQ_API_KEY

# 4. Run the Streamlit application
streamlit run app.py
```

---

## 🌐 Live Web Research (DuckDuckGo Tool)

Unlike standard LLM-only pipelines that rely solely on outdated pre-training knowledge, the **Market Intelligence Specialist** agent is equipped with a real-time **DuckDuckGo Search Tool** (`tools/search_tool.py`).
- Searches live competitor websites, recent fundraising rounds, regulatory shifts, and industry benchmarks in real time.
- Requires **zero extra API keys** (utilizes DuckDuckGo's live web endpoints).
- Can be toggled on/off directly from the Streamlit UI sidebar.

---

## 🗄️ Supabase Cloud Storage (Optional Persistence)

The application includes plug-and-play **Supabase** persistence (`db_supabase.py`):
- **Automatic Archival**: Every generated consulting engagement is saved with timestamp, metadata, and full step-by-step agent outputs.
- **Report History Tab**: Browse, reload, and review past client advisory reports directly in the Streamlit UI.
- **Zero Lock-In / Optional**: If Supabase credentials are not provided, the app seamlessly runs using local session memory.

### Setting Up Supabase (1-Minute Setup):
1. Create a free project at [supabase.com](https://supabase.com).
2. Run this SQL in your Supabase SQL Editor:
```sql
create table consulting_reports (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  business_idea text,
  target_industry text,
  target_market text,
  budget_or_stage text,
  strategic_focus text,
  final_report text,
  step_outputs jsonb,
  model_used text,
  elapsed_time float
);
```
3. Add `SUPABASE_URL` and `SUPABASE_KEY` to your Streamlit Cloud Secrets.
