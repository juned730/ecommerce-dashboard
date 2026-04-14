import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Title
st.title("E-Commerce Dashboard 📊")
st.set_page_config(layout="wide")
st.markdown("### Interactive E-Commerce Insights Dashboard")

# Load datasets
orders = pd.read_csv("Data/olist_orders_dataset.csv")
payments = pd.read_csv("Data/olist_order_payments_dataset.csv")
order_items = pd.read_csv("Data/olist_order_items_dataset.csv")
products = pd.read_csv("Data/olist_products_dataset.csv")
category = pd.read_csv("Data/product_category_name_translation.csv")

# Data Cleaning
# Filter delivered orders
orders = orders[
    (orders['order_status'] == 'delivered') &
    (orders['order_delivered_customer_date'].notnull())
]

# Convert dates
orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
orders['order_delivered_customer_date'] = pd.to_datetime(orders['order_delivered_customer_date'])
orders['order_estimated_delivery_date'] = pd.to_datetime(orders['order_estimated_delivery_date'])

# Features
orders['month'] = orders['order_purchase_timestamp'].dt.month
orders['year'] = orders['order_purchase_timestamp'].dt.year

# Delivery delay
orders['delivery_delay'] = (
    orders['order_delivered_customer_date'] - 
    orders['order_estimated_delivery_date']
).dt.days

orders['delivery_status'] = orders['delivery_delay'].apply(
    lambda x: 'On Time' if x <= 0 else 'Late'
)

# 🎛️ Sidebar Filters
st.sidebar.header("Filters")

# Year filter (latest first)
selected_year = st.sidebar.selectbox(
    "Select Year",
    sorted(orders['year'].unique(), reverse=True)
)

# Filter data by year
filtered_orders = orders[orders['year'] == selected_year]

# Month filter (NEW)
selected_month = st.sidebar.multiselect(
    "Select Month",
    sorted(filtered_orders['month'].unique()),
    default=sorted(filtered_orders['month'].unique())
)

# Apply month filter
filtered_orders = filtered_orders[
    filtered_orders['month'].isin(selected_month)
]

if filtered_orders.shape[0] < 500:
    st.warning("Limited data for selected filters. Insights may not be reliable.")

# 📊 KPIs
st.subheader("Key Metrics")

total_orders = filtered_orders.shape[0]

revenue_df = filtered_orders.merge(payments, on='order_id')
total_revenue = revenue_df['payment_value'].sum()

avg_delivery = filtered_orders['delivery_delay'].mean()

col1, col2, col3 = st.columns(3)

col1.metric("Total Orders", f"{total_orders:,}")
col2.metric("Total Revenue", f"${total_revenue:,.0f}")
col3.metric("Avg Delivery Delay (Days)", f"{avg_delivery:.2f}")

# Revenue Analysis
st.header("Revenue Analysis 💰")

monthly_revenue = revenue_df.groupby(['month'])['payment_value'].sum().reset_index()

fig, ax = plt.subplots()

ax.plot(monthly_revenue['month'], monthly_revenue['payment_value'], marker='o')

ax.set_title("Monthly Revenue Trend", fontsize=14)
ax.set_xlabel("Month")
ax.set_ylabel("Revenue")
ax.grid(True, linestyle='--', alpha=0.5)

# Delivery Performance
st.header("Delivery Performance ⏱️")

fig2, ax2 = plt.subplots()
sns.countplot(data=filtered_orders, x='delivery_status', ax=ax2)

col1, col2 = st.columns(2)

with col1:
    st.pyplot(fig)

with col2:
    st.pyplot(fig2)
    
delivery_counts = filtered_orders['delivery_status'].value_counts(normalize=True) * 100

st.write("### Delivery Performance (%)")
st.write(delivery_counts.round(2))

# Product Analysis
st.header("Top Categories 🛒")

product_df = order_items.merge(products, on='product_id')
product_df = product_df.merge(category, on='product_category_name', how='left')

product_df = product_df[product_df['order_id'].isin(filtered_orders['order_id'])]

top_categories = product_df['product_category_name_english'].value_counts().head(10)

fig3, ax3 = plt.subplots()
top_categories.sort_values().plot(kind='barh', ax=ax3)

st.pyplot(fig3)

st.header("📌 Key Insights")

st.write(f"""
- 📈 Total Revenue in {selected_year}: ${total_revenue:,.0f}
- 🚚 Average Delivery Delay: {avg_delivery:.2f} days
- ⏱️ Most orders delivered on time
- 🛒 Top Category: {top_categories.index[0]}
""")