# enhanced_streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import altair as alt
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Cancer Analytics Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced dark theme
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
    }
    
    .metric-card {
        background: linear-gradient(45deg, #1f1f2e, #2d2d3a);
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #ff00ff;
        box-shadow: 0 0 20px rgba(255, 0, 255, 0.3);
        margin: 10px 0;
    }
    
    .trend-up {
        color: #00ff88 !important;
        font-weight: bold;
    }
    
    .trend-down {
        color: #ff4444 !important;
        font-weight: bold;
    }
    
    .trend-neutral {
        color: #ffaa00 !important;
        font-weight: bold;
    }
    
    .stSelectbox > div > div {
        background-color: #2d2d3a;
        border: 1px solid #ff00ff;
    }
    
    .summary-box {
        background: rgba(255, 0, 255, 0.1);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #ff00ff;
        margin: 10px 0;
    }
    
    .export-button {
        background: linear-gradient(45deg, #ff00ff, #aa00aa);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# Constants
MAGENTA = "#ff00ff"
GREEN = "#00ff88"
RED = "#ff4444"
YELLOW = "#ffaa00"

# File paths
AFFECTED_PATH = "CANCER (2018-2024).csv"
MORTALITY_PATH = "CANCER MORTALITY (2018-2022).csv"

# Data loading function with enhanced error handling
@st.cache_data
def load_data():
    """Load and process cancer data with comprehensive error handling"""
    try:
        # Load datasets
        df_aff = pd.read_csv(AFFECTED_PATH)
        df_mort = pd.read_csv(MORTALITY_PATH)
        
        # # Debug: Show first few rows and column names
        # st.sidebar.write("**Debug Info:**")
        # st.sidebar.write("Affected CSV columns:", df_aff.columns.tolist())
        # st.sidebar.write("Mortality CSV columns:", df_mort.columns.tolist())
        # st.sidebar.write("Affected CSV shape:", df_aff.shape)
        # st.sidebar.write("First few rows of Affected CSV:")
        # st.sidebar.dataframe(df_aff.head(3))
        
        # Clean column names
        df_aff.columns = [c.strip() for c in df_aff.columns]
        df_mort.columns = [c.strip() for c in df_mort.columns]
        
        # Auto-detect data structure
        # Look for year columns (should contain only numeric values 2018-2024)
        year_col_aff = None
        year_col_mort = None
        
        # Find year columns
        for col in df_aff.columns:
            if df_aff[col].dtype in ['int64', 'float64'] or str(df_aff[col].iloc[0]).isdigit():
                try:
                    years = pd.to_numeric(df_aff[col], errors='coerce')
                    if years.notna().any() and years.min() >= 2015 and years.max() <= 2025:
                        year_col_aff = col
                        break
                except:
                    continue
        
        for col in df_mort.columns:
            if df_mort[col].dtype in ['int64', 'float64'] or str(df_mort[col].iloc[0]).isdigit():
                try:
                    years = pd.to_numeric(df_mort[col], errors='coerce')
                    if years.notna().any() and years.min() >= 2015 and years.max() <= 2025:
                        year_col_mort = col
                        break
                except:
                    continue
        
        # If no year column found, check if data is in wide format (years as columns)
        if year_col_aff is None:
            # Check if columns contain years (like '2018', '2019', etc.)
            year_columns = [col for col in df_aff.columns if str(col).isdigit() and 2015 <= int(col) <= 2025]
            if year_columns:
                # Reshape from wide to long format
                id_cols = [col for col in df_aff.columns if col not in year_columns]
                df_aff_long = pd.melt(df_aff, 
                                    id_vars=id_cols, 
                                    value_vars=year_columns,
                                    var_name='Year', 
                                    value_name='Affected')
                df_aff_long['Year'] = pd.to_numeric(df_aff_long['Year'])
                
                # If there are multiple regions, sum them up for now
                if len(id_cols) > 0:
                    df_aff = df_aff_long.groupby('Year')['Affected'].sum().reset_index()
                else:
                    df_aff = df_aff_long
                    
                year_col_aff = 'Year'
        
        # Same for mortality data
        if year_col_mort is None:
            year_columns = [col for col in df_mort.columns if str(col).isdigit() and 2015 <= int(col) <= 2025]
            if year_columns:
                id_cols = [col for col in df_mort.columns if col not in year_columns]
                df_mort_long = pd.melt(df_mort, 
                                     id_vars=id_cols, 
                                     value_vars=year_columns,
                                     var_name='Year', 
                                     value_name='Deaths')
                df_mort_long['Year'] = pd.to_numeric(df_mort_long['Year'])
                
                if len(id_cols) > 0:
                    df_mort = df_mort_long.groupby('Year')['Deaths'].sum().reset_index()
                else:
                    df_mort = df_mort_long
                    
                year_col_mort = 'Year'
        
        # Final fallback - use original logic but with better error handling
        if year_col_aff is None:
            year_col_aff = df_aff.columns[0] if len(df_aff.columns) > 0 else 'Year'
        if year_col_mort is None:
            year_col_mort = df_mort.columns[0] if len(df_mort.columns) > 0 else 'Year'
        
        # Standardize column names
        df_aff = df_aff.rename(columns={year_col_aff: 'Year'})
        df_mort = df_mort.rename(columns={year_col_mort: 'Year'})
        
        # Find value columns (should be numeric)
        affected_col = None
        deaths_col = None
        
        for col in df_aff.columns:
            if col != 'Year' and pd.to_numeric(df_aff[col], errors='coerce').notna().any():
                affected_col = col
                break
        
        for col in df_mort.columns:
            if col != 'Year' and pd.to_numeric(df_mort[col], errors='coerce').notna().any():
                deaths_col = col
                break
        
        if affected_col:
            df_aff = df_aff.rename(columns={affected_col: 'Affected'})
        if deaths_col:
            df_mort = df_mort.rename(columns={deaths_col: 'Deaths'})
        
        # Ensure we have the required columns
        if 'Affected' not in df_aff.columns:
            df_aff['Affected'] = 0
        if 'Deaths' not in df_mort.columns:
            df_mort['Deaths'] = 0
        
        # Convert to proper data types with error handling
        df_aff['Year'] = pd.to_numeric(df_aff['Year'], errors='coerce')
        df_mort['Year'] = pd.to_numeric(df_mort['Year'], errors='coerce')
        df_aff['Affected'] = pd.to_numeric(df_aff['Affected'], errors='coerce')
        df_mort['Deaths'] = pd.to_numeric(df_mort['Deaths'], errors='coerce')
        
        # Remove rows with invalid years
        df_aff = df_aff.dropna(subset=['Year'])
        df_mort = df_mort.dropna(subset=['Year'])
        
        # Convert years to int
        df_aff['Year'] = df_aff['Year'].astype(int)
        df_mort['Year'] = df_mort['Year'].astype(int)
        
        # Merge datasets
        df = pd.merge(df_aff, df_mort, on='Year', how='left')
        
        # Fill missing values
        df['Affected'] = df['Affected'].fillna(0)
        df['Deaths'] = df['Deaths'].fillna(0)
        
        # Calculate derived metrics
        df['Survivors'] = df.apply(lambda r: r['Affected'] - r['Deaths'] if pd.notna(r['Deaths']) else None, axis=1)
        df['Mortality_Rate'] = df.apply(lambda r: (r['Deaths'] / r['Affected'] * 100) if pd.notna(r['Deaths']) and r['Affected'] > 0 else None, axis=1)
        df['Survival_Rate'] = df.apply(lambda r: 100 - r['Mortality_Rate'] if pd.notna(r['Mortality_Rate']) else None, axis=1)
        
        # Calculate year-over-year changes
        df = df.sort_values('Year')
        df['Affected_YoY'] = df['Affected'].pct_change() * 100
        df['Deaths_YoY'] = df['Deaths'].pct_change() * 100
        df['Survivors_YoY'] = df['Survivors'].pct_change() * 100
        
        return df
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.write("**Troubleshooting:**")
        st.write("1. Check if your CSV files have the correct structure")
        st.write("2. Years should be in a numeric column (2018, 2019, etc.)")
        st.write("3. Data values should be numeric")
        try:
            st.write("**Raw data preview:**")
            st.write("Affected CSV:")
            st.dataframe(pd.read_csv(AFFECTED_PATH).head())
            st.write("Mortality CSV:")
            st.dataframe(pd.read_csv(MORTALITY_PATH).head())
        except:
            st.write("Could not load raw data for preview")
        return None

# Utility functions
def format_number(num):
    """Format numbers with commas"""
    if pd.isna(num):
        return "N/A"
    return f"{int(num):,}"

def format_percentage(num):
    """Format percentages"""
    if pd.isna(num):
        return "N/A"
    return f"{num:.1f}%"

def get_trend_indicator(value):
    """Get trend indicator with color"""
    if pd.isna(value):
        return "N/A", "trend-neutral"
    elif value > 0:
        return f"↗ +{value:.1f}%", "trend-up"
    elif value < 0:
        return f"↘ {value:.1f}%", "trend-down"
    else:
        return "→ 0.0%", "trend-neutral"

def create_enhanced_bar_chart(row, selected_year):
    """Create enhanced bar chart with better styling"""
    affected = row['Affected'] if pd.notna(row['Affected']) else 0
    deaths = row['Deaths'] if pd.notna(row['Deaths']) else 0
    survivors = row['Survivors'] if pd.notna(row['Survivors']) else 0
    
    fig = go.Figure()
    
    # Add bars with custom colors
    fig.add_trace(go.Bar(
        name='Affected',
        x=['Affected'], 
        y=[affected],
        marker_color=MAGENTA,
        text=format_number(affected),
        textposition='outside'
    ))
    
    fig.add_trace(go.Bar(
        name='Deaths',
        x=['Deaths'], 
        y=[deaths],
        marker_color=RED,
        text=format_number(deaths),
        textposition='outside'
    ))
    
    fig.add_trace(go.Bar(
        name='Survivors',
        x=['Survivors'], 
        y=[survivors],
        marker_color=GREEN,
        text=format_number(survivors),
        textposition='outside'
    ))
    
    fig.update_layout(
        title=f'Cancer Statistics for {selected_year}',
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=False,
        height=400
    )
    
    return fig

def create_trend_chart(df):
    """Create comprehensive trend chart"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Population Trends', 'Rates Over Time', 'Year-over-Year Changes', 'Survival Analysis'),
        specs=[[{"secondary_y": False}, {"secondary_y": True}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Population trends
    fig.add_trace(go.Scatter(
        x=df['Year'], y=df['Affected'], 
        mode='lines+markers', name='Affected',
        line=dict(color=MAGENTA, width=3),
        marker=dict(size=8)
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=df['Year'], y=df['Deaths'], 
        mode='lines+markers', name='Deaths',
        line=dict(color=RED, width=3, dash='dash'),
        marker=dict(size=8)
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=df['Year'], y=df['Survivors'], 
        mode='lines+markers', name='Survivors',
        line=dict(color=GREEN, width=3, dash='dot'),
        marker=dict(size=8)
    ), row=1, col=1)
    
    # Rates over time
    fig.add_trace(go.Scatter(
        x=df['Year'], y=df['Mortality_Rate'],
        mode='lines+markers', name='Mortality Rate',
        line=dict(color=RED, width=3),
        marker=dict(size=8)
    ), row=1, col=2)
    
    fig.add_trace(go.Scatter(
        x=df['Year'], y=df['Survival_Rate'],
        mode='lines+markers', name='Survival Rate',
        line=dict(color=GREEN, width=3),
        marker=dict(size=8)
    ), row=1, col=2)
    
    # Year-over-year changes
    fig.add_trace(go.Bar(
        x=df['Year'], y=df['Affected_YoY'],
        name='Affected YoY%', marker_color=MAGENTA,
        opacity=0.7
    ), row=2, col=1)
    
    fig.add_trace(go.Bar(
        x=df['Year'], y=df['Deaths_YoY'],
        name='Deaths YoY%', marker_color=RED,
        opacity=0.7
    ), row=2, col=1)
    
    # Survival analysis
    fig.add_trace(go.Scatter(
        x=df['Affected'], y=df['Survivors'],
        mode='markers', name='Survival Correlation',
        marker=dict(color=df['Year'], colorscale='Viridis', 
                   size=10, colorbar=dict(title="Year")),
        text=df['Year']
    ), row=2, col=2)
    
    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=800,
        showlegend=True
    )
    
    return fig

def create_donut_chart(row):
    """Create donut chart for affected vs survivors vs deaths"""
    affected = row['Affected'] if pd.notna(row['Affected']) else 0
    deaths = row['Deaths'] if pd.notna(row['Deaths']) else 0
    survivors = row['Survivors'] if pd.notna(row['Survivors']) else 0
    
    labels = ['Survivors', 'Deaths']
    values = [survivors, deaths]
    colors = [GREEN, RED]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels, 
        values=values,
        hole=.6,
        marker_colors=colors,
        textinfo='label+percent',
        textfont_size=12
    )])
    
    fig.update_layout(
        title='Survival vs Mortality Distribution',
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=400
    )
    
    return fig

def generate_insights(df, selected_year):
    """Generate automated insights"""
    insights = []
    row = df[df['Year'] == selected_year].iloc[0]
    
    # Survival rate insight
    if pd.notna(row['Survival_Rate']):
        if row['Survival_Rate'] > 80:
            insights.append(f" High survival rate of {row['Survival_Rate']:.1f}% in {selected_year}")
        elif row['Survival_Rate'] > 60:
            insights.append(f" Moderate survival rate of {row['Survival_Rate']:.1f}% in {selected_year}")
        else:
            insights.append(f" Concerning survival rate of {row['Survival_Rate']:.1f}% in {selected_year}")
    
    # Trend insight
    if pd.notna(row['Affected_YoY']):
        if abs(row['Affected_YoY']) > 10:
            direction = "increase" if row['Affected_YoY'] > 0 else "decrease"
            insights.append(f"Significant {direction} of {abs(row['Affected_YoY']):.1f}% in affected cases")
    
    # Mortality trend
    if pd.notna(row['Deaths_YoY']):
        if row['Deaths_YoY'] < -5:
            insights.append(f" Deaths decreased by {abs(row['Deaths_YoY']):.1f}% - positive trend!")
        elif row['Deaths_YoY'] > 5:
            insights.append(f" Deaths increased by {row['Deaths_YoY']:.1f}% - needs attention")
    
    return insights

# Main application
def main():
    # Header
    st.image("clg logo.jpg")
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <h1 style='color: #ff00ff; font-size: 3em; margin-bottom: 0;'>Cancer Analytics Dashboard</h1>
        <p style='color: #cccccc; font-size: 1.2em;'>Advanced Healthcare Data Insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    if df is None:
        st.error("Unable to load data. Please check file paths.")
        st.info(f"Expected files:\n- {AFFECTED_PATH}\n- {MORTALITY_PATH}")
        return
    
    # Sidebar
    with st.sidebar:
        st.markdown("### Dashboard Controls")
        
        # Year selector
        years = sorted(df['Year'].tolist())
        selected_year = st.selectbox(
            'Select Year', 
            years, 
            index=len(years)-1,
            help="Choose a year to analyze cancer statistics"
        )
        
        # Filter options (placeholder for future features)
        st.markdown("###  Analysis Options")
        show_trends = st.checkbox("Show Trend Analysis", value=True)
        show_insights = st.checkbox("Show AI Insights", value=True)
        show_advanced = st.checkbox("Show Advanced Charts", value=True)
        
        # Export options
        st.markdown("###  Export Data")
        if st.button(" Download CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Full Dataset",
                data=csv,
                file_name=f"cancer_analytics_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    # Get current year data
    row = df[df['Year'] == selected_year].iloc[0]
    
    # Main metrics row
    st.markdown("###Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        affected = int(row['Affected']) if pd.notna(row['Affected']) else 0
        yoy_trend, trend_class = get_trend_indicator(row['Affected_YoY'])
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: {MAGENTA};">Affected</h3>
            <h2>{format_number(affected)}</h2>
            <p class="{trend_class}">{yoy_trend}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        deaths = int(row['Deaths']) if pd.notna(row['Deaths']) else 0
        deaths_trend, deaths_trend_class = get_trend_indicator(row['Deaths_YoY'])
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: {RED};">Deaths</h3>
            <h2>{format_number(deaths)}</h2>
            <p class="{deaths_trend_class}">{deaths_trend}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        survivors = int(row['Survivors']) if pd.notna(row['Survivors']) else 0
        survivors_trend, survivors_trend_class = get_trend_indicator(row['Survivors_YoY'])
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: {GREEN};"> Survivors</h3>
            <h2>{format_number(survivors)}</h2>
            <p class="{survivors_trend_class}">{survivors_trend}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        survival_rate = row['Survival_Rate'] if pd.notna(row['Survival_Rate']) else 0
        mortality_rate = row['Mortality_Rate'] if pd.notna(row['Mortality_Rate']) else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: {YELLOW};">Rates</h3>
            <p>Survival: <strong style="color: {GREEN};">{format_percentage(survival_rate)}</strong></p>
            <p>Mortality: <strong style="color: {RED};">{format_percentage(mortality_rate)}</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    # AI Insights
    if show_insights:
        st.markdown("###  AI-Generated Insights")
        insights = generate_insights(df, selected_year)
        if insights:
            for insight in insights:
                st.markdown(f"""
                <div class="summary-box">
                    {insight}
                </div>
                """, unsafe_allow_html=True)
    
    # Charts section
    st.markdown("### Visual Analytics")
    
    if show_advanced:
        # Enhanced charts in tabs
        tab1, tab2, tab3 = st.tabs([" Current Year", " Trends", " Distribution"])
        
        with tab1:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.plotly_chart(create_enhanced_bar_chart(row, selected_year), use_container_width=True)
            with col2:
                st.plotly_chart(create_donut_chart(row), use_container_width=True)
        
        with tab2:
            if show_trends:
                st.plotly_chart(create_trend_chart(df), use_container_width=True)
        
        with tab3:
            # Altair correlation chart
            scatter_chart = alt.Chart(df).mark_circle(size=100, opacity=0.8).add_selection(
                alt.selection_interval(bind='scales')
            ).encode(
                x=alt.X('Affected:Q', title='People Affected'),
                y=alt.Y('Deaths:Q', title='Deaths'),
                color=alt.Color('Year:O', scale=alt.Scale(scheme='viridis')),
                size=alt.Size('Survivors:Q', title='Survivors'),
                tooltip=['Year:O', 'Affected:Q', 'Deaths:Q', 'Survivors:Q', 'Survival_Rate:Q']
            ).properties(
                title='Cancer Statistics Correlation Analysis',
                width=600,
                height=400
            ).configure_axis(
                gridColor='#444444'
            ).configure_view(
                strokeWidth=0
            )
            
            st.altair_chart(scatter_chart, use_container_width=True)
    
    # Data table
    # st.markdown("### Detailed Data Table")
    
    # # Format the dataframe for display
    # display_df = df.copy()
    # numeric_columns = ['Affected', 'Deaths', 'Survivors']
    # percentage_columns = ['Mortality_Rate', 'Survival_Rate', 'Affected_YoY', 'Deaths_YoY', 'Survivors_YoY']
    
    # for col in numeric_columns:
    #     if col in display_df.columns:
    #         display_df[col] = display_df[col].apply(lambda x: format_number(x) if pd.notna(x) else "N/A")
    
    # for col in percentage_columns:
    #     if col in display_df.columns:
    #         display_df[col] = display_df[col].apply(lambda x: format_percentage(x) if pd.notna(x) else "N/A")
    
    # st.dataframe(
    #     display_df,
    #     use_container_width=True,
    #     hide_index=True
    # )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #888888; padding: 20px;'>
        <p>Data Period: 2018-2024 | Last Updated: {}</p>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M")), unsafe_allow_html=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Application Error: {str(e)}")
        st.info("Please refresh the page or contact support if the issue persists.")