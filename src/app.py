import random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import duckdb

# PAGE SETUP
st.set_page_config(page_title="Sales Dashboard", page_icon=":bar_chart:", layout="wide")

st.title("Sales Dashboard")
# st.markdown("_Prototype v0.4.1_")
# Define the link
url = "data/sales_dataset_cleaned_100k.csv"
file_path = pd.read_csv(url).to_csv(index=False).encode('utf-8')

with st.sidebar:
    st.header("Configuration")
    uploaded_file = st.file_uploader("Choose a file")

# Ensure the file is uploaded before proceeding
if uploaded_file is None:
    st.info("Upload a file", icon="ℹ️")
    # Additional text with a message
    st.markdown("You can use this sample dataset provided for visualizing the project.")
    # Create a download button
    st.download_button(
        label="Download Sample Dataset",
        data=file_path,
        file_name='sales_dataset_cleaned_100k.csv',
        mime='text/csv'
    )
    st.stop()

# DATA LOADING
@st.cache_data
def load_data(file):
    # Load the data from the uploaded file
    df = pd.read_csv(file)  # Assuming CSV format, change to pd.read_excel if needed
    return df

df = load_data(uploaded_file)

# Allow product selection after data is loaded
product_name = st.sidebar.selectbox(
    'Select a product to analyze',
    df['Product Name'].unique()
)

with st.expander("Data Preview"):
    st.dataframe(df)

# New Graphs

# 1. Sales by Product Grade
def plot_sales_by_grade():
    grade_data = df.groupby('Grade')['Sales Amount'].sum().reset_index()
    fig = px.bar(grade_data, x='Grade', y='Sales Amount', title='Sales by Product Grade')
    st.plotly_chart(fig, use_container_width=True)

# 2. Sales Channel Performance
def plot_sales_by_channel():
    channel_data = df.groupby('Sales Channel')['Sales Amount'].sum().reset_index()
    fig = px.pie(channel_data, names='Sales Channel', values='Sales Amount', title='Sales Channel Performance')
    st.plotly_chart(fig, use_container_width=True)

# 3. Sales Trend by Product Size
def plot_sales_by_size():
    size_data = df.groupby(['Size', 'Date'])['Sales Amount'].sum().reset_index()
    fig = px.line(size_data, x='Date', y='Sales Amount', color='Size', title='Sales Trend by Product Size')
    st.plotly_chart(fig, use_container_width=True)

# 4. Order and Return Status Overview
def plot_order_return_status():
    status_data = df.groupby(['Order Status', 'Return Status'])['Quantity Sold'].sum().reset_index()
    fig = px.bar(status_data, x='Order Status', y='Quantity Sold', color='Return Status', barmode='stack',
                 title='Order and Return Status Overview')
    st.plotly_chart(fig, use_container_width=True)

# 5. Product Sales by Customer Segment (Grade)
def plot_sales_by_segment():
    segment_data = df.groupby('Grade')['Sales Amount'].sum().reset_index()
    fig = px.treemap(segment_data, path=['Grade'], values='Sales Amount', title='Product Sales by Customer Segment (Grade)')
    st.plotly_chart(fig, use_container_width=True)

# 6. Discounts Impact on Sales
def plot_discounts_impact():
    fig = px.scatter(df, x='Discounts Applied', y='Sales Amount', title='Discounts Impact on Sales')
    st.plotly_chart(fig, use_container_width=True)

# 7. Sales by Region and Sales Channel (Sunburst)
def plot_region_channel_sunburst():
    region_channel_data = df.groupby(['Region(Statewise)', 'Sales Channel'])['Sales Amount'].sum().reset_index()
    fig = px.sunburst(region_channel_data, path=['Region(Statewise)', 'Sales Channel'], values='Sales Amount',
                      title='Sales by Region and Channel')
    st.plotly_chart(fig, use_container_width=True)

# 8. Average Sales per Transaction (Histogram)
def plot_avg_sales_per_transaction():
    fig = px.histogram(df, x='Sales Amount', title='Average Sales per Transaction')
    st.plotly_chart(fig, use_container_width=True)

# 9. Sales Growth Over Time (Area Chart)
def plot_sales_growth():
    sales_growth = df.groupby('Date')['Sales Amount'].sum().reset_index()
    fig = px.area(sales_growth, x='Date', y='Sales Amount', title='Sales Growth Over Time')
    st.plotly_chart(fig, use_container_width=True)

# 10. Top 5 Selling Products (Horizontal Bar)
def plot_top_selling_products():
    top_products = df.groupby('Product Name')['Sales Amount'].sum().nlargest(5).reset_index()
    fig = px.bar(top_products, x='Sales Amount', y='Product Name', orientation='h', title='Top 5 Selling Products')
    st.plotly_chart(fig, use_container_width=True)


# EXISTING VISUALIZATION METHODS AND LAYOUTS
def plot_metric(label, value, prefix="", suffix="", show_graph=False, color_graph=""):
    fig = go.Figure()
    fig.add_trace(
        go.Indicator(
            value=value,
            gauge={"axis": {"visible": False}},
            number={
                "prefix": prefix,
                "suffix": suffix,
                "font.size": 12,
            },
            title={
                "text": label,
                "font": {"size": 16},
            },
        )
    )

    if show_graph:
        fig.add_trace(
            go.Scatter(
                y=random.sample(range(0, 101), 30),
                hoverinfo="skip",
                fill="tozeroy",
                fillcolor=color_graph,
                line={
                    "color": color_graph,
                },
            )
        )

    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(visible=False, fixedrange=True)
    fig.update_layout(
        margin=dict(t=30, b=0),
        showlegend=False,
        plot_bgcolor="white",
        height=100,
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_gauge(indicator_number, indicator_color, indicator_suffix, indicator_title, max_bound):
    fig = go.Figure(
        go.Indicator(
            value=indicator_number,
            mode="gauge+number",
            domain={"x": [0, 1], "y": [0, 1]},
            number={
                "suffix": indicator_suffix,
                "font.size": 12,
            },
            gauge={
                "axis": {"range": [0, max_bound], "tickwidth": 1},
                "bar": {"color": indicator_color},
            },
            title={
                "text": indicator_title,
                "font": {"size": 14},
            },
        )
    )
    fig.update_layout(
        height=200,
        margin=dict(l=10, r=10, t=50, b=10, pad=8),
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_top_right():
    con = duckdb.connect()
    sales_data = con.execute(
        """
        WITH sales_data AS (
            SELECT 
                "Region(Statewise)" AS region,
                SUM("Sales Amount") AS sales
            FROM df
            WHERE "Date" BETWEEN '2023-01-01' AND '2023-12-31'
            GROUP BY "Region(Statewise)"
        )
        SELECT * FROM sales_data
        """
    ).df()
    con.close()

    fig = px.bar(
        sales_data,
        x="region",
        y="sales",
        title="Sales by Region for Year 2023",
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_bottom_left():
    # Connect to DuckDB and fetch data for the selected product
    con = duckdb.connect()

    sales_data = con.execute(
        f"""
        WITH sales_data AS (
            SELECT
                "Date",
                "Sales Amount"
            FROM df
            WHERE "Product Name" = '{product_name}' 
            AND "Date" BETWEEN '2023-01-01' AND '2023-12-31'
        )
        SELECT * FROM sales_data
        """
    ).df()
    con.close()

    # Check if the data is available
    if sales_data.empty:
        st.error(f"No data available for '{product_name}' in 2023.")
        return

    # Data Processing
    sales_data['Date'] = pd.to_datetime(sales_data['Date'])
    sales_data.set_index('Date', inplace=True)
    sales_data = sales_data.resample('M').sum().reset_index()

    # Check the processed data
    if sales_data.empty:
        st.error("No sales data available after resampling.")
        return

    # Plotting the data
    fig = px.line(
        sales_data,
        x="Date",
        y="Sales Amount",
        title=f"Monthly Sales for {product_name} in 2023",
        markers=True,
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_bottom_right():
    con = duckdb.connect()
    sales_data = con.execute(
        """
        WITH sales_data AS (
            SELECT 
                "Product Name",
                SUM("Sales Amount") AS sales
            FROM df
            WHERE "Date" BETWEEN '2023-01-01' AND '2023-12-31'
            GROUP BY "Product Name"
        )
        SELECT * FROM sales_data
        """
    ).df()
    con.close()

    fig = px.bar(
        sales_data,
        x="Product Name",
        y="sales",
        title="Total Sales by Product for Year 2023",
    )
    st.plotly_chart(fig, use_container_width=True)

# STREAMLIT LAYOUT
top_left_column, top_right_column = st.columns((2, 1))
bottom_left_column, bottom_right_column = st.columns(2)

with top_left_column:
    column_1, column_2, column_3, column_4 = st.columns(4)

    with column_1:
        plot_metric(
            "Total Sales Amount",
            df["Sales Amount"].sum(),
            prefix="$",
            show_graph=True,
            color_graph="rgba(0, 104, 201, 0.2)",
        )
        plot_gauge(df["Sales Amount"].sum() / df["Quantity Sold"].sum(), "#0068C9", "", "Average Sales per Unit", 1000)

    with column_2:
        plot_metric(
            "Total Quantity Sold",
            df["Quantity Sold"].sum(),
            prefix="",
            show_graph=True,
            color_graph="rgba(255, 43, 43, 0.2)",
        )
        plot_gauge(df["Quantity Sold"].mean(), "#FF8700", " units", "Average Quantity per Sale", 1000)

    with column_3:
        plot_metric("Total Cost", df["Cost"].sum(), prefix="$", suffix="")
        plot_gauge(df["Cost"].mean(), "#FF2B2B", "$", "Average Cost per Sale", 10000)

    with column_4:
        plot_metric("Total Discounts", df["Discounts Applied"].sum(), prefix="$", suffix="")
        plot_gauge(df["Discounts Applied"].mean(), "#29B09D", "$", "Average Discount per Sale", 1000)

with top_right_column:
    plot_top_right()

with bottom_left_column:
    plot_bottom_left()

with bottom_right_column:
    plot_bottom_right()


# Add new graphs below the existing layout
st.header("Additional Analysis")

additional_col1, additional_col2 = st.columns((2,4))

with additional_col1:
    plot_sales_by_grade() #1


with additional_col2:
    sub_col1, sub_col2 = st.columns(2)

    with sub_col1:
        plot_order_return_status() #1
    with sub_col2:
        plot_sales_by_segment()

additional_row2_col1, additional_row2_col2 = st.columns((4,2))

with additional_row2_col1:
    plot_sales_by_size()

with additional_row2_col2:
    plot_sales_by_channel()

plot_discounts_impact()

# Additional full-width visualizations

st.header("Other Key Insights")

key_insights_col1, key_insights_col2 = st.columns((1,3))


with key_insights_col1:
    plot_region_channel_sunburst()

with key_insights_col2:
    plot_avg_sales_per_transaction()

key_insights_row2_col1, key_insights_row2_col2 = st.columns(2)

with key_insights_row2_col1:
    plot_sales_growth()

with key_insights_row2_col2:
    plot_top_selling_products()
