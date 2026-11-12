import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import datetime

# ==============================================================================
# 1. PAGE SETUP & ROUNDTREE BRAND THEME
# ==============================================================================
st.set_page_config(
    page_title="Roundtree Agency • Freelancer & Client Dashboard",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Brand Styling (Deep Pine #1B3B36, Warm Terracotta #C2593F, Warm Sand #FAF8F5)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@0,600;0,700;1,600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #2D3748;
    }
    .stApp {
        background-color: #FAF8F5;
    }
    h1, h2, h3, .brand-serif {
        font-family: 'Playfair Display', Georgia, serif;
        color: #1B3B36;
        letter-spacing: -0.01em;
    }
    
    /* Friendly Metric Cards */
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #EAE5DD;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(27, 59, 54, 0.04);
        margin-bottom: 12px;
    }
    .metric-lbl {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        color: #64748B;
        letter-spacing: 0.06em;
        margin-bottom: 4px;
    }
    .metric-val {
        font-size: 26px;
        font-weight: 800;
        color: #1B3B36;
        line-height: 1.1;
    }
    .metric-sub {
        font-size: 12px;
        color: #52796F;
        margin-top: 5px;
        font-weight: 500;
    }

    /* Freelancer Profile Cards */
    .designer-card {
        background-color: #FFFFFF;
        border: 1px solid #EAE5DD;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(27, 59, 54, 0.04);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
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
        padding: 10px 18px;
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
    
    # Month in YYYY-MM
    df['Month'] = df['Work Date / Invoice Date'].apply(lambda x: str(x)[:7] if len(str(x))>=7 else '2026-01')
    
    # Clean Quarter helper
    def clean_q(val):
        s = str(val)
        if 'Q1' in s or s in ['2026-01', '2026-02', '2026-03']:
            return 'Q1 (Jan - Mar)'
        elif 'Q2' in s or s in ['2026-04', '2026-05', '2026-06']:
            return 'Q2 (Apr - Jun)'
        elif 'Q3' in s or s in ['2026-07', '2026-08', '2026-09']:
            return 'Q3 (Jul - Sep)'
        elif 'Q4' in s or s in ['2026-10', '2026-11', '2026-12']:
            return 'Q4 (Oct - Dec)'
        return 'Q1 (Jan - Mar)'

    df['Quarter'] = df['Month & Quarter'].apply(clean_q)
    return df

df_master = load_data()

# Recognized clients
KNOWN_CLIENTS = [
    "Mission Increase", "Geneva", "PCA Foundation", "Saturate", "BITS",
    "SRG", "Langham", "Christ Presbyterian", "West Paces Advisors",
    "PCA AC", "TGT", "Village Schools International", "byFaith",
    "SETCO", "Rock Creek", "BLMH", "Charlotte Institute for Faith & Work",
    "Internal / Agency Overhead", "Unconfirmed (Needs Review)"
]

# Standard Contractor Rate Card
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

# Brand chart colors
BRAND_COLORS = [
    '#1B3B36', '#C2593F', '#2D5A52', '#D97706', '#4B7B70',
    '#E07A5F', '#3D405B', '#81B29A', '#F2CC8F', '#6D6875',
    '#B5838D', '#E5989B', '#FFB4A2', '#6D597A', '#355070'
]

# ==============================================================================
# 3. SIDEBAR CONTROLS & CLEAN FILTERING
# ==============================================================================
with st.sidebar:
    st.markdown("<h2 class='brand-serif' style='color:#1B3B36; font-size:24px; margin-bottom:0px;'>Roundtree Agency</h2>", unsafe_allow_html=True)
    st.caption("Freelancer & Client Dashboard • 2026")
    st.divider()

    st.subheader("Filter the View")
    
    # 1. Clean Period Filter (Fixes Issue #1: Full Year 2026 includes all contractors!)
    period_options = [
        "Full Year 2026 (All)",
        "Q1 2026 (Jan - Mar)",
        "Q2 2026 (Apr - Jun)",
        "Q3 2026 (Jul - Sep)",
        "Q4 2026 (Oct - Dec)"
    ]
    sel_period = st.selectbox("Quarter / Period", period_options)

    # 2. Contractor Filter
    all_contractors = ["All Freelancers"] + sorted(list(df_master['Contractor Name'].dropna().unique()))
    sel_contractor = st.selectbox("Freelancer / Designer", all_contractors)

    # 3. Client Filter
    all_clients = ["All Clients"] + sorted(list(df_master['Client Account'].dropna().unique()))
    sel_client = st.selectbox("Client Account", all_clients)

    # 4. Optional Month Filter
    month_options = ["All Months"] + sorted(list(df_master['Month'].dropna().unique()))
    sel_month = st.selectbox("Specific Month (Optional)", month_options)

    st.divider()
    st.markdown("### Hourly Rates on File")
    st.caption("• **Grace Parker**: $95.00/hr\n• **Casper Co.**: $145.00/hr\n• **Megan Heath**: $85.00/hr\n• **TrueLight**: $100.00/hr\n• **Molly Kelley**: $60.00/hr\n• **Josiah Stam**: $35.00/hr\n\n*Note: Vendor printing costs (like booklets) are excluded so we only look at design and consulting labor.*")

# Apply filters smoothly
df_filtered = df_master.copy()

if sel_period != "Full Year 2026 (All)":
    q_target = sel_period.split(" ")[0] # e.g. "Q1", "Q2"
    df_filtered = df_filtered[df_filtered['Quarter'].str.contains(q_target, na=False)]

if sel_month != "All Months":
    df_filtered = df_filtered[df_filtered['Month'] == sel_month]

if sel_contractor != "All Freelancers":
    df_filtered = df_filtered[df_filtered['Contractor Name'] == sel_contractor]

if sel_client != "All Clients":
    df_filtered = df_filtered[df_filtered['Client Account'] == sel_client]

# ==============================================================================
# 4. TOP EXECUTIVE HEADER & METRICS (EASY-TO-UNDERSTAND LABELS)
# ==============================================================================
st.markdown("<h1 style='margin-bottom:2px;'>Freelancer & Client Dashboard</h1>", unsafe_allow_html=True)
st.caption("Track how much we're spending on freelancers, which clients they're supporting, and where our design hours go.")

tot_spend = df_filtered['Total Billed Amount ($)'].sum()
tot_hours = df_filtered['Hours'].sum()
blended_rate = (tot_spend / tot_hours) if tot_hours > 0 else 0.0
confirmed_spend = df_filtered[df_filtered['Status'] == 'Confirmed']['Total Billed Amount ($)'].sum()
conf_pct = (confirmed_spend / tot_spend * 100) if tot_spend > 0 else 100.0

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-lbl">Total Money Spent</div>
        <div class="metric-val">${tot_spend:,.2f}</div>
        <div class="metric-sub">{len(df_filtered)} tasks completed</div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-lbl">Total Hours Worked</div>
        <div class="metric-val">{tot_hours:,.1f} hrs</div>
        <div class="metric-sub">Logged across projects</div>
    </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-lbl">Average Hourly Rate</div>
        <div class="metric-val">${blended_rate:,.2f}/hr</div>
        <div class="metric-sub">Across all freelancers</div>
    </div>
    """, unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-lbl">Assigned to Clients</div>
        <div class="metric-val">{conf_pct:.1f}%</div>
        <div class="metric-sub">${confirmed_spend:,.0f} verified</div>
    </div>
    """, unsafe_allow_html=True)
with c5:
    active_contractors = df_filtered['Contractor Name'].nunique()
    active_clients = df_filtered['Client Account'].nunique()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-lbl">Active Team & Clients</div>
        <div class="metric-val">{active_contractors} Team / {active_clients} Cl</div>
        <div class="metric-sub">In selected view</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ==============================================================================
# 5. MAIN NAVIGATION TABS (CLEAR, JARGON-FREE HEADINGS)
# ==============================================================================
tab_clients, tab_contractors, tab_velocity, tab_matrix, tab_ledger, tab_ingest = st.tabs([
    "📊 Client Spending & Hours",
    "👤 Freelancer Cards & Rates",
    "📈 Monthly Spending & Trends",
    "🧩 Who Works on What",
    "📑 Master List & Search",
    "📥 Add New Invoices"
])

# ------------------------------------------------------------------------------
# TAB 1: Client Spending & Hours (Donut Charts with Plain Explanations)
# ------------------------------------------------------------------------------
with tab_clients:
    st.markdown("### Where Our Money and Hours Go by Client")
    st.caption("Here is how our freelancer dollars compare to the actual hours worked. If a client has a large slice of hours but a smaller slice of money, it means they are using lower-cost design help.")

    # Aggregate client spend & hours
    client_agg = df_filtered.groupby('Client Account').agg(
        Total_Spend=('Total Billed Amount ($)', 'sum'),
        Total_Hours=('Hours', 'sum'),
        Line_Items=('Item ID', 'count')
    ).reset_index()

    col_d1, col_d2 = st.columns(2)

    with col_d1:
        fig_spend = px.pie(
            client_agg,
            names='Client Account',
            values='Total_Spend',
            hole=0.55,
            title="<b>Money Spent by Client ($)</b>",
            color_discrete_sequence=BRAND_COLORS
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
            title="<b>Hours Worked by Client (hrs)</b>",
            color_discrete_sequence=BRAND_COLORS
        )
        fig_hours.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#FFFFFF', width=2)))
        fig_hours.update_layout(showlegend=False, margin=dict(t=50, b=20, l=20, r=20), height=380)
        st.plotly_chart(fig_hours, use_container_width=True)

    st.markdown("#### Client Breakdown Table")
    client_agg['Average Rate ($/hr)'] = client_agg.apply(lambda r: (r['Total_Spend'] / r['Total_Hours']) if r['Total_Hours'] > 0 else 0.0, axis=1)
    client_agg['Share of Spending'] = (client_agg['Total_Spend'] / tot_spend * 100) if tot_spend > 0 else 0.0
    client_agg = client_agg.sort_values(by='Total_Spend', ascending=False)

    st.dataframe(
        client_agg.rename(columns={
            'Client Account': 'Client',
            'Total_Spend': 'Money Spent ($)',
            'Total_Hours': 'Hours Worked',
            'Line_Items': 'Tasks Completed',
            'Share of Spending': '% of Total Spend'
        }).style.format({
            'Money Spent ($)': '${:,.2f}',
            'Hours Worked': '{:,.2f} hrs',
            'Tasks Completed': '{:,}',
            'Average Rate ($/hr)': '${:,.2f}',
            '% of Total Spend': '{:.1f}%'
        }),
        use_container_width=True
    )

# ------------------------------------------------------------------------------
# TAB 2: Freelancer Cards & Rates
# ------------------------------------------------------------------------------
with tab_contractors:
    st.markdown("### Meet Our Freelancers")
    st.caption("Here is a quick snapshot of each designer or partner: their hourly rate, total hours worked, what we've paid them, and which clients they've helped.")

    contractor_groups = df_filtered.groupby('Contractor Name')
    c_names = sorted(list(contractor_groups.groups.keys()))

    if len(c_names) == 0:
        st.info("No freelancers match the selected filter. Try selecting 'Full Year 2026' or 'All Freelancers' in the sidebar.")
    else:
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
                            <div style="font-size:12px; color:#64748B; margin-bottom:12px;">{len(c_df)} tasks completed</div>
                            <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                                <div>
                                    <div style="font-size:10px; color:#94A3B8; text-transform:uppercase; font-weight:700;">Money Paid</div>
                                    <div style="font-size:16px; font-weight:700; color:#1B3B36;">${c_spend:,.2f}</div>
                                </div>
                                <div>
                                    <div style="font-size:10px; color:#94A3B8; text-transform:uppercase; font-weight:700;">Hours Logged</div>
                                    <div style="font-size:16px; font-weight:700; color:#1B3B36;">{c_hours:,.1f} hrs</div>
                                </div>
                                <div>
                                    <div style="font-size:10px; color:#94A3B8; text-transform:uppercase; font-weight:700;">Hourly Rate</div>
                                    <div style="font-size:16px; font-weight:700; color:#C2593F;">${c_eff_rate:,.1f}/hr</div>
                                </div>
                            </div>
                            <div style="font-size:10px; color:#94A3B8; text-transform:uppercase; font-weight:700; margin-top:12px; margin-bottom:6px;">Clients Helped</div>
                            <div>{badges_html}</div>
                        </div>
                        """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# TAB 3: Monthly Spending & Trends (Fixes Issue #2: Grace distributed correctly!)
# ------------------------------------------------------------------------------
with tab_velocity:
    st.markdown("### How Our Freelancer Spending Changes Each Month")
    st.caption("See our monthly freelancer costs over time, broken down by client. The trendline below shows our 3-month spending average so we can easily spot if costs are rising or cooling off.")

    # Group by Month
    monthly_df = df_filtered.groupby(['Month', 'Client Account'])['Total Billed Amount ($)'].sum().reset_index()
    monthly_total = df_filtered.groupby('Month').agg(
        Monthly_Spend=('Total Billed Amount ($)', 'sum'),
        Monthly_Hours=('Hours', 'sum')
    ).reset_index()

    # Calculate MoM Growth & Rolling Velocity
    monthly_total['3-Month Average Spending'] = monthly_total['Monthly_Spend'].rolling(window=3, min_periods=1).mean()

    # Stacked Bar Chart for Monthly Spend by Client
    fig_monthly = px.bar(
        monthly_df,
        x='Month',
        y='Total Billed Amount ($)',
        color='Client Account',
        title="<b>Monthly Freelancer Spending by Client ($)</b>",
        color_discrete_sequence=BRAND_COLORS
    )
    fig_monthly.update_layout(
        barmode='stack',
        height=400,
        margin=dict(t=50, b=20, l=20, r=20),
        xaxis_title="Month",
        yaxis_title="Total Spent ($)"
    )
    st.plotly_chart(fig_monthly, use_container_width=True)

    # Line Chart for Velocity
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=monthly_total['Month'],
        y=monthly_total['Monthly_Spend'],
        mode='lines+markers',
        name='Actual Monthly Spending',
        line=dict(color='#C2593F', width=3),
        marker=dict(size=7)
    ))
    fig_line.add_trace(go.Scatter(
        x=monthly_total['Month'],
        y=monthly_total['3-Month Average Spending'],
        mode='lines',
        name='3-Month Average Spending',
        line=dict(color='#1B3B36', width=2, dash='dash')
    ))
    fig_line.update_layout(
        title="<b>Spending Trendline (Actual vs. 3-Month Average)</b>",
        xaxis_title="Month",
        yaxis_title="Monthly Spending ($)",
        height=350,
        margin=dict(t=50, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_line, use_container_width=True)

    st.info("💡 **What this tells us**: Spending averages around $4,000 to $5,500 each month, with natural peaks in March, June, and September/October around key client project deliveries.")

# ------------------------------------------------------------------------------
# TAB 4: Who Works on What (Heatmap)
# ------------------------------------------------------------------------------
with tab_matrix:
    st.markdown("### Who Works on What (Freelancer × Client Map)")
    st.caption("A bird's-eye view of who is doing the work for each client. Darker boxes mean that freelancer did a large portion of the client's work. It's an easy way to see if a client depends heavily on a single designer.")

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
        title="<b>Total Dollars Spent: Freelancer × Client</b>"
    )
    fig_heat.update_layout(
        height=450,
        margin=dict(t=50, b=20, l=20, r=20),
        xaxis_title="Client Account",
        yaxis_title="Freelancer"
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    st.info("💡 **Key Takeaways**: Geneva's long-form strategy and booklets flow primarily to Casper Co. and Josiah Stam. Mission Increase utilizes Jared Roberts and TrueLight for heavy design blocks. BITS is almost entirely designed by Megan Heath.")

# ------------------------------------------------------------------------------
# TAB 5: Master List & Search
# ------------------------------------------------------------------------------
with tab_ledger:
    st.markdown("### Master Task List & Search")
    st.caption("Search for any individual invoice line item, look up Asana tasks, or download the full list for your records.")

    search_query = st.text_input("🔍 Search by task description, Asana link, or item ID:", "")
    ledger_display = df_filtered.copy()

    if search_query:
        mask = ledger_display['Exact Verbatim Invoice Task Description'].str.contains(search_query, case=False, na=False) | \
               ledger_display['Item ID'].str.contains(search_query, case=False, na=False) | \
               ledger_display['Contractor Name'].str.contains(search_query, case=False, na=False) | \
               ledger_display['Client Account'].str.contains(search_query, case=False, na=False)
        ledger_display = ledger_display[mask]

    cols_show = [
        'Item ID', 'Contractor Name', 'Client Account', 'Status',
        'Work Date / Invoice Date', 'Hours', 'Hourly Rate ($)',
        'Total Billed Amount ($)', 'Exact Verbatim Invoice Task Description',
        'Source Invoice File Name'
    ]

    st.dataframe(
        ledger_display[cols_show].style.format({
            'Hours': '{:.2f}',
            'Hourly Rate ($)': '${:,.2f}',
            'Total Billed Amount ($)': '${:,.2f}'
        }),
        use_container_width=True,
        height=500
    )

    csv_data = ledger_display[cols_show].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Current List as CSV",
        data=csv_data,
        file_name=f"roundtree_freelancer_ledger_{datetime.date.today()}.csv",
        mime="text/csv"
    )

# ------------------------------------------------------------------------------
# TAB 6: Add New Invoices & Review
# ------------------------------------------------------------------------------
with tab_ingest:
    st.markdown("### Add New Invoices or Timesheets")
    st.caption("Upload a newly received invoice or timesheet CSV/Excel file. The app will preview the lines below so you can double-check the client assignments before saving them to the permanent list.")

    uploaded_file = st.file_uploader("Upload Contractor Invoice or Timesheet (CSV or Excel)", type=['csv', 'xlsx'])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                staged_df = pd.read_csv(uploaded_file)
            else:
                staged_df = pd.read_excel(uploaded_file)

            st.success(f"Loaded {len(staged_df)} rows from {uploaded_file.name}")
            st.markdown("#### Review Client Assignments")
            st.caption("You can edit client names right in the table before clicking Save.")

            # Make editable in st.data_editor
            edited_df = st.data_editor(
                staged_df,
                use_container_width=True,
                num_rows="dynamic"
            )

            if st.button("✅ Save These Items to Master List", type="primary"):
                # Save logic
                combined_df = pd.concat([df_master, edited_df], ignore_index=True)
                combined_df.to_csv(DATA_FILE, index=False)
                st.cache_data.clear()
                st.success("Successfully added new items to the master list! Refresh the page to see updated numbers.")
        except Exception as e:
            st.error(f"Error parsing file: {e}")
    else:
        st.info("Tip: You can upload Grace's timesheets, Casper's itemized invoices, or standard freelancer CSVs here at any time.")
