#!/usr/bin/env python3
"""generate_readme.py
Utility to auto‑generate a detailed README.md for the AI Reputation Monitoring Agent project.
It extracts package information, imports, top‑level docstrings and builds a markdown file using a Jinja2 template.
Usage:
    python generate_readme.py   # creates README.md in the current directory
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict

# ---------- Helper Functions ----------

def extract_docstring(file_path: Path) -> str:
    """Return the first top‑level docstring from a Python file, or an empty string."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return ""
    # Look for triple‑quoted strings at the very start of the file
    match = re.search(r"^\s*([']{3})(.*?)\1", content, re.DOTALL)
    return match.group(2).strip() if match else ""

def collect_modules(src_dir: Path) -> List[Dict[str, str]]:
    """Walk the source directory and collect module names with their docstrings."""
    modules = []
    for py_file in src_dir.rglob("*.py"):
        # Skip test files and virtual‑env artefacts
        if py_file.name.startswith("test_") or "site-packages" in str(py_file):
            continue
        rel_path = py_file.relative_to(src_dir)
        module_name = ".".join(rel_path.with_suffix("").parts)
        doc = extract_docstring(py_file)
        modules.append({"name": module_name, "doc": doc})
    return modules

def load_requirements(req_path: Path) -> List[str]:
    """Parse a requirements.txt file into a list of package specifications."""
    if not req_path.exists():
        return []
    return [line.strip() for line in req_path.read_text().splitlines() if line.strip() and not line.startswith("#")]

# ---------- Jinja2 Template ----------
TEMPLATE = """# AI Reputation Monitoring Agent

## 📖 Project Overview
{{ overview }}

## 🏗️ Architecture
{{ architecture_diagram }}

## 🔧 Tech Stack
{% for tech in tech_stack %}- **{{ tech.category }}**: {{ tech.items | join(", ") }}
{% endfor %}

## 📦 Installation & Quick‑Start
```bash
# Clone the repository
git clone https://github.com/smuhammadtaha3/Reputation-Monitoring-Agent.git
cd Reputation-Monitoring-Agent

# Create a virtual environment
python -m venv .venv && ./.venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt

# Set required environment variables (Railway or .env)
# GROQ_API_KEY, SUPABASE_URL, SUPABASE_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

# Run the API server
uvicorn app.main:app --reload

# In another terminal start the worker
celery -A app.worker worker -B
```

## 📚 Modules & Docstrings
{% for mod in modules %}### {{ mod.name }}
{{ mod.doc or "*No module‑level docstring.*" }}

{% endfor %}

## 📃 Dependencies
```
{{ dependencies | join('\n') }}
```

## 🚀 Future Roadmap
{{ roadmap }}
"""

def main():
    project_root = Path(__file__).parent
    src_dir = project_root / "app"
    req_file = project_root / "requirements.txt"

    overview = "An automated system that monitors online reviews, classifies sentiment with RoBERTa, generates LLaMA‑based response drafts, and notifies via Telegram."
    architecture_diagram = "(see architecture diagram in README)"
    tech_stack = [
        {"category": "API", "items": ["FastAPI", "Uvicorn", "Pydantic"]},
        {"category": "NLP", "items": ["HuggingFace Transformers", "RoBERTa (cardiffnlp/twitter-roberta-base-sentiment)"]},
        {"category": "Generative AI", "items": ["Groq API", "LLaMA 3.3 70B"]},
        {"category": "Data", "items": ["Supabase (PostgreSQL)", "SQLAlchemy"]},
        {"category": "Queue", "items": ["Celery", "Redis (Upstash)"]},
        {"category": "Alerts", "items": ["python‑telegram‑bot"]},
        {"category": "Deployment", "items": ["Railway", "Docker"]},
    ]
    modules = collect_modules(src_dir)
    dependencies = load_requirements(req_file)
    roadmap = "* Phase 2 – Real‑data connectors (Google Places, Yelp)\n* Phase 3 – Analytics (Pandas, dashboards)\n* Phase 4 – React UI\n* Phase 5 – Custom model fine‑tuning"

    # Render the template (simple replacement – no external Jinja2 needed)
    from string import Template
    tmpl = Template(TEMPLATE)
    rendered = tmpl.substitute(
        overview=overview,
        architecture_diagram=architecture_diagram,
        tech_stack=json.dumps(tech_stack, indent=2),
        modules=json.dumps(modules, indent=2),
        dependencies=dependencies,
        roadmap=roadmap,
    )
    # Write the README
    readme_path = project_root / "README_generated.md"
    readme_path.write_text(rendered, encoding="utf-8")
    print(f"Generated {readme_path}")

if __name__ == "__main__":
    main()
""
