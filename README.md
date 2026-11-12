# Roundtree Agency — Contractor & Client Intelligence Dashboard

A custom financial analytics and audit intelligence dashboard built with Streamlit and Plotly for Roundtree Agency.

## Brand Styling
The dashboard is styled after Roundtree Agency digital brand identity:
- Primary Color: Deep Forest / Pine (#1B3B36)
- Secondary Color: Warm Clay / Terracotta (#C2593F)
- Neutral: Warm Sand (#F4F1EA), Off-white (#FAF8F5)
- Typography: Playfair Display serif headers with Plus Jakarta Sans body font.

## Features Included
1. Executive Scorecard: KPIs tracking subcontractor spend, production hours, and blended rates.
2. Client Analytics & Donut Charts: Interactive donut charts showing Share of Spend vs Share of Hours.
3. Designer Profile Cards: Capacity cards for each freelancer displaying rate, hours, and client badges.
4. Contractor Utilization & Client Dependency Matrix: Heatmap highlighting contractor distribution.
5. Monthly Burn Rate & Spend Velocity Tracking: Monthly spend by client with moving-average velocity.
6. Master Ledger Explorer: Filterable audit ledger with exact verbatim task descriptions and CSV export.
7. Smart Ingestion & Staging Review: Drag-and-drop new invoices and review client tags before committing.

## Deployment Instructions

### Option 1: Run Locally
1. Install dependencies:
   pip install -r requirements.txt
2. Run the application:
   streamlit run app.py

### Option 2: Deploy to Streamlit Cloud
1. Push the files in this folder to your repository.
2. In your cloud dashboard, connect your repo, set the main file path to app.py, and click Deploy.
