import streamlit as st
import pandas as pd
import plotly.express as px

# ======================
# PAGE CONFIG
# ======================
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

# ======================
# STYLING
# ======================
st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}

h1 {
    font-size: 32px !important;
    font-weight: 800 !important;
}

[data-testid="stMetric"] {
    background-color: #111827;
    border: 1px solid #374151;
    padding: 15px;
    border-radius: 14px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

[data-testid="stMetric"] * {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ======================
# LOAD DATA
# ======================
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

df = pd.read_csv(ROOT_DIR / "SuperStoreOrders.csv")

df["sales"] = pd.to_numeric(df["sales"], errors="coerce")
df["profit"] = pd.to_numeric(df["profit"], errors="coerce")
df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
df["order_date"] = pd.to_datetime(df["order_date"], dayfirst=True, errors="coerce")

# ======================
# TITLE
# ======================
st.title("📊 Business Sales Performance Analytics Dashboard")
st.caption("Client-ready dashboard analyzing sales, profit, regional performance, and product trends.")

# ======================
# SIDEBAR FILTERS
# ======================
st.sidebar.header("Dashboard Filters")

years = sorted(df["year"].dropna().unique())
selected_years = st.sidebar.multiselect("Select Year", years, default=years)

regions = sorted(df["region"].dropna().unique())
selected_regions = st.sidebar.multiselect("Select Region", regions, default=regions)

categories = sorted(df["category"].dropna().unique())
selected_categories = st.sidebar.multiselect("Select Category", categories, default=categories)

filtered_df = df[
    (df["year"].isin(selected_years)) &
    (df["region"].isin(selected_regions)) &
    (df["category"].isin(selected_categories))
]

# ======================
# KPI CARDS
# ======================
profit_margin = (total_profit / total_sales) * 100 if total_sales != 0 else 0

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

kpi1.metric("Total Sales", f"${total_sales:,.0f}")
kpi2.metric("Total Profit", f"${total_profit:,.0f}")
kpi3.metric("Total Orders", f"{total_orders:,}")
kpi4.metric("Quantity Sold", f"{total_quantity:,}")
kpi5.metric("Profit Margin", f"{profit_margin:.2f}%")

# ======================
# DATA FOR CHARTS
# ======================
monthly_sales = (
    filtered_df.groupby(filtered_df["order_date"].dt.to_period("M"))["sales"]
    .sum()
    .reset_index()
)

monthly_sales["order_date"] = monthly_sales["order_date"].astype(str)

category_sales = (
    filtered_df.groupby("category")["sales"]
    .sum()
    .reset_index()
    .sort_values("sales", ascending=False)
)

region_sales = (
    filtered_df.groupby("region")["sales"]
    .sum()
    .reset_index()
    .sort_values("sales", ascending=False)
)

top_products = (
    filtered_df.groupby("product_name")["sales"]
    .sum()
    .reset_index()
    .sort_values("sales", ascending=False)
    .head(10)
)

profit_category = (
    filtered_df.groupby("category")["profit"]
    .sum()
    .reset_index()
    .sort_values("profit", ascending=False)
)

# ======================
# CHARTS
# ======================
fig_trend = px.line(
    monthly_sales,
    x="order_date",
    y="sales",
    title="Revenue Trend",
    markers=True
)

fig_category = px.bar(
    category_sales,
    x="category",
    y="sales",
    title="Sales by Category"
)

fig_region = px.bar(
    region_sales,
    x="region",
    y="sales",
    title="Sales by Region"
)

fig_products = px.bar(
    top_products,
    x="sales",
    y="product_name",
    orientation="h",
    title="Top 10 Products"
)

fig_profit = px.bar(
    profit_category,
    x="category",
    y="profit",
    title="Profit by Category"
)

fig_donut = px.pie(
    category_sales,
    values="sales",
    names="category",
    hole=0.55,
    title="Sales Share by Category"
)

fig_donut.update_layout(
    height=300,
    margin=dict(l=20, r=20, t=45, b=20),
    title_font_size=16
)

# Chart sizing
for fig in [fig_trend, fig_category, fig_region, fig_products, fig_profit]:
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=45, b=20),
        title_font_size=16
    )

fig_products.update_layout(yaxis=dict(autorange="reversed"))

# ======================
# DASHBOARD LAYOUT
# ======================
row1_col1, row1_col2, row1_col3 = st.columns(3)

with row1_col1:
    st.plotly_chart(fig_trend, use_container_width=True)

with row1_col2:
    st.plotly_chart(fig_category, use_container_width=True)

with row1_col3:
    st.plotly_chart(fig_region, use_container_width=True)

row2_col1, row2_col2, row2_col3 = st.columns(3)

with row2_col1:
    st.plotly_chart(fig_donut, use_container_width=True)

with row2_col2:
    st.plotly_chart(fig_profit, use_container_width=True)

with row2_col3:
    st.plotly_chart(fig_products, use_container_width=True)

# ===================
#DATA SET PREVIEW
#======================
st.markdown("---")
st.subheader("Dataset Preview")

st.dataframe(
    filtered_df.head(20),
    use_container_width=True
)

csv = filtered_df.to_csv(index=False)

st.download_button(
    "Download Filtered Dataset",
    csv,
    file_name="sales_data.csv",
    mime="text/csv"
)

# ======================
# RECOMMENDATIONS
# ======================
st.markdown("---")
st.subheader("Business Recommendations")

rec1, rec2, rec3, rec4 = st.columns(4)

rec1.info("Invest more in high-profit Technology products.")
rec2.info("Replicate Central region strategies in weaker regions.")
rec3.info("Promote top-selling products through targeted campaigns.")
rec4.info("Improve margins in low-profit categories.")
