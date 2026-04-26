📊 Groww Weekly Product Pulse Engine

This project transforms recent App Store & Play Store reviews into a one-page weekly product pulse with actionable insights.

It helps Product, Growth, and Support teams quickly understand what users are experiencing and what to fix next.

🚀 How to Run
python pulse.py run --product groww --weeks 8
Inputs
Public review dataset (CSV)
Fields required:
rating
title
text
date
Output
One-page weekly pulse (Markdown/PDF)
Email draft (text)
⚙️ Pipeline Overview
Import Reviews
Load App Store & Play Store reviews (last 8–12 weeks)
Preprocessing
Clean text
Remove noise / invalid entries
Ensure no PII
Embedding Generation
Convert reviews into vector representations
Theme Clustering (max 5)
Group similar reviews into key themes using clustering
Theme Summarization
Generate concise descriptions for each theme
Quote Extraction
Select representative real user quotes
Weekly Note Generation
Create a ≤250 word scannable summary:
Top themes
User quotes
Action ideas
Email Draft Generation
Convert the note into a ready-to-send email
🧠 Theme Legend (Example)
Theme 1 → KYC / Verification Issues
Theme 2 → App Performance / Lag
Theme 3 → Withdrawals / Payments
Theme 4 → UI / UX Feedback
Theme 5 → Customer Support

(Themes are dynamically generated per run)

📄 Sample Output Structure
Top Themes:
1. KYC delays
2. App performance issues
3. Withdrawal delays

User Quotes:
- “KYC stuck for days…”
- “App freezes during trading…”
- “Withdrawal took too long…”

Action Ideas:
- Improve KYC turnaround time
- Optimize performance during peak hours
- Add better withdrawal tracking
⚠️ Constraints Followed
✅ Uses public review data only
✅ Max 5 themes
✅ Output ≤ 250 words
✅ No PII included (no usernames/emails/IDs)
✅ Scannable, decision-ready format
🛠️ Tech Stack
Python
Embeddings + Clustering (UMAP / similar)
LLM (via LiteLLM / Groq / OpenAI)
Pandas / NumPy
🔁 Re-running for a New Week

To generate a fresh pulse:

python pulse.py run --product groww --weeks 4
Adjust --weeks based on required timeframe
Replace input CSV with updated review data
💡 Key Learnings
User feedback is noisy → clustering is critical
Prompt design directly impacts insight quality
Simplicity in output > complexity in pipeline
📦 Deliverables Included
Weekly pulse (MD/PDF)
Email draft
Reviews dataset (sample/redacted)
Working script (pulse.py)
