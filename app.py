import streamlit as st
import pandas as pd
import plotly.express as px
from pypdf import PdfReader
import os
import io

st.set_page_config(page_title="Roundtree Freelancer Tracker", layout="wide")

DB_FILE = "freelancer_database.csv"
LOG_FILE = "uploaded_files_log.txt"

# --- BASELINE DATA (Loaded only if no saved DB exists yet) ---
INITIAL_DATA = [
    # Geneva
    {"client": "Geneva", "contractor": "Josiah Stam", "date": "2026-03-31", "month": "Mar 2026", "hours": 84.22, "amount": 2947.70, "task": "Annual report design & collateral"},
    {"client": "Geneva", "contractor": "Josiah Stam", "date": "2026-05-23", "month": "May 2026", "hours": 10.48, "amount": 366.80, "task": "Retirement brochure layout"},
    {"client": "Geneva", "contractor": "Josiah Stam", "date": "2026-02-27", "month": "Feb 2026", "hours": 48.41, "amount": 1694.30, "task": "Monthly giving collateral & tabletop"},
    {"client": "Geneva", "contractor": "Megan Heath (Zeta)", "date": "2026-04-15", "month": "Apr 2026", "hours": 3.50, "amount": 297.50, "task": "Geneva donor brochures"},
    # Mission Increase
    {"client": "Mission Increase", "contractor": "Jared Roberts", "date": "2026-03-31", "month": "Mar 2026", "hours": 32.50, "amount": 3650.00, "task": "Website impact stories & bug fixes"},
    {"client": "Mission Increase", "contractor": "Jared Roberts", "date": "2026-04-30", "month": "Apr 2026", "hours": 20.25, "amount": 2275.00, "task": "Email templates & core services"},
    {"client": "Mission Increase", "contractor": "Jared Roberts", "date": "2026-05-30", "month": "May 2026", "hours": 19.98, "amount": 2236.25, "task": "Resources page overhaul"},
    {"client": "Mission Increase", "contractor": "Josiah Stam", "date": "2026-01-30", "month": "Jan 2026", "hours": 11.30, "amount": 395.50, "task": "Donor pitch deck & webinar slides"},
    {"client": "Mission Increase", "contractor": "Josiah Stam", "date": "2026-02-27", "month": "Feb 2026", "hours": 27.50, "amount": 962.50, "task": "Area Director training decks"},
    {"client": "Mission Increase", "contractor": "TrueLight Branding", "date": "2026-05-01", "month": "May 2026", "hours": 20.70, "amount": 2070.00, "task": "Communications & Ops Guide"},
    {"client": "Mission Increase", "contractor": "TrueLight Branding", "date": "2026-07-13", "month": "Jul 2026", "hours": 9.30, "amount": 930.00, "task": "Executive PowerPoint presentations"},
    {"client": "Mission Increase", "contractor": "Megan Heath (Zeta)", "date": "2026-07-31", "month": "Jul 2026", "hours": 12.00, "amount": 1020.00, "task": "Ashley Shaffer PPT & Dan flyer"},
    {"client": "Mission Increase", "contractor": "Megan Heath (Zeta)", "date": "2026-09-30", "month": "Sep 2026", "hours": 15.50, "amount": 1317.50, "task": "Impact reports & commitment cards"},
    {"client": "Mission Increase", "contractor": "Molly Kelley", "date": "2026-01-09", "month": "Jan 2026", "hours": 15.50, "amount": 465.00, "task": "Gratitude Report layout"},
    {"client": "Mission Increase", "contractor": "Molly Kelley", "date": "2026-03-18", "month": "Mar 2026", "hours": 7.25, "amount": 217.50, "task": "Gratitude Report revisions"},
    {"client": "Mission Increase", "contractor": "Olivia Noelle", "date": "2026-08-15", "month": "Aug 2026", "hours": 2.83, "amount": 170.00, "task": "Logo edits & brand assets"},
    {"client": "Mission Increase", "contractor": "Grace Parker", "date": "2026-06-30", "month": "Jun 2026", "hours": 18.00, "amount": 540.00, "task": "Project coordination & reporting"},
    # Saturate Design & Others
    {"client": "Saturate Design", "contractor": "Jared Roberts", "date": "2026-03-11", "month": "Mar 2026", "hours": 14.23, "amount": 1779.16, "task": "Web design sprint"},
    {"client": "BITS", "contractor": "Josiah Stam", "date": "2026-03-31", "month": "Mar 2026", "hours": 1.00, "amount": 35.00, "task": "Prospectus design"},
    {"client": "Rock Creek", "contractor": "Jared Roberts", "date": "2026-07-24", "month": "Jul 2026", "hours": 1.00, "amount": 125.00, "task": "Template fix"},
    {"client": "BLMH", "contractor": "Josiah Stam", "date": "2026-02-27", "month": "Feb 2026", "hours": 0.60, "amount": 21.00, "task": "Business card updates"}
]

# --- PERSISTENCE FUNCTIONS ---
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

# Load persistent dataset
if "df" not in st.session_state:
    st.session_state.df = load_data()
if "uploaded_files_log" not in st.session_state:
    st.session_state.uploaded_files_log = load_uploaded_log()

# --- HEADER ---
st.title("📊 Roundtree Freelancer Tracker & Client Allocator")
st.markdown("All updates, client reassignments, and uploaded invoices are **permanently saved**.")

# --- FILE UPLOADER WIDGET ---
with st.expander("📥 Upload Additional Invoices / CSVs (Auto-Saved & Deduplicated)", expanded=False):
    uploaded_files = st.file_uploader("Drop new PDF invoices or CSV reports here:", accept_multiple_files=True, type=["pdf", "csv"])
    if uploaded_files:
        new_records = []
        for f in uploaded_files:
            if f.name in st.session_state.uploaded_files_log:
                st.info(f"Skipping already uploaded file: {f.name}")
                continue
            
            # Log file permanently so it won't be duplicated
            st.session_state.uploaded_files_log.add(f.name)
            log_uploaded_file(f.name)

            if f.name.endswith(".csv"):
                new_df = pd.read_csv(f)
                st.success(f"Loaded and saved {len(new_df)} rows from {f.name}")
            elif f.name.endswith(".pdf"):
                reader = PdfReader(f)
                text = "\n".join([page.extract_text() or "" for page in reader.pages])
                st.success(f"Parsed and logged {f.name} successfully!")

# --- KPI METRICS ---
col1, col2, col3, col4 = st.columns(4)
total_spend = st.session_state.df["amount"].sum()
total_hours = st.session_state.df["hours"].sum()
top_client = st.session_state.df.groupby("client")["hours"].sum().idxmax()
top_contractor = st.session_state.df.groupby("contractor")["amount"].sum().idxmax()

col1.metric("Total Contractor Spend", f"${total_spend:,.2f}")
col2.metric("Total Hours Logged", f"{total_hours:,.1f} hrs")
col3.metric("Largest Client by Hours", top_client)
col4.metric("Top Paid Contractor", top_contractor)

st.divider()

# --- VISUAL CHARTS ---
c1, c2 = st.columns(2)
with c1:
    fig_client = px.bar(
        st.session_state.df.groupby("client")[["hours", "amount"]].sum().reset_index(),
        x="client", y="hours", color="client",
        title="Total Contractor Hours by Client",
        labels={"hours": "Hours Logged", "client": "Client"}
    )
    st.plotly_chart(fig_client, use_container_width=True)

with c2:
    fig_contractor = px.pie(
        st.session_state.df.groupby("contractor")["amount"].sum().reset_index(),
        names="contractor", values="amount",
        title="Contractor Spend Distribution",
        hole=0.4
    )
    st.plotly_chart(fig_contractor, use_container_width=True)

st.divider()

# --- MONTHLY AUDIT GRID ---
st.subheader("🗓️ 2026 Monthly Invoice Audit (Missing vs. Uploaded)")
contractors = ["Josiah Stam", "Jared Roberts", "Megan Heath (Zeta)", "TrueLight Branding", "Casper Co.", "Molly Kelley"]
months = ["Jan 2026", "Feb 2026", "Mar 2026", "Apr 2026", "May 2026", "Jun 2026", "Jul 2026", "Aug 2026", "Sep 2026", "Oct 2026", "Nov 2026", "Dec 2026"]

audit_data = []
for c in contractors:
    row = {"Contractor": c}
    for m in months:
        has_inv = not st.session_state.df[(st.session_state.df["contractor"] == c) & (st.session_state.df["month"] == m)].empty
        row[m] = "✅ On File" if has_inv else "❌ Missing"
    audit_data.append(row)

st.dataframe(pd.DataFrame(audit_data), use_container_width=True)

st.divider()

# --- INTERACTIVE DATA TABLE & CLIENT REASSIGNMENT ---
st.subheader("✏️ Interactive Client Allocation & Line Items")
st.caption("Any edits you make here are automatically saved to your permanent database:")

edited_df = st.data_editor(
    st.session_state.df,
    column_config={
        "client": st.column_config.SelectboxColumn(
            "Client",
            options=["Mission Increase", "Geneva", "Saturate Design", "BITS", "Rock Creek", "BLMH", "PCA", "Internal/Agency"],
            required=True
        ),
        "amount": st.column_config.NumberColumn("Amount ($)", format="$%.2f"),
        "hours": st.column_config.NumberColumn("Hours", format="%.2f hrs"),
    },
    num_rows="dynamic",
    use_container_width=True
)

# Auto-save changes immediately to disk
if not edited_df.equals(st.session_state.df):
    st.session_state.df = edited_df
    save_data(edited_df)
    st.toast("Changes auto-saved!", icon="💾")

# Download backup button
csv_bytes = st.session_state.df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Database Backup (CSV)",
    data=csv_bytes,
    file_name="roundtree_freelancer_database.csv",
    mime="text/csv"
)
