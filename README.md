# 🏪 Digital Health Checker for Local Businesses

A free Python tool that audits how visible a local business is online —
gives a score out of 100 and generates a PDF report with actionable tips.

---

## 📁 Project Structure

```
digital_health_checker/
│
├── app.py          ← Run this file to start the program
├── checker.py      ← All the "checking" logic (Google, website, social)
├── report.py       ← PDF report generator
├── requirements.txt← List of packages to install
├── README.md       ← This file
└── output/         ← PDFs get saved here (created automatically)
```

---

## ⚙️ Setup (One-Time)

1. **Make sure Python is installed** (Python 3.8 or newer):
   ```bash
   python --version
   ```

2. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 How to Run

```bash
python app.py
```

Then answer the prompts:
```
Business Name: Sharma Cafe
City: Mumbai
Website URL (press Enter to skip): https://sharmacafe.com
```

The tool will:
1. ✅ Search Google for the business
2. ✅ Check the website speed, security, and mobile-friendliness
3. ✅ Check social media presence
4. ✅ Calculate a score out of 100
5. ✅ Save a PDF report in the `output/` folder

---

## 📊 How Scoring Works

| Category        | Max Points | What it checks |
|----------------|------------|----------------|
| Google Presence | 40 pts     | Appears in search + Knowledge Panel |
| Website Health  | 40 pts     | Speed, HTTPS, mobile, contact info |
| Social Media    | 20 pts     | Facebook, Instagram, Twitter |
| **Total**       | **100 pts**| |

**Grades:**
- 80–100 → **A** — Excellent
- 60–79  → **B** — Good
- 40–59  → **C** — Average
- 20–39  → **D** — Poor
- 0–19   → **F** — Critical

---

## 🛠️ How to Use in Your Own Code

```python
from checker import run_full_audit
from report import generate_pdf_report

# Run the audit
audit = run_full_audit("Sharma Cafe", "Mumbai", "https://sharmacafe.com")

# Print the score
print(audit["score"]["total"])  # e.g. 72

# Generate PDF
pdf_path = generate_pdf_report(audit, "./output")
print(f"Report saved at: {pdf_path}")
```

---

## 📦 Dependencies

- `requests` — HTTP requests
- `beautifulsoup4` — HTML parsing
- `reportlab` — PDF generation

---

## 💡 Ideas to Extend This Project

- Add a **Streamlit web UI** so non-technical users can use it via browser
- Add **WhatsApp/email delivery** of the PDF report
- Add a **database** to track multiple businesses over time
- Add **Google Maps API** to pull real ratings and review count
- Build it into a **freelance service** for local businesses

---

*Built with Python 🐍 | A beginner-friendly real-world project*
