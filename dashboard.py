import streamlit as st
import plotly.express as px
import pandas as pd
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Configure Streamlit page
st.set_page_config(page_title="AVAA", page_icon=":bar_chart:", layout="wide")
st.title(" :bar_chart: Auto Visualizer And Analyzer")
st.markdown(
    """
    <style>
        h1 {
            font-size: 48px !important; /* Increase font size */
            color: white !important; /* Change font color to white */
            text-align: center; /* Center the text */
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7); /* Add shadow for better visibility */
        }
        div.block-container {
            padding-top: 5rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# File uploader
fl = st.file_uploader(":file_folder: Upload a file", type=["csv", "txt", "xlsx", "xls"])
if fl is not None:
    filename = fl.name
    st.write(f"Uploaded File: {filename}")
    try:
        if filename.endswith(".xls"):
            df = pd.read_excel(fl, engine="xlrd")
        else:
            df = pd.read_excel(fl, engine="openpyxl")
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()
else:
    # Use relative path to load the default file
    default_file = "/Superstore.xls"  # Ensure the file is in a 'data' folder in the repo
    try:
        if default_file.endswith(".xls"):
            df = pd.read_excel(default_file, engine="xlrd")
        else:
            df = pd.read_excel(default_file, engine="openpyxl")
    except Exception as e:
        st.error(f"Error loading default file: {e}")
        st.stop()

# Process dates
col1, col2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"])
startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))
with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

# Sidebar filters
st.sidebar.header("Choose your filter:")
region = st.sidebar.multiselect("Pick your Region", df["Region"].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]

state = st.sidebar.multiselect("Pick the State", df2["State"].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(state)]

city = st.sidebar.multiselect("Pick the City", df3["City"].unique())

if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif state and city:
    filtered_df = df3[df3["State"].isin(state) & df3["City"].isin(city)]
elif region and city:
    filtered_df = df3[df3["Region"].isin(region) & df3["City"].isin(city)]
elif region and state:
    filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state)]
elif city:
    filtered_df = df3[df3["City"].isin(city)]
else:
    filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3["City"].isin(city)]

# Category-wise sales
category_df = filtered_df.groupby(by=["Category"], as_index=False)["Sales"].sum()
with col1:
    st.subheader("Category wise Sales")
    fig = px.bar(category_df, x="Category", y="Sales", text=['₹{:,.2f}'.format(x) for x in category_df["Sales"]],
                 template="seaborn")
    st.plotly_chart(fig, use_container_width=True)

# Region-wise sales
with col2:
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.5)
    st.plotly_chart(fig, use_container_width=True)

# Data download
cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Category.csv", mime="text/csv")

with cl2:
    with st.expander("Region_ViewData"):
        region = filtered_df.groupby(by="Region", as_index=False)["Sales"].sum()
        st.write(region.style.background_gradient(cmap="Oranges"))
        csv = region.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Region.csv", mime="text/csv")

# Time series analysis
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader('Time Series Analysis')
linechart = filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum().reset_index()
fig2 = px.line(linechart, x="month_year", y="Sales", labels={"Sales": "Amount"}, height=500, template="gridon")
st.plotly_chart(fig2, use_container_width=True)

# Tree map
st.subheader("Hierarchical view of Sales using TreeMap")
fig3 = px.treemap(filtered_df, path=["Region", "Category", "Sub-Category"], values="Sales", hover_data=["Sales"],
                  color="Sub-Category")
st.plotly_chart(fig3, use_container_width=True)

# Pie charts
chart1, chart2 = st.columns((2))
with chart1:
    st.subheader('Segment wise Sales')
    fig = px.pie(filtered_df, values="Sales", names="Segment", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with chart2:
    st.subheader('Category wise Sales')
    fig = px.pie(filtered_df, values="Sales", names="Category", template="gridon")
    st.plotly_chart(fig, use_container_width=True)

# Scatter plot
st.subheader(":point_right: Relationship between Sales and Profits")
data1 = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity")
st.plotly_chart(data1, use_container_width=True)

# Download original dataset
csv = df.to_csv(index=False).encode('utf-8')
st.download_button('Download Data', data=csv, file_name="Data.csv", mime="text/csv")
