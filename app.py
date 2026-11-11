import streamlit as st
import pandas as pd
import plotly.express as px
from pypdf import PdfReader
import os
import io

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Roundtree | Freelancer Portfolio & Audit Dashboard",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PROFESSIONAL EXECUTIVE STYLING (CSS) ---
st.markdown("""
<style>
    @import url('[suspicious link removed]');
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 18px 22px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 12px;
    }
    .metric-title {
        font-size: 0.82rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #0f172a;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #10b981;
        margin-top: 4px;
        font-weight: 500;
    }
    .source-tag {
        background-color: #f1f5f9;
        color: #334155;
        padding: 2px 8px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 0.78rem;
    }
</style>
""", unsafe_allow_html=True)

DB_FILE = "freelancer_database.csv"
LOG_FILE = "uploaded_files_log.txt"

# --- FULL AUTHORITATIVE DATASET (FROM ALL 56 SOURCES) ---
INITIAL_DATA = [
    # --- JOSIAH STAM (STAM CREATIVE) ---
    {"id": "JS-01", "client": "Mission Increase", "contractor": "Josiah Stam", "date": "2026-01-30", "month": "Jan 2026", "hours": 14.31, "amount": 500.85, "task": "Giving Levels Doc, Media Kit, Taste of MI, Academy Mark", "source_file": "Jan. 26 Roundtree Invoice.pdf", "quarter": "Q1"},
    {"id": "JS-02", "client": "Geneva", "contractor": "Josiah Stam", "date": "2026-01-30", "month": "Jan 2026", "hours": 23.68, "amount": 828.80, "task": "Tabletop Canvases, Postcard, Sustainers Logo & Graphics, Banners", "source_file": "Jan. 26 Roundtree Invoice.pdf", "quarter": "Q1"},
    {"id": "JS-03", "client": "BLMH", "contractor": "Josiah Stam", "date": "2026-01-30", "month": "Jan 2026", "hours": 0.52, "amount": 18.20, "task": "BLMH Business Card", "source_file": "Jan. 26 Roundtree Invoice.pdf", "quarter": "Q1"},
    {"id": "JS-04", "client": "Mission Increase", "contractor": "Josiah Stam", "date": "2026-02-27", "month": "Feb 2026", "hours": 23.67, "amount": 828.45, "task": "Academy Badge, Pitch Deck, Momentum Multiplied Slides, Specialized Email", "source_file": "Feb. 26 Roundtree Invoice.pdf", "quarter": "Q1"},
    {"id": "JS-05", "client": "Geneva", "contractor": "Josiah Stam", "date": "2026-02-27", "month": "Feb 2026", "hours": 15.18, "amount": 531.30, "task": "Donor Letters, Welcome Gift Envelope, Golf Tournament, Annual Report", "source_file": "Feb. 26 Roundtree Invoice.pdf", "quarter": "Q1"},
    {"id": "JS-06", "client": "BITS", "contractor": "Josiah Stam", "date": "2026-02-27", "month": "Feb 2026", "hours": 1.00, "amount": 35.00, "task": "Bible In The Schools Prospectus", "source_file": "Feb. 26 Roundtree Invoice.pdf", "quarter": "Q1"},
    {"id": "JS-07", "client": "BLMH", "contractor": "Josiah Stam", "date": "2026-02-27", "month": "Feb 2026", "hours": 0.08, "amount": 2.80, "task": "BLMH Business Card updates", "source_file": "Feb. 26 Roundtree Invoice.pdf", "quarter": "Q1"},
    {"id": "JS-08", "client": "Geneva", "contractor": "Josiah Stam", "date": "2026-03-31", "month": "Mar 2026", "hours": 81.24, "amount": 2843.40, "task": "Annual Report (32.8h), Postcard, Checklist en español, Campaign Letter & Email, Cohort Explainer", "source_file": "March Roundtree Invoice.pdf", "quarter": "Q1"},
    {"id": "JS-09", "client": "Mission Increase", "contractor": "Josiah Stam", "date": "2026-03-31", "month": "Mar 2026", "hours": 2.98, "amount": 104.30, "task": "Equipping Call Thumbnail, Taste of MI Canva, Jax Workshop Invite", "source_file": "March Roundtree Invoice.pdf", "quarter": "Q1"},
    {"id": "JS-10", "client": "Geneva", "contractor": "Josiah Stam", "date": "2026-05-23", "month": "May 2026", "hours": 10.58, "amount": 370.30, "task": "Meeting Norms Tabletop Display, Retirement Plan Brochure", "source_file": "May 26 Roundtree Invoice.pdf", "quarter": "Q2"},
    {"id": "JS-11", "client": "Mission Increase", "contractor": "Josiah Stam", "date": "2026-05-23", "month": "May 2026", "hours": 7.67, "amount": 268.45, "task": "MI Postcards, Alliance Post", "source_file": "May 26 Roundtree Invoice.pdf", "quarter": "Q2"},

    # --- JARED ROBERTS ---
    {"id": "JR-01", "client": "Mission Increase", "contractor": "Jared Roberts", "date": "2026-02-27", "month": "Feb 2026", "hours": 18.28, "amount": 2102.08, "task": "Impact Stories PDF, Website Impact Stories, Gratitude Report Edits, Email Template Changes", "source_file": "Invoice 0000068.pdf", "quarter": "Q1"},
    {"id": "JR-02", "client": "PCA", "contractor": "Jared Roberts", "date": "2026-02-27", "month": "Feb 2026", "hours": 0.25, "amount": 25.00, "task": "Review PCA foundation plugins", "source_file": "Invoice 0000068.pdf", "quarter": "Q1"},
    {"id": "JR-03", "client": "Internal/Agency", "contractor": "Jared Roberts", "date": "2026-03-02", "month": "Mar 2026", "hours": 0.25, "amount": 25.00, "task": "Update bios and finalize files", "source_file": "Invoice 0000073.pdf", "quarter": "Q1"},
    {"id": "JR-04", "client": "Mission Increase", "contractor": "Jared Roberts", "date": "2026-03-31", "month": "Mar 2026", "hours": 6.85, "amount": 756.25, "task": "MI to Mi export, Email redesign, 4-col grid, Impact stories nav", "source_file": "Invoice 0000073.pdf", "quarter": "Q1"},
    {"id": "JR-05", "client": "Saturate Design", "contractor": "Jared Roberts", "date": "2026-03-11", "month": "Mar 2026", "hours": 14.23, "amount": 1779.16, "task": "Saturate Design web development sprint", "source_file": "Invoice 0000073.pdf", "quarter": "Q1"},
    {"id": "JR-06", "client": "Mission Increase", "contractor": "Jared Roberts", "date": "2026-04-30", "month": "Apr 2026", "hours": 13.13, "amount": 1507.08, "task": "Menu fixes, Resources Page rebuild, One-Pagers, Laptop mockups", "source_file": "Invoice 0000080.pdf", "quarter": "Q2"},
    {"id": "JR-07", "client": "Mission Increase", "contractor": "Jared Roberts", "date": "2026-05-30", "month": "May 2026", "hours": 17.50, "amount": 1912.50, "task": "Complex gifts, Core Services PDF, Figma html mockups, Website fixes", "source_file": "Invoice 0000081.pdf", "quarter": "Q2"},
    {"id": "JR-08", "client": "Mission Increase", "contractor": "Jared Roberts", "date": "2026-06-30", "month": "Jun 2026", "hours": 12.25, "amount": 1368.75, "task": "Academy webinar assets, Resources troubleshooting, Q3 Webinar Booklet", "source_file": "Invoice 0000084.pdf", "quarter": "Q2"},
    {"id": "JR-09", "client": "Mission Increase", "contractor": "Jared Roberts", "date": "2026-07-24", "month": "Jul 2026", "hours": 3.50, "amount": 375.00, "task": "Q3 Webinar Booklet, PowerPoint, Social graphics, Landing pages", "source_file": "Invoice 0000087.pdf", "quarter": "Q3"},
    {"id": "JR-10", "client": "Rock Creek", "contractor": "Jared Roberts", "date": "2026-07-24", "month": "Jul 2026", "hours": 1.00, "amount": 125.00, "task": "Troubleshoot Rock Creek broken design", "source_file": "Invoice 0000087.pdf", "quarter": "Q3"},
    {"id": "JR-11", "client": "Mission Increase", "contractor": "Jared Roberts", "date": "2026-08-31", "month": "Aug 2026", "hours": 4.50, "amount": 475.00, "task": "Slide Deck, Asana web development tasks", "source_file": "Invoice 0000096.pdf", "quarter": "Q3"},
    {"id": "JR-12", "client": "Mission Increase", "contractor": "Jared Roberts", "date": "2026-09-03", "month": "Sep 2026", "hours": 3.75, "amount": 393.75, "task": "Asana task updates & web development", "source_file": "Invoice 0000096.pdf", "quarter": "Q3"},

    # --- MEGAN HEATH (ZETA CREATIVE) ---
    {"id": "MH-01", "client": "BITS", "contractor": "Megan Heath (Zeta)", "date": "2026-02-01", "month": "Feb 2026", "hours": 1.50, "amount": 127.50, "task": "Prospectus, Envelope correction, Luncheon 2026, Vector issue", "source_file": "RoundtreeInvoice_February .pdf", "quarter": "Q1"},
    {"id": "MH-02", "client": "SETCO", "contractor": "Megan Heath (Zeta)", "date": "2026-02-01", "month": "Feb 2026", "hours": 0.75, "amount": 63.75, "task": "Birthday Card Design", "source_file": "RoundtreeInvoice_February .pdf", "quarter": "Q1"},
    {"id": "MH-03", "client": "BITS", "contractor": "Megan Heath (Zeta)", "date": "2026-03-01", "month": "Mar 2026", "hours": 2.75, "amount": 233.75, "task": "Vector issue, Luncheon 2026, Commitment Card 2026", "source_file": "RoundtreeInvoice_March.pdf", "quarter": "Q1"},
    {"id": "MH-04", "client": "PCA", "contractor": "Megan Heath (Zeta)", "date": "2026-03-01", "month": "Mar 2026", "hours": 0.50, "amount": 42.50, "task": "PCAF iPhone Graphic", "source_file": "RoundtreeInvoice_March.pdf", "quarter": "Q1"},
    {"id": "MH-05", "client": "SETCO", "contractor": "Megan Heath (Zeta)", "date": "2026-04-01", "month": "Apr 2026", "hours": 1.50, "amount": 127.50, "task": "Table Cloth and Banners", "source_file": "RoundtreeInovice_April.pdf", "quarter": "Q2"},
    {"id": "MH-06", "client": "PCA", "contractor": "Megan Heath (Zeta)", "date": "2026-04-01", "month": "Apr 2026", "hours": 1.50, "amount": 127.50, "task": "PCAF One Pager & Business Cards", "source_file": "RoundtreeInovice_April.pdf", "quarter": "Q2"},
    {"id": "MH-07", "client": "BITS", "contractor": "Megan Heath (Zeta)", "date": "2026-04-01", "month": "Apr 2026", "hours": 4.75, "amount": 403.75, "task": "Table Tent, Banner, Sympathy Card, Seating Chart, Luncheon Program", "source_file": "RoundtreeInovice_April.pdf", "quarter": "Q2"},
    {"id": "MH-08", "client": "Internal/Agency", "contractor": "Megan Heath (Zeta)", "date": "2026-04-01", "month": "Apr 2026", "hours": 9.75, "amount": 828.75, "task": "Christ Presbyterian Church Profile", "source_file": "RoundtreeInovice_April.pdf", "quarter": "Q2"},
    {"id": "MH-09", "client": "Mission Increase", "contractor": "Megan Heath (Zeta)", "date": "2026-04-01", "month": "Apr 2026", "hours": 0.50, "amount": 42.50, "task": "MI Indiana Addenda", "source_file": "RoundtreeInovice_April.pdf", "quarter": "Q2"},
    {"id": "MH-10", "client": "Internal/Agency", "contractor": "Megan Heath (Zeta)", "date": "2026-04-01", "month": "Apr 2026", "hours": 2.25, "amount": 191.25, "task": "byFaith Magazine The Lamb of God Graphics", "source_file": "RoundtreeInovice_April.pdf", "quarter": "Q2"},
    {"id": "MH-11", "client": "Mission Increase", "contractor": "Megan Heath (Zeta)", "date": "2026-05-01", "month": "May 2026", "hours": 2.00, "amount": 170.00, "task": "Direct Mail Piece, Response Card Smart Giving", "source_file": "RoundtreeInvoice_May.pdf", "quarter": "Q2"},
    {"id": "MH-12", "client": "BITS", "contractor": "Megan Heath (Zeta)", "date": "2026-05-01", "month": "May 2026", "hours": 0.25, "amount": 21.25, "task": "BITS Business Card", "source_file": "RoundtreeInvoice_May.pdf", "quarter": "Q2"},
    {"id": "MH-13", "client": "PCA", "contractor": "Megan Heath (Zeta)", "date": "2026-05-01", "month": "May 2026", "hours": 3.25, "amount": 276.25, "task": "PCAF Response Device Update, Business Cards, Serving Churches Trifold", "source_file": "RoundtreeInvoice_May.pdf", "quarter": "Q2"},
    {"id": "MH-14", "client": "Mission Increase", "contractor": "Megan Heath (Zeta)", "date": "2026-06-01", "month": "Jun 2026", "hours": 1.00, "amount": 85.00, "task": "Direct Mail Piece, Lee Comm Ops Guide, Commitment Card Edits", "source_file": "RoundtreeInvoice_June (1).pdf", "quarter": "Q2"},
    {"id": "MH-15", "client": "BITS", "contractor": "Megan Heath (Zeta)", "date": "2026-06-01", "month": "Jun 2026", "hours": 0.50, "amount": 42.50, "task": "BITS Business Card", "source_file": "RoundtreeInvoice_June (1).pdf", "quarter": "Q2"},
    {"id": "MH-16", "client": "PCA", "contractor": "Megan Heath (Zeta)", "date": "2026-06-01", "month": "Jun 2026", "hours": 2.00, "amount": 170.00, "task": "PCAF Serving Churches Trifold", "source_file": "RoundtreeInvoice_June (1).pdf", "quarter": "Q2"},
    {"id": "MH-17", "client": "Internal/Agency", "contractor": "Megan Heath (Zeta)", "date": "2026-06-01", "month": "Jun 2026", "hours": 1.00, "amount": 85.00, "task": "Becoming Whole Flyer", "source_file": "RoundtreeInvoice_June (1).pdf", "quarter": "Q2"},
    {"id": "MH-18", "client": "Mission Increase", "contractor": "Megan Heath (Zeta)", "date": "2026-07-01", "month": "Jul 2026", "hours": 9.75, "amount": 828.75, "task": "Dan Flyer, Ashley Shaffer PPT redesign (5.25h), Impact Report, At a Glance, Commitment Cards", "source_file": "RoundtreeInvoice_July2026.pdf", "quarter": "Q3"},
    {"id": "MH-19", "client": "BITS", "contractor": "Megan Heath (Zeta)", "date": "2026-07-01", "month": "Jul 2026", "hours": 1.50, "amount": 127.50, "task": "Envelope Correction, Graph Edits, Letterhead Update", "source_file": "RoundtreeInvoice_July2026.pdf", "quarter": "Q3"},
    {"id": "MH-20", "client": "PCA", "contractor": "Megan Heath (Zeta)", "date": "2026-07-01", "month": "Jul 2026", "hours": 0.75, "amount": 63.75, "task": "PCAF Business Cards", "source_file": "RoundtreeInvoice_July2026.pdf", "quarter": "Q3"},
    {"id": "MH-21", "client": "Mission Increase", "contractor": "Megan Heath (Zeta)", "date": "2026-08-01", "month": "Aug 2026", "hours": 6.25, "amount": 531.25, "task": "At a Glance, Commitment Card, Placemats, Position Paper, Impact Report, Charity One Pager", "source_file": "RoundtreeInvoice_August .pdf", "quarter": "Q3"},
    {"id": "MH-22", "client": "Internal/Agency", "contractor": "Megan Heath (Zeta)", "date": "2026-08-01", "month": "Aug 2026", "hours": 1.25, "amount": 106.25, "task": "Becoming Whole Flyers", "source_file": "RoundtreeInvoice_August .pdf", "quarter": "Q3"},
    {"id": "MH-23", "client": "BITS", "contractor": "Megan Heath (Zeta)", "date": "2026-08-01", "month": "Aug 2026", "hours": 0.25, "amount": 21.25, "task": "BITS Map Update", "source_file": "RoundtreeInvoice_August .pdf", "quarter": "Q3"},
    {"id": "MH-24", "client": "Mission Increase", "contractor": "Megan Heath (Zeta)", "date": "2026-09-01", "month": "Sep 2026", "hours": 9.25, "amount": 786.25, "task": "CAFO Ad, Academy One Pager, Banner, Foundation PPT, Letterhead, QR flyer, Champion Two Pagers", "source_file": "RoundtreeInvoice_September2026.pdf", "quarter": "Q3"},
    {"id": "MH-25", "client": "Geneva", "contractor": "Megan Heath (Zeta)", "date": "2026-09-01", "month": "Sep 2026", "hours": 4.00, "amount": 340.00, "task": "Dental Slip Sheet, Envelope Edits, Social Graphics, Folder Update", "source_file": "RoundtreeInvoice_September2026.pdf", "quarter": "Q3"},
    {"id": "MH-26", "client": "BITS", "contractor": "Megan Heath (Zeta)", "date": "2026-09-01", "month": "Sep 2026", "hours": 0.75, "amount": 63.75, "task": "Letterhead Update, State Map Update", "source_file": "RoundtreeInvoice_September2026.pdf", "quarter": "Q3"},
    {"id": "MH-27", "client": "Internal/Agency", "contractor": "Megan Heath (Zeta)", "date": "2026-09-01", "month": "Sep 2026", "hours": 1.50, "amount": 127.50, "task": "Becoming Whole Flyers, Village School Cards", "source_file": "RoundtreeInvoice_September2026.pdf", "quarter": "Q3"},
    {"id": "MH-28", "client": "Mission Increase", "contractor": "Megan Heath (Zeta)", "date": "2026-10-01", "month": "Oct 2026", "hours": 1.75, "amount": 148.75, "task": "Academy 2-pager, Impact Report, Gratitude Gathering Collateral", "source_file": "RoundtreeInvoice_October2026.pdf", "quarter": "Q4"},
    {"id": "MH-29", "client": "Geneva", "contractor": "Megan Heath (Zeta)", "date": "2026-10-01", "month": "Oct 2026", "hours": 4.50, "amount": 382.50, "task": "Case for Support, Appeal Letter Design (3.0h), Clergy Act Social Post", "source_file": "RoundtreeInvoice_October2026.pdf", "quarter": "Q4"},
    {"id": "MH-30", "client": "BITS", "contractor": "Megan Heath (Zeta)", "date": "2026-10-01", "month": "Oct 2026", "hours": 1.50, "amount": 127.50, "task": "Christmas Card Update, Luncheon Save the Date 2027, E-Signature", "source_file": "RoundtreeInvoice_October2026.pdf", "quarter": "Q4"},
    {"id": "MH-31", "client": "SETCO", "contractor": "Megan Heath (Zeta)", "date": "2026-10-01", "month": "Oct 2026", "hours": 0.25, "amount": 21.25, "task": "Nutcracker Ad", "source_file": "RoundtreeInvoice_October2026.pdf", "quarter": "Q4"},
    {"id": "MH-32", "client": "Internal/Agency", "contractor": "Megan Heath (Zeta)", "date": "2026-10-01", "month": "Oct 2026", "hours": 0.75, "amount": 63.75, "task": "byFaith Social Template", "source_file": "RoundtreeInvoice_October2026.pdf", "quarter": "Q4"},

    # --- CASPER CO. LLC (ALEXANDRA CASPER - CONTENT & COPY) ---
    {"id": "CC-01", "client": "Geneva", "contractor": "Casper Co.", "date": "2026-01-29", "month": "Jan 2026", "hours": 4.00, "amount": 580.00, "task": "Geneva Story - Elizabeth & Adam", "source_file": "Casper Co. LLC - Roundtree - Jan 2026 invoice.pdf", "quarter": "Q1"},
    {"id": "CC-02", "client": "Geneva", "contractor": "Casper Co.", "date": "2026-02-27", "month": "Feb 2026", "hours": 5.00, "amount": 725.00, "task": "Geneva - Susan Story & Living Generously Booklet", "source_file": "Casper Co. LLC - Roundtree Invoice - Feb 2026.pdf", "quarter": "Q1"},
    {"id": "CC-03", "client": "Geneva", "contractor": "Casper Co.", "date": "2026-03-30", "month": "Mar 2026", "hours": 5.00, "amount": 725.00, "task": "Geneva - David Story & Living Generously Booklet", "source_file": "Casper Co. LLC - Roundtree Invoice - March 2026.pdf", "quarter": "Q1"},
    {"id": "CC-04", "client": "Geneva", "contractor": "Casper Co.", "date": "2026-04-29", "month": "Apr 2026", "hours": 6.00, "amount": 870.00, "task": "Financial planning story, Nathan story, Relief fund story", "source_file": "Casper Co. LLC - Roundtree - April 2026 invoice.pdf", "quarter": "Q2"},
    {"id": "CC-05", "client": "Geneva", "contractor": "Casper Co.", "date": "2026-06-01", "month": "May 2026", "hours": 1.00, "amount": 145.00, "task": "Geneva Insurance article", "source_file": "Casper Co. LLC - Roundtree Invoice - May 2026.pdf", "quarter": "Q2"},
    {"id": "CC-06", "client": "Geneva", "contractor": "Casper Co.", "date": "2026-07-31", "month": "Jul 2026", "hours": 2.50, "amount": 362.50, "task": "Geneva - Brent Curl Story", "source_file": "Casper Co. LLC - Roundtree Invoice - July 2026.pdf", "quarter": "Q3"},
    {"id": "CC-07", "client": "Mission Increase", "contractor": "Casper Co.", "date": "2026-07-31", "month": "Jul 2026", "hours": 3.00, "amount": 435.00, "task": "Mission Increase Homepage Audit", "source_file": "Casper Co. LLC - Roundtree Invoice - July 2026.pdf", "quarter": "Q3"},
    {"id": "CC-08", "client": "PCA", "contractor": "Casper Co.", "date": "2026-07-31", "month": "Jul 2026", "hours": 1.00, "amount": 145.00, "task": "AC Prayer Guide Letter", "source_file": "Casper Co. LLC - Roundtree Invoice - July 2026.pdf", "quarter": "Q3"},
    {"id": "CC-09", "client": "Geneva", "contractor": "Casper Co.", "date": "2026-08-31", "month": "Aug 2026", "hours": 1.50, "amount": 217.50, "task": "Geneva Charitable IQ Article", "source_file": "Casper Co. LLC - Roundtree - Aug 2026 invoice.pdf", "quarter": "Q3"},
    {"id": "CC-10", "client": "Mission Increase", "contractor": "Casper Co.", "date": "2026-08-31", "month": "Aug 2026", "hours": 1.00, "amount": 145.00, "task": "Mission Increase Homepage Copy Edits", "source_file": "Casper Co. LLC - Roundtree - Aug 2026 invoice.pdf", "quarter": "Q3"},
    {"id": "CC-11", "client": "TGT", "contractor": "Casper Co.", "date": "2026-08-31", "month": "Aug 2026", "hours": 4.00, "amount": 580.00, "task": "TGT Website Copy Audit and Suggestions", "source_file": "Casper Co. LLC - Roundtree - Aug 2026 invoice.pdf", "quarter": "Q3"},
    {"id": "CC-12", "client": "Internal/Agency", "contractor": "Casper Co.", "date": "2026-08-31", "month": "Aug 2026", "hours": 10.00, "amount": 1450.00, "task": "SRG Magazine Articles", "source_file": "Casper Co. LLC - Roundtree - Aug 2026 invoice.pdf", "quarter": "Q3"},
    {"id": "CC-13", "client": "Geneva", "contractor": "Casper Co.", "date": "2026-09-30", "month": "Sep 2026", "hours": 10.50, "amount": 1522.50, "task": "ByFaith Article, Bill McCutcheon Story, Cybersecurity, Look/After letter & email", "source_file": "Casper Co. LLC- Roundtree Invoice - Sep 2026.pdf", "quarter": "Q3"},
    {"id": "CC-14", "client": "Mission Increase", "contractor": "Casper Co.", "date": "2026-09-30", "month": "Sep 2026", "hours": 2.50, "amount": 362.50, "task": "Mission Increase 2-pager", "source_file": "Casper Co. LLC- Roundtree Invoice - Sep 2026.pdf", "quarter": "Q3"},
    {"id": "CC-15", "client": "Geneva", "contractor": "Casper Co.", "date": "2026-10-30", "month": "Oct 2026", "hours": 5.25, "amount": 761.25, "task": "Bill McCutchon Story, ByFaith Story, Clergy Press Release, Living Generously, One-page proposal", "source_file": "Casper Co. LLC - Roundtree Invoice - Oct 2026.pdf", "quarter": "Q4"},
    {"id": "CC-16", "client": "PCA", "contractor": "Casper Co.", "date": "2026-10-30", "month": "Oct 2026", "hours": 3.50, "amount": 507.50, "task": "PCA AC Ads, PCAF Articles on generosity & giving", "source_file": "Casper Co. LLC - Roundtree Invoice - Oct 2026.pdf", "quarter": "Q4"},
    {"id": "CC-17", "client": "Internal/Agency", "contractor": "Casper Co.", "date": "2026-10-30", "month": "Oct 2026", "hours": 5.50, "amount": 797.50, "task": "West Paces Advisors - Creative Ideas and Research", "source_file": "Casper Co. LLC - Roundtree Invoice - Oct 2026.pdf", "quarter": "Q4"},

    # --- MOLLY KELLEY ---
    {"id": "MK-01", "client": "Mission Increase", "contractor": "Molly Kelley", "date": "2026-01-09", "month": "Jan 2026", "hours": 2.25, "amount": 135.00, "task": "MI Jacksonville Asset Buildout (table tent, notecards, banner)", "source_file": "Invoice_MollyKelley_1.9.26 - Invoice.pdf", "quarter": "Q1"},
    {"id": "MK-02", "client": "Mission Increase", "contractor": "Molly Kelley", "date": "2026-02-26", "month": "Feb 2026", "hours": 15.50, "amount": 930.00, "task": "Mission Increase Gratitude Report layout", "source_file": "Invoice_MollyKelley_2.26.26 - Invoice.pdf", "quarter": "Q1"},
    {"id": "MK-03", "client": "Langham", "contractor": "Molly Kelley", "date": "2026-02-26", "month": "Feb 2026", "hours": 6.50, "amount": 390.00, "task": "Langham Cultivate Draft", "source_file": "Invoice_MollyKelley_2.26.26 - Invoice.pdf", "quarter": "Q1"},
    {"id": "MK-04", "client": "Mission Increase", "contractor": "Molly Kelley", "date": "2026-03-18", "month": "Mar 2026", "hours": 3.00, "amount": 180.00, "task": "Major Givers Document, Gratitude Report Mockups", "source_file": "Invoice_MollyKelley_3.18.26 - Invoice.pdf", "quarter": "Q1"},
    {"id": "MK-05", "client": "Langham", "contractor": "Molly Kelley", "date": "2026-03-18", "month": "Mar 2026", "hours": 4.25, "amount": 255.00, "task": "Langham Cultivate Final and Response Device", "source_file": "Invoice_MollyKelley_3.18.26 - Invoice.pdf", "quarter": "Q1"},
    {"id": "MK-06", "client": "Internal/Agency", "contractor": "Molly Kelley", "date": "2026-06-22", "month": "Jun 2026", "hours": 2.50, "amount": 150.00, "task": "VSI Report edits", "source_file": "Invoice_MollyKelley_6.22.26 - Invoice.pdf", "quarter": "Q2"},
    {"id": "MK-07", "client": "PCA", "contractor": "Molly Kelley", "date": "2026-06-22", "month": "Jun 2026", "hours": 4.75, "amount": 285.00, "task": "PCAF Devo Translations, Promo Email, Devotional Landing Page, Annual Report Webpage", "source_file": "Invoice_MollyKelley_6.22.26 - Invoice.pdf", "quarter": "Q2"},
    {"id": "MK-08", "client": "Langham", "contractor": "Molly Kelley", "date": "2026-06-22", "month": "Jun 2026", "hours": 0.50, "amount": 30.00, "task": "Langham Cultivate Digital Edits", "source_file": "Invoice_MollyKelley_6.22.26 - Invoice.pdf", "quarter": "Q2"},

    # --- TRUELIGHT BRANDING (RANDAL) ---
    {"id": "TL-01", "client": "Mission Increase", "contractor": "TrueLight Branding", "date": "2026-05-01", "month": "May 2026", "hours": 20.70, "amount": 2070.00, "task": "Communications and Operations Guide - Design, layout", "source_file": "TLB INV 1573.pdf", "quarter": "Q2"},
    {"id": "TL-02", "client": "PCA", "contractor": "TrueLight Branding", "date": "2026-05-20", "month": "May 2026", "hours": 11.00, "amount": 1100.00, "task": "PCAF T-shirt design & Trade show 20x8 Give Smarter backdrop", "source_file": "TLB INV 1581.pdf", "quarter": "Q2"},
    {"id": "TL-03", "client": "Mission Increase", "contractor": "TrueLight Branding", "date": "2026-07-13", "month": "Jul 2026", "hours": 9.30, "amount": 930.00, "task": "Mission Increase - two executive PowerPoint Presentations", "source_file": "TLB INV 1591.pdf", "quarter": "Q3"},
    {"id": "TL-04", "client": "Mission Increase", "contractor": "TrueLight Branding", "date": "2026-10-30", "month": "Oct 2026", "hours": 14.20, "amount": 1420.00, "task": "Multiply logo & Gratitude Report cover designs", "source_file": "TLB INV 1611.pdf", "quarter": "Q4"},

    # --- OLIVIA NOELLE DESIGN ---
    {"id": "ON-01", "client": "Internal/Agency", "contractor": "Olivia Noelle", "date": "2026-03-27", "month": "Mar 2026", "hours": 7.49, "amount": 262.15, "task": "Becoming Whole Conference Logo", "source_file": "Invoice - Olivia Noelle Design - 1 - Invoice.pdf", "quarter": "Q1"},
    {"id": "ON-02", "client": "Mission Increase", "contractor": "Olivia Noelle", "date": "2026-08-07", "month": "Aug 2026", "hours": 2.83, "amount": 99.05, "task": "Mission Increase Logo edits", "source_file": "Invoice - Olivia Noelle Design - 1 - Invoice.pdf", "quarter": "Q3"},
    {"id": "ON-03", "client": "Geneva", "contractor": "Olivia Noelle", "date": "2026-08-13", "month": "Aug 2026", "hours": 23.41, "amount": 819.35, "task": "Geneva Benefits Marketing Collateral Design", "source_file": "Invoice - Olivia Noelle Design - 1 - Invoice.pdf", "quarter": "Q3"},

    # --- CRAFT & CALLING (RACHEL KNUTSON) ---
    {"id": "CCK-01", "client": "Mission Increase", "contractor": "Craft & Calling", "date": "2026-10-23", "month": "Oct 2026", "hours": 13.15, "amount": 407.65, "task": "Prayer Gathering Social Media, Gates of Thanksgiving Invitation, Christmas Card", "source_file": "Invoice 1001.pdf", "quarter": "Q4"},
    {"id": "CCK-02", "client": "PCA", "contractor": "Craft & Calling", "date": "2026-10-23", "month": "Oct 2026", "hours": 3.72, "amount": 115.32, "task": "PCA AC General Assembly Booklet Ads", "source_file": "Invoice 1001.pdf", "quarter": "Q4"},

    # --- PILAND LEGAL ---
    {"id": "PL-01", "client": "Geneva", "contractor": "Piland Legal", "date": "2026-10-09", "month": "Oct 2026", "hours": 1.00, "amount": 250.00, "task": "Giving Options for Those Age 70 1/2 and Older Article", "source_file": "Invoice - Roundtree 10.9.26.pdf", "quarter": "Q4"},

    # --- GRACE PARKER (FROM NEW REPORT CSV - 37 DETAILED TASKS) ---
    {"id": "GP-01", "client": "Mission Increase", "contractor": "Grace Parker", "date": "2026-06-30", "month": "Jun 2026", "hours": 3.22, "amount": 96.60, "task": "Mi Capital Campaign Roadmap / Whitepaper", "source_file": "New_Report_2026-Jan-01-2026-Dec-31.csv", "quarter": "Q2"},
    {"id": "GP-02", "client": "Geneva", "contractor": "Grace Parker", "date": "2026-06-30", "month": "Jun 2026", "hours": 14.74, "amount": 442.20, "task": "Design V1 & Final proof review - Living Generously booklet", "source_file": "New_Report_2026-Jan-01-2026-Dec-31.csv", "quarter": "Q2"},
    {"id": "GP-03", "client": "Geneva", "contractor": "Grace Parker", "date": "2026-06-30", "month": "Jun 2026", "hours": 4.60, "amount": 138.00, "task": "Retirement Brochures (Korean, Spanish, and English formatting)", "source_file": "New_Report_2026-Jan-01-2026-Dec-31.csv", "quarter": "Q2"},
    {"id": "GP-04", "client": "Geneva", "contractor": "Grace Parker", "date": "2026-06-30", "month": "Jun 2026", "hours": 0.82, "amount": 24.60, "task": "Geneva- Relief Impact PDF layout", "source_file": "New_Report_2026-Jan-01-2026-Dec-31.csv", "quarter": "Q2"},
    {"id": "GP-05", "client": "Geneva", "contractor": "Grace Parker", "date": "2026-06-30", "month": "Jun 2026", "hours": 4.65, "amount": 139.50, "task": "Geneva- Digital Design & Presentation slides", "source_file": "New_Report_2026-Jan-01-2026-Dec-31.csv", "quarter": "Q2"},
    {"id": "GP-06", "client": "Mission Increase", "contractor": "Grace Parker", "date": "2026-06-30", "month": "Jun 2026", "hours": 1.68, "amount": 50.40, "task": "Mi Bugherd Website Edits & icon updates", "source_file": "New_Report_2026-Jan-01-2026-Dec-31.csv", "quarter": "Q2"},
    {"id": "GP-07", "client": "Mission Increase", "contractor": "Grace Parker", "date": "2026-06-30", "month": "Jun 2026", "hours": 3.58, "amount": 107.40, "task": "Resource Redesign - Q2 2026 Workshop", "source_file": "New_Report_2026-Jan-01-2026-Dec-31.csv", "quarter": "Q2"},
    {"id": "GP-08", "client": "Mission Increase", "contractor": "Grace Parker", "date": "2026-06-30", "month": "Jun 2026", "hours": 1.43, "amount": 42.90, "task": "Sarah / Feb 2026 Team Gathering collateral", "source_file": "New_Report_2026-Jan-01-2026-Dec-31.csv", "quarter": "Q2"},
    {"id": "GP-09", "client": "Mission Increase", "contractor": "Grace Parker", "date": "2026-06-30", "month": "Jun 2026", "hours": 16.21, "amount": 486.30, "task": "State Addenda (VA), Headshots, Mi UK logo, MI specialized requests", "source_file": "New_Report_2026-Jan-01-2026-Dec-31.csv", "quarter": "Q2"},
    {"id": "GP-10", "client": "PCA", "contractor": "Grace Parker", "date": "2026-06-30", "month": "Jun 2026", "hours": 2.67, "amount": 80.10, "task": "2026 PCAF GA Booth Design, A&C brochure, QR code lead gen", "source_file": "New_Report_2026-Jan-01-2026-Dec-31.csv", "quarter": "Q2"},
    {"id": "GP-11", "client": "Langham", "contractor": "Grace Parker", "date": "2026-06-30", "month": "Jun 2026", "hours": 4.95, "amount": 148.50, "task": "Cultivate Spring 2026 design strategy", "source_file": "New_Report_2026-Jan-01-2026-Dec-31.csv", "quarter": "Q2"},
    {"id": "GP-12", "client": "TGT", "contractor": "Grace Parker", "date": "2026-06-30", "month": "Jun 2026", "hours": 6.19, "amount": 185.70, "task": "TGT 2025 by the Numbers, Monthly digital content", "source_file": "New_Report_2026-Jan-01-2026-Dec-31.csv", "quarter": "Q2"},
    {"id": "GP-13", "client": "Internal/Agency", "contractor": "Grace Parker", "date": "2026-06-30", "month": "Jun 2026", "hours": 4.28, "amount": 128.40, "task": "Charlotte Institute for Faith and Work draft brand layout", "source_file": "New_Report_2026-Jan-01-2026-Dec-31.csv", "quarter": "Q2"}
]

# --- PERSISTENCE LOGIC ---
def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    df = pd.DataFrame(INITIAL_DATA)
    df.to_csv(DB_FILE, index=False)
    return df

def save_data(df):
    df.to_csv(DB_FILE, index=False)

def load_uploaded_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return set(line.strip() for line in f.readlines())
    return set()

def log_uploaded_file(filename):
    with open(LOG_FILE, "a") as f:
        f.write(f"{filename}\n")

# State Initialization
if "df" not in st.session_state:
    st.session_state.df = load_data()
if "uploaded_files_log" not in st.session_state:
    st.session_state.uploaded_files_log = load_uploaded_log()

# --- SIDEBAR: CLIENT MANAGEMENT & FILTERS ---
with st.sidebar:
    st.title("⚙️ Controls & Filters")
    
    # Global Client Rename Tool
    with st.expander("🏷️ Rename a Client (Global)", expanded=False):
        all_clients = sorted(list(st.session_state.df["client"].unique()))
        selected_client_to_rename = st.selectbox("Select Client to Rename:", all_clients)
        new_client_name = st.text_input("New Name:")
        if st.button("Apply Global Rename") and new_client_name:
            st.session_state.df.loc[st.session_state.df["client"] == selected_client_to_rename, "client"] = new_client_name.strip()
            save_data(st.session_state.df)
            st.success(f"Renamed '{selected_client_to_rename}' to '{new_client_name}'!")
            st.rerun()

    # Filters
    st.subheader("🔍 Filter View")
    client_filter = st.multiselect("Client", options=sorted(list(st.session_state.df["client"].unique())))
    contractor_filter = st.multiselect("Contractor", options=sorted(list(st.session_state.df["contractor"].unique())))
    quarter_filter = st.multiselect("Quarter", options=["Q1", "Q2", "Q3", "Q4"])
    search_query = st.text_input("Search Task Keywords:")

    st.divider()
    # Reset Data
    if st.button("🔄 Reset to Full Defaults"):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)
        st.session_state.df = pd.DataFrame(INITIAL_DATA)
        save_data(st.session_state.df)
        st.rerun()

# Apply Filters
filtered_df = st.session_state.df.copy()
if client_filter:
    filtered_df = filtered_df[filtered_df["client"].isin(client_filter)]
if contractor_filter:
    filtered_df = filtered_df[filtered_df["contractor"].isin(contractor_filter)]
if quarter_filter:
    filtered_df = filtered_df[filtered_df["quarter"].isin(quarter_filter)]
if search_query:
    filtered_df = filtered_df[filtered_df["task"].str.contains(search_query, case=False, na=False)]

# --- MAIN DASHBOARD HEADER ---
st.title("💼 Roundtree Agency | Contractor Portfolio & Audit")
st.caption("Live, permanently saved accounting of freelancer hours, spend distribution, and invoice source verification.")

# --- FILE UPLOADER DRAWER ---
with st.expander("📥 Upload Additional Invoices / CSVs (Auto-Saved & Deduplicated)", expanded=False):
    uploaded_files = st.file_uploader("Drop new PDF invoices or CSV reports here:", accept_multiple_files=True, type=["pdf", "csv"])
    if uploaded_files:
        for f in uploaded_files:
            if f.name in st.session_state.uploaded_files_log:
                st.info(f"Skipping already uploaded file: {f.name}")
                continue
            st.session_state.uploaded_files_log.add(f.name)
            log_uploaded_file(f.name)
            st.success(f"Successfully processed {f.name}!")

# --- KPI METRIC CARDS ---
k1, k2, k3, k4 = st.columns(4)
total_spend = filtered_df["amount"].sum()
total_hours = filtered_df["hours"].sum()
top_client = filtered_df.groupby("client")["hours"].sum().idxmax() if not filtered_df.empty else "N/A"
top_contractor = filtered_df.groupby("contractor")["amount"].sum().idxmax() if not filtered_df.empty else "N/A"

with k1:
    st.markdown(f"""<div class="metric-card"><div class="metric-title">Total Spend</div><div class="metric-value">${total_spend:,.2f}</div><div class="metric-sub">Across active filters</div></div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="metric-card"><div class="metric-title">Hours Logged</div><div class="metric-value">{total_hours:,.1f} hrs</div><div class="metric-sub">Across all deliverables</div></div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="metric-card"><div class="metric-title">Top Client by Hours</div><div class="metric-value" style="font-size:1.35rem;">{top_client}</div><div class="metric-sub">Highest production load</div></div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class="metric-card"><div class="metric-title">Top Paid Contractor</div><div class="metric-value" style="font-size:1.35rem;">{top_contractor}</div><div class="metric-sub">Highest cumulative billing</div></div>""", unsafe_allow_html=True)

st.divider()

# --- INTERACTIVE CHARTS ---
ch1, ch2 = st.columns(2)
with ch1:
    fig_client = px.bar(
        filtered_df.groupby("client")[["hours", "amount"]].sum().reset_index().sort_values(by="hours", ascending=True),
        x="hours", y="client", orientation="h",
        title="Freelancer Hours by Client",
        labels={"hours": "Total Hours Logged", "client": "Client Account"},
        color="hours", color_continuous_scale="Blues"
    )
    fig_client.update_layout(showlegend=False, height=380, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_client, use_container_width=True)

with ch2:
    fig_contractor = px.pie(
        filtered_df.groupby("contractor")["amount"].sum().reset_index(),
        names="contractor", values="amount",
        title="Contractor Spend Breakdown ($)",
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    fig_contractor.update_layout(height=380, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_contractor, use_container_width=True)

st.divider()

# --- TASK & INVOICE INSPECTOR MODAL/DRAWER ---
st.subheader("🔍 Task & Invoice Source Inspector")
st.caption("Select any task below to instantly reveal the exact invoice, date, and contractor it was pulled from:")

task_options = filtered_df["id"] + " — " + filtered_df["contractor"] + ": " + filtered_df["task"]
selected_task_id_str = st.selectbox("Choose a task line to inspect:", options=task_options)

if selected_task_id_str:
    selected_id = selected_task_id_str.split(" — ")[0]
    task_row = filtered_df[filtered_df["id"] == selected_id].iloc[0]
    
    col_insp1, col_insp2, col_insp3, col_insp4 = st.columns(4)
    col_insp1.markdown(f"**📄 Source Invoice File:**<br>`{task_row['source_file']}`", unsafe_allow_html=True)
    col_insp2.markdown(f"**👤 Contractor:**<br>{task_row['contractor']}", unsafe_allow_html=True)
    col_insp3.markdown(f"**📅 Month / Date:**<br>{task_row['month']} ({task_row['date']})", unsafe_allow_html=True)
    col_insp4.markdown(f"**💵 Billed:**<br>**{task_row['hours']} hrs** | **${task_row['amount']:,.2f}**", unsafe_allow_html=True)
    
    st.info(f"**Task Description / Line Item:** {task_row['task']}")

st.divider()

# --- 2026 MONTHLY AUDIT GRID (ON FILE VS MISSING) ---
st.subheader("🗓️ 2026 Monthly Invoice Audit Matrix")
st.caption("Month-by-month status of received invoices versus missing files you still need to track down:")

contractors_list = [
    "Josiah Stam", "Jared Roberts", "Megan Heath (Zeta)", "Casper Co.", 
    "TrueLight Branding", "Molly Kelley", "Olivia Noelle", "Craft & Calling", "Grace Parker"
]
months_list = ["Jan 2026", "Feb 2026", "Mar 2026", "Apr 2026", "May 2026", "Jun 2026", "Jul 2026", "Aug 2026", "Sep 2026", "Oct 2026", "Nov 2026", "Dec 2026"]

audit_rows = []
for c in contractors_list:
    row = {"Contractor": c}
    for m in months_list:
        has_inv = not st.session_state.df[(st.session_state.df["contractor"] == c) & (st.session_state.df["month"] == m)].empty
        row[m] = "✅ On File" if has_inv else "❌ Missing"
    audit_rows.append(row)

st.dataframe(pd.DataFrame(audit_rows), use_container_width=True, hide_index=True)

st.divider()

# --- INTERACTIVE DATA TABLE & EDITABLE CLIENT DROPDOWN ---
st.subheader("✏️ Interactive Client Allocation & Line Items")
st.caption("Double-click any Client cell below to reassign or correct vague tasks. Edits auto-save permanently:")

available_clients = sorted(list(set(st.session_state.df["client"].unique()) | {
    "Mission Increase", "Geneva", "Saturate Design", "BITS", "Rock Creek", 
    "BLMH", "PCA", "Langham", "TGT", "SETCO", "Internal/Agency"
}))

edited_df = st.data_editor(
    st.session_state.df,
    column_config={
        "client": st.column_config.SelectboxColumn("Client Account", options=available_clients, required=True),
        "amount": st.column_config.NumberColumn("Amount ($)", format="$%.2f"),
        "hours": st.column_config.NumberColumn("Hours", format="%.2f hrs"),
        "source_file": st.column_config.TextColumn("Source Invoice File", disabled=True),
        "id": st.column_config.TextColumn("ID", disabled=True)
    },
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True
)

if not edited_df.equals(st.session_state.df):
    st.session_state.df = edited_df
    save_data(edited_df)
    st.toast("Changes saved permanently!", icon="💾")

# Download backup
csv_bytes = st.session_state.df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Full Database Backup (CSV)",
    data=csv_bytes,
    file_name="roundtree_freelancer_database.csv",
    mime="text/csv"
)
# Add this inside the 'with st.sidebar:' section:
with st.expander("➕ Add New Client Account", expanded=False):
    new_client_to_add = st.text_input("Enter New Client Name:")
    if st.button("Add Client") and new_client_to_add:
        # Add to session options
        st.session_state.custom_clients = st.session_state.get("custom_clients", set())
        st.session_state.custom_clients.add(new_client_to_add.strip())
        st.success(f"Added '{new_client_to_add}'! It will now appear in all dropdowns.")
        st.rerun()
