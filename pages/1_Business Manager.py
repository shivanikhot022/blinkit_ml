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


actual_orders = (orders.groupby("customer_id")["order_id"].nunique().reset_index(name="actual_total_orders"))
customers = customers.merge(actual_orders,on="customer_id",how="left")
customers["actual_total_orders"] = (customers["actual_total_orders"].fillna(0).astype(int))
customers["total_orders"] = (customers["actual_total_orders"])
customers.drop(columns="actual_total_orders",inplace=True)
customers['customer_type']=np.where(customers['total_orders']>1,'repeat_customers',np.where(customers['total_orders']==1,'one_time_customers','no_order_customers'))

#only one table for analysis
ord_items_prod_cust=orders.merge(order_items,on='order_id',how='left',suffixes=("","_item"))\
    .merge(products,left_on='product_id',right_on='product_id',how='left',suffixes=("","_prod"))\
        .merge(customers,on='customer_id',how='right',suffixes=("","_cust"))
        
ord_items_prod_cust['revenue'] = (ord_items_prod_cust['quantity'] *ord_items_prod_cust['unit_price'])
ord_items_prod_cust['profit_amount'] = (ord_items_prod_cust['revenue'] *ord_items_prod_cust['margin_percentage'] / 100)
ord_items_prod_cust['cost'] = (ord_items_prod_cust['revenue'] -ord_items_prod_cust['profit_amount'])
ord_items_prod_cust['order_date']=pd.to_datetime(ord_items_prod_cust['order_date'], errors='coerce')
ord_items_prod_cust['month_number']=ord_items_prod_cust['order_date'].dt.month
ord_items_prod_cust['year']=ord_items_prod_cust['order_date'].dt.year
ord_items_prod_cust['year'] = (ord_items_prod_cust['year'].fillna(0).astype(int))
ord_items_prod_cust['year'] = (ord_items_prod_cust['year'].astype(int))
ord_items_prod_cust['month_name']=ord_items_prod_cust['order_date'].dt.month_name()
ord_items_prod_cust['day_name']=ord_items_prod_cust['order_date'].dt.day_name()
ord_items_prod_cust['quarters']='Q'+ord_items_prod_cust['order_date'].dt.quarter.astype(str)
ord_items_prod_cust['day_type']=ord_items_prod_cust['day_name'].apply(lambda x: 'Weekend' if x in ['Saturday', 'Sunday'] else 'Weekday')
ord_items_prod_cust["month"] = ord_items_prod_cust["order_date"].dt.strftime("%b")

#st.write(ord_items_prod_cust.head())


# TITLE
st.markdown('<style>.block-container{padding-top:0.0rem;padding-bottom:0.0rem}</style>', unsafe_allow_html=True)
st.title("Dashboard For Business Manager :bar_chart:")
st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
# SIDEBAR FILTERS

st.sidebar.header("Choose Filters")
oipc = ord_items_prod_cust.copy()

# FORMAT FUNCTION
def format_number(num):

    if num >= 1000000:
        return f"{num/1000000:.2f}M"

    elif num >= 1000:
        return f"{num/1000:.0f}K"  

    else:
        return f"{num:.0f}"

available_year = sorted([y for y in oipc["year"].unique() if y != 0])
years = st.sidebar.multiselect("Year",available_year)
if years:
    oipc = oipc[oipc["year"].isin(years)]

month_order = ["Jan", "Feb", "Mar", "Apr","May", "Jun", "Jul", "Aug","Sep", "Oct", "Nov", "Dec"]
sorted_months = sorted(oipc["month"].dropna().unique(),key=lambda x: month_order.index(x))
month_name = st.sidebar.multiselect("Month",sorted_months)
if month_name:
    oipc = oipc[oipc["month"].isin(month_name)]
    
payment_method = st.sidebar.multiselect("Payment Method",oipc["payment_method"].dropna().unique())
if payment_method:
    oipc = oipc[oipc["payment_method"].isin(payment_method)]

brand= st.sidebar.multiselect("Brand", sorted(oipc["brand"].dropna().unique()))
if brand:
    oipc = oipc[oipc["brand"].isin(brand)]
    
product_name= st.sidebar.multiselect("Product Name", oipc["product_name"].dropna().unique())
if product_name:
    oipc = oipc[oipc["product_name"].isin(product_name)]
    
category = st.sidebar.multiselect("Category", oipc["category"].dropna().unique())
if category:
    oipc = oipc[oipc["category"].isin(category)]

area = st.sidebar.multiselect("Area",sorted(oipc["area"].dropna().unique()))
if area:
    oipc = oipc[oipc["area"].isin(area)]
    
#----------------------------------------------------------------------------------------------------------------#
# TABS
tab1, tab2 = st.tabs([ "🛒 Sales, Order & Product Performance 💰","📖 Glossary"])
st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 

with tab1:
# KPI METRICS (FIXED)
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    col1, col2, col3, col4,col5= st.columns(5)

    top_prod=oipc.groupby('product_name')['revenue'].sum().reset_index(name='total_revenue').sort_values(by='total_revenue',ascending=False).head(1)
    
    total_orders = oipc["order_id"].nunique()
    total_revenue = (oipc.drop_duplicates(subset="order_id")["revenue"].sum())
    total_profit= (oipc.drop_duplicates(subset="order_id")["profit_amount"].sum())
    total_cost=(oipc.drop_duplicates(subset="order_id")["cost"].sum())
    profit_percentage=(total_profit/total_revenue)*100
    avg_order_value=total_revenue/total_orders
    total_items_sold=(oipc.drop_duplicates(subset="order_id")["quantity"].sum())
    total_products=oipc["product_id"].nunique()
    total_customers=oipc["customer_id"].nunique()
    top_prod_by_rev = top_prod.iloc[0]["product_name"]
    
    col1.metric("Total Orders",format_number( total_orders))
    col2.metric("Total Items Sold", format_number( total_items_sold))
    col3.metric("Total Revenue", f"₹{format_number( total_revenue)}")
    col4.metric("Total Profit", f"₹{format_number( total_profit)}")
    col5.metric("Total cost", f"₹{format_number( total_cost)}")
    
    col6,col7,col8,col9,col10 = st.columns(5)
    
    col6.metric("Total Customers", total_customers)
    col7.metric("Total Products", format_number( total_products))
    col8.metric("Avg Order Value", f"₹{format_number( avg_order_value)}")
    col9.metric("Profit %", f"{profit_percentage:.2f}%")
    col10.metric("Top Product", top_prod_by_rev)
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    #-------------------------------------------------------------------------------------------------------------


    # Revenue & Profit by Month
    st.subheader("Revenue and Profit by Month")
    month_data = (oipc.groupby("month")[["revenue","profit_amount"]].sum().reset_index())
    month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    month_data["month"] = pd.Categorical(month_data["month"], categories=month_order, ordered=True )
    fig, ax = plt.subplots(figsize=(6,3))
    sns.lineplot(data=month_data,x="month",y="revenue",marker="o",label="Revenue",ax=ax,color='green')
    sns.lineplot(data=month_data,x="month",y="profit_amount",marker="o",label="Profit",ax=ax,color='#AA336A')
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount")
    st.pyplot(fig)
    with st.expander("📈 Revenue and Profit by Month - Insights"):
        st.markdown("""
                Revenue and profit show strong growth from March to August.  
            August recorded the highest revenue and profit performance.  
            Revenue declines sharply during November and December, indicating possible seasonal slowdown.  
            Profit trend follows revenue trend, showing stable profitability margins throughout the year.  
            Business performance is strongest during mid-year months.  
        """)
    
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    c2,c3 = st.columns(2)
    # Revenue by Day Type
    with c2:
        st.subheader("Revenue,Profit and Orders by DayType")
        daytype_data = (oipc.groupby("day_type").agg({"revenue":"sum","profit_amount":"sum","order_id":"nunique"}).reset_index())
        daytype_data.rename(columns={"order_id":"total_orders"}, inplace=True)
        fig, ax1 = plt.subplots(figsize=(5,3))
        # BAR WIDTH
        x = np.arange(len(daytype_data["day_type"]))
        width = 0.35
        # REVENUE BAR
        ax1.bar(x - width/2,daytype_data["revenue"],width,label="Revenue",color="green")
        # PROFIT BAR
        ax1.bar(x + width/2,daytype_data["profit_amount"],width,label="Profit",color="#AA336A")
        # X LABELS
        ax1.set_xticks(x)
        ax1.set_xticklabels(daytype_data["day_type"])
        ax1.set_xlabel("Day Type")
        ax1.set_ylabel("Revenue / Profit")
        # SECOND AXIS FOR ORDERS
        ax2 = ax1.twinx()
        ax2.plot(x,daytype_data["total_orders"],marker="o",linewidth=3,label="Orders",color="blue")
        ax2.set_ylabel("Total Orders")
        # TITLE
        plt.title("Revenue, Profit and Orders by Day Type")
        # LEGENDS
        ax1.legend(loc="upper left")
        ax2.legend(loc="upper right")
        plt.tight_layout()
        st.pyplot(fig,use_container_width=True)
        with st.expander("📊 Revenue, Profit and Orders by Day Type - Insights"):
                st.markdown(f"""
                Weekdays generated approximately **₹3.5M revenue** and **₹1M profit**.  
                Weekend revenue contribution is much lower at approximately **₹1.4M**.  
                Total weekday orders are around **3.6K**, much higher than weekends (~1.4K).  
                Customer purchasing activity is strongest during weekdays.  
                Weekend sales can be improved through promotional campaigns and discounts.  
                """)
    # Orders by Area
    with c3:
        st.subheader("Top Areas by Orders")
        area_orders = (oipc.groupby("area")["order_id"].nunique().reset_index(name="total_orders").sort_values(by="total_orders", ascending=False).head(10))
        fig, ax = plt.subplots(figsize=(6,4))
        sns.barplot(data=area_orders,y="area",x="total_orders",ax=ax,color='green')
        ax.set_xlabel("Orders")
        ax.set_ylabel("Area")
        st.pyplot(fig)
        with st.expander("🌍 Top Areas by Orders - Insights"):
            st.markdown(f"""
            **Orai** generated the highest orders (**~45 orders**).  
            **Deoghar** and **Gandhinagar** are also strong-performing regions.  
            Top 5 areas contribute major share of total customer orders.  
            Area-wise order analysis helps optimize delivery operations.  
            Lower-performing locations may require additional marketing focus.  
            """)

    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    c4,c5 = st.columns(2)

    # Revenue by Category
    with c4:
        st.subheader("Top 10 Category by Revenue")
        cat_data = (oipc.groupby("category")["revenue"].sum().reset_index().sort_values(by="revenue", ascending=False)).head(10)
        fig, ax = plt.subplots(figsize=(7,5))
        sns.barplot(data=cat_data,y="category",x="revenue",ax=ax,color='green')
        ax.set_xlabel("Revenue")
        ax.set_ylabel("Category")
        plt.tight_layout()
        st.pyplot(fig)
        with st.expander("🏷️ Top 10 Category by Revenue - Insights"):
            st.markdown(f"""
            **Dairy & Breakfast** generated the highest category revenue (**~₹6.3 Lakhs**).  
            **Pharmacy** and **Fruits & Vegetables** are also major revenue contributors.  
            Grocery and healthcare categories dominate overall business sales.  
            Lower-performing categories contribute below **₹4 Lakhs** revenue.  
            Category analysis helps identify high-demand business segments.  
            """)

    # Orders by Product
    with c5:
        st.subheader("Top 10 Products by Total Orders ")
        prod_orders = (oipc.groupby("product_name")["quantity"].sum().reset_index().sort_values(by="quantity", ascending=False).head(10))
        fig, ax = plt.subplots(figsize=(7,5))
        sns.barplot(data=prod_orders,x="product_name",y="quantity",ax=ax,color='green')
        plt.xticks(rotation=90)
        ax.set_xlabel("Product")
        ax.set_ylabel("Orders")
        plt.tight_layout()
        st.pyplot(fig)
        plt.tight_layout()
        with st.expander("🛒 Top 10 Products by Total Orders - Insights"):
            st.markdown(f"""
            **Pet Treats** received the highest total orders with approximately **470 orders**.  
            **Toilet Cleaner** generated around **430 orders**.  
            **Dish Soap**, **Vitamins**, and **Cough Syrup** also show strong customer demand.  
            Top ordered products indicate high-frequency customer purchasing patterns.  
            Inventory planning should prioritize these fast-moving products.  
            Low ordered products may require marketing support or stock optimization.  
            """)
        
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    c6,c7=st.columns(2)
    # Top Products by Revenue
    with c6:
        st.subheader("Top 10 Products by Revenue")
        top_rev = (oipc.groupby("product_name")["revenue"].sum().reset_index().sort_values(by="revenue", ascending=False).head(10))
        fig, ax = plt.subplots(figsize=(5,5))
        sns.barplot(data=top_rev,y="product_name",x="revenue",ax=ax,color='green')
        ax.set_xlabel("Revenue")
        ax.set_ylabel("Product")
        plt.tight_layout()
        st.pyplot(fig)
        with st.expander("🏆 Top 10 Products by Revenue - Insights"):
            st.markdown(f"""
            **Vitamins** generated the highest product revenue of approximately **₹2.6 Lakhs**.  
            **Pet Treats** contributed around **₹2.5 Lakhs** revenue.  
            **Cough Syrup** and **Toilet Cleaner** also generated revenue above **₹2 Lakhs**.  
            Healthcare and wellness products contribute significantly to business profitability.  
            Top revenue-generating products should receive higher inventory focus.  
            Product revenue analysis helps identify profitable business segments.  
            """)

    with c7:
        st.subheader("Revenue by Payment Method")
        payment_data = (oipc.groupby("payment_method")["revenue"].sum().reset_index())
        fig, ax = plt.subplots(figsize=(5,4))
        ax.pie(payment_data["revenue"],labels=payment_data["payment_method"],autopct='%1.1f%%')
        plt.tight_layout()
        st.pyplot(fig)
        with st.expander("💳 Revenue by Payment Method - Insights"):
            st.markdown(f"""
            **Card payments** contributed the highest revenue share at approximately **26.7%**.  
            **Cash payments** contributed around **24.8%** revenue share.  
            **UPI payments** generated approximately **24.6%** contribution.  
            **Wallet payments** contributed the lowest share at around **24.0%**.  
            Revenue contribution across payment methods is relatively balanced.  
            Payment method analysis helps understand customer transaction preferences.  
            """)
            
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    c8,c9=st.columns(2)
    # Top Products by Revenue
    with c8:
        st.subheader("Less Performing Products By Revenue")
        top_rev = (oipc.groupby("product_name")["revenue"].sum().reset_index().sort_values(by="revenue", ascending=True).head(10))
        fig, ax = plt.subplots(figsize=(5,4))
        sns.barplot(data=top_rev,y="product_name",x="revenue",ax=ax,color='green')
        ax.set_xlabel("Revenue")
        ax.set_ylabel("Product")
        plt.tight_layout()
        st.pyplot(fig)
        
        with st.expander("📉 Less Performing Products by Revenue - Insights"):
            st.markdown(f"""
            **Lemonade** generated the lowest revenue at approximately **₹15K**.  
            **Rice**, **Cereal**, and **Spinach** also contributed relatively lower revenue below **₹25K**.  
            Low-performing products indicate weaker customer demand or lower sales volume.  
            Products with low revenue may require discounts, promotions, or bundling strategies.  
            Inventory levels for low-performing products should be optimized to reduce holding costs.  
            Product performance analysis helps identify weak business segments requiring improvement.  
            """)


        
    with c9:
        st.subheader("Top 10 Brand by Revenue")
        cat_data = (oipc.groupby("brand")["revenue"].sum().reset_index().sort_values(by="revenue", ascending=False)).head(10)
        fig, ax = plt.subplots(figsize=(7,5.5))
        sns.barplot(data=cat_data,y="brand",x="revenue",ax=ax,color='green')
        ax.set_xlabel("Revenue")
        ax.set_ylabel("Brand")
        plt.tight_layout()
        st.pyplot(fig)
        with st.expander("🏷️ Top 10 Brand by Revenue - Insights"):
            st.markdown(f"""
            **Karnik PLC** generated the highest brand revenue at approximately **₹65K**.  
            **Mandal-Kar** and **Roy-Char** also contributed strong revenue above **₹50K**.  
            Top-performing brands contribute a major share of total business revenue.  
            Revenue difference between top and bottom brands is relatively moderate, showing balanced brand contribution.  
            High-performing brands should receive stronger inventory and marketing focus.  
            Brand-wise revenue analysis helps identify the most profitable business partnerships.  
            """)
        
#---------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------
with tab2:
    st.subheader("📖 KPI Glossary")

    col1 , col2 = st.columns(2)
    with col1:
        with st.expander("📦 Total Orders"):
            st.write("**Meaning:** Total number of orders placed by customers.")
            st.write("**Formula:** COUNT(DISTINCT order_id)")
    with col2:
        with st.expander("🛒 Total Items Sold"):
            st.write("**Meaning:** Total quantity of products sold.")
            st.write("**Formula:** SUM(quantity)")
    col1 , col2 = st.columns(2)
    with col1:
        with st.expander("💰 Total Revenue"):
            st.write("**Meaning:** Total revenue generated from all sales.")
            st.write("**Formula:** SUM(revenue)")
    with col2:
        with st.expander("📈 Total Profit"):
            st.write("**Meaning:** Profit earned after deducting costs.")
            st.write("**Formula:** Total Revenue - Total Cost")
    col1 , col2 = st.columns(2)
    with col1:
        with st.expander("💸 Total Cost"):
            st.write("**Meaning:** Total operational and product cost.")
            st.write("**Formula:** SUM(cost)")
    with col2:
        with st.expander("👥 Total Customers"):
            st.write("**Meaning:** Total unique customers who placed orders.")
            st.write("**Formula:** COUNT(DISTINCT customer_id)")
    col1 , col2 = st.columns(2)
    with col1:
        with st.expander("📦 Total Products"):
            st.write("**Meaning:** Total number of available products.")
            st.write("**Formula:** COUNT(DISTINCT product_id)")
    with col2:
        with st.expander("💳 Average Order Value"):
            st.write("**Meaning:** Average revenue generated per order.")
            st.write("**Formula:** Total Revenue / Total Orders")
    col1 , col2 = st.columns(2)
    with col1:
        with st.expander("📊 Profit %"):
            st.write("**Meaning:** Percentage of profit earned from revenue.")
            st.write("**Formula:** (Total Profit / Total Revenue) × 100")
    with col2:
        with st.expander("🏆 Top Product"):
            st.write("**Meaning:** Product generating highest sales revenue.")
            st.write("**Formula:** Product with MAX(total sales)")
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    st.subheader("🎛️ Filters Used In Dashboard")

    st.markdown("""
    ✅ **Year Filter**  
    - Filters dashboard data based on selected year  
    - Helps compare yearly business performance trends  

    ✅ **Month Filter**  
    - Filters dashboard data for selected month  
    - Helps analyze monthly sales and profit patterns  

    ✅ **Payment Method Filter**  
    - Filters orders based on payment type  
    - Helps identify customer payment preferences  

    ✅ **Brand Filter**  
    - Filters dashboard data by selected product brand  
    - Helps analyze brand-wise performance and revenue  
    """)


    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    st.subheader("📊 Analysis Performed In Dashboard")
    st.markdown("""
    📈 **Total Revenue and Profit Analysis**  
    - Analyzes monthly revenue and profit trends  
    - Helps identify business growth and profitable months  

    📦 **Sales and Orders Analysis**  
    - Tracks total orders and total items sold  
    - Helps measure overall sales performance  

    💰 **Cost and Profitability Analysis**  
    - Compares total revenue, total cost, and total profit  
    - Helps evaluate overall business profitability  

    📅 **Monthly Revenue Trend Analysis**  
    - Analyzes month-wise revenue and profit fluctuations  
    - Helps identify seasonal sales patterns  

    🗓️ **Day Type Analysis (Weekday vs Weekend)**  
    - Compares revenue, profit, and orders by day type  
    - Helps understand customer purchasing behavior  

    🌍 **Area-wise Order Analysis**  
    - Identifies areas generating highest number of orders  
    - Helps target high-performing locations  

    🏷️ **Category-wise Revenue Analysis**  
    - Analyzes revenue generated by each product category  
    - Helps identify top-performing categories  

    🛒 **Product-wise Order Analysis**  
    - Tracks products with highest number of orders  
    - Helps identify customer demand trends  

    🏆 **Top Products Revenue Analysis**  
    - Identifies products generating highest revenue  
    - Helps focus on best-selling products  

    💳 **Payment Method Analysis**  
    - Compares revenue contribution by payment methods  
    - Helps understand customer payment preferences  

    👥 **Customer Analysis**  
    - Tracks total customers and customer engagement  
    - Helps evaluate customer reach and growth  

    📦 **Product Performance Analysis**  
    - Evaluates total products and item sales performance  
    - Helps identify strong and weak products  
""")
