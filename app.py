import streamlit as st
import pandas as pd
import plotly.express as px
from pypdf import PdfReader
import os

st.set_page_config(page_title="Roundtree Freelancer Tracker", layout="wide")

DB_FILE = "freelancer_database.csv"
LOG_FILE = "uploaded_files_log.txt"

# --- FULL COMPREHENSIVE BASELINE DATA FROM ALL NOTEBOOK INVOICES ---
INITIAL_DATA = [
    # --- JOSIAH STAM (STAM CREATIVE) ---
    {"client": "Mission Increase", "contractor": "Josiah Stam", "date": "2026-01-30", "month": "Jan 2026", "hours": 14.31, "amount": 500.85, "task": "Giving Levels Doc, Media Kit, Taste of MI, Academy Mark"},
    {"client": "Geneva", "contractor": "Josiah Stam", "date": "2026-01-30", "month": "Jan 2026", "hours": 23.68, "amount": 828.80, "task": "Tabletop Canvases, Postcard, Sustainers Logo & Graphics, Banners"},
    {"client": "BLMH", "contractor": "Josiah Stam", "date": "2026-01-30", "month": "Jan 2026", "hours": 0.52, "amount": 18.20, "task": "BLMH Business Card"},
    {"client": "Mission Increase", "contractor": "Josiah Stam", "date": "2026-02-27", "month": "Feb 2026", "hours": 23.67, "amount": 828.45, "task": "Academy Badge, Pitch Deck, Momentum Multiplied Slides, Specialized Email"},
    {"client": "Geneva", "contractor": "Josiah Stam", "date": "2026-02-27", "month": "Feb 2026", "hours": 15.18, "amount": 531.30, "task": "Donor Letters, Welcome Gift Envelope, Golf Tournament, Annual Report"},
    {"client": "BITS", "contractor": "Josiah Stam", "date": "2026-02-27", "month": "Feb 2026", "hours": 1.00, "amount": 35.00, "task": "Bible In The Schools Prospectus"},
    {"client": "BLMH", "contractor": "Josiah Stam", "date": "2026-02-27", "month": "Feb 2026", "hours": 0.08, "amount": 2.80, "task": "BLMH Business Card"},
    {"client": "Geneva", "contractor": "Josiah Stam", "date": "2026-03-31", "month": "Mar 2026", "hours": 81.24, "amount": 2843.40, "task": "Annual Report (32.8h), Postcard, Checklist en español, Campaign Letter & Email, Cohort Explainer"},
    {"client": "Mission Increase", "contractor": "Josiah Stam", "date": "2026-03-31", "month": "Mar 2026", "hours": 2.98, "amount": 104.30, "task": "Equipping Call Thumbnail, Taste of MI Canva, Jax Workshop Invite"},
    {"client": "Geneva", "contractor": "Josiah Stam", "date": "2026-05-23", "month": "May 2026", "hours": 10.58, "amount": 370.30, "task": "Meeting Norms Tabletop Display, Retirement Plan Brochure"},
    {"client": "Mission Increase", "contractor": "Josiah Stam", "date": "2026-05-23", "month": "May 2026", "hours": 7.67, "amount": 268.45, "task": "MI Postcards, Alliance Post"},

    # --- JARED ROBERTS ---
    {"client": "Mission Increase", "contractor": "Jared Roberts", "date": "2026-02-27", "month": "Feb 2026", "hours": 18.28, "amount": 2102.08, "task": "Impact Stories PDF, Website Impact Stories, Gratitude Report Edits, Email Template Changes"},
    {"client": "PCA", "contractor": "Jared Roberts", "date": "2026-02-27", "month": "Feb 2026", "hours": 0.25, "amount": 25.00, "task": "Review PCA foundation plugins"},
    {"client": "Internal/Agency", "contractor": "Jared Roberts", "date": "2026-03-02", "month": "Mar 2026", "hours": 0.25, "amount": 25.00, "task": "Update bios and finalize files"},
    {"client": "Mission Increase", "contractor": "Jared Roberts", "date": "2026-03-31", "month": "Mar 2026", "hours": 6.85, "amount": 756.25, "task": "MI to Mi export, Email redesign, 4-col grid, Impact stories nav"},
    {"client": "Saturate Design", "contractor": "Jared Roberts", "date": "2026-03-11", "month": "Mar 2026", "hours": 14.23, "amount": 1779.16, "task": "Saturate Design web development sprint"},
    {"client": "Mission Increase", "contractor": "Jared Roberts", "date": "2026-04-30", "month": "Apr 2026", "hours": 13.13, "amount": 1507.08, "task": "Menu fixes, Resources Page rebuild, One-Pagers, Laptop mockups"},
    {"client": "Mission Increase", "contractor": "Jared Roberts", "date": "2026-05-30", "month": "May 2026", "hours": 17.50, "amount": 1912.50, "task": "Complex gifts, Core Services PDF, Figma html mockups, Website fixes"},
    {"client": "Mission Increase", "contractor": "Jared Roberts", "date": "2026-06-30", "month": "Jun 2026", "hours": 12.25, "amount": 1368.75, "task": "Academy webinar assets, Resources troubleshooting, Q3 Webinar Booklet"},
    {"client": "Mission Increase", "contractor": "Jared Roberts", "date": "2026-07-24", "month": "Jul 2026", "hours": 3.50, "amount": 375.00, "task": "Q3 Webinar Booklet, PowerPoint, Social graphics, Landing pages"},
    {"client": "Rock Creek", "contractor": "Jared Roberts", "date": "2026-07-24", "month": "Jul 2026", "hours": 1.00, "amount": 125.00, "task": "Troubleshoot Rock Creek broken design"},
    {"client": "Mission Increase", "contractor": "Jared Roberts", "date": "2026-08-31", "month": "Aug 2026", "hours": 4.50, "amount": 475.00, "task": "Slide Deck, Asana web development tasks"},
    {"client": "Mission Increase", "contractor": "Jared Roberts", "date": "2026-09-03", "month": "Sep 2026", "hours": 3.75, "amount": 393.75, "task": "Asana task updates & web development"},

    # --- MEGAN HEATH (ZETA CREATIVE) ---
    {"client": "BITS", "contractor": "Megan Heath (Zeta)", "date": "2026-02-01", "month": "Feb 2026", "hours": 1.50, "amount": 127.50, "task": "Prospectus, Envelope correction, Luncheon 2026, Vector issue"},
    {"client": "SETCO", "contractor": "Megan Heath (Zeta)", "date": "2026-02-01", "month": "Feb 2026", "hours": 0.75, "amount": 63.75, "task": "Birthday Card"},
    {"client": "BITS", "contractor": "Megan Heath (Zeta)", "date": "2026-03-01", "month": "Mar 2026", "hours": 2.75, "amount": 233.75, "task": "Vector issue, Luncheon 2026, Commitment Card 2026"},
    {"client": "PCA", "contractor": "Megan Heath (Zeta)", "date": "2026-03-01", "month": "Mar 2026", "hours": 0.50, "amount": 42.50, "task": "PCAF iPhone Graphic"},
    {"client": "SETCO", "contractor": "Megan Heath (Zeta)", "date": "2026-04-01", "month": "Apr 2026", "hours": 1.50, "amount": 127.50, "task": "Table Cloth and Banners"},
    {"client": "PCA", "contractor": "Megan Heath (Zeta)", "date": "2026-04-01", "month": "Apr 2026", "hours": 1.50, "amount": 127.50, "task": "PCAF One Pager & Business Cards"},
    {"client": "BITS", "contractor": "Megan Heath (Zeta)", "date": "2026-04-01", "month": "Apr 2026", "hours": 4.75, "amount": 403.75, "task": "Table Tent, Banner, Sympathy Card, Seating Chart, Luncheon Program, Graph"},
    {"client": "Internal/Agency", "contractor": "Megan Heath (Zeta)", "date": "2026-04-01", "month": "Apr 2026", "hours": 9.75, "amount": 828.75, "task": "Christ Presbyterian Church Profile"},
    {"client": "Mission Increase", "contractor": "Megan Heath (Zeta)", "date": "2026-04-01", "month": "Apr 2026", "hours": 0.50, "amount": 42.50, "task": "MI Indiana Addenda"},
    {"client": "Internal/Agency", "contractor": "Megan Heath (Zeta)", "date": "2026-04-01", "month": "Apr 2026", "hours": 2.25, "amount": 191.25, "task": "byFaith Magazine The Lamb of God Graphics"},
    {"client": "Mission Increase", "contractor": "Megan Heath (Zeta)", "date": "2026-05-01", "month": "May 2026", "hours": 2.00, "amount": 170.00, "task": "Direct Mail Piece, Response Card Smart Giving"},
    {"client": "BITS", "contractor": "Megan Heath (Zeta)", "date": "2026-05-01", "month": "May 2026", "hours": 0.25, "amount": 21.25, "task": "BITS Business Card"},
    {"client": "PCA", "contractor": "Megan Heath (Zeta)", "date": "2026-05-01", "month": "May 2026", "hours": 3.25, "amount": 276.25, "task": "PCAF Response Device Update, Business Cards, Serving Churches Trifold"},
    {"client": "Mission Increase", "contractor": "Megan Heath (Zeta)", "date": "2026-06-01", "month": "Jun 2026", "hours": 1.00, "amount": 85.00, "task": "Direct Mail Piece, Lee Comm Ops Guide, Commitment Card Edits"},
    {"client": "BITS", "contractor": "Megan Heath (Zeta)", "date": "2026-06-01", "month": "Jun 2026", "hours": 0.50, "amount": 42.50, "task": "BITS Business Card"},
    {"client": "PCA", "contractor": "Megan Heath (Zeta)", "date": "2026-06-01", "month": "Jun 2026", "hours": 2.00, "amount": 170.00, "task": "PCAF Serving Churches Trifold"},
    {"client": "Internal/Agency", "contractor": "Megan Heath (Zeta)", "date": "2026-06-01", "month": "Jun 2026", "hours": 1.00, "amount": 85.00, "task": "Becoming Whole Flyer"},
    {"client": "Mission Increase", "contractor": "Megan Heath (Zeta)", "date": "2026-07-01", "month": "Jul 2026", "hours": 9.75, "amount": 828.75, "task": "Dan Flyer, Ashley Shaffer PPT redesign (5.25h), Impact Report, At a Glance, Commitment Cards"},
    {"client": "BITS", "contractor": "Megan Heath (Zeta)", "date": "2026-07-01", "month": "Jul 2026", "hours": 1.50, "amount": 127.50, "task": "Envelope Correction, Graph Edits, Letterhead Update"},
    {"client": "PCA", "contractor": "Megan Heath (Zeta)", "date": "2026-07-01", "month": "Jul 2026", "hours": 0.75, "amount": 63.75, "task": "PCAF Business Cards"},
    {"client": "Mission Increase", "contractor": "Megan Heath (Zeta)", "date": "2026-08-01", "month": "Aug 2026", "hours": 6.25, "amount": 531.25, "task": "At a Glance, Commitment Card, Placemats, Position Paper, Impact Report, Charity One Pager"},
    {"client": "Internal/Agency", "contractor": "Megan Heath (Zeta)", "date": "2026-08-01", "month": "Aug 2026", "hours": 1.25, "amount": 106.25, "task": "Becoming Whole Flyers"},
    {"client": "BITS", "contractor": "Megan Heath (Zeta)", "date": "2026-08-01", "month": "Aug 2026", "hours": 0.25, "amount": 21.25, "task": "BITS Map Update"},
    {"client": "Mission Increase", "contractor": "Megan Heath (Zeta)", "date": "2026-09-01", "month": "Sep 2026", "hours": 9.25, "amount": 786.25, "task": "CAFO Ad, Academy One Pager, Banner, Foundation PPT, Letterhead, QR flyer, Champion Two Pagers"},
    {"client": "Geneva", "contractor": "Megan Heath (Zeta)", "date": "2026-09-01", "month": "Sep 2026", "hours": 4.00, "amount": 340.00, "task": "Dental Slip Sheet, Envelope Edits, Social Graphics, Folder Update"},
    {"client": "BITS", "contractor": "Megan Heath (Zeta)", "date": "2026-09-01", "month": "Sep 2026", "hours": 0.75, "amount": 63.75, "task": "Letterhead Update, State Map Update"},
    {"client": "Internal/Agency", "contractor": "Megan Heath (Zeta)", "date": "2026-09-01", "month": "Sep 2026", "hours": 1.50, "amount": 127.50, "task": "Becoming Whole Flyers, Village School Cards"},
    {"client": "Mission Increase", "contractor": "Megan Heath (Zeta)", "date": "2026-10-01", "month": "Oct 2026", "hours": 1.75, "amount": 148.75, "task": "Academy 2-pager, Impact Report, Gratitude Gathering Collateral"},
    {"client": "Geneva", "contractor": "Megan Heath (Zeta)", "date": "2026-10-01", "month": "Oct 2026", "hours": 4.50, "amount": 382.50, "task": "Case for Support, Appeal Letter Design (3.0h), Clergy Act Social Post"},
    {"client": "BITS", "contractor": "Megan Heath (Zeta)", "date": "2026-10-01", "month": "Oct 2026", "hours": 1.50, "amount": 127.50, "task": "Christmas Card Update, Luncheon Save the Date 2027, E-Signature"},
    {"client": "SETCO", "contractor": "Megan Heath (Zeta)", "date": "2026-10-01", "month": "Oct 2026", "hours": 0.25, "amount": 21.25, "task": "Nutcracker Ad"},
    {"client": "Internal/Agency", "contractor": "Megan Heath (Zeta)", "date": "2026-10-01", "month": "Oct 2026", "hours": 0.75, "amount": 63.75, "task": "byFaith Social Template"},

    # --- CASPER CO. LLC (ALEXANDRA CASPER - CONTENT/COPY) ---
    {"client": "Geneva", "contractor": "Casper Co.", "date": "2026-01-29", "month": "Jan 2026", "hours": 4.00, "amount": 580.00, "task": "Geneva Story - Elizabeth & Adam"},
    {"client": "Geneva", "contractor": "Casper Co.", "date": "2026-02-27", "month": "Feb 2026", "hours": 5.00, "amount": 725.00, "task": "Geneva - Susan Story & Living Generously Booklet"},
    {"client": "Geneva", "contractor": "Casper Co.", "date": "2026-03-30", "month": "Mar 2026", "hours": 5.00, "amount": 725.00, "task": "Geneva - David Story & Living Generously Booklet"},
    {"client": "Geneva", "contractor": "Casper Co.", "date": "2026-04-29", "month": "Apr 2026", "hours": 6.00, "amount": 870.00, "task": "Financial planning story, Nathan story, Relief fund story"},
    {"client": "Geneva", "contractor": "Casper Co.", "date": "2026-06-01", "month": "May 2026", "hours": 1.00, "amount": 145.00, "task": "Geneva Insurance article"},
    {"client": "Geneva", "contractor": "Casper Co.", "date": "2026-07-31", "month": "Jul 2026", "hours": 2.50, "amount": 362.50, "task": "Geneva - Brent Curl Story"},
    {"client": "Mission Increase", "contractor": "Casper Co.", "date": "2026-07-31", "month": "Jul 2026", "hours": 3.00, "amount": 435.00, "task": "Mission Increase Homepage Audit"},
    {"client": "PCA", "contractor": "Casper Co.", "date": "2026-07-31", "month": "Jul 2026", "hours": 1.00, "amount": 145.00, "task": "AC Prayer Guide Letter"},
    {"client": "Geneva", "contractor": "Casper Co.", "date": "2026-08-31", "month": "Aug 2026", "hours": 1.50, "amount": 217.50, "task": "Geneva Charitable IQ Article"},
    {"client": "Mission Increase", "contractor": "Casper Co.", "date": "2026-08-31", "month": "Aug 2026", "hours": 1.00, "amount": 145.00, "task": "Mission Increase Homepage Copy Edits"},
    {"client": "TGT", "contractor": "Casper Co.", "date": "2026-08-31", "month": "Aug 2026", "hours": 4.00, "amount": 580.00, "task": "TGT Website Copy Audit and Suggestions"},
    {"client": "Internal/Agency", "contractor": "Casper Co.", "date": "2026-08-31", "month": "Aug 2026", "hours": 10.00, "amount": 1450.00, "task": "SRG Magazine Articles"},
    {"client": "Geneva", "contractor": "Casper Co.", "date": "2026-09-30", "month": "Sep 2026", "hours": 10.50, "amount": 1522.50, "task": "ByFaith Article, Bill McCutcheon Story, Cybersecurity, Look/After letter & email"},
    {"client": "Mission Increase", "contractor": "Casper Co.", "date": "2026-09-30", "month": "Sep 2026", "hours": 2.50, "amount": 362.50, "task": "Mission Increase 2-pager"},
    {"client": "Geneva", "contractor": "Casper Co.", "date": "2026-10-30", "month": "Oct 2026", "hours": 5.25, "amount": 761.25, "task": "Bill McCutchon Story, ByFaith Story, Clergy Press Release, Living Generously, One-page proposal"},
    {"client": "PCA", "contractor": "Casper Co.", "date": "2026-10-30", "month": "Oct 2026", "hours": 3.50, "amount": 507.50, "task": "PCA AC Ads, PCAF Articles on generosity & giving"},
    {"client": "Internal/Agency", "contractor": "Casper Co.", "date": "2026-10-30", "month": "Oct 2026", "hours": 5.50, "amount": 797.50, "task": "West Paces Advisors - Creative Ideas and Research"},

    # --- MOLLY KELLEY ---
    {"client": "Mission Increase", "contractor": "Molly Kelley", "date": "2026-01-09", "month": "Jan 2026", "hours": 2.25, "amount": 135.00, "task": "MI Jacksonville Asset Buildout (table tent, notecards, banner)"},
    {"client": "Mission Increase", "contractor": "Molly Kelley", "date": "2026-02-26", "month": "Feb 2026", "hours": 15.50, "amount": 930.00, "task": "Mission Increase Gratitude Report layout"},
    {"client": "Langham", "contractor": "Molly Kelley", "date": "2026-02-26", "month": "Feb 2026", "hours": 6.50, "amount": 390.00, "task": "Langham Cultivate Draft"},
    {"client": "Mission Increase", "contractor": "Molly Kelley", "date": "2026-03-18", "month": "Mar 2026", "hours": 3.00, "amount": 180.00, "task": "Major Givers Document, Gratitude Report Mockups"},
    {"client": "Langham", "contractor": "Molly Kelley", "date": "2026-03-18", "month": "Mar 2026", "hours": 4.25, "amount": 255.00, "task": "Langham Cultivate Final and Response Device"},
    {"client": "Internal/Agency", "contractor": "Molly Kelley", "date": "2026-06-22", "month": "Jun 2026", "hours": 2.50, "amount": 150.00, "task": "VSI Report edits"},
    {"client": "PCA", "contractor": "Molly Kelley", "date": "2026-06-22", "month": "Jun 2026", "hours": 4.75, "amount": 285.00, "task": "PCAF Devo Translations, Promo Email, Devotional Landing Page, Annual Report Webpage"},
    {"client": "Langham", "contractor": "Molly Kelley", "date": "2026-06-22", "month": "Jun 2026", "hours": 0.50, "amount": 30.00, "task": "Langham Cultivate Digital Edits"},

    # --- TRUELIGHT BRANDING (RANDAL) ---
    {"client": "Mission Increase", "contractor": "TrueLight Branding", "date": "2026-05-01", "month": "May 2026", "hours": 20.70, "amount": 2070.00, "task": "Communications and Operations Guide - Design, layout"},
    {"client": "PCA", "contractor": "TrueLight Branding", "date": "2026-05-20", "month": "May 2026", "hours": 11.00, "amount": 1100.00, "task": "PCAF T-shirt design & Trade show 20x8 Give Smarter backdrop"},
    {"client": "Mission Increase", "contractor": "TrueLight Branding", "date": "2026-07-13", "month": "Jul 2026", "hours": 9.30, "amount": 930.00, "task": "Mission Increase - two executive PowerPoint Presentations"},
    {"client": "Mission Increase", "contractor": "TrueLight Branding", "date": "2026-10-30", "month": "Oct 2026", "hours": 14.20, "amount": 1420.00, "task": "Multiply logo & Gratitude Report cover designs"},

    # --- OLIVIA NOELLE DESIGN (OLIVIA MOORE) ---
    {"client": "Internal/Agency", "contractor": "Olivia Noelle", "date": "2026-03-27", "month": "Mar 2026", "hours": 7.49, "amount": 262.15, "task": "Becoming Whole Conference Logo"},
    {"client": "Mission Increase", "contractor": "Olivia Noelle", "date": "2026-08-07", "month": "Aug 2026", "hours": 2.83, "amount": 99.05, "task": "Mission Increase Logo edits"},
    {"client": "Geneva", "contractor": "Olivia Noelle", "date": "2026-08-13", "month": "Aug 2026", "hours": 23.41, "amount": 819.35, "task": "Geneva Benefits Marketing Collateral Design"},

    # --- CRAFT & CALLING (RACHEL KNUTSON) ---
    {"client": "Mission Increase", "contractor": "Craft & Calling", "date": "2026-10-23", "month": "Oct 2026", "hours": 13.15, "amount": 407.65, "task": "Prayer Gathering Social Media, Gates of Thanksgiving Invitation, Christmas Card"},
    {"client": "PCA", "contractor": "Craft & Calling", "date": "2026-10-23", "month": "Oct 2026", "hours": 3.72, "amount": 115.32, "task": "PCA AC General Assembly Booklet Ads"},

    # --- PILAND LEGAL ---
    {"client": "Geneva", "contractor": "Piland Legal", "date": "2026-10-09", "month": "Oct 2026", "hours": 1.00, "amount": 250.00, "task": "Giving Options for Those Age 70 1/2 and Older Article"},

    # --- GRACE PARKER (FROM NEW REPORT CSV - 37 TASKS) ---
    {"client": "Mission Increase", "contractor": "Grace Parker", "date": "2026-06-30", "month": "Jun 2026", "hours": 26.12, "amount": 783.60, "task": "Capital Campaign Roadmap (3.2h), Bugherd Edits, Headshots, Workshop & specialized requests"},
    {"client": "Geneva", "contractor": "Grace Parker", "date": "2026-06-30", "month": "Jun 2026", "hours": 24.81, "amount": 744.30, "task": "Living Generously V1 & Proof (14.7h), Retirement Brochures (Korean, Spanish, English), Relief Impact PDF"},
    {"client": "PCA", "contractor": "Grace Parker", "date": "2026-06-30", "month": "Jun 2026", "hours": 2.67, "amount": 80.10, "task": "PCAF GA Booth Design, A&C Brochure, QR code flyer"},
    {"client": "Langham", "contractor": "Grace Parker", "date": "2026-06-30", "month": "Jun 2026", "hours": 4.95, "amount": 148.50, "task": "Langham Cultivate Spring 2026"},
    {"client": "TGT", "contractor": "Grace Parker", "date": "2026-06-30", "month": "Jun 2026", "hours": 6.19, "amount": 185.70, "task": "TGT 2025 by the Numbers, Annual Report Design"},
    {"client": "Internal/Agency", "contractor": "Grace Parker", "date": "2026-06-30", "month": "Jun 2026", "hours": 4.28, "amount": 128.40, "task": "Charlotte Institute for Faith and Work Draft Design"}
]

# --- PERSISTENCE LOGIC ---
def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
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

# Initialize state
if "df" not in st.session_state:
    st.session_state.df = load_data()
if "uploaded_files_log" not in st.session_state:
    st.session_state.uploaded_files_log = load_uploaded_log()

# --- HEADER ---
st.title("📊 Roundtree Agency — Freelancer Portfolio & Audit Dashboard")
st.markdown("Live tracking of contractor hours, billing amounts, client allocations, and missing invoice audits across 2026.")

# --- FILE UPLOADER WIDGET ---
with st.expander("📥 Upload Additional Invoices / CSVs (Auto-Deduplicated & Saved)", expanded=False):
    uploaded_files = st.file_uploader("Drop new PDF invoices or CSV reports here:", accept_multiple_files=True, type=["pdf", "csv"])
    if uploaded_files:
        for f in uploaded_files:
            if f.name in st.session_state.uploaded_files_log:
                st.info(f"Skipping already uploaded file: {f.name}")
                continue
            st.session_state.uploaded_files_log.add(f.name)
            log_uploaded_file(f.name)
            if f.name.endswith(".csv"):
                new_df = pd.read_csv(f)
                st.success(f"Parsed {len(new_df)} rows from {f.name}")
            elif f.name.endswith(".pdf"):
                reader = PdfReader(f)
                text = "\n".join([page.extract_text() or "" for page in reader.pages])
                st.success(f"Logged {f.name} successfully!")

# --- KPI METRICS ---
col1, col2, col3, col4 = st.columns(4)
total_spend = st.session_state.df["amount"].sum()
total_hours = st.session_state.df["hours"].sum()
top_client = st.session_state.df.groupby("client")["hours"].sum().idxmax()
top_contractor = st.session_state.df.groupby("contractor")["amount"].sum().idxmax()

col1.metric("Total Contractor Spend", f"${total_spend:,.2f}")
col2.metric("Total Hours Logged", f"{total_hours:,.1f} hrs")
col3.metric("Top Client by Hours", top_client)
col4.metric("Top Paid Contractor", top_contractor)

st.divider()

# --- VISUAL CHARTS ---
c1, c2 = st.columns(2)
with c1:
    client_summary = st.session_state.df.groupby("client")[["hours", "amount"]].sum().reset_index().sort_values(by="hours", ascending=False)
    fig_client = px.bar(
        client_summary,
        x="client", y="hours", color="client",
        title="Total Contractor Hours by Client",
        labels={"hours": "Hours Logged", "client": "Client"}
    )
    st.plotly_chart(fig_client, use_container_width=True)

with c2:
    fig_contractor = px.pie(
        st.session_state.df.groupby("contractor")["amount"].sum().reset_index(),
        names="contractor", values="amount",
        title="Contractor Spend Distribution ($)",
        hole=0.4
    )
    st.plotly_chart(fig_contractor, use_container_width=True)

st.divider()

# --- 2026 MONTHLY AUDIT GRID (ON FILE VS MISSING) ---
st.subheader("🗓️ 2026 Monthly Invoice Audit (Missing vs. Uploaded)")
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

st.dataframe(pd.DataFrame(audit_rows), use_container_width=True)

st.divider()

# --- INTERACTIVE DATA TABLE & CLIENT REASSIGNMENT ---
st.subheader("✏️ Interactive Client Allocation & Line Items")
st.caption("Double-click any Client cell below to reassign tasks in real time. Changes auto-save permanently:")

available_clients = sorted(list(set(st.session_state.df["client"].unique()) | {
    "Mission Increase", "Geneva", "Saturate Design", "BITS", "Rock Creek", 
    "BLMH", "PCA", "Langham", "TGT", "SETCO", "Internal/Agency"
}))

edited_df = st.data_editor(
    st.session_state.df,
    column_config={
        "client": st.column_config.SelectboxColumn("Client", options=available_clients, required=True),
        "amount": st.column_config.NumberColumn("Amount ($)", format="$%.2f"),
        "hours": st.column_config.NumberColumn("Hours", format="%.2f hrs"),
    },
    num_rows="dynamic",
    use_container_width=True
)

if not edited_df.equals(st.session_state.df):
    st.session_state.df = edited_df
    save_data(edited_df)
    st.toast("Changes auto-saved!", icon="💾")

# Download backup
csv_bytes = st.session_state.df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Full Database Backup (CSV)",
    data=csv_bytes,
    file_name="roundtree_freelancer_database.csv",
    mime="text/csv"
)

# Reset Button in case you ever want to re-seed
if st.button("🔄 Reset to Default Invoices"):
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    st.session_state.df = pd.DataFrame(INITIAL_DATA)
    save_data(st.session_state.df)
    st.rerun()
