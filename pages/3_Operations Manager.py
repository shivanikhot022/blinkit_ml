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
</style>
""", unsafe_allow_html=True)
st.markdown("""<style>
 /* Tab container */button[data-baseweb="tab"] { padding: 10px 24px !important;}

/* Tab text */
button[data-baseweb="tab"] > div > p {font-size: 20px !important;color:green !important;font-weight: 500 !important;}

/* Active tab */
button[data-baseweb="tab"][aria-selected="true"] > div > p {color:#AA336A  !important;}
</style>""", unsafe_allow_html=True)

# LOAD DATA
base_dir = os.path.dirname(os.path.dirname(__file__))  # goes one folder up from 'pages'
data_path = os.path.join(base_dir, "data")

orders=pd.read_csv(os.path.join(data_path,"blinkit_orders.csv"))
order_items=pd.read_csv(os.path.join(data_path,"blinkit_order_items.csv"))
customers=pd.read_csv(os.path.join(data_path,"blinkit_customers.csv"))
products=pd.read_csv(os.path.join(data_path,"blinkit_products.csv"))
delivery_performance=pd.read_csv(os.path.join(data_path,"blinkit_delivery_performance.csv"))
customer_feedback=pd.read_csv(os.path.join(data_path,"blinkit_customer_feedback.csv"))
marketing_performance=pd.read_csv(os.path.join(data_path,"blinkit_marketing_performance.csv"))
inventory=pd.read_csv(os.path.join(data_path,"blinkit_inventory.csv"))
inventory_new=pd.read_csv(os.path.join(data_path,"blinkit_inventoryNew.csv"))

inventory['date'] = pd.to_datetime(inventory['date'],errors='coerce').dt.strftime('%b-%y')

# combine both inventory tables first
all_inventory = pd.concat([inventory, inventory_new])
all_inventory[['stock_received', 'damaged_stock']] = \
all_inventory[['stock_received', 'damaged_stock']].fillna(0)
inventory_merged = all_inventory.groupby(['product_id','date'],as_index=False).agg({'stock_received': 'sum','damaged_stock': 'sum'})
all_inv = inventory_merged.merge(products,on='product_id',how='left')
    
customers['customer_type']=np.where(customers['total_orders']>1,'repeat_customers',np.where(customers['total_orders']==1,'one_time_customers','no_order_customers'))

# #only one table for analysis
ord_items_prod_cust=orders.merge(order_items,on='order_id',how='left',suffixes=("","_item"))\
    .merge(products,left_on='product_id',right_on='product_id',how='left',suffixes=("","_prod"))\
        .merge(delivery_performance,on='order_id',how='left',suffixes=("","_dp"))
        
ord_items_prod_cust['order_date']=pd.to_datetime(ord_items_prod_cust['order_date'])
ord_items_prod_cust['month_number']=ord_items_prod_cust['order_date'].dt.month
ord_items_prod_cust['year']=ord_items_prod_cust['order_date'].dt.year
ord_items_prod_cust['year'] = (ord_items_prod_cust['year'].fillna(0).astype(int))
ord_items_prod_cust['year'] = (ord_items_prod_cust['year'].astype(int))
ord_items_prod_cust['month_name']=ord_items_prod_cust['order_date'].dt.month_name()
ord_items_prod_cust['day_name']=ord_items_prod_cust['order_date'].dt.day_name()
ord_items_prod_cust['quarters']='Q'+ord_items_prod_cust['order_date'].dt.quarter.astype(str)
ord_items_prod_cust['day_type']=ord_items_prod_cust['day_name'].apply(lambda x: 'Weekend' if x in ['Saturday', 'Sunday'] else 'Weekday')
ord_items_prod_cust["month"] = ord_items_prod_cust["order_date"].dt.strftime("%b")

all_inv['date']=pd.to_datetime(all_inv['date'],format='%b-%y')
all_inv['month_number']=all_inv['date'].dt.month
all_inv['year']=all_inv['date'].dt.year
all_inv['year'] = (all_inv['year'].fillna(0).astype(int))
all_inv['year'] = (all_inv['year'].astype(int))
all_inv['month_name']=all_inv['date'].dt.month_name()
all_inv['quarters']='Q'+all_inv['date'].dt.quarter.astype(str)
all_inv["month"] = all_inv["date"].dt.strftime("%b")

#st.write(ord_items_prod_cust.head())

# TITLE
st.markdown('<style>.block-container{padding-top:0.0rem;padding-bottom:0.0rem}</style>', unsafe_allow_html=True)
st.title("Dashboard For Operations Manager :bar_chart:")
st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True)

# SIDEBAR FILTERS

st.sidebar.header("Choose Filters")
dp = ord_items_prod_cust.copy()

# FORMAT FUNCTION
def format_number(num):

    if num >= 1000000:
        return f"{num/1000000:.2f}M"

    elif num >= 1000:
        return f"{num/1000:.0f}K"  

    else:
        return f"{num:.0f}"


year=st.sidebar.multiselect("Year",sorted(dp["year"].dropna().unique()))
dp=dp[dp["year"].isin(year)] if year else dp

month_order=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
months=sorted(dp["month"].dropna().unique(),key=lambda x:month_order.index(x))
month=st.sidebar.multiselect("Month Name",months)
dp=dp[dp["month"].isin(month)] if month else dp

day_type=st.sidebar.multiselect("Day Type",sorted(dp["day_type"].dropna().unique()))
dp=dp[dp["day_type"].isin(day_type)] if day_type else dp

delay_reason=st.sidebar.multiselect("Delay Reason",sorted(dp["reasons_if_delayed"].dropna().unique()))
dp=dp[dp["reasons_if_delayed"].isin(delay_reason)] if delay_reason else dp


category=st.sidebar.multiselect("Category",sorted(dp["category"].dropna().unique()))
dp=dp[dp["category"].isin(category)] if category else dp


delivery_status=st.sidebar.multiselect("Delivery Status",sorted(dp["delivery_status_dp"].dropna().unique()))
dp=dp[dp["delivery_status_dp"].isin(delivery_status)] if delivery_status else dp

    
#----------------------------------------------------------------------------------------------------------------#
# TABS
tab1, tab2 = st.tabs([  "🚚 Delivery & Operations Efficiency 📍","📖 Glossary"])

with tab1:
 
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True)
    
    total_delivery=dp['order_id'].nunique()
    total_delivery_partners=dp['delivery_partner_id'].nunique()
    avg_delivery_time=dp['delivery_time_minutes'].mean()
    damaged_stocks=all_inv['damaged_stock'].sum()
    stocks_received=all_inv['stock_received'].sum()
    available_stocks=stocks_received-damaged_stocks
    damage_perc=(damaged_stocks/stocks_received)*100
    available_stocks_perc=available_stocks/stocks_received
    on_time_orders=dp[dp['delivery_status']=='On Time']['order_id'].count()
    delayed_orders=dp[dp['delivery_status']=='Significantly Delayed']['order_id'].count()
    on_time_orders_perc=(on_time_orders*100)/total_delivery
    delayed_orders_perc=(delayed_orders*100)/total_delivery
    inventory_health_score =(available_stocks/stocks_received)*100
    
    
    k1,k2,k3,k4,k5=st.columns(5)

    k1.metric("Total Deliveries",format_number(total_delivery))
    k2.metric("Delivery Partners",format_number(total_delivery_partners))
    k3.metric("Avg Delivery Time",f"{avg_delivery_time:.2f} Min")
    k4.metric("Damage %",f"{damage_perc:.2f}%")
    k6,k7,k8,k9,k10=st.columns(5)
    k5.metric("Inventory Health %",f"{inventory_health_score:.2f}%")
    k6.metric("Available Stock",f"{available_stocks/1000:.1f}K")
    k7.metric("Delay %",f"{delayed_orders_perc:.2f}%")
    k8.metric("On-Time Delivery %",f"{on_time_orders_perc:.2f}%")
    k9.metric(" Stock received",format_number(stocks_received))
    k10.metric(" Stock damaged",f"{damaged_stocks/1000:.1f}K")
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True)
    
    st.subheader("Deliveries By Delivery Status Over Month")
    trend=dp.groupby(["month","delivery_status"])["order_id"].nunique().reset_index(name="deliveries")
    trend["month"]=pd.Categorical(trend["month"],categories=month_order,ordered=True)
    trend=trend.sort_values("month");fig,ax=plt.subplots(figsize=(8,4))
    sns.lineplot(data=trend,x="month",y="deliveries",hue="delivery_status",marker="o",ax=ax)
    plt.xticks(rotation=45)
    st.pyplot(fig)
    with st.expander("1️⃣ Deliveries by Status Over Month - Insights & Recommendations"):
        st.markdown("""
        • On-time deliveries are highest across all months.  
        • Highest on-time deliveries were recorded during April to October (~340–375 deliveries).  
        • Significantly delayed deliveries remained below 60 deliveries in most months.  
        • Delivery performance dropped during November and December.  
        • Slightly delayed deliveries increased during July and August.  

        Recommendations:
        1. Improve delivery planning during peak months.  
        2. Reduce delayed deliveries through route optimization.  
        3. Increase delivery staff during high-demand periods.  
        """)
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True)
    
    st.subheader("Stocks Received and Damaged Stock By Month")
    stock=all_inv.groupby("month")[["stock_received","damaged_stock"]].sum().reset_index()
    stock["month"]=pd.Categorical(stock["month"],categories=month_order,ordered=True)
    stock=stock.sort_values("month")
    fig,ax=plt.subplots(figsize=(8,4))
    sns.lineplot(data=stock,x="month",y="stock_received",marker="o",label="Stock Received",ax=ax)
    sns.lineplot(data=stock,x="month",y="damaged_stock",marker="o",label="Damaged Stock",ax=ax)
    plt.xticks(rotation=45)
    st.pyplot(fig)
    with st.expander("2️⃣ Total Stock Received and Total Damaged Stock by Month - Insights & Recommendations"):
        st.markdown("""
        • Stock received increased from around 9.8K in January to 18K in October.  
        • Damaged stock remained between 4K and 8K across most months.  
        • Highest stock received was recorded during October (~18.3K).  
        • Damaged stock percentage remained relatively high throughout the year.  
        • Stock levels dropped significantly during November and December.  

        Recommendations:
        1. Improve inventory handling to reduce damaged stock.  
        2. Monitor warehouse operations during peak inventory months.  
        3. Focus on stock quality checks and packaging improvements.  
        """)
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True)

    col1,col2=st.columns(2)
    with col1:
        st.subheader("Total Orders by Delivery Status")
        status=dp["delivery_status"].value_counts().reset_index()
        fig,ax=plt.subplots(figsize=(5,4))
        ax.pie(status["count"],labels=status["delivery_status"],autopct="%1.1f%%")
        st.pyplot(fig)
        with st.expander("3️⃣ Total Orders by Delivery Status - Insights & Recommendations"):
            st.markdown("""
            • On-time deliveries contribute around 69.4% of total orders (~3.47K orders).  
            • Slightly delayed deliveries contribute around 20.7% of orders.  
            • Significantly delayed deliveries contribute around 9.8% of orders.  
            • Majority of deliveries are completed successfully on time.  

            Recommendations:
            1. Reduce significantly delayed deliveries further.  
            2. Improve delivery tracking and monitoring systems.  
            3. Focus on improving delivery speed during busy periods.  
            """)
    with col2:
        st.subheader("TOP 10 Products By Damaged stock")
        damage=all_inv.groupby("product_name")["damaged_stock"].sum().reset_index().sort_values(by="damaged_stock",ascending=False).head(10)
        fig,ax=plt.subplots(figsize=(6,5.2))
        sns.barplot(data=damage,y="product_name",x="damaged_stock",ax=ax,color="green")
        st.pyplot(fig)
        with st.expander("4️⃣ Top 10 Products by Damaged Stock - Insights & Recommendations"):
            st.markdown("""
            • Dish Soap recorded the highest damaged stock (~3.1K units).  
            • Detergent and Bread also showed high damaged stock levels (~2.2K units).  
            • Some products experience consistently high inventory damage.  
            • High damaged stock increases operational losses.  

            Recommendations:
            1. Improve packaging and storage conditions.  
            2. Monitor frequently damaged products carefully.  
            3. Reduce overstocking of sensitive products.  
            """)

    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True)
    col1,col2=st.columns(2)
    with col1:
        st.subheader("TOP 10 Products by stock")
        stocks=all_inv.groupby("product_name")["stock_received"].sum().reset_index().sort_values(by="stock_received",ascending=False).head(10)
        fig,ax=plt.subplots(figsize=(6,7))
        sns.barplot(data=stocks,y="product_name",x="stock_received",ax=ax,color="green")
        st.pyplot(fig)
        with st.expander("5️⃣ Top 10 Products by Stock Received - Insights & Recommendations"):
            st.markdown("""
            • Pet Treats received the highest stock quantity (~9.8K units).  
            • Vitamins and Cough Syrup also received high stock volumes.  
            • Healthcare and pet products have strong inventory demand.  
            • High stock levels indicate strong customer demand for these products.  

            Recommendations:
            1. Maintain sufficient stock for high-demand products.  
            2. Monitor fast-moving inventory regularly.  
            3. Improve inventory forecasting for top-selling products.  
            """)
    with col2:
        st.subheader("Orders By Delay Reason")
        delay=dp["reasons_if_delayed"].value_counts().reset_index()
        fig,ax=plt.subplots(figsize=(5,3))
        ax.pie(delay["count"],labels=delay["reasons_if_delayed"],autopct="%1.1f%%")
        st.pyplot(fig)
        with st.expander("6️⃣ Orders by Reasons Delayed - Insights & Recommendations"):
            st.markdown("""
            • Traffic is the main reason for delayed deliveries (~61.9%).  
            • Unknown reasons contribute around 38% of delayed orders.  
            • Traffic conditions heavily affect delivery performance.  
            • Some delays are not properly categorized.  

            Recommendations:
            1. Optimize delivery routes to avoid traffic congestion.  
            2. Improve delay tracking systems for better analysis.  
            4. Reduce uncategorized delays through better reporting.  
            """)
    
with tab2:
    st.subheader("📖 KPI Glossary")

    col1 , col2 = st.columns(2)
    with col1:
        with st.expander("🚚 Total Deliveries"):
            st.write("**Meaning:** Total number of unique deliveries completed.")
            st.write("**Formula:** COUNT(DISTINCT order_id)")
    with col2:
        with st.expander("👨‍💼 Delivery Partners"):
            st.write("**Meaning:** Total unique delivery partners handling deliveries.")
            st.write("**Formula:** COUNT(DISTINCT delivery_partner_id)")

    col1 , col2 = st.columns(2)
    with col1:
        with st.expander("⏱️ Avg Delivery Time"):
            st.write("**Meaning:** Average time taken to deliver orders.")
            st.write("**Formula:** AVG(delivery_time_minutes)")
    with col2:
        with st.expander("📦 Stock Received"):
            st.write("**Meaning:** Total stock received into inventory.")
            st.write("**Formula:** SUM(stock_received)")

    col1 , col2 = st.columns(2)
    with col1:
        with st.expander("📉 Stock Damaged"):
            st.write("**Meaning:** Total damaged stock in inventory.")
            st.write("**Formula:** SUM(damaged_stock)")
    with col2:
        with st.expander("🏬 Available Stock"):
            st.write("**Meaning:** Remaining usable inventory stock.")
            st.write("**Formula:** Stock Received - Damaged Stock")

    col1 , col2 = st.columns(2)
    with col1:
        with st.expander("⚠️ Damage %"):
            st.write("**Meaning:** Percentage of stock damaged from total stock received.")
            st.write("**Formula:** (Damaged Stock / Stock Received) × 100")
    with col2:
        with st.expander("💚 Inventory Health %"):
            st.write("**Meaning:** Percentage of healthy usable inventory stock.")
            st.write("**Formula:** ((Stock Received - Damaged Stock) / Stock Received) × 100")

    col1 , col2 = st.columns(2)
    with col1:
        with st.expander("⏳ Delay %"):
            st.write("**Meaning:** Percentage of significantly delayed deliveries.")
            st.write("**Formula:** (Delayed Orders / Total Deliveries) × 100")
    with col2:
        with st.expander("✅ On-Time Delivery %"):
            st.write("**Meaning:** Percentage of orders delivered on time.")
            st.write("**Formula:** (On-Time Orders / Total Deliveries) × 100")


    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True)
    st.subheader("🎛️ Filters Used In Dashboard")
    st.markdown("""
    ✅ **Year Filter**  
    - Filters dashboard data based on selected year  
    - Helps compare yearly operational performance trends  

    ✅ **Month Name Filter**  
    - Filters dashboard data based on selected month  
    - Helps analyze monthly delivery and stock trends  

    ✅ **Day Type Filter**  
    - Filters data into weekday and weekend categories  
    - Helps analyze delivery performance by day type  

    ✅ **Delay Reason Filter**  
    - Filters orders based on reasons for delayed deliveries  
    - Helps identify operational bottlenecks  

    ✅ **Category Filter**  
    - Filters inventory and deliveries by product category  
    - Helps analyze category-wise operational efficiency  

    ✅ **Delivery Status Filter**  
    - Filters data by delivery status  
    - Helps analyze on-time and delayed deliveries  
    """)


    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True)

    st.subheader("📊 Analysis Performed In Dashboard")

    st.markdown("""
    🚚 **Delivery Status Trend Analysis**  
    - Tracks monthly deliveries by delivery status  
    - Helps monitor operational delivery performance trends  

    📦 **Stock Received vs Damaged Stock Analysis**  
    - Compares stock inflow and damaged inventory over months  
    - Helps monitor inventory quality and losses  

    📊 **Delivery Status Distribution Analysis**  
    - Shows percentage distribution of delivery statuses  
    - Helps evaluate delivery efficiency  

    🏆 **Top 10 Products by Damaged Stock Analysis**  
    - Identifies products with highest damaged stock  
    - Helps identify inventory handling issues  

    📈 **Top 10 Products by Stock Received Analysis**  
    - Tracks products receiving highest stock quantities  
    - Helps monitor inventory demand and supply trends  

    ⏳ **Delay Reason Analysis**  
    - Analyzes major causes of delayed deliveries  
    - Helps improve operational planning and logistics  

    📅 **Monthly Operational Trend Analysis**  
    - Evaluates operational KPIs across months  
    - Helps identify seasonal operational patterns  

    🏬 **Inventory Health Analysis**  
    - Measures healthy inventory percentage after damages  
    - Helps evaluate warehouse and stock management efficiency  

    🚛 **Delivery Performance Analysis**  
    - Tracks on-time deliveries, delayed deliveries, and delivery speed  
    - Helps improve customer delivery experience  
    """)
