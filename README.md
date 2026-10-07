# VulnX

> Automated web vulnerability scanning and reconnaissance toolkit for security testing.

VulnX is a cybersecurity tool built to automate common web reconnaissance and vulnerability discovery workflows. It combines security checks, reconnaissance, and scan results into a single workflow.

## Features

- 🔎 Web reconnaissance
- 🛡️ Automated vulnerability checks
- ⚡ XSS testing
- 🔐 SSL/TLS certificate analysis
- 📊 Scan result visualization
- 🤖 Automated security testing workflow
- 💾 SQLite-based result storage

## Tech Stack

- **Frontend:** React, Vite
- **Backend:** Python, Flask
- **Database:** SQLite
- **Security:** Web reconnaissance, XSS testing, SSL/TLS analysis
- **Environment:** Linux

## Workflow

```text
Target
  ↓
Reconnaissance
  ↓
Service & Endpoint Discovery
  ↓
Security Checks
  ↓
Vulnerability Analysis
  ↓
Results


Installation
git clone https://github.com/AnuragR3k/vulnx.git
cd vulnx

Backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py

Frontend
cd frontend
npm install
npm run dev

Use Cases
- Web application security testing
- Bug bounty reconnaissance
- Vulnerability assessment
- Security research
- Learning web application security
- Automating repetitive security workflows
Roadmap
- [ ] More vulnerability detection modules
- [ ] Improved reconnaissance
- [ ] Automated security reports
- [ ] Better scan visualization
- [ ] Parallel scanning
- [ ] Docker support
Disclaimer
VulnX is intended for authorized security testing, research, and educational purposes only.
Only scan systems that you own or have explicit permission to test.
Author
Anurag
