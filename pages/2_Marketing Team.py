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
import plotly.graph_objects as go
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

actual_orders = (orders.groupby("customer_id")["order_id"].nunique().reset_index(name="actual_total_orders"))
customers = customers.merge(actual_orders,on="customer_id",how="left")
customers["actual_total_orders"] = (customers["actual_total_orders"].fillna(0).astype(int))
customers["total_orders"] = (customers["actual_total_orders"])
customers.drop(columns="actual_total_orders",inplace=True)
customers['customer_type']=np.where(customers['total_orders']>1,'repeat_customers',np.where(customers['total_orders']==1,'one_time_customers','no_order_customers'))

#only one table for analysis
# ord_items_prod_cust=orders.merge(order_items,on='order_id',how='left',suffixes=("","_item"))\
#     .merge(products,left_on='product_id',right_on='product_id',how='left',suffixes=("","_prod"))\
#         .merge(customers,on='customer_id',how='right',suffixes=("","_cust"))\
#             .merge(customer_feedback,on='customer_id',how='right',suffixes=("","_feed"))

ord_items_prod_cust=customers.merge(orders,on='customer_id',how='left')\
    .merge(order_items,on='order_id',how='left',suffixes=("","_item"))\
        .merge(customer_feedback,on='customer_id',how='left',suffixes=("","_feed"))
#orders related columns     
ord_items_prod_cust['revenue'] = (ord_items_prod_cust['quantity'] *ord_items_prod_cust['unit_price'])
ord_items_prod_cust['registration_date']=pd.to_datetime(ord_items_prod_cust['registration_date'],dayfirst=True,errors='coerce')
#ord_items_prod_cust['order_date']=pd.to_datetime(ord_items_prod_cust['order_date'])
ord_items_prod_cust['month_number']=ord_items_prod_cust['registration_date'].dt.month
ord_items_prod_cust['year']=ord_items_prod_cust['registration_date'].dt.year
ord_items_prod_cust['year'] = (ord_items_prod_cust['year'].fillna(0).astype(int))
ord_items_prod_cust['year'] = (ord_items_prod_cust['year'].astype(int))
ord_items_prod_cust['month_name']=ord_items_prod_cust['registration_date'].dt.month_name()
ord_items_prod_cust['day_name']=ord_items_prod_cust['registration_date'].dt.day_name()
ord_items_prod_cust['quarters']='Q'+ord_items_prod_cust['registration_date'].dt.quarter.astype(str)
ord_items_prod_cust['day_type']=ord_items_prod_cust['day_name'].apply(lambda x: 'Weekend' if x in ['Saturday', 'Sunday'] else 'Weekday')
ord_items_prod_cust["month"] = ord_items_prod_cust["registration_date"].dt.strftime("%b")

#marketing performance related columns
marketing_performance['date']=pd.to_datetime(marketing_performance['date'],dayfirst=True)
marketing_performance['month_number']=marketing_performance['date'].dt.month
marketing_performance['year']=marketing_performance['date'].dt.year
marketing_performance['year'] = (marketing_performance['year'].fillna(0).astype(int))
marketing_performance['year'] = (marketing_performance['year'].astype(int))
marketing_performance['month_name']=marketing_performance['date'].dt.month_name()
marketing_performance['day_name']=marketing_performance['date'].dt.day_name()
marketing_performance['quarters']='Q'+marketing_performance['date'].dt.quarter.astype(str)
marketing_performance['day_type']=marketing_performance['day_name'].apply(lambda x: 'Weekend' if x in ['Saturday', 'Sunday'] else 'Weekday')
marketing_performance["month"] = marketing_performance["date"].dt.strftime("%b")
# TITLE
st.markdown('<style>.block-container{padding-top:0.0rem;padding-bottom:0.0rem}</style>', unsafe_allow_html=True)
st.title("Dashboard For Marketing Team :bar_chart:")
st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
# SIDEBAR FILTERS

st.sidebar.header("Choose Filters")
oipc = ord_items_prod_cust.copy()
mp=marketing_performance.copy()

# FORMAT FUNCTION
def format_number(num):

    if num >= 1000000:
        return f"{num/1000000:.2f}M"

    elif num >= 1000:
        return f"{num/1000:.0f}K"  

    else:
        return f"{num:.0f}"

available_years = sorted([y for y in mp["year"].unique() if y != 0])
year = st.sidebar.multiselect("Year",available_years)
if year:
    mp = mp[mp["year"].isin(year)]

month_order = ["Jan", "Feb", "Mar", "Apr","May", "Jun", "Jul", "Aug","Sep", "Oct", "Nov", "Dec"]
sorted_months = sorted(mp["month"].dropna().unique(),key=lambda x: month_order.index(x))
month_name = st.sidebar.multiselect("Month",sorted_months)
if month_name:
    mp = mp[mp["month"].isin(month_name)]
       
target_audience = st.sidebar.multiselect("Target Audience",mp["target_audience"].dropna().unique())
if target_audience:
    mp = mp[mp["target_audience"].isin(target_audience)]

campaign= st.sidebar.multiselect("Campaign", sorted(mp["campaign_name"].dropna().unique()))
if campaign:
    mp = mp[mp["campaign_name"].isin(campaign)]
    
    
channel = st.sidebar.multiselect("Channel", mp["channel"].dropna().unique())
if channel:
    mp = mp[mp["channel"].isin(channel)]
    

available_year = sorted([y for y in oipc["year"].unique() if y != 0])
years = st.sidebar.multiselect("Years",available_year)
if years:
    oipc = oipc[oipc["year"].isin(years)]

month_order = ["Jan", "Feb", "Mar", "Apr","May", "Jun", "Jul", "Aug","Sep", "Oct", "Nov", "Dec"]
sorted_months = sorted(oipc["month"].dropna().unique(),key=lambda x: month_order.index(x))
month_name = st.sidebar.multiselect("Month Name",sorted_months)
if month_name:
    oipc = oipc[oipc["month"].isin(month_name)]
        
customer_type = st.sidebar.multiselect("Customer_Type",oipc["customer_type"].dropna().unique())
if customer_type:
    oipc = oipc[oipc["customer_type"].isin(customer_type)]
        
day_type= st.sidebar.multiselect("Day Type", sorted(oipc["day_type"].dropna().unique()))
if day_type:
    oipc = oipc[oipc["day_type"].isin(day_type)]

area= st.sidebar.multiselect("Area", sorted(oipc["area"].dropna().unique()))
if area:
    oipc = oipc[oipc["area"].isin(area)]
        
        
sentiment = st.sidebar.multiselect("Sentiment", oipc["sentiment"].dropna().unique())
if sentiment:
    oipc = oipc[oipc["sentiment"].isin(sentiment)]

#-----------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
# TABS
tab1, tab2,tab3 = st.tabs([ "📢 Marketing Performance Dashboard 📈 ", "👥 Customer & Feedback Dashboard ⭐","📖 Glossary"])

st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 

with tab1:
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    total_campaigns = mp["campaign_id"].nunique()
    total_campaign_revenue = (mp["revenue_generated"].sum())
    total_spend = (mp["spend"].sum())
    campaign_profit = (total_campaign_revenue -total_spend)
    total_impressions=mp['impressions'].sum()
    total_clicks=mp['clicks'].sum()
    total_conversions=mp['conversions'].sum()
    conversion_rate = (total_conversions/total_clicks)*100
    ctr = (total_clicks/total_impressions)*100
    revenue_per_click = total_campaign_revenue/total_clicks
    roas = (total_campaign_revenue /total_spend)
    
    k1,k2,k3,k4 = st.columns(4)
    k1.metric("Total Campaigns",f"{total_campaigns/1000:.1f}K")
    k2.metric("Campaign Revenue",f"₹{total_campaign_revenue/1000000:.2f}M")
    k3.metric("Total Spend",f"₹{total_spend/1000000:.2f}M")
    k4.metric("Campaign Profit",f"₹{campaign_profit/1000000:.2f}M")

    k5,k6,k7,k8 = st.columns(4)
    k5.metric("Conversion Rate %",f"{conversion_rate:.2f}%")
    k6.metric("CTR %",f"{ctr:.2f}%")
    k7.metric("Revenue Per Click",f"{revenue_per_click:.2f}")
    k8.metric(" Avg ROAS",f"{roas:.2f}")

    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    st.subheader("Campaign Revenue & Spend Trend")

    trend = (mp.groupby("month")[["revenue_generated","spend"]].sum().reset_index())
    month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    trend["month"] = pd.Categorical(trend["month"],categories=month_order,ordered=True)
    trend = trend.sort_values("month")
    fig, ax = plt.subplots(figsize=(8,4))
    sns.lineplot(data=trend,x="month",y="revenue_generated",marker="o",label="Revenue",ax=ax,color='green')
    sns.lineplot(data=trend,x="month",y="spend",marker="o",label="Spend",ax=ax,color="#8c0c4c")
    ax.set_title("Revenue vs Spend Over Month")
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount")
    plt.xticks(rotation=45)
    st.pyplot(fig)
    with st.expander("1️⃣ Total Campaign Revenue and Spend by Month - Insights & Recommendations"):
        st.markdown("""
        • Campaign revenue increased from around ₹1.6M in January to ₹3.4M in May.  
        • Highest campaign revenue was recorded during May, July, and October (~₹3.3M–₹3.4M).  
        • Campaign spend remained stable around ₹1.6M–₹1.7M during most months.  
        • Revenue dropped significantly during November and December.  
        • Campaign profit remained positive throughout the year.  

        Recommendations:
        1. Increase marketing investment during high-performing months.  
        2. Analyze reasons for low revenue during November and December.  
        3. Focus more on profitable campaigns with lower spending.  
        """)
    
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    c1,c2= st.columns(2)
    with c1:
        st.subheader("Top 5 Campaign by Revenue")
        top_campaign = (mp.groupby("campaign_name")["revenue_generated"].sum().reset_index().sort_values(by="revenue_generated",ascending=False).head(5))
        fig, ax = plt.subplots(figsize=(8,9))
        sns.barplot(data=top_campaign,y="campaign_name",x="revenue_generated",ax=ax,color='green')
        ax.set_title("Top Campaign Revenue")
        st.pyplot(fig)
        with st.expander(" Top Campaign Revenue Analysis - Insights & Recommendations"):
            st.markdown("""
            • Referral Program generated the highest campaign revenue (₹3.7M).  
            • New User Discount and Email Campaign also generated strong revenue (₹3.6M).  
            • All top campaigns contributed similar revenue values.  
            • Referral-based marketing campaigns perform very well.  

            Recommendations:
            1. Increase investment in referral campaigns.  
            2. Continue email marketing campaigns for customer engagement.  
            3. Improve low-performing campaigns through optimization.  
            """)

    with c2:
        st.subheader("Revenue by Channel")
        channel_rev = (mp.groupby("channel")["revenue_generated"].sum().reset_index())
        fig, ax = plt.subplots(figsize=(5,4))
        ax.pie(channel_rev["revenue_generated"],labels=channel_rev["channel"],autopct="%1.1f%%")
        st.pyplot(fig)
        with st.expander("3️⃣ Total Campaign Revenue by Channel - Insights & Recommendations"):
            st.markdown("""
            • Email channel generated the highest revenue share (~25.4%).  
            • App and Social Media channels also contributed around 24–25% revenue.  
            • Revenue contribution across channels is balanced.  
            • SMS channel generated the lowest revenue share.  

            Recommendations:
            1. Focus more on high-performing channels like Email and App campaigns.  
            2. Improve SMS campaign effectiveness.  
            3. Allocate marketing budget based on channel performance.  
            """)
        
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    c4,c5 = st.columns(2)
    with c4:
        st.subheader(" Top 10 Campaign by ConversionRate")
        conv = mp.groupby("campaign_name").agg(clicks=('clicks','sum'),conversion=('conversions','sum')).reset_index()
        conv['conversion_rate']=(conv['conversion']/conv['clicks'])
        conv=conv.sort_values(by="conversion_rate",ascending=False).head(10)
        fig, ax = plt.subplots(figsize=(8,8))
        sns.barplot(data=conv,y="campaign_name",x="conversion_rate",ax=ax,color='green')
        plt.tight_layout()
        st.pyplot(fig)
        with st.expander("4️⃣ Conversion Rate % by Campaign Name - Insights & Recommendations"):
            st.markdown("""
            • Most campaigns achieved around 10% conversion rate.  
            • Weekend Special and New User Discount campaigns have strong conversion performance.  
            • Conversion rates are stable across campaigns.  
            • Campaigns are successfully converting customer clicks into sales.  

            Recommendations:
            1. Continue optimizing campaigns with high conversion rates.  
            2. Improve customer targeting for weaker campaigns.  
            3. Use successful campaign strategies in future campaigns.  
            """)
    with c5:
        mp['ctr']=mp['clicks']/mp['impressions']
        st.subheader("Top Campaigns by CTR%")
        ctr_data = (mp.groupby("campaign_name")["ctr"].mean().reset_index().sort_values(by="ctr",ascending=False).head(5))
        fig, ax = plt.subplots(figsize=(5,4))
        sns.barplot(data=ctr_data,x="campaign_name",y="ctr",ax=ax,color='green')
        plt.xticks(rotation=45)
        st.pyplot(fig)
        with st.expander("5️⃣ Top 5 Campaign by CTR % - Insights & Recommendations"):
            st.markdown("""
            • App Push Notification campaign achieved the highest CTR (~10.4%).  
            • Email Campaign and Flash Sale campaigns also achieved strong CTR performance.  
            • All top campaigns maintained CTR above 10%.  
            • Customers are actively engaging with marketing campaigns.  

            Recommendations:
            1. Increase focus on App Push Notification campaigns.  
            2. Improve ad creatives to increase customer engagement.  
            3. Continue testing campaign content for better click performance.  
            """)

    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    c6,c7=st.columns(2)
    with c6:
        st.subheader("Campaigns By ROAS")
        roas_data = (mp.groupby("campaign_name")["return_on_ad_spend"].mean().reset_index().sort_values(by="return_on_ad_spend",ascending=False))
        fig, ax = plt.subplots(figsize=(5,5))
        sns.barplot(data=roas_data,y="campaign_name",x="return_on_ad_spend",ax=ax,color='green')
        plt.tight_layout()
        st.pyplot(fig)
        with st.expander("6️⃣ Return On Ad Spend by Campaign Name - Insights & Recommendations"):
            st.markdown("""
            • Referral Program achieved the highest ROAS (~2.03).  
            • Email Campaign and App Push Notification campaigns also generated strong ROAS.  
            • Most campaigns generated nearly 2x return on advertising spend.  
            • Marketing campaigns are generating profitable returns.  

            Recommendations:
            1. Increase budget for high ROAS campaigns.  
            2. Reduce spending on low-performing campaigns.  
            3. Focus on campaigns generating strong profitability.  
            """)

    with c7:
        st.subheader("Marketing Conversion Funnel")
        impressions = (mp["impressions"].sum())
        clicks = (mp["clicks"].sum())
        conversions = (mp["conversions"].sum())
        funnel = pd.DataFrame({"Stage":["Impressions","Clicks","Conversions"],"Values":[impressions,clicks,conversions]})
        fig, ax = plt.subplots(figsize=(5,5))
        sns.barplot(data=funnel,y="Stage",x="Values",ax=ax,color='green')
        ax.set_title("Marketing Funnel")
        st.pyplot(fig)
        with st.expander("7️⃣ Marketing Conversion Funnel - Insights & Recommendations"):
            st.markdown("""
            • Total impressions reached approximately 2948K users.  
            • Total clicks reduced to around 297K users.  
            • Final conversions were around 29K users.  
            • Significant customer drop-off is visible between impressions and clicks.  
            • Funnel conversion percentage is relatively low compared to impressions.  

            Recommendations:
            1. Improve ad quality and targeting to increase clicks.  
            2. Optimize landing pages to improve conversions.  
            3. Focus on customer engagement strategies to reduce drop-offs.  
            4. Improve campaign messaging and call-to-action performance.  
            """)
#***************************************************************************************************************************
#****************************************************************************************************************************
with tab2:

    k1,k2,k3,k4,k5 = st.columns(5)

    total_customers = oipc["customer_id"].nunique()
    avg_customer_spend = oipc.groupby("customer_id")["revenue"].sum().mean()
    one_time_customers = (oipc[oipc["customer_type"] == "one_time_customers"]["customer_id"].nunique())
    repeat_customers = (oipc[oipc["customer_type"] == "repeat_customers"]["customer_id"].nunique())
    repeat_customer_percent = (repeat_customers / total_customers) * 100
    one_time_customer_percent = (one_time_customers / total_customers) * 100
    total_feedbacks = oipc["feedback_id"].nunique()
    negative_feedback =(oipc[oipc["sentiment"] == "Negative"]['feedback_id'].nunique())
    negative_feedback_percent=(negative_feedback/total_feedbacks)*100
    positive_feedback =(oipc[oipc["sentiment"] == "Positive"]['feedback_id'].nunique())
    neutral_feedback =(oipc[oipc["sentiment"] == "Neutral"]['feedback_id'].nunique())
    neutral_feedback_percent = (neutral_feedback/total_feedbacks) * 100
    positive_feedback_percent = (positive_feedback/total_feedbacks) * 100
    avg_rating = oipc["rating"].mean()
    happy_customers = (oipc[oipc['rating'] >= 4]['feedback_id'].nunique())
    happy_customers_percent=(happy_customers/total_feedbacks)*100

    k1.metric("Total Customers", f"{total_customers/1000:.0f}K")
    k2.metric("Avg Customer Spend", f"₹{avg_customer_spend/1000:.2f}K")
    k3.metric("One-Time Customers %",f"{one_time_customer_percent:.2f}%")
    k4.metric("Repeat Customers %", f"{repeat_customer_percent:.2f}%")
    k5.metric("Total Feedbacks", f"{total_feedbacks/1000:.0f}K")
    
    k1,k2,k3,k4,k5 = st.columns(5)
    k1.metric("Negative Feedback %", negative_feedback)
    k2.metric("Neutral Feedback %", f"{neutral_feedback_percent:.2f}%")
    k3.metric("Positive Feedback %", f"{positive_feedback_percent:.2f}%")
    k4.metric("Average Rating", round(avg_rating,2))
    k5.metric("Happy Customers %", f"{happy_customers_percent:.2f}%")

    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    st.subheader("📈 Customers by Month & Type")
    cust_month = (oipc.groupby(["month","customer_type"])["customer_id"].nunique().reset_index())
    month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    cust_month["month"] = pd.Categorical(cust_month["month"],categories=month_order,ordered=True)
    cust_month = cust_month.sort_values("month")
    fig, ax = plt.subplots(figsize=(9,3))
    sns.lineplot(data=cust_month,x="month",y="customer_id",hue="customer_type",marker="o",ax=ax)
    ax.set_title("Customers Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Customers")
    plt.xticks(rotation=45)
    st.pyplot(fig)
    with st.expander("1️⃣ Total Customers by Month and Customer Type - Insights & Recommendations"):
        st.markdown("""
        • Repeat customers are higher than one-time customers in all months.  
        • Customer count is highest during March and October.  
        • Customer activity is lower during November, December, and January.  
        • One-time customers are fewer compared to repeat customers.  
        Recommendations:
        1. Give offers to one-time customers to make them repeat customers.  
        2. Run special campaigns during low-sales months.  
        3. Focus more on customer retention programs.  
        """)
    
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    c1,c2 = st.columns(2)
    with c1:
        st.subheader("🏙️ Top 10 Areas by Customers")
        top_area = (oipc.groupby("area")["customer_id"].nunique().reset_index(name="total_customers").sort_values(by="total_customers",ascending=False).head(10))
        fig, ax = plt.subplots(figsize=(8,6.2))
        top_area["total_customers"] = top_area["total_customers"].astype(int)
        sns.barplot(data=top_area,y="area",x="total_customers",ax=ax,color='green')
        ax.set_xticks(range(0, int(top_area["total_customers"].max()) + 1))
        ax.set_title("Top Customer Areas")
        ax.set_xlabel("Customers")
        ax.set_ylabel("Area")
        st.pyplot(fig)
        with st.expander("2️⃣ Top 10 Areas by Total Customers - Insights & Recommendations"):
            st.markdown("""
            • Jalna has the highest number of customers (~18 customers).  
            • Bathinda, Deoghar, and Orai also have high customer counts.  
            • Top areas generate most of the customer activity.  
            • Some areas have lower customer reach.  
            Recommendations:
            1. Increase marketing in low-performing areas.  
            2. Improve delivery services in top areas.  
            3. Focus more on customer engagement in weaker regions.  
            """)
    with c2:
        st.subheader("Total Customers By customerType")
        cust_data =oipc.groupby("customer_type")['customer_id'].nunique().reset_index(name='customers')
        fig, ax = plt.subplots(figsize=(7,4))
        ax.pie(cust_data["customers"],labels=cust_data["customer_type"],autopct="%1.1f%%")
        st.pyplot(fig)
        with st.expander("3️⃣ Total Customers by Customer Type - Insights & Recommendations"):
            st.markdown("""
            • Repeat customers contribute around 60%  of total customers.  
            • One-time customers contribute around 27% of customers.  
            • Repeat customers are the main strength of the business.  
            • Very few customers are inactive.  

            Recommendations:
            1. Reward repeat customers with loyalty offers.  
            2. Encourage one-time customers to order again.  
            3. Improve customer engagement activities.  
            """)
        
        
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    c4,c5=st.columns(2)
    with c4:
        st.subheader("💰 Revenue by Customer Type")
        cust_rev = (oipc.groupby("customer_type")["revenue"].sum().reset_index(name='revenue'))
        cust_rev['revenue'] = cust_rev['revenue'].astype(int)
        fig, ax = plt.subplots(figsize=(8,8))
        ax.get_yaxis().get_major_formatter().set_scientific(False)
        sns.barplot(data=cust_rev,x="customer_type",y="revenue",ax=ax,hue="customer_type")
        ax.set_title("Revenue Contribution")
        ax.set_xlabel("Customer Type")
        ax.set_ylabel("Revenue")
        plt.xticks(rotation=15)
        st.pyplot(fig)
        with st.expander("5️⃣ Total Revenue by Customer Type - Insights & Recommendations"):
            st.markdown("""
            • Repeat customers generated around ₹4.3 Million revenue.  
            • One-time customers generated around ₹0.7 Million revenue.  
            • Most revenue comes from repeat customers.  
            • Repeat customers are very important for profitability.  

            Recommendations:
            1. Focus on customer retention strategies.  
            2. Improve customer satisfaction to increase repeat orders.  
            3. Give special offers for repeat purchases.  
            """)
        
    with c5:
        st.subheader("😊 Feedback Sentiment")
        sentiment_data = (oipc["sentiment"].value_counts().reset_index())
        fig, ax = plt.subplots(figsize=(7,4.5))
        ax.pie(sentiment_data["count"],labels=sentiment_data["sentiment"],autopct="%1.1f%%")
        ax.set_title("Sentiment Distribution")
        st.pyplot(fig)
        with st.expander("6️⃣ Feedbacks by Feedback Category - Insights & Recommendations"):
            st.markdown("""
            • Feedback is received from delivery, products, app experience, and customer service.  
            • Delivery and app experience receive slightly more feedback.  
            • Customers are actively sharing their opinions.  
            • Feedback helps identify service problems.  

            Recommendations:
            1. Improve delivery quality and app performance.  
            2. Solve customer complaints quickly.  
            3. Regularly monitor feedback categories.  
            """)
            
    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True) 
    c6,c7=st.columns(2)
    with c6:
        st.subheader("Total Feedbacks by FeedbackCategory")
        se_data = oipc.groupby("feedback_category")['feedback_id'].nunique().reset_index(name='feedbacks')
        fig, ax = plt.subplots(figsize=(7,4))
        ax.pie(se_data["feedbacks"],labels=se_data["feedback_category"],autopct="%1.1f%%")
        st.pyplot(fig)
        with st.expander("6️⃣ Feedbacks by Feedback Category - Insights & Recommendations"):
            st.markdown("""
            • Feedback is received from delivery, products, app experience, and customer service.  
            • Delivery and app experience receive slightly more feedback.  
            • Customers are actively sharing their opinions.  
            • Feedback helps identify service problems.  

            Recommendations:
            1. Improve delivery quality and app performance.  
            2. Solve customer complaints quickly.  
            3. Regularly monitor feedback categories.  
            """)
    with c7:
        st.subheader("Customers by Ratings")
        cus_rev = (oipc.groupby("rating")["feedback_id"].nunique().reset_index(name='feedbacks'))
        cus_rev['rating']=cus_rev['rating'].astype(int) 
        
        fig, ax = plt.subplots(figsize=(8,6))
        sns.barplot(data=cus_rev,x="rating",y="feedbacks",ax=ax,color='green')
        ax.set_xlabel("Ratings")
        ax.set_ylabel("Feedbacks")
        plt.xticks(rotation=15)
        st.pyplot(fig)
        with st.expander("7️⃣ Customers by Rating - Insights & Recommendations"):
            st.markdown("""
            • Rating 4 has the highest number of customers (~1700 feedbacks).  
            • Most customers gave positive ratings.  
            • Very few customers gave low ratings.  
            • Overall customer satisfaction is good.  

            Recommendations:
            1. Maintain current service quality.  
            2. Improve areas causing low ratings.  
            3. Focus on customer support and fast delivery.  
            """)

with tab3:
    st.subheader("📖 KPI Glossary For Marketing & Customer Dashboard")
    
    col1 , col2 = st.columns(2)
    with col1:
        with st.expander("📢 Total Campaigns"):
            st.write("**Meaning:** Total number of marketing campaigns.")
            st.write("**Formula:** COUNT(DISTINCT campaign_id)")
    with col2:
        with st.expander("💰 Campaign Revenue"):
            st.write("**Meaning:** Total revenue generated through marketing campaigns.")
            st.write("**Formula:** SUM(revenue_generated)")

    col1 , col2 = st.columns(2)
    with col1:
        with st.expander("💸 Total Spend"):
            st.write("**Meaning:** Total amount spent on marketing campaigns.")
            st.write("**Formula:** SUM(spend)")
    with col2:
        with st.expander("📈 Campaign Profit"):
            st.write("**Meaning:** Profit generated after deducting campaign spend.")
            st.write("**Formula:** Campaign Revenue - Total Spend")

    col1 , col2 = st.columns(2)
    with col1:
        with st.expander("🎯 Conversion Rate %"):
            st.write("**Meaning:** Percentage of clicks converted into customers.")
            st.write("**Formula:** (Conversions / Clicks) × 100")
    with col2:
        with st.expander("📊 CTR %"):
            st.write("**Meaning:** Percentage of impressions converted into clicks.")
            st.write("**Formula:** (Clicks / Impressions) × 100")

    col1 , col2 = st.columns(2)
    with col1:
        with st.expander("💵 Revenue Per Click"):
            st.write("**Meaning:** Average revenue generated per click.")
            st.write("**Formula:** Campaign Revenue / Total Clicks")
    with col2:
        with st.expander("🏆 Avg ROAS"):
            st.write("**Meaning:** Return generated for every ₹1 spent on ads.")
            st.write("**Formula:** Revenue Generated / Total Spend")

    col1 , col2 = st.columns(2)
    with col1:
        with st.expander("👥 Total Customers"):
            st.write("**Meaning:** Total unique customers.")
            st.write("**Formula:** COUNT(DISTINCT customer_id)")
    with col2:
        with st.expander("💳 Avg Customer Spend"):
            st.write("**Meaning:** Average amount spent by each customer.")
            st.write("**Formula:** Total Revenue / Total Customers")

    col1 , col2 = st.columns(2)
    with col1:
        with st.expander("🔁 Repeat Customers %"):
            st.write("**Meaning:** Percentage of customers purchasing more than once.")
            st.write("**Formula:** (Repeat Customers / Total Customers) × 100")
    with col2:
        with st.expander("🆕 One-Time Customers %"):
            st.write("**Meaning:** Percentage of customers purchasing only once.")
            st.write("**Formula:** (One-Time Customers / Total Customers) × 100")
    
    col1 , col2 = st.columns(2)

    with col1:
        with st.expander("😞 Negative Feedback %"):
            st.write("**Meaning:** Percentage of negative customer feedback received.")
            st.write("**Formula:** (Negative Feedbacks / Total Feedbacks) × 100")
    with col2:
        with st.expander("😐 Neutral Feedback %"):
            st.write("**Meaning:** Percentage of neutral customer feedback received.")
            st.write("**Formula:** (Neutral Feedbacks / Total Feedbacks) × 100")

    col1 , col2 = st.columns(2)
    with col1:
        with st.expander("😊 Positive Feedback %"):
            st.write("**Meaning:** Percentage of positive customer feedback received.")
            st.write("**Formula:** (Positive Feedbacks / Total Feedbacks) × 100")
    with col2:
        with st.expander("📝 Total Feedbacks"):
            st.write("**Meaning:** Total feedback responses received from customers.")
            st.write("**Formula:** COUNT(DISTINCT feedback_id)")

    col1 , col2 = st.columns(2)
    with col1:
        with st.expander("⭐ Average Rating"):
            st.write("**Meaning:** Average customer feedback rating.")
            st.write("**Formula:** AVG(rating)")
    with col2:
        with st.expander("😊 Happy Customers %"):
            st.write("**Meaning:** Percentage of customers with rating 4 and above.")
            st.write("**Formula:** (Happy Customers / Total Feedbacks) × 100")


    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True)

    st.subheader("🎛️ Filters Used In Dashboard")

    st.markdown("""
    ✅ **Year Filter**  
    - Filters dashboard data based on selected year  
    - Helps analyze yearly trends and performance  

    ✅ **Month Filter**  
    - Filters dashboard data based on selected month  
    - Helps analyze monthly campaign and customer trends  

    ✅ **Target Audience Filter**  
    - Filters campaigns by audience category  
    - Helps analyze audience-specific campaign performance  

    ✅ **Campaign Filter**  
    - Filters dashboard by campaign name  
    - Helps analyze individual campaign performance  

    ✅ **Channel Filter**  
    - Filters data based on marketing channels  
    - Helps compare channel-wise revenue and engagement  

    ✅ **Customer Type Filter**  
    - Filters customers by one-time or repeat customers  
    - Helps analyze customer retention patterns  

    ✅ **Day Type Filter**  
    - Filters data into weekday and weekend categories  
    - Helps analyze customer activity trends  

    ✅ **Area Filter**  
    - Filters customers by area/location  
    - Helps analyze area-wise customer distribution  

    ✅ **Sentiment Filter**  
    - Filters feedback by sentiment type  
    - Helps analyze customer satisfaction levels  
    """)


    st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True)

    st.subheader("📊 Analysis Performed In Dashboard")

    st.markdown("""
    📈 **Revenue vs Spend Trend Analysis**  
    - Compares campaign revenue and marketing spend over months  
    - Helps identify profitable periods and spending efficiency  

    🏆 **Top Campaign Revenue Analysis**  
    - Identifies campaigns generating highest revenue  
    - Helps focus on best-performing campaigns  

    📢 **Channel-wise Revenue Analysis**  
    - Analyzes revenue contribution from marketing channels  
    - Helps evaluate channel effectiveness  

    🎯 **Campaign Conversion Rate Analysis**  
    - Tracks campaigns with highest conversion rates  
    - Helps identify successful customer acquisition strategies  

    📊 **CTR Analysis**  
    - Compares click-through rate across campaigns  
    - Helps evaluate ad engagement performance  

    💰 **ROAS Analysis**  
    - Evaluates return generated from advertising spend  
    - Helps measure campaign profitability  

    🔻 **Marketing Funnel Analysis**  
    - Tracks Impressions → Clicks → Conversions flow  
    - Helps identify customer drop-off stages  

    👥 **Customer Trend Analysis**  
    - Tracks customer growth by month and customer type  
    - Helps analyze customer engagement patterns  

    🌍 **Top Areas by Customers Analysis**  
    - Identifies locations with highest customers  
    - Helps target high-performing regions  

    💵 **Revenue by Customer Type Analysis**  
    - Compares revenue contribution from one-time and repeat customers  
    - Helps understand customer value  

    😊 **Feedback Sentiment Analysis**  
    - Analyzes Positive, Neutral, and Negative feedback distribution  
    - Helps evaluate customer satisfaction  

    ⭐ **Customer Rating Analysis**  
    - Tracks customer feedback ratings distribution  
    - Helps monitor service quality and experience  

    📝 **Feedback Category Analysis**  
    - Analyzes feedback categories received from customers  
    - Helps identify operational improvement areas  
    """)