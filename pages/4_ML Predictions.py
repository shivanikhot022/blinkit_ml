import streamlit as st

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login first")
    st.switch_page("Login.py")
    st.stop()

    
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.switch_page("Login.py")


# IMPORTS PACKAGES
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import joblib
import pickle
import os
from datetime import date
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Dashboard", layout="wide")
# =========================================

st.markdown("""
<style>
/* MAIN BACKGROUND */
.main {
    background-color:#FFFDE7 !important;
}
.block-container {
    background-color:#FFFDE7 !important;
    padding-top:1rem;
}
/* KPI CARD */
[data-testid="metric-container"]{
    background-color:#F5EE9E !important;
    border:2px solid green !important;
    border-radius:12px !important;
    padding:12px !important;
}

/* KPI LABEL */
[data-testid="stMetricLabel"] {
    color:green !important;
    font-weight:bold !important;
    font-size:22px !important;
}

/* KPI VALUE */
[data-testid="stMetricValue"] {
    color:green !important;
    font-weight:bold !important;
    font-size:38px !important;
}

/* DELTA VALUE */
[data-testid="stMetricDelta"] {
    color:green !important;
    font-weight:bold !important;
}
/* HEADINGS */
h1,h2,h3,h4{
    color:green !important;
    font-weight:bold !important;
}
/* CHART BACKGROUND */
.stPyplot{
    background-color:#F5EE9E !important;
    border-radius:12px;
}
/* SIDEBAR */
section[data-testid="stSidebar"]{
    background-color:#F5EE9E;
}
section[data-testid="stSidebar"] *{
    color:green !important;
    font-weight:bold !important;
}
/* FILTER BOX */
div[data-baseweb="select"] > div {
    background-color:#F5EE9E !important;
    border:2px solid green !important;
    border-radius:10px !important;
}
/* BUTTON */
.stButton > button {
    background-color:#F5EE9E !important;
    color:green !important;
    border:2px solid green !important;
    font-weight:bold !important;
    border-radius:10px !important;
}
table {
    color: black !important;
    background-color:white !important;
}
th {
    color: black !important;
    font-weight: bold !important;
}
td {
    color: black !important;
}
</style>
""", unsafe_allow_html=True)
st.markdown("""<style>
 /* Tab container */button[data-baseweb="tab"] { padding: 10px 24px !important;}

/* Tab text */
button[data-baseweb="tab"] > div > p {font-size: 20px !important;color:green !important;font-weight: 500 !important;}

/* Active tab */
button[data-baseweb="tab"][aria-selected="true"] > div > p {color:#AA336A  !important;}
</style>""", unsafe_allow_html=True)

st.title("🤖 Machine Learning Analytics Dashboard")
#---------------------------------------------------------------------------------------------------------------------
# Load segmented customer data
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
rfm= pd.read_csv("customer_segments.csv")
path="D:/datascience/Analytix_Internship_data_analyst/blinkit/streamlit/"
customers = pd.read_csv(os.path.join(BASE_DIR, "unclean_data", "blinkit_customers.csv"))
customer_info = customers[["customer_id","customer_name","area"]]
df = rfm.merge(customer_info,on="customer_id",how="left")
df = df[["customer_id","customer_name","area","Recency","Frequency","Monetary","Cluster","Segment"]]
df.to_csv("df.csv",index=False)
#---------------------------------------------------------------------------------------------------------------------
tab1, tab2 = st.tabs(["📚 About Customer Segmentation","📊 Customer Segmentation Dashboard"])

with tab1:
    st.header("What is Machine Learning?")
    st.write("""
        Machine Learning (ML) is a branch of Artificial Intelligence (AI)
        that enables computers to learn patterns from data and make
        decisions without being explicitly programmed.
    """)
     
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    st.header("What is Customer Segmentation?")
    st.write("""
        Customer Segmentation is the process of dividing customers into
        groups based on their purchasing behaviour.
    """)
    st.write("""It helps businesses to :""")
    st.write("""
        - Identify high value customers
        - Retain customers at risk of leaving
        - Create targeted marketing campaigns
        - Improve customer satisfaction
    """)
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    st.header("Why K-Means Clustering?")
    st.write("""
        K-Means is an Unsupervised Machine Learning algorithm.
    """)
    st.write("""We selected K-Means because:""")
    st.write("""
        - Easy to understand
        - Suitable for customer segmentation
        - Groups similar customers together
        - Works well with RFM features
    """)
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    st.header("What is RFM Analysis?")
    st.subheader("1. Recency (R)")
    st.write("""
        Recency measures how recently a customer placed an order.
        Lower Recency = Better Customer
        Example:
        - 10 days ago → Active Customer
        - 400 days ago → Inactive Customer
    """)
    st.subheader("2. Frequency (F)")
    st.write("""
        Frequency measures how many orders a customer has placed.
        Higher Frequency = Better Customer
        Example:
        - 8 Orders → Loyal Customer
        - 1 Order → Occasional Customer
    """)
    st.subheader("3. Monetary (M)")
    st.write("""
        Monetary measures the total amount spent by a customer.
        Higher Monetary = More Valuable Customer
        Example:
        - ₹10,000 → Premium Customer
        - ₹500 → Low Value Customer
    """)
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    st.header("How Were Customer Groups Created?")
    st.write("""
        We first calculated:
        - Recency
        - Frequency
        - Monetary

        Then StandardScaler was applied to normalize the data.
        Finally K-Means clustering was used with K = 4 clusters
        (selected using the Elbow Method).
    """)
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True)  
    st.header("Customer Segments Created")
    st.markdown("""
        **Premium Customers**
        - High Frequency
        - High Monetary
        - Active Customers

        **Loyal Customers**
        - Good Frequency
        - Good Spending Pattern

        **Regular Customers**
        - Average Buying Behaviour

        **At Risk Customers**
        - Long Time Since Last Order
        - Low Frequency
        - Low Spending
    """)
      
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    st.header("Business Benefits")
    st.markdown("""
    - Reward Premium Customers
    - Increase loyalty of Regular Customers
    - Retain At Risk Customers using offers
    - Improve marketing effectiveness
    """)

with tab2:
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    col1, col2, col3, col4,col5 = st.columns(5)

    col1.metric("Total Customers", len(df))
    col2.metric("Loyal Customers",(df["Segment"] == "Loyal Customers").sum())
    col3.metric("Premium Customers",(df["Segment"] == "Premium Customers").sum())
    col4.metric("At Risk Customers",(df["Segment"] == "At Risk Customers").sum())
    col5.metric("Regular Customers",(df["Segment"] == "Regular Customers").sum())

    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    #---------------------------------------------------------------------------------------------------------------------
    # Segment Distribution

    st.subheader("Customer Segment Distribution")
    segment_counts = df["Segment"].value_counts()
    fig = px.bar(x=segment_counts.index,y=segment_counts.values,labels={"x": "Customer Segment","y": "Number of Customers"},
        title="Customer Segment Distribution"
    )
    fig.update_traces(
    marker_color="green"
    )
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(showline=True, linewidth=2, linecolor="black"),
        yaxis=dict(showline=True, linewidth=2, linecolor="black")
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    #---------------------------------------------------------------------------------------------------------------------
    # Segment Summary

    st.subheader("Segment Wise RFM Summary")
    summary = df.groupby("Segment")[["Recency","Frequency","Monetary"]].mean().round(2)
    st.table(summary)
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    #---------------------------------------------------------------------------------------------------------------------
    st.subheader("Customer Details By Segment")
    selected_segment = st.selectbox("Select Segment",df["Segment"].unique())

    segment_customers = df[df["Segment"] == selected_segment]
    display_df = segment_customers[["customer_id","customer_name","area","Recency","Frequency","Monetary"]]
    col1, col2, col3, col4 = st.columns(4)

    with col1:st.metric("Total Customers",len(display_df))
    with col2:st.metric("Avg Recency",round(display_df["Recency"].mean(), 0))
    with col3:st.metric("Avg Frequency",round(display_df["Frequency"].mean(), 2))
    with col4:st.metric("Avg Monetary",f"₹{display_df['Monetary'].mean():,.0f}")
    st.write(display_df)

    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    
    #----------------------------------------------------------------------------------------------------------------
    st.subheader("Try Customer Segmentation")
    st.write("Enter customer RFM values and predict the customer segment.")
    recency = st.number_input("Recency (Days Since Last Order)", key="recency")
    frequency = st.number_input("Frequency (Number of Orders)", key="frequency")
    monetary = st.number_input("Monetary (Total Spend ₹)", key="monetary")
    if st.button("Predict Segment"):
        try:
            recency = float(recency)
            frequency = float(frequency)
            monetary = float(monetary)
            BASE_DIR = os.path.dirname(os.path.dirname(__file__))
            scaler = joblib.load(os.path.join(BASE_DIR, "rfm_scaler.pkl"))
            model = joblib.load(os.path.join(BASE_DIR, "customer_segmentation_model.pkl"))
            input_data = pd.DataFrame({
                "Recency":[recency],
                "Frequency":[frequency],
                "Monetary":[monetary]})
            input_scaled = scaler.transform(input_data)
            cluster = model.predict(input_scaled)[0]
            segment_map = {
                0: "Premium Customers",
                1: "At Risk Customers",
                2: "Regular Customers",
                3: "Loyal Customers"}
            segment = segment_map[cluster]
            st.success(f"Predicted Segment: {segment}")

            if segment == "Premium Customers":
                st.markdown("""
                ⭐ Premium Customers

                - Highest spending customers
                - Purchase frequently
                - Generate maximum revenue
                - Priority customers for loyalty programs
                """)

            elif segment == "Loyal Customers":
                st.markdown("""
                💚 Loyal Customers

                - Regular and consistent buyers
                - Good purchase frequency
                - Important repeat customers
                - Suitable for upselling and rewards
                """)

            elif segment == "Regular Customers":
                st.markdown("""
                📦 Regular Customers

                - Average purchase behaviour
                - Moderate spending
                - Opportunity for targeted marketing campaigns
                - Can be converted into loyal customers
                """)

            elif segment == "At Risk Customers":
                st.markdown("""
                ⚠️ At Risk Customers

                - Have not purchased recently
                - Low engagement
                - May stop purchasing completely
                - Need re-engagement offers and discounts
                """)
        except ValueError: 
            st.error("Please enter numeric values only.")
        except Exception as e: 
            st.error(f"Error: {e}")