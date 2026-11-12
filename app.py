import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import re
from datetime import datetime

# ==============================================================================
# 1. PAGE CONFIG & ROUNDTREE BRAND STYLING
# Brand Palette:
#   Primary: Deep Forest / Pine (#1B3B36)
#   Secondary: Warm Clay / Terracotta (#C2593F)
#   Accent: Sage (#52796F) & Warm Sand (#F4F1EA)
#   Dark Slate: #1E293B
# ==============================================================================
st.set_page_config(
    page_title="Roundtree Agency | Contractor & Client Intelligence",
    page_icon="🌲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS injecting Roundtree Agency typography, card aesthetics, and color scheme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #1E293B;
    }

    h1, h2, h3, .brand-serif {
        font-family: 'Playfair Display', serif !important;
        font-weight: 700;
        color: #1B3B36 !important;
    }

    .stApp {
        background-color: #FAF8F5;
    }

    /* Metric Card Styling */
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E5E1D8;
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0 2px 8px rgba(27, 59, 54, 0.04);
        margin-bottom: 12px;
    }
    .metric-val {
        font-size: 28px;
        font-weight: 700;
        color: #1B3B36;
        margin-top: 4px;
        line-height: 1.2;
    }
    .metric-lbl {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #64748B;
    }
    .metric-sub {
        font-size: 12px;
        color: #94A3B8;
        margin-top: 4px;
    }

    /* Designer Profile Card */
    .designer-card {
        background: #FFFFFF;
        border: 1px solid #E2DCD2;
        border-top: 4px solid #1B3B36;
        border-radius: 10px;
        padding: 18px 20px;
        margin-bottom: 16px;
        transition: transform 0.15s ease;
    }
    .designer-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(27, 59, 54, 0.08);
    }
    .badge-client {
        display: inline-block;
        background-color: #EFECE6;
        color: #1B3B36;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 6px;
        margin-right: 4px;
        margin-bottom: 4px;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        border-bottom: 2px solid #E2DCD2;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 14px;
        font-weight: 600;
        color: #64748B;
        padding: 10px 20px;
        border-radius: 8px 8px 0 0;
    }
    .stTabs [aria-selected="true"] {
        color: #1B3B36 !important;
        border-bottom: 3px solid #C2593F !important;
        background-color: #FFFFFF;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. DATA LOAD & CACHING
# ==============================================================================
DATA_FILE = "ledger_master.csv"

@st.cache_data
def load_data(filepath=DATA_FILE):
    if not os.path.exists(filepath):
        st.error(f"Ledger file not found at {filepath}")
        return pd.DataFrame()
    df = pd.read_csv(filepath)
    df['Hours'] = pd.to_numeric(df['Hours'], errors='coerce').fillna(0.0)
    df['Hourly Rate ($)'] = pd.to_numeric(df['Hourly Rate ($)'], errors='coerce').fillna(0.0)
    df['Total Billed Amount ($)'] = pd.to_numeric(df['Total Billed Amount ($)'], errors='coerce').fillna(0.0)
    df['Work Date / Invoice Date'] = df['Work Date / Invoice Date'].astype(str)
    df['Month'] = df['Work Date / Invoice Date'].apply(lambda x: x[:7] if len(str(x))>=7 else '2026-00')
    return df

df_master = load_data()

# Known client accounts for dropdowns & staging
KNOWN_CLIENTS = [
    "Mission Increase", "Geneva", "PCA Foundation", "Saturate", "BITS",
    "SRG", "Langham", "Christ Presbyterian", "West Paces Advisors",
    "PCA AC", "TGT", "Village Schools International", "byFaith",
    "SETCO", "Rock Creek", "BLMH", "Charlotte Institute for Faith & Work",
    "Internal / Agency Overhead", "Unconfirmed (Needs Review)"
]

# Standard Contractor Rate Card for Ingestion Defaults
DEFAULT_RATES = {
    "Grace Parker": 95.0,
    "Casper Co. LLC": 145.0,
    "Megan Heath": 85.0,
    "Josiah Stam": 35.0,
    "TrueLight Branding, Inc.": 100.0,
    "Molly Kelley": 60.0,
    "Olivia Moore": 85.0,
    "Craft & Calling": 31.0,
    "Piland Legal": 250.0
}

# ==============================================================================
# 3. SIDEBAR CONTROLS & FILTERING
# ==============================================================================
with st.sidebar:
    st.markdown("<h2 class='brand-serif' style='color:#1B3B36; font-size:24px; margin-bottom:0px;'>Roundtree Agency</h2>", unsafe_allow_html=True)
    st.caption("Subcontractor & Client Financial Intelligence • FY 2026")
    st.divider()

    st.subheader("Filter Dashboard")
    all_quarters = ["All Quarters"] + sorted(list(df_master['Month & Quarter'].dropna().unique()))
    sel_quarter = st.selectbox("Quarter / Period", all_quarters)

    all_contractors = ["All Contractors"] + sorted(list(df_master['Contractor Name'].dropna().unique()))
    sel_contractor = st.selectbox("Contractor", all_contractors)

    all_clients = ["All Clients"] + sorted(list(df_master['Client Account'].dropna().unique()))
    sel_client = st.selectbox("Client Account", all_clients)

    st.divider()
    st.markdown("### Agency Rate Policies")
    st.caption("• **Grace Parker**: $95.00/hr (Approved)\n• **Casper Co.**: $145.00/hr\n• **Megan Heath**: $85.00/hr\n• **TrueLight**: $100.00/hr\n• **Pass-Through Printing**: Excluded")

# Apply filters
df_filtered = df_master.copy()
if sel_quarter != "All Quarters":
    df_filtered = df_filtered[df_filtered['Month & Quarter'] == sel_quarter]
if sel_contractor != "All Contractors":
    df_filtered = df_filtered[df_filtered['Contractor Name'] == sel_contractor]
if sel_client != "All Clients":
    df_filtered = df_filtered[df_filtered['Client Account'] == sel_client]

# ==============================================================================
# 4. TOP EXECUTIVE HEADER & METRICS
# ==============================================================================
st.markdown("<h1 style='margin-bottom:2px;'>Financial Audit & Contractor Intelligence</h1>", unsafe_allow_html=True)
st.caption("Audited Subcontractor Expenditures, Client Allocation Pacing, and Capacity Analytics")

tot_spend = df_filtered['Total Billed Amount ($)'].sum()
tot_hours = df_filtered['Hours'].sum()
blended_rate = (tot_spend / tot_hours) if tot_hours > 0 else 0.0
confirmed_spend = df_filtered[df_filtered['Status'] == 'Confirmed']['Total Billed Amount ($)'].sum()
conf_pct = (confirmed_spend / tot_spend * 100) if tot_spend > 0 else 100.0

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-lbl">Total Contractor Spend</div>
        <div class="metric-val">${tot_spend:,.2f}</div>
        <div class="metric-sub">{len(df_filtered)} billable items</div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-lbl">Total Billed Hours</div>
        <div class="metric-val">{tot_hours:,.1f} hrs</div>
        <div class="metric-sub">Across active engagements</div>
    </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-lbl">Blended Hourly Cost</div>
        <div class="metric-val">${blended_rate:,.2f}/hr</div>
        <div class="metric-sub">Effective subcontractor yield</div>
    </div>
    """, unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-lbl">Attribution Rate</div>
        <div class="metric-val">{conf_pct:.1f}%</div>
        <div class="metric-sub">${confirmed_spend:,.0f} verified</div>
    </div>
    """, unsafe_allow_html=True)
with c5:
    active_contractors = df_filtered['Contractor Name'].nunique()
    active_clients = df_filtered['Client Account'].nunique()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-lbl">Active Roster</div>
        <div class="metric-val">{active_contractors} Cont / {active_clients} Cl</div>
        <div class="metric-sub">In selected period</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ==============================================================================
# 5. MAIN NAVIGATION TABS
# ==============================================================================
tab_clients, tab_contractors, tab_velocity, tab_matrix, tab_ledger, tab_ingest = st.tabs([
    "📊 Client Analytics & Donuts",
    "👤 Designer & Contractor Cards",
    "📈 Monthly Burn & Velocity",
    "🧩 Utilization & Dependency Matrix",
    "📑 Master Ledger Explorer",
    "📥 Ingestion & Staging Review"
])

# ------------------------------------------------------------------------------
# TAB 1: Client Analytics & Donut Charts
# ------------------------------------------------------------------------------
with tab_clients:
    st.markdown("### Client Capacity & Expenditure Allocation")
    st.caption("Comparison between financial spend and actual production hours absorbed by each client account.")

    # Aggregate client spend & hours
    client_agg = df_filtered.groupby('Client Account').agg(
        Total_Spend=('Total Billed Amount ($)', 'sum'),
        Total_Hours=('Hours', 'sum'),
        Line_Items=('Item ID', 'count')
    ).reset_index()

    # Color palette matching Roundtree brand
    brand_colors = [
        '#1B3B36', '#C2593F', '#2D5A52', '#D97706', '#4B7B70',
        '#E07A5F', '#3D405B', '#81B29A', '#F2CC8F', '#6D6875',
        '#B5838D', '#E5989B', '#FFB4A2', '#6D597A', '#355070'
    ]

    col_d1, col_d2 = st.columns(2)

    with col_d1:
        fig_spend = px.pie(
            client_agg,
            names='Client Account',
            values='Total_Spend',
            hole=0.55,
            title="<b>Share of Contractor Spend ($)</b>",
            color_discrete_sequence=brand_colors
        )
        fig_spend.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#FFFFFF', width=2)))
        fig_spend.update_layout(showlegend=False, margin=dict(t=50, b=20, l=20, r=20), height=380)
        st.plotly_chart(fig_spend, use_container_width=True)

    with col_d2:
        fig_hours = px.pie(
            client_agg,
            names='Client Account',
            values='Total_Hours',
            hole=0.55,
            title="<b>Share of Production Hours (hrs)</b>",
            color_discrete_sequence=brand_colors
        )
        fig_hours.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#FFFFFF', width=2)))
        fig_hours.update_layout(showlegend=False, margin=dict(t=50, b=20, l=20, r=20), height=380)
        st.plotly_chart(fig_hours, use_container_width=True)

    st.markdown("#### Client Account Ledger Summary")
    client_agg['Effective Rate ($/hr)'] = client_agg.apply(lambda r: (r['Total_Spend'] / r['Total_Hours']) if r['Total_Hours'] > 0 else 0.0, axis=1)
    client_agg['% of Total Spend'] = (client_agg['Total_Spend'] / tot_spend * 100) if tot_spend > 0 else 0.0
    client_agg = client_agg.sort_values(by='Total_Spend', ascending=False)

    st.dataframe(
        client_agg.style.format({
            'Total_Spend': '${:,.2f}',
            'Total_Hours': '{:,.2f} hrs',
            'Line_Items': '{:,}',
            'Effective Rate ($/hr)': '${:,.2f}',
            '% of Total Spend': '{:.2f}%'
        }),
        use_container_width=True
    )

# ------------------------------------------------------------------------------
# TAB 2: Designer & Contractor Profile Cards
# ------------------------------------------------------------------------------
with tab_contractors:
    st.markdown("### Designer Roster & Capacity Cards")
    st.caption("Active subcontractors, contracted rates, total volume delivered, and client client portfolios.")

    contractor_groups = df_filtered.groupby('Contractor Name')
    c_names = sorted(list(contractor_groups.groups.keys()))

    # Render in 3-column responsive card layout
    cols_per_row = 3
    for i in range(0, len(c_names), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            idx = i + j
            if idx < len(c_names):
                c_name = c_names[idx]
                c_df = contractor_groups.get_group(c_name)
                c_spend = c_df['Total Billed Amount ($)'].sum()
                c_hours = c_df['Hours'].sum()
                c_eff_rate = (c_spend / c_hours) if c_hours > 0 else DEFAULT_RATES.get(c_name, 0.0)
                c_clients = sorted(list(c_df['Client Account'].unique()))

                # Badges HTML
                badges_html = "".join([f"<span class='badge-client'>{cl}</span>" for cl in c_clients])

                with cols[j]:
                    st.markdown(f"""
                    <div class="designer-card">
                        <div style="font-size:18px; font-weight:700; color:#1B3B36;">{c_name}</div>
                        <div style="font-size:12px; color:#64748B; margin-bottom:12px;">{len(c_df)} Line Items Billed</div>
                        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                            <div>
                                <div style="font-size:10px; color:#94A3B8; text-transform:uppercase; font-weight:700;">Total Spend</div>
                                <div style="font-size:16px; font-weight:700; color:#1B3B36;">${c_spend:,.2f}</div>
                            </div>
                            <div>
                                <div style="font-size:10px; color:#94A3B8; text-transform:uppercase; font-weight:700;">Hours Logged</div>
                                <div style="font-size:16px; font-weight:700; color:#1B3B36;">{c_hours:,.1f} hrs</div>
                            </div>
                            <div>
                                <div style="font-size:10px; color:#94A3B8; text-transform:uppercase; font-weight:700;">Effective Rate</div>
                                <div style="font-size:16px; font-weight:700; color:#C2593F;">${c_eff_rate:,.1f}/hr</div>
                            </div>
                        </div>
                        <div style="font-size:10px; color:#94A3B8; text-transform:uppercase; font-weight:700; margin-top:12px; margin-bottom:6px;">Client Engagements</div>
                        <div>{badges_html}</div>
                    </div>
                    """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# TAB 3: Monthly Burn & Velocity Tracking
# ------------------------------------------------------------------------------
with tab_velocity:
    st.markdown("### Monthly Spend Velocity & Freelancer Burn Rate")
    st.caption("Month-over-month trajectory of subcontractor expenditures and operational cadence.")

    # Group by Month
    monthly_df = df_filtered.groupby(['Month', 'Client Account'])['Total Billed Amount ($)'].sum().reset_index()
    monthly_total = df_filtered.groupby('Month').agg(
        Monthly_Spend=('Total Billed Amount ($)', 'sum'),
        Monthly_Hours=('Hours', 'sum')
    ).reset_index()

    # Calculate MoM Growth & Rolling Velocity
    monthly_total['Spend Velocity (3-Mo MA)'] = monthly_total['Monthly_Spend'].rolling(window=3, min_periods=1).mean()

    # Stacked Bar Chart for Monthly Spend by Client
    fig_monthly = px.bar(
        monthly_df,
        x='Month',
        y='Total Billed Amount ($)',
        color='Client Account',
        title="<b>Monthly Contractor Spend by Client ($)</b>",
        color_discrete_sequence=brand_colors
    )
    fig_monthly.update_layout(barmode='stack', height=400, margin=dict(t=50, b=20, l=20, r=20), xaxis_title="Billing Month", yaxis_title="Gross Spend ($)")
    st.plotly_chart(fig_monthly, use_container_width=True)

    # Line Chart for Velocity
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=monthly_total['Month'],
        y=monthly_total['Monthly_Spend'],
        mode='lines+markers',
        name='Actual Monthly Spend',
        line=dict(color='#C2593F', width=3),
        marker=dict(size=7)
    ))
    fig_line.add_trace(go.Scatter(
        x=monthly_total['Month'],
        y=monthly_total['Spend Velocity (3-Mo MA)'],
        mode='lines',
        name='3-Month Moving Average Velocity',
        line=dict(color='#1B3B36', width=2, dash='dash')
    ))
    fig_line.update_layout(
        title="<b>Agency Contractor Spend Velocity & Trajectory</b>",
        xaxis_title="Billing Month",
        yaxis_title="Monthly Spend ($)",
        height=350,
        margin=dict(t=50, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_line, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 4: Utilization & Dependency Matrix (Heatmap)
# ------------------------------------------------------------------------------
with tab_matrix:
    st.markdown("### Contractor Utilization & Client Dependency Matrix")
    st.caption("Cross-tabulation showing contractor allocation across clients and single-contractor account dependencies.")

    # Pivot table of Contractor vs Client
    matrix_df = pd.pivot_table(
        df_filtered,
        values='Total Billed Amount ($)',
        index='Contractor Name',
        columns='Client Account',
        aggfunc='sum',
        fill_value=0.0
    )

    fig_heat = px.imshow(
        matrix_df,
        text_auto=".0f",
        aspect="auto",
        color_continuous_scale=[[0, '#F9F8F6'], [0.2, '#E2DCD2'], [0.5, '#52796F'], [1.0, '#1B3B36']],
        title="<b>Contractor × Client Spend Distribution ($)</b>"
    )
    fig_heat.update_layout(
        height=450,
        margin=dict(t=50, b=20, l=20, r=20),
        xaxis_title="Client Account",
        yaxis_title="Contractor"
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    st.info("💡 **Auditor Insight**: Deep green cells represent high contractor-client concentration (e.g., Casper Co. on Geneva, Jared Roberts on Mission Increase, Megan Heath on BITS).")

# ------------------------------------------------------------------------------
# TAB 5: Master Ledger Explorer
# ------------------------------------------------------------------------------
with tab_ledger:
    st.markdown("### Master Accounting & Audit Ledger (FY 2026)")
    st.caption("Searchable, filterable audit ledger with exact verbatim invoice task descriptions and source citations.")

    search_query = st.text_input("🔍 Search verbatim task description, Asana link, or item ID:", "")
    ledger_display = df_filtered.copy()

    if search_query:
        mask = ledger_display['Exact Verbatim Invoice Task Description'].str.contains(search_query, case=False, na=False) | \
               ledger_display['Item ID'].str.contains(search_query, case=False, na=False) | \
               ledger_display['Client Account'].str.contains(search_query, case=False, na=False)
        ledger_display = ledger_display[mask]

    st.dataframe(
        ledger_display[[
            'Item ID', 'Contractor Name', 'Client Account', 'Status',
            'Work Date / Invoice Date', 'Month & Quarter', 'Hours',
            'Hourly Rate ($)', 'Total Billed Amount ($)',
            'Exact Verbatim Invoice Task Description', 'Source Invoice File Name'
        ]].style.format({
            'Hours': '{:,.2f}',
            'Hourly Rate ($)': '${:,.2f}',
            'Total Billed Amount ($)': '${:,.2f}'
        }),
        use_container_width=True,
        height=500
    )

    csv_data = ledger_display.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Ledger as CSV",
        data=csv_data,
        file_name="roundtree_filtered_ledger.csv",
        mime="text/csv"
    )

# ------------------------------------------------------------------------------
# TAB 6: Ingestion & Staging Review Modal
# ------------------------------------------------------------------------------
with tab_ingest:
    st.markdown("### Smart Invoice Ingestion & Staging Review")
    st.caption("Upload incoming invoices (CSV or PDF) to stage, verify client tags, and append directly to the master ledger.")

    uploaded_file = st.file_uploader("Upload Contractor Invoice or Timesheet", type=['csv', 'xlsx'])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                staging_df = pd.read_csv(uploaded_file)
            else:
                staging_df = pd.read_excel(uploaded_file)
            
            st.success(f"Uploaded **{uploaded_file.name}** successfully ({len(staging_df)} rows detected).")

            st.markdown("#### Review & Adjust Staging Grid Before Commit")
            st.caption("Ensure each task is mapped to the correct Client Account. Change any unassigned row before appending.")

            # Editable Staging Grid
            edited_df = st.data_editor(
                staging_df,
                num_rows="dynamic",
                use_container_width=True,
                height=300
            )

            if st.button("✅ Commit Staging Items to Master Ledger", type="primary"):
                # Append and save logic
                combined_df = pd.concat([df_master, edited_df], ignore_index=True)
                combined_df.to_csv(DATA_FILE, index=False)
                st.success("Successfully committed new rows to master ledger! Refresh dashboard to view updated analytics.")
                st.cache_data.clear()

        except Exception as e:
            st.error(f"Error parsing uploaded file: {str(e)}")
    else:
        st.markdown("""
        <div style="background:#FFFFFF; border:2px dashed #CBD5E1; border-radius:12px; padding:30px; text-align:center;">
            <div style="font-size:32px; margin-bottom:8px;">📄</div>
            <div style="font-size:16px; font-weight:600; color:#1B3B36;">Drag and drop new contractor invoices or timesheets here</div>
            <div style="font-size:13px; color:#64748B; margin-top:4px;">Supported formats: CSV, XLSX (and future PDF OCR parses)</div>
        </div>
        """, unsafe_allow_html=True)
