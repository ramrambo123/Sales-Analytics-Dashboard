import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os
import warnings

# Try to import statsmodels for decomposition
try:
    from statsmodels.tsa.seasonal import seasonal_decompose
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False

warnings.filterwarnings('ignore')

# File path
DATA_PATH = r'D:\Dashboard-main\data\Flipkart_Proxy_Transactions_20000.xlsx'

# Page config
st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #1f77b4;
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    div[data-testid="metric-container"] {
        background-color: #f0f2f6;
        border: 1px solid #d6d6d6;
        padding: 10px;
        border-radius: 10px;
        color: black;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load Sales dataset"""
    if not os.path.exists(DATA_PATH):
        st.error(f"File not found at: {DATA_PATH}")
        return pd.DataFrame()

    try:
        df = pd.read_excel(DATA_PATH)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return pd.DataFrame()
    
    # Normalize column names
    df.columns = df.columns.str.strip()
    
    # Map specific columns to standard names
    column_mapping = {
        'Final Sales Amount (INR)': 'Sales Amount',
        'Sales': 'Sales Amount',
        'Profit': 'Profit (INR)',
        'Unit Price': 'Unit Price (INR)'
    }
    
    # Apply mapping
    df.rename(columns=column_mapping, inplace=True)
    
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    
    # Add Time-Series specific columns
    df['Month'] = df['Order Date'].dt.month_name()
    df['Year'] = df['Order Date'].dt.year
    df['YearMonth'] = df['Order Date'].dt.to_period('M').astype(str)
    df['Week'] = df['Order Date'].dt.isocalendar().week
    df['DayOfWeek'] = df['Order Date'].dt.day_name()
    df['Quarter'] = df['Order Date'].dt.to_period('Q').astype(str)
    
    return df

def analyze_profitability(df):
    """Analyze profitability metrics"""
    total_profit = df['Profit (INR)'].sum()
    avg_profit = df['Profit (INR)'].mean()
    profit_margin = (total_profit / df['Sales Amount'].sum()) * 100 if df['Sales Amount'].sum() > 0 else 0
    
    category_profit = df.groupby('Category').agg({
        'Profit (INR)': 'sum',
        'Sales Amount': 'sum',
        'Quantity': 'sum'
    }).reset_index()
    category_profit['Margin%'] = (category_profit['Profit (INR)'] / category_profit['Sales Amount'] * 100).round(2)
    
    return total_profit, avg_profit, profit_margin, category_profit

def calculate_growth_rate(current, previous):
    if previous == 0: return 0
    return ((current - previous) / abs(previous)) * 100

def calculate_abc_analysis(data):
    """ABC Classification with strict Recommendation column generation"""
    product_metrics = data.groupby('Product Name').agg({
        'Sales Amount': 'sum',
        'Order Date': 'count', 
        'Profit (INR)': 'mean'
    }).reset_index()
    product_metrics.columns = ['Product', 'Total_Sales', 'Frequency', 'Avg_Profit']
    product_metrics = product_metrics.sort_values('Total_Sales', ascending=False)
    
    product_metrics['Cumulative_Sales'] = product_metrics['Total_Sales'].cumsum()
    product_metrics['Total_Revenue_Sum'] = product_metrics['Total_Sales'].sum()
    product_metrics['Cumulative_Pct'] = (product_metrics['Cumulative_Sales'] / product_metrics['Total_Revenue_Sum']) * 100
    
    def categorize_abc(pct):
        if pct <= 80: return 'A'
        elif pct <= 95: return 'B'
        else: return 'C'
    
    product_metrics['Class'] = product_metrics['Cumulative_Pct'].apply(categorize_abc)
    
    # Explicitly create Recommendation column
    conditions = [
        product_metrics['Class'] == 'A',
        product_metrics['Class'] == 'B',
        product_metrics['Class'] == 'C'
    ]
    choices = [
        "🔥 Restock Immediately",
        "✅ Maintain Stock",
        "📉 Monitor / Clearance"
    ]
    product_metrics['Recommendation'] = np.select(conditions, choices, default="Unknown")
    
    return product_metrics

def analyze_operations(df):
    """Analyze Order Status for Operations View"""
    status_counts = df['Order Status'].value_counts()
    total_orders = len(df)
    
    # Safe get in case status doesn't exist
    delivered = status_counts.get('Delivered', 0)
    returned = status_counts.get('Returned', 0)
    cancelled = status_counts.get('Cancelled', 0)
    
    fulfillment_rate = (delivered / total_orders * 100) if total_orders > 0 else 0
    return_rate = (returned / total_orders * 100) if total_orders > 0 else 0
    cancellation_rate = (cancelled / total_orders * 100) if total_orders > 0 else 0
    
    return status_counts, fulfillment_rate, return_rate, cancellation_rate

# Load data
df = load_data()

if df.empty:
    st.warning("Data not loaded. Please check the file path.")
else:
    # ============ SIDEBAR FILTERS ============
    st.sidebar.title("🔍 Global Filters")

    col1, col2 = st.sidebar.columns(2)
    with col1:
        min_d = df['Order Date'].min().date()
        start_date = st.date_input("Start Date", min_d)
    with col2:
        max_d = df['Order Date'].max().date()
        end_date = st.date_input("End Date", max_d)

    date_filtered_df = df[(df['Order Date'].dt.date >= start_date) & (df['Order Date'].dt.date <= end_date)]

    all_states = sorted(df['State'].unique())
    selected_states = st.sidebar.multiselect("Select States", all_states, default=all_states[:5] if len(all_states) >= 5 else all_states)

    available_cities = df[df['State'].isin(selected_states)]['City'].unique()
    selected_cities = st.sidebar.multiselect("Select Cities", sorted(available_cities), default=sorted(available_cities)[:5] if len(available_cities) >= 5 else sorted(available_cities))

    all_categories = sorted(df['Category'].unique())
    selected_categories = st.sidebar.multiselect("Select Categories", all_categories, default=all_categories)

    filtered_df = date_filtered_df[
        (date_filtered_df['State'].isin(selected_states)) &
        (date_filtered_df['City'].isin(selected_cities)) & 
        (date_filtered_df['Category'].isin(selected_categories))
    ]

    st.sidebar.markdown("---")
    st.sidebar.info(f"📊 **Records:** {len(filtered_df):,}")

    # ============ MAIN DASHBOARD ============
    st.title("📊 Sales Analytics Dashboard")
    st.markdown("Comprehensive analysis of Sales, Profit, Time Series trends, and Deep Dives.")

    if len(filtered_df) == 0:
        st.warning("No data available for the selected filters.")
    else:
        # Create tabs
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
            ["📈 Overview", "🎯 Scenario Calculator", "💰 Profitability", "💡 Insights Deep Dive", 
             "⏰ Advanced Time-Series", "📦 Demand (ABC)", "🚚 Operations"]
        )

        # ============ TAB 1: OVERVIEW ============
        with tab1:
            st.subheader("High-Level Overview")
            
            # KPI Cards
            c1, c2, c3, c4, c5 = st.columns(5)
            total_sales = filtered_df['Sales Amount'].sum()
            total_qty = filtered_df['Quantity'].sum()
            total_profit = filtered_df['Profit (INR)'].sum()
            
            with c1: st.metric("Total Sales", f"₹{total_sales:,.0f}", delta=f"{calculate_growth_rate(total_sales, df['Sales Amount'].sum()):.1f}%")
            with c2: st.metric("Total Quantity", f"{total_qty:,}", delta=f"{calculate_growth_rate(total_qty, df['Quantity'].sum()):.1f}%")
            with c3: st.metric("Total Profit", f"₹{total_profit:,.0f}", delta=f"{calculate_growth_rate(total_profit, df['Profit (INR)'].sum()):.1f}%")
            with c4: st.metric("Avg Order Value", f"₹{filtered_df['Sales Amount'].mean():,.0f}")
            with c5: st.metric("Unique Customers", f"{filtered_df['Order ID'].nunique():,}")
            
            st.markdown("---")
            
            # Row 1
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Daily Sales Trend")
                daily = filtered_df.groupby(filtered_df['Order Date'].dt.date)['Sales Amount'].sum().reset_index()
                fig_trend = px.line(daily, x='Order Date', y='Sales Amount', markers=True, line_shape='spline')
                fig_trend.update_traces(line_color='#1f77b4')
                st.plotly_chart(fig_trend, use_container_width=True)
            
            with col2:
                st.subheader("Sales by State Map (Proxy)")
                state_sales = filtered_df.groupby('State')['Sales Amount'].sum().reset_index().sort_values('Sales Amount', ascending=False)
                fig_map = px.bar(state_sales, x='Sales Amount', y='State', orientation='h', color='Sales Amount', 
                                 title="Top Performing States", color_continuous_scale='Viridis')
                st.plotly_chart(fig_map, use_container_width=True)

            # Row 2
            col3, col4, col5 = st.columns(3)
            with col3:
                st.subheader("Category Mix")
                fig_pie = px.pie(filtered_df, values='Sales Amount', names='Category', hole=0.3)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col4:
                st.subheader("Payment Methods")
                fig_donut = px.pie(filtered_df, values='Sales Amount', names='Payment Method', hole=0.6)
                st.plotly_chart(fig_donut, use_container_width=True)
                
            with col5:
                st.subheader("Top 10 Products")
                top_prods = filtered_df.groupby('Product Name')['Sales Amount'].sum().nlargest(10).reset_index()
                fig_bar = px.bar(top_prods, x='Sales Amount', y='Product Name', orientation='h')
                fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_bar, use_container_width=True)

        # ============ TAB 2: SCENARIO PLANNER (SIMPLIFIED) ============
        with tab2:
            st.subheader("🎯 Simple Growth Calculator")
            st.markdown("Estimate your future revenue by adjusting Volume and Price expectations.")
            
            c1, c2 = st.columns([1, 2])
            
            with c1:
                st.markdown("### 🔢 Inputs")
                current_revenue = filtered_df['Sales Amount'].sum()
                
                vol_change = st.number_input("Expected Volume Growth (%)", min_value=-50.0, max_value=200.0, value=10.0, step=1.0)
                price_change = st.number_input("Expected Price Increase (%)", min_value=-50.0, max_value=200.0, value=5.0, step=1.0)
                
                st.info("Positive values mean growth/increase. Negative values mean decline/decrease.")
            
            with c2:
                st.markdown("### 📊 Projection")
                
                # Calculation: New Revenue = Current * (1 + Vol%) * (1 + Price%)
                projected_revenue = current_revenue * (1 + vol_change/100) * (1 + price_change/100)
                difference = projected_revenue - current_revenue
                
                # Display Metrics
                m1, m2 = st.columns(2)
                with m1:
                    st.metric("Current Revenue", f"₹{current_revenue:,.0f}")
                with m2:
                    st.metric("Projected Revenue", f"₹{projected_revenue:,.0f}", delta=f"₹{difference:,.0f}")
                
                # Simple Visual
                comp_df = pd.DataFrame({
                    'Scenario': ['Current', 'Projected'],
                    'Revenue': [current_revenue, projected_revenue],
                    'Color': ['Current', 'Projected']
                })
                
                fig_comp = px.bar(comp_df, x='Revenue', y='Scenario', orientation='h', color='Color', 
                                  text_auto='.2s', title="Revenue Comparison",
                                  color_discrete_map={'Current': 'gray', 'Projected': '#2ca02c'})
                st.plotly_chart(fig_comp, use_container_width=True)
                
                if difference > 0:
                    st.success(f"🎉 Great! You are projected to make **₹{difference:,.0f}** more.")
                else:
                    st.error(f"⚠️ Warning: You are projected to make **₹{abs(difference):,.0f}** less.")

        # ============ TAB 3: PROFITABILITY ============
        with tab3:
            st.subheader("Profitability Analysis")
            tot_p, avg_p, p_margin, cat_p = analyze_profitability(filtered_df)
            
            # Metrics
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Profit Margin", f"{p_margin:.2f}%")
            with c2: st.metric("Total Profit", f"₹{tot_p:,.0f}")
            with c3: st.metric("Avg Profit/Order", f"₹{avg_p:,.0f}")
            
            # Row 1
            col1, col2 = st.columns(2)
            with col1:
                fig_bubble = px.scatter(cat_p, x='Sales Amount', y='Profit (INR)', size='Quantity', color='Category',
                                        title="Category Profitability Bubble Chart (Size=Qty)", hover_name='Category')
                st.plotly_chart(fig_bubble, use_container_width=True)
            
            with col2:
                city_prof = filtered_df.groupby('City')['Profit (INR)'].sum().nlargest(10).reset_index()
                fig_waterfall = go.Figure(go.Waterfall(
                    name = "20", orientation = "v",
                    measure = ["relative"] * len(city_prof),
                    x = city_prof['City'],
                    y = city_prof['Profit (INR)'],
                    connector = {"line":{"color":"rgb(63, 63, 63)"}},
                ))
                fig_waterfall.update_layout(title = "Top 10 Cities Contribution to Profit")
                st.plotly_chart(fig_waterfall, use_container_width=True)
            
            # Row 2
            col3, col4 = st.columns(2)
            with col3:
                # Profit over time
                prof_time = filtered_df.groupby('YearMonth')['Profit (INR)'].sum().reset_index()
                fig_prof_line = px.area(prof_time, x='YearMonth', y='Profit (INR)', title="Monthly Profit Trend")
                st.plotly_chart(fig_prof_line, use_container_width=True)
            
            with col4:
                fig_box = px.box(filtered_df, x='Category', y='Profit (INR)', color='Category', title="Profit Distribution Consistency")
                st.plotly_chart(fig_box, use_container_width=True)

        # ============ TAB 4: DEEP DIVE (REDESIGNED & SIMPLIFIED) ============
        with tab4:
            st.subheader("💡 Insights Deep Dive")
            st.markdown("Simple answers to complex questions about your business.")
            
            # Question 1: Does Discounting Hurt Profit?
            st.markdown("### 1. Does giving higher discounts hurt our profit?")
            
            # Bin the discounts
            filtered_df['Discount_Range'] = pd.cut(filtered_df['Discount'], bins=[-0.01, 0.10, 0.20, 0.30, 0.50, 1.0], 
                                                 labels=['0-10%', '10-20%', '20-30%', '30-50%', '50%+'])
            
            disc_impact = filtered_df.groupby('Discount_Range', observed=True)['Profit (INR)'].mean().reset_index()
            
            fig_disc = px.bar(disc_impact, x='Discount_Range', y='Profit (INR)', 
                              color='Profit (INR)', title="Average Profit per Order by Discount Level",
                              labels={'Profit (INR)': 'Avg Profit (₹)'}, color_continuous_scale='RdYlGn')
            st.plotly_chart(fig_disc, use_container_width=True)
            
            st.info("💡 **Insight:** Use this chart to find the 'Sweet Spot' where you give enough discount to sell, but still make a good profit.")

            st.markdown("---")
            
            # Question 2: What is the most common order size?
            st.markdown("### 2. How much do customers typically spend?")
            
            fig_hist = px.histogram(filtered_df, x='Sales Amount', nbins=30, 
                                    title="Distribution of Order Values", 
                                    color_discrete_sequence=['#1f77b4'])
            fig_hist.update_layout(xaxis_title="Order Value (₹)", yaxis_title="Number of Orders")
            st.plotly_chart(fig_hist, use_container_width=True)
            
            st.info("💡 **Insight:** Most of your orders fall in the taller bars. Marketing to this price point is usually most effective.")

            st.markdown("---")

            # Question 3: Weekday vs Weekend
            st.markdown("### 3. Do we sell more on Weekends?")
            
            filtered_df['Is_Weekend'] = filtered_df['DayOfWeek'].isin(['Saturday', 'Sunday'])
            filtered_df['Day_Type'] = filtered_df['Is_Weekend'].map({True: 'Weekend', False: 'Weekday'})
            
            weekend_perf = filtered_df.groupby('Day_Type')['Sales Amount'].mean().reset_index()
            
            fig_week = px.bar(weekend_perf, x='Sales Amount', y='Day_Type', orientation='h',
                              title="Average Daily Sales: Weekday vs Weekend",
                              color='Day_Type', text_auto='.0f')
            st.plotly_chart(fig_week, use_container_width=True)

        # ============ TAB 5: TIME-SERIES (ADVANCED) ============
        with tab5:
            st.subheader("⏰ Advanced Time-Series Analysis")
            
            # 1. Monthly & Weekly Trends
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### Monthly Performance")
                monthly_agg = filtered_df.groupby('YearMonth')['Sales Amount'].sum().reset_index()
                fig_m = px.bar(monthly_agg, x='YearMonth', y='Sales Amount', color='Sales Amount', 
                               title="Total Sales by Month")
                st.plotly_chart(fig_m, use_container_width=True)
            
            with c2:
                st.markdown("### Weekly Performance")
                weekly_agg = filtered_df.groupby('Week')['Sales Amount'].sum().reset_index()
                fig_w = px.line(weekly_agg, x='Week', y='Sales Amount', markers=True, 
                                title="Sales Trend by Week Number")
                st.plotly_chart(fig_w, use_container_width=True)

            # 2. Seasonality & Decomposition
            c3, c4 = st.columns(2)
            with c3:
                st.markdown("### Seasonal Heatmap (Day vs Month)")
                season_pivot = filtered_df.pivot_table(index='DayOfWeek', columns='Month', values='Sales Amount', aggfunc='mean')
                # Order days and months
                days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                months_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
                season_pivot = season_pivot.reindex(index=days_order, columns=months_order)
                
                fig_season = px.imshow(season_pivot, color_continuous_scale='RdBu_r', title="Heatmap: Best Selling Times")
                st.plotly_chart(fig_season, use_container_width=True)
            
            with c4:
                st.markdown("### Time Series Decomposition")
                daily_ts = filtered_df.groupby('Order Date')['Sales Amount'].sum().asfreq('D').fillna(0)
                if len(daily_ts) > 30 and STATSMODELS_AVAILABLE:
                    decomp = seasonal_decompose(daily_ts, model='additive', period=30)
                    fig_decomp = make_subplots(rows=3, cols=1, subplot_titles=("Trend", "Seasonal", "Residual"))
                    fig_decomp.add_trace(go.Scatter(x=decomp.trend.index, y=decomp.trend, name='Trend'), row=1, col=1)
                    fig_decomp.add_trace(go.Scatter(x=decomp.seasonal.index, y=decomp.seasonal, name='Seasonal'), row=2, col=1)
                    fig_decomp.add_trace(go.Scatter(x=decomp.resid.index, y=decomp.resid, name='Residual'), row=3, col=1)
                    fig_decomp.update_layout(height=600, showlegend=False)
                    st.plotly_chart(fig_decomp, use_container_width=True)
                else:
                    st.info("Insufficient data or statsmodels library missing for decomposition.")

        # ============ TAB 6: DEMAND (PARETO) ============
        with tab6:
            st.subheader("📦 Demand & ABC Analysis")
            
            # Re-calculate with fixed function
            abc_df = calculate_abc_analysis(filtered_df)
            
            c1, c2 = st.columns([2, 1])
            with c1:
                # Dual Axis Pareto
                pareto_view = abc_df.head(50)
                fig_pareto = make_subplots(specs=[[{"secondary_y": True}]])
                fig_pareto.add_trace(go.Bar(x=pareto_view['Product'], y=pareto_view['Total_Sales'], name="Sales"), secondary_y=False)
                fig_pareto.add_trace(go.Scatter(x=pareto_view['Product'], y=pareto_view['Cumulative_Pct'], name="Cum %", mode="lines+markers", line=dict(color='red')), secondary_y=True)
                fig_pareto.update_layout(title="Pareto Analysis (80/20 Rule) - Top 50 Products")
                st.plotly_chart(fig_pareto, use_container_width=True)
                
                # Inventory Velocity Simulation
                st.subheader("Inventory Turnover Simulation")
                # Simulate inventory: Assume avg stock is 20% of sales volume
                abc_df['Est_Inventory'] = abc_df['Total_Sales'] * 0.2
                abc_df['Turnover_Ratio'] = abc_df['Total_Sales'] / abc_df['Est_Inventory']
                
                # Check if data exists before plotting
                if not abc_df.empty:
                    fig_turn = px.histogram(abc_df, x='Turnover_Ratio', color='Class', title="Inventory Turnover Distribution by Class")
                    st.plotly_chart(fig_turn, use_container_width=True)
                else:
                    st.warning("Not enough data for Inventory Simulation")

            with c2:
                # Matrix
                fig_mat = px.scatter(abc_df, x='Frequency', y='Total_Sales', color='Class', log_x=True, log_y=True,
                                     title="Value vs Frequency Matrix", hover_name='Product')
                st.plotly_chart(fig_mat, use_container_width=True)
                
                # Ensure columns exist before displaying
                cols_to_show = ['Product', 'Class', 'Recommendation']
                if all(col in abc_df.columns for col in cols_to_show):
                    st.dataframe(abc_df[cols_to_show].head(15), use_container_width=True)
                else:
                    st.error("Error generating recommendations.")

        # ============ TAB 7: OPERATIONS ============
        with tab7:
            st.subheader("🚚 Operations & Fulfillment Analysis")
            
            # 1. Analyze Status
            status_counts, fill_rate, ret_rate, can_rate = analyze_operations(filtered_df)
            
            # KPIs
            k1, k2, k3 = st.columns(3)
            with k1: st.metric("Fulfillment Rate", f"{fill_rate:.1f}%", help="% of orders Delivered")
            with k2: st.metric("Return Rate", f"{ret_rate:.1f}%", help="% of orders Returned")
            with k3: st.metric("Cancellation Rate", f"{can_rate:.1f}%", help="% of orders Cancelled")
            
            st.markdown("---")
            
            # 2. Charts
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### Order Status Distribution")
                fig_status = px.pie(values=status_counts.values, names=status_counts.index, hole=0.5, 
                                    color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig_status, use_container_width=True)
                
            with c2:
                st.markdown("### Returns by Category")
                # Filter for returns
                returns_df = filtered_df[filtered_df['Order Status'] == 'Returned']
                if not returns_df.empty:
                    ret_cat = returns_df['Category'].value_counts().reset_index()
                    ret_cat.columns = ['Category', 'Count']
                    fig_ret_cat = px.bar(ret_cat, x='Category', y='Count', color='Count', title="Which Category has most returns?")
                    st.plotly_chart(fig_ret_cat, use_container_width=True)
                else:
                    st.info("No return data available for the selected period.")

            # 3. Top Returned Products (Specific Request)
            st.markdown("### ⚠️ Top Returned Products")
            if not returns_df.empty:
                top_ret_prods = returns_df['Product Name'].value_counts().nlargest(10).reset_index()
                top_ret_prods.columns = ['Product Name', 'Return Count']
                
                fig_ret_prod = px.bar(top_ret_prods, x='Return Count', y='Product Name', orientation='h',
                                      color='Return Count', color_continuous_scale='Reds',
                                      title="Products with Highest Returns")
                fig_ret_prod.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_ret_prod, use_container_width=True)
            else:
                 st.info("No returns found to analyze products.")

    # Footer
    st.divider()
    st.markdown("<div style='text-align: center; color: gray;'>Sales Analytics Dashboard | Simplified & Enhanced</div>", unsafe_allow_html=True)