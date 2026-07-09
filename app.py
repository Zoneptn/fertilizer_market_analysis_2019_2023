import streamlit as st
import pandas as pd
import plotly.express as px
import calendar


st.set_page_config(
    page_title="Thailand Fertilizer Import Dashboard",
    layout="wide"
)

st.title("Thailand Fertilizer Import Dashboard")
st.caption("Overview of Fertilizer Imports (2019–2023)")

df = pd.read_excel("fertilizer_import_2019_2023_cleaned.xlsx")


#==========================
# Clean data
#==========================
df.columns = df.columns.str.strip()

df["QUANTITY(MT)"] = pd.to_numeric(df["QUANTITY(MT)"], errors="coerce")
df["VALUE CIF(BAHT)"] = pd.to_numeric(df["VALUE CIF(BAHT)"], errors="coerce")
df["Avg Bht/MT"] = pd.to_numeric(df["Avg Bht/MT"], errors="coerce")

df = df.dropna(subset=["QUANTITY(MT)", "VALUE CIF(BAHT)"])

#==========================
# Side bar
#==========================
st.sidebar.header("Filters")

year = st.sidebar.multiselect(
    "Year",
    sorted(df["Year"].unique()),
    default=sorted(df["Year"].unique())
)
df_year = df[df["Year"].isin(year)]

formula = st.sidebar.multiselect(
    "Formula",
    sorted(df_year["FORMULA"].unique())
)
df_formula = df_year.copy()

if formula:
    df_formula = df_formula[df_formula["FORMULA"].isin(formula)]

importer = st.sidebar.multiselect(
    "Importer",
    sorted(df_formula["Importer"].unique())
)
df_importer = df_formula.copy()

if importer:
    df_importer = df_importer[df_importer["Importer"].isin(importer)]

origin = st.sidebar.multiselect(
    "Origin",
    sorted(df_importer["Origin"].unique())
)
df_origin = df_importer.copy()

if origin:
    df_origin = df_origin[df_origin["Origin"].isin(origin)]

fert_type = st.sidebar.multiselect(
    "Type",
    sorted(df_origin["Type"].dropna().unique())
)
filtered = df_origin.copy()

if fert_type:
    filtered = filtered[filtered["Type"].isin(fert_type)]

#==========================
# Apply filters
#==========================
filtered = df.copy()

if year:
    filtered = filtered[filtered["Year"].isin(year)]

if formula:
    filtered = filtered[filtered["FORMULA"].isin(formula)]

if importer:
    filtered = filtered[filtered["Importer"].isin(importer)]

if origin:
    filtered = filtered[filtered["Origin"].isin(origin)]

if fert_type:
    filtered = filtered[filtered["Type"].isin(fert_type)]
    


#==========================
# KPI calculation
#==========================
total_volume = filtered["QUANTITY(MT)"].sum()

total_value = filtered["VALUE CIF(BAHT)"].sum()

avg_price = total_value / total_volume if total_volume > 0 else 0

num_importers = filtered["Importer"].nunique()

num_origin = filtered["Origin"].nunique()

num_formula = filtered["FORMULA"].nunique()


#==========================
# KPI cards
#==========================
st.subheader("Overview")

c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric(
    "Import Volume",
    f"{total_volume:,.0f} MT"
)

c2.metric(
    "Import Value",
    f"{total_value/1e9:,.2f} B THB"
)

c3.metric(
    "Avg Price",
    f"{avg_price:,.0f} THB/MT"
)

c4.metric(
    "Importers",
    num_importers
)

c5.metric(
    "Origins",
    num_origin
)

c6.metric(
    "Formulas",
    num_formula
)


#==========================
# Yearly trends
#==========================

yearly = (
    filtered
    .groupby("Year", as_index=False)
    .agg(
        Volume=("QUANTITY(MT)", "sum"),
        Value=("VALUE CIF(BAHT)", "sum")
    )
)

yearly["Avg Price"] = yearly["Value"] / yearly["Volume"]

#==========================
# Volume trends
#==========================

fig = px.line(
    yearly,
    x="Year",
    y="Volume",
    markers=True,
    title="Import Volume by Year"
)
fig.update_traces(
    hovertemplate="%{y:,.2f}<extra></extra>"
)
st.plotly_chart(fig, use_container_width=True)

#==========================
# Value trends
#==========================
fig = px.line(
    yearly,
    x="Year",
    y="Value",
    markers=True,
    title="Import Value by Year"
)
fig.update_traces(
    hovertemplate="%{y:,.2f}<extra></extra>"
)
st.plotly_chart(fig, use_container_width=True)

#==========================
# Average Price trends
#==========================
fig = px.line(
    yearly,
    x="Year",
    y="Avg Price",
    markers=True,
    title="Average Import Price"
)
fig.update_traces(
    hovertemplate="%{y:,.2f}<extra></extra>"
)

st.plotly_chart(fig, use_container_width=True)


#==========================
# Top Formulas
#==========================
formula_df = (
    filtered
    .groupby("FORMULA", as_index=False)["QUANTITY(MT)"]
    .sum()
    .sort_values("QUANTITY(MT)", ascending=False)
    .head(10)
)

fig = px.bar(
    formula_df,
    x="QUANTITY(MT)",
    y="FORMULA",
    orientation="h",
    title="Top 10 Fertilizer Formulas"
)

fig.update_layout(yaxis=dict(categoryorder="total ascending"))
fig.update_yaxes(type="category")
fig.update_traces(
    hovertemplate="Quantity: %{x:,.2f} MT<br>Formula: %{y}<extra></extra>"
)

st.plotly_chart(fig, use_container_width=True)

#==========================
# Top Importers
#==========================
company_df = (
    filtered
    .groupby("Importer", as_index=False)["QUANTITY(MT)"]
    .sum()
    .sort_values("QUANTITY(MT)", ascending=False)
    .head(10)
)

fig = px.bar(
    company_df,
    x="QUANTITY(MT)",
    y="Importer",
    orientation="h",
    title="Top 10 Importers"
)

fig.update_layout(yaxis=dict(categoryorder="total ascending"))
fig.update_traces(
    hovertemplate="Quantity: %{x:,.2f} MT<br>Importer: %{y}<extra></extra>"
)

st.plotly_chart(fig, use_container_width=True)


#==========================
# Top Origins
#==========================

origin_df = (
    filtered
    .groupby("Origin", as_index=False)["QUANTITY(MT)"]
    .sum()
    .sort_values("QUANTITY(MT)", ascending=False)
    .head(10)
)

fig = px.bar(
    origin_df,
    x="QUANTITY(MT)",
    y="Origin",
    orientation="h",
    title="Top Origin Countries"
)

fig.update_layout(yaxis=dict(categoryorder="total ascending"))
fig.update_traces(
    hovertemplate="Quantity: %{x:,.2f} MT<br>Origin: %{y}<extra></extra>"
)

st.plotly_chart(fig, use_container_width=True)

#==========================
# Type of Distirbution
#==========================
type_df = (
    filtered["Type"]
    .value_counts()
    .reset_index()
)

type_df.columns = ["Type", "Count"]

fig = px.pie(
    type_df,
    names="Type",
    values="Count",
    hole=0.5,
    title="Fertilizer Type Distribution"
)

st.plotly_chart(fig, use_container_width=True)


#==========================
# Monthly trends
#==========================

filtered["Month_Name"] = filtered["Month"].apply(
    lambda x: calendar.month_abbr[int(x)]
)

month_order = [
    "Jan","Feb","Mar","Apr","May","Jun",
    "Jul","Aug","Sep","Oct","Nov","Dec"
]

filtered["Month_Name"] = pd.Categorical(
    filtered["Month_Name"],
    categories=month_order,
    ordered=True
)

monthly = (
    filtered
    .groupby("Month_Name", as_index=False)["QUANTITY(MT)"]
    .sum()
)

fig = px.line(
    monthly,
    x="Month_Name",
    y="QUANTITY(MT)",
    markers=True,
    title="Monthly Import Volume"
)

st.plotly_chart(fig, use_container_width=True)



st.write(df["Month"].unique())
