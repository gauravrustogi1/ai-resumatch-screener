# Job Match Agent
### An autonomous job-hunting agent built from scratch in Python

---

## What This Does

This agent runs locally on your machine and automates the most tedious part of job hunting — reading through dozens of recruiter emails, visiting each job posting, and figuring out which ones are actually worth your time.

Every morning, run it once. It:

1. Connects to your Yahoo Mail inbox via IMAP
2. Finds unread emails from iimjobs.com
3. Extracts job posting links from each email (handles 4 different iimjobs email formats)
4. Opens each job page using a real browser (Playwright) — authenticated with your session
5. Skips jobs you've already applied to
6. Scrapes the full Job Description from each posting
7. Sends your resume + each JD to a local LLM (Ollama) for intelligent scoring
8. Generates a dated HTML report sorted by match score, saved to `./reports/` in YYYYMMDD.html name format
9. Marks processed emails as read so you never see the same jobs twice

---

## Why I Built This

Built as a **learning project** to understand how AI agents actually work under the hood — without using AI code generation tools. Every line of code was written and understood by hand, referencing documentation and debugging real errors. The goal was to go from "I've done Python tutorials" to "I built a working agent" — and understand what that actually means technically.

This project deliberately avoids frameworks like CrewAI or LangChain to expose the real mechanics: IMAP protocol, browser automation, HTML parsing, LLM API integration, and prompt engineering — all wired together manually.

---

## Pipeline Architecture

```
Yahoo Mail (IMAP)
        │
        ▼
Filter UNSEEN emails from iimjobs.com
        │
        ▼
Parse email HTML → Extract job URLs
(handles 4 email format types, deduplicates across emails)
        │
        ▼
Playwright Browser (authenticated session)
        ├── Check: Already Applied? → Skip
        └── Scrape full Job Description
        │
        ▼
Local LLM via Ollama
(resume.md + JD → score 1-10 + match analysis)
        │
        ▼
HTML Report → ~/Downloads/JobAgent/YYYYMMDD.html
        │
        ▼
Mark processed emails as Read (IMAP UID store)
```

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.13 |
| Email | `imaplib` (IMAP4 SSL, UID-based) |
| HTML Parsing | BeautifulSoup4 |
| Browser Automation | Playwright (sync API, persistent auth) |
| AI Scoring | Ollama (local LLM — `llama3.1:8b` or similar) |
| Secrets | `python-dotenv` |
| Report | Pure Python HTML generation |

---

## Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com) installed and running locally
- A local LLM pulled: `ollama pull llama3.1:8b` (or any model of your choice)
- Yahoo Mail with IMAP enabled + App Password generated
- Node.js (for Playwright browser installation)

---

## Setup

**1. Clone and create virtual environment**
```bash
git clone https://github.com/gauravrustogi1/ai-resumatch-screener.git
cd jobagent
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
playwright install chromium
```

**3. Configure environment**

Create a `.env` file in the project root:
```
YAHOO_EMAIL=your_email@yahoo.com
YAHOO_APP_PASSWORD=your_16_char_app_password
AI_PROVIDER=ollama
```

To generate a Yahoo App Password:
- Go to [account.yahoo.com](https://account.yahoo.com) → Security → Generate App Password
- Name it `JobAgent` and save the 16-character password

**4. Set up browser authentication**

Run the one-time auth setup to save your iimjobs.com session:
```bash
python save_auth.py
```
A browser window will open — log in to iimjobs.com manually, then press Enter in the terminal.

**5. Add your resume**

Create a `resume.md` file in the project root with your resume in Markdown format. This is what the LLM compares against each job description.

---

## Running the Agent

```bash
python main.py
```

Output:
- Progress dots for scraping (`.` per job)
- Progress bars for AI scoring (`|` per scored job)
- Summary of skipped/failed jobs
- HTML report path printed at the end

Open the report in your browser:
```
file:///path/to/your/repo/reports/20260617.html
```

---

## HTML Report

The report is sorted by overall match score (highest first). Each row shows:

- **Score badge** — colour-coded (green ≥8, yellow ≥6, red <6)
- **Job title** — clickable link to the actual posting
- **Expand button** — reveals email metadata, what matches your profile, what's missing

---

## Currently Supports

- **iimjobs.com** — all 4 email formats (job digest, single job alert, unpublished notifications, post-application recommendations)

## Extending to Other Portals

The architecture is deliberately modular. To add LinkedIn, Naukri, or any other job portal:

1. Add a new IMAP search filter in `getEmailsFromIMAP()` for that sender
2. Add link extraction logic in `filterLinks()` for that portal's URL structure
3. Add CSS selectors in `scraper.py` for that portal's JD page structure
4. Everything else (scoring, reporting, marking as read) works as-is

---

## Project Structure

```
jobagent/
├── main.py              # Orchestration — pipeline entry point
├── scraper.py           # Playwright browser automation + JD extraction
├── ai_scorer.py         # Ollama LLM integration + prompt + JSON parsing
├── report_generator.py  # HTML report generation + file saving
├── save_auth.py         # One-time browser auth setup
├── resume.md            # Your resume (gitignored — add your own)
├── .env                 # Secrets (gitignored)
├── auth.json            # Browser session (gitignored)
└── requirements.txt     # Python dependencies
```

---

## What I Learned Building This

- **IMAP protocol** — IMAP4 SSL, UID vs sequence numbers, PEEK fetching, flag manipulation
- **Email parsing** — multipart MIME, quoted-printable encoding, BeautifulSoup HTML traversal
- **Browser automation** — Playwright session persistence, JS-rendered pages, CSS selector fallbacks, timeout handling
- **Prompt engineering** — structured JSON output, handling LLM non-compliance, validation patterns
- **Agent design** — the difference between a script and an agent; what "agentic" actually means at the code level
- **Python practices** — type hints, list comprehensions, virtual environments, `.env` secrets management, modular design

---

## Limitations

- Yahoo Mail only (IMAP credentials required)
- iimjobs.com only out of the box (extensible — see above)
- Local LLM quality depends on model choice — larger models give better scoring accuracy
- iimjobs CSS selectors may break if they redesign their job pages (two fallback selectors included)
- Browser session (`auth.json`) expires periodically — re-run `save_auth.py` when it does

---

## Author

**Gaurav Rustogi** — Engineering Leader with 20+ years experience  
[linkedin.com/in/gauravrustogi](https://linkedin.com/in/gauravrustogi)

---

*Built from scratch as a Python learning project. No AI code generation tools were used in writing this codebase — every line was written by hand to ensure genuine understanding of each component.*
