import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- Page Configuration ---
st.set_page_config(
    page_title="Automotive Financial Forecast Dashboard",
    page_icon="🚗",
    layout="wide"
)

# --- Custom Styling (CSS) ---
st.markdown("""
<style>
    .main { background-color: #F0F2F6; }
    h1, h2, h3 { font-weight: 600; }
    .metric-card {
        background-color: #000000;
        border: 1px solid #E6EAF1;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.04);
        height: 100%;
    }
    .stMetric {
        border-bottom: 1px solid #F0F2F6;
        padding-bottom: 10px;
        margin-bottom: 10px;
    }
    .stMetric:last-child { border-bottom: none; margin-bottom: 0; }
</style>
""", unsafe_allow_html=True)

# --- 1. DATA LOADING & VALIDATION ---
@st.cache_data
def load_and_validate_data(file_path, required_columns):
    """
    Loads and rigorously validates a CSV file. If any check fails, it stops the app with a specific error.
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"FATAL ERROR: The file '{file_path}' was not found. Please ensure it is in the same directory as the script.")
        st.stop()

    if df.empty:
        st.error(f"VALIDATION ERROR: The file '{file_path}' is empty. Please check the file content.")
        st.stop()

    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        st.error(f"VALIDATION ERROR: Your file '{file_path}' is missing the required columns: **{', '.join(missing_cols)}**.")
        st.info(f"The columns that were found are: {list(df.columns)}")
        st.stop()

    if df['english_name'].dropna().empty:
        st.error(f"VALIDATION ERROR: The 'english_name' column in '{file_path}' contains no data. The dashboard cannot function without KPI names.")
        st.stop()

    try:
        df['date'] = pd.to_datetime(df['date'])
    except Exception as e:
        st.error(f"VALIDATION ERROR: Could not process the 'date' column in '{file_path}'. Please ensure all dates are in a valid format (e.g., YYYY-MM-DD). Details: {e}")
        st.stop()
        
    return df

# --- 2. DATA PROCESSING ---
def calculate_summary_kpis(df):
    """
    Takes the validated forecast DataFrame and adds summary KPIs (Total Sales, Total Gross Profit).
    This function is case-insensitive.
    """
    df_processed = df.copy()
    unique_kpis = df_processed['english_name'].unique()
    kpi_map = {kpi.lower().strip(): kpi for kpi in unique_kpis}

    # Define the lowercase versions of the KPIs we need to sum
    new_sales_lower = 'new vehicles - retail'
    used_sales_lower = 'used vehicles - retail'
    new_gp_lower = 'gross profit - new vehicles'
    used_gp_lower = 'gross profit - used vehicles'

    # Calculate Total Sales if components exist
    if new_sales_lower in kpi_map and used_sales_lower in kpi_map:
        new_sales_kpi = kpi_map[new_sales_lower]
        used_sales_kpi = kpi_map[used_sales_lower]
        
        new_sales = df_processed[df_processed['english_name'] == new_sales_kpi].set_index('date')
        used_sales = df_processed[df_processed['english_name'] == used_sales_kpi].set_index('date')
        
        total = new_sales.add(used_sales, fill_value=0)[['actual_value', 'predicted_value']].reset_index()
        total['english_name'] = 'Total Vehicle Sales (Verified)'
        df_processed = pd.concat([df_processed, total], ignore_index=True)

    # Calculate Total Gross Profit if components exist
    if new_gp_lower in kpi_map and used_gp_lower in kpi_map:
        new_gp_kpi = kpi_map[new_gp_lower]
        used_gp_kpi = kpi_map[used_gp_lower]

        new_gp = df_processed[df_processed['english_name'] == new_gp_kpi].set_index('date')
        used_gp = df_processed[df_processed['english_name'] == used_gp_kpi].set_index('date')
        
        total = new_gp.add(used_gp, fill_value=0)[['actual_value', 'predicted_value']].reset_index()
        total['english_name'] = 'Total Gross Profit (Verified)'
        df_processed = pd.concat([df_processed, total], ignore_index=True)
        
    return df_processed

# --- 3. UI RENDERING FUNCTIONS ---
def render_header(df):
    """Displays the main 3-month forecast summary."""
    st.header("📈 Key Financial Forecast (Next 3 Months)")
    
    key_kpis_lower = {
        "Total Gross Profit": "total gross profit",
        "Total Sales": "total sales",
        "profit or loss before income tax": "profit or loss before income tax",
    }
    
    available_kpi_map = {kpi.lower().strip(): kpi for kpi in df['english_name'].unique()}
    cols = st.columns(len(key_kpis_lower))

    for i, (title, kpi_lower) in enumerate(key_kpis_lower.items()):
        with cols[i]:
            st.markdown(f"<div class='metric-card'><h4>{title}</h4>", unsafe_allow_html=True)
            if kpi_lower in available_kpi_map:
                kpi_name = available_kpi_map[kpi_lower]
                forecasts = df[(df['english_name'] == kpi_name) & (df['actual_value'].isna())].head(3)
                if not forecasts.empty:
                    for _, row in forecasts.iterrows():
                        month = row['date'].strftime('%B')
                        value = row['predicted_value']
                        display_val = f"${value:,.0f}" if "Gross" in title else f"{value:,.0f}  "
                        st.metric(label=month, value=display_val)
                else:
                    st.info("No forecast")
            else:
                st.warning("KPI not found")
            st.markdown("</div>", unsafe_allow_html=True)

def render_scenario_planner(forecast_df, cleaned_df, driver_kpi, impacted_kpi):
    """Displays the scenario planning tool and results."""
    st.header("⚙️ Scenario Planning")
    
    driver_data = forecast_df[forecast_df['english_name'] == driver_kpi]
    future_dates = driver_data[driver_data['actual_value'].isna()]['date']
    
    if future_dates.empty:
        st.warning(f"The selected Driver KPI ('{driver_kpi}') has no future forecast data available for planning.")
        return

    # --- Sidebar controls for this section ---
    selected_month = st.sidebar.selectbox("Select Month for Scenario:", future_dates, format_func=lambda x: x.strftime('%B %Y'))
    change_percentage = st.sidebar.slider("Percentage Change (%):", -50, 50, 10) / 100.0
    
    # --- Calculations ---
    correlation_matrix = cleaned_df.pivot_table(index='date', columns='english_name', values='monthly_value').fillna(0).corr()
    correlation = correlation_matrix.loc[driver_kpi, impacted_kpi] if driver_kpi in correlation_matrix and impacted_kpi in correlation_matrix else 0.0

    original_driver_pred = driver_data.loc[driver_data['date'] == selected_month, 'predicted_value'].iloc[0]
    original_impacted_pred = forecast_df.loc[(forecast_df['english_name'] == impacted_kpi) & (forecast_df['date'] == selected_month), 'predicted_value'].iloc[0]

    adjusted_driver_pred = original_driver_pred * (1 + change_percentage)
    adjusted_impacted_pred = original_impacted_pred * (1 + (change_percentage * correlation))

    # --- Display Results ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='metric-card'><h4>Driver: {driver_kpi.split(' (')[0]}</h4>", unsafe_allow_html=True)
        st.metric(f"Original Forecast ({selected_month.strftime('%B')})", f"{original_driver_pred:,.2f}")
        st.metric(f"Adjusted by {change_percentage:.0%}", f"{adjusted_driver_pred:,.2f}", f"{(adjusted_driver_pred - original_driver_pred):,.2f}")
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><h4>Impact on: {impacted_kpi.split(' (')[0]}</h4>", unsafe_allow_html=True)
        st.metric("Original Forecast", f"{original_impacted_pred:,.2f}")
        st.metric("Potential New Value", f"{adjusted_impacted_pred:,.2f}", f"{(adjusted_impacted_pred - original_impacted_pred):,.2f}")
        st.markdown("</div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='metric-card'><h4>Relationship</h4>", unsafe_allow_html=True)
        st.metric("Historical Correlation", f"{correlation:.2f}")
        st.caption(f"A value of {correlation:.2f} suggests a {correlation*100:.0f}% correlation in historical movements.")
        st.markdown("</div>", unsafe_allow_html=True)

def render_kpi_deep_dive(df, selected_kpi):
    """Displays the detailed historical and forecast charts."""
    st.header(f"📊 KPI Deep Dive: {selected_kpi}")
    
    kpi_data = df[df['english_name'] == selected_kpi]
    
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=kpi_data['date'], y=kpi_data.get('yhat_upper'), fill=None, mode='lines', line_color='rgba(0,104,201,0.2)', showlegend=False))
        fig.add_trace(go.Scatter(x=kpi_data['date'], y=kpi_data.get('yhat_lower'), fill='tonexty', mode='lines', line_color='rgba(0,104,201,0.2)', name='Confidence'))
        fig.add_trace(go.Scatter(x=kpi_data['date'], y=kpi_data['actual_value'], mode='lines+markers', name='Historical', line=dict(color='#0068C9', width=3)))
        fig.add_trace(go.Scatter(x=kpi_data['date'], y=kpi_data['predicted_value'], mode='lines', name='Forecast', line=dict(color='#D80032', dash='dot', width=2.5)))
        fig.update_layout(title="Historical vs. Forecast Performance", legend=dict(x=0.01, y=0.99))
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("3-Month Forecast")
        forecasts = kpi_data[kpi_data['actual_value'].isna()].head(3)
        if not forecasts.empty:
            bar_fig = go.Figure()
            bar_fig.add_trace(go.Bar(x=forecasts['date'].dt.strftime('%B'), y=forecasts['predicted_value'], text=forecasts['predicted_value'].apply(lambda x: f'{x:,.0f}')))
            bar_fig.update_layout(title_text="Next 3 Months", margin=dict(t=40))
            st.plotly_chart(bar_fig, use_container_width=True)

# --- 4. MAIN APP ---
def main():
    """Main function to run the Streamlit app."""
    # --- Load and Validate Data ---
    forecast_df_raw = load_and_validate_data('forecast_master_data.csv', ['date', 'english_name', 'actual_value', 'predicted_value'])
    cleaned_df_raw = load_and_validate_data('cleaned_master_data.csv', ['date', 'english_name', 'monthly_value'])
    
    # --- Process Data ---
    forecast_df = calculate_summary_kpis(forecast_df_raw)
    cleaned_df = cleaned_df_raw.copy()
    kpi_list = sorted(forecast_df['english_name'].unique())

    # --- Sidebar Controls ---
    st.sidebar.title("Controls & Filters")
    default_driver = 'Total Vehicle Sales (Verified)' if 'Total Vehicle Sales (Verified)' in kpi_list else kpi_list[0]
    default_impacted = 'Total Gross Profit (Verified)' if 'Total Gross Profit (Verified)' in kpi_list else (kpi_list[1] if len(kpi_list) > 1 else kpi_list[0])
    
    st.sidebar.header("KPI Deep Dive")
    selected_kpi = st.sidebar.selectbox("Choose a KPI to analyze:", kpi_list, index=kpi_list.index(default_driver))

    st.sidebar.header("Scenario Planning")
    driver_kpi = st.sidebar.selectbox("Driver KPI:", kpi_list, index=kpi_list.index(default_driver))
    impacted_kpi = st.sidebar.selectbox("Impacted KPI:", kpi_list, index=kpi_list.index(default_impacted))
    
    # --- Render Page Sections ---
    render_header(forecast_df)
    st.markdown("<hr>", unsafe_allow_html=True)
    render_scenario_planner(forecast_df, cleaned_df, driver_kpi, impacted_kpi)
    st.markdown("<hr>", unsafe_allow_html=True)
    render_kpi_deep_dive(forecast_df, selected_kpi)

if __name__ == "__main__":
    main()