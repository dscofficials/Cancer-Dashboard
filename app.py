# India Cancer Mortality Dashboard with Interactive Map Visualization
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import altair as alt
from datetime import datetime
import numpy as np
import json

# Page configuration
st.set_page_config(
    page_title="India Cancer Mortality Dashboard",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
    }
    
    .metric-card {
        background: linear-gradient(45deg, #1f1f2e, #2d2d3a);
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #00d4aa;
        box-shadow: 0 0 20px rgba(0, 212, 170, 0.3);
        margin: 10px 0;
        text-align: center;
    }
    
    .state-info {
        background: rgba(0, 212, 170, 0.1);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #00d4aa;
        margin: 10px 0;
    }
    
    .summary-box {
        background: rgba(255, 99, 132, 0.1);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #ff6384;
        margin: 10px 0;
    }
    
    .trend-up {
        color: #ff6384 !important;
        font-weight: bold;
    }
    
    .trend-down {
        color: #00d4aa !important;
        font-weight: bold;
    }
    
    .trend-neutral {
        color: #ffa500 !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Constants
PRIMARY_COLOR = "#00d4aa"
SECONDARY_COLOR = "#ff6384"
WARNING_COLOR = "#ffa500"
SUCCESS_COLOR = "#00d4aa"
DANGER_COLOR = "#ff6384"

# Data loading function
@st.cache_data
def load_data():
    """Load and process India cancer mortality data"""
    try:
        # Load the synthetic dataset
        df = pd.read_csv("CANCER-MORTALITY-2018-2024-SYNTHETIC.csv")
        
        # Clean the data
        df.columns = [c.strip() for c in df.columns]
        
        # Rename first column to 'State' for consistency
        df = df.rename(columns={df.columns[0]: 'State'})
        
        # Remove total row if present
        df = df[df['State'] != 'Total']
        
        # Clean state names
        df['State'] = df['State'].str.strip()
        df['State'] = df['State'].str.replace('Telangana ', 'Telangana')
        
        return df
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

@st.cache_data
def prepare_map_data(df, year):
    """Prepare data for map visualization"""
    # Create a comprehensive mapping for state names to match with plotly's India geojson
    # Testing multiple variations to ensure Jammu & Kashmir shows up
    state_mapping = {
        'Andhra Pradesh': 'Andhra Pradesh',
        'Arunachal Pradesh': 'Arunachal Pradesh', 
        'Assam': 'Assam',
        'Bihar': 'Bihar',
        'Chhattisgarh': 'Chhattisgarh',
        'Goa': 'Goa',
        'Gujarat': 'Gujarat',
        'Haryana': 'Haryana',
        'Himachal Pradesh': 'Himachal Pradesh',
        'Jharkhand': 'Jharkhand',
        'Karnataka': 'Karnataka',
        'Kerala': 'Kerala',
        'Madhya Pradesh': 'Madhya Pradesh',
        'Maharashtra': 'Maharashtra',
        'Manipur': 'Manipur',
        'Meghalaya': 'Meghalaya',
        'Mizoram': 'Mizoram',
        'Nagaland': 'Nagaland',
        'Orissa': 'Odisha',
        'Punjab': 'Punjab',
        'Rajasthan': 'Rajasthan',
        'Sikkim': 'Sikkim',
        'Tamil Nadu': 'Tamil Nadu',
        'Telangana': 'Telangana',
        'Tripura': 'Tripura',
        'Uttar Pradesh': 'Uttar Pradesh',
        'Uttaranchal': 'Uttarakhand',
        'West Bengal': 'West Bengal',
        'Delhi': 'Delhi',
        # Try multiple variations for Jammu & Kashmir
        'Jammu & Kashmir': 'Jammu & Kashmir',
        'Jammu and Kashmir': 'Jammu & Kashmir',
        'Chandigarh': 'Chandigarh',
        'Dadra & Nagar Haveli': 'Dadra and Nagar Haveli and Daman and Diu',
        'Daman': 'Dadra and Nagar Haveli and Daman and Diu',
        'Lakshadweep': 'Lakshadweep',
        'Pondicherry': 'Puducherry',
        'Andaman & Nicobar Islands': 'Andaman & Nicobar'
    }
    
    # Apply mapping
    df_copy = df.copy()
    df_copy['State_Mapped'] = df_copy['State'].map(state_mapping)
    
    # Debug: Check for unmapped states
    unmapped = df_copy[df_copy['State_Mapped'].isna()]
    if not unmapped.empty:
        # For unmapped states, use original name
        df_copy.loc[df_copy['State_Mapped'].isna(), 'State_Mapped'] = df_copy.loc[df_copy['State_Mapped'].isna(), 'State']
    
    # Create base map data
    map_data = pd.DataFrame({
        'State': df_copy['State_Mapped'],
        'Original_State': df_copy['State'],
        'Deaths': df_copy[str(year)],
        'Year': year
    })
    
    # SPECIAL HANDLING: Map both J&K and Ladakh regions to show as "Jammu & Kashmir"
    # The GeoJSON has separate regions, but we want both to show the same J&K data
    jk_row = df_copy[df_copy['State'].str.contains('Jammu', case=False, na=False)]
    if not jk_row.empty:
        jk_deaths = jk_row[str(year)].iloc[0]
        
        # Map BOTH geographic regions to the same "Jammu & Kashmir" data
        # This makes the entire region (including Ladakh area) show as Jammu & Kashmir
        jk_data = pd.DataFrame({
            'State': ['Jammu & Kashmir', 'Ladakh'],
            'Original_State': ['Jammu & Kashmir', 'Jammu & Kashmir (Ladakh area)'],
            'Deaths': [jk_deaths, jk_deaths],  # Same data for both regions
            'Year': [year, year]
        })
        
        # Remove original J&K row and add unified mapping
        map_data = map_data[~map_data['Original_State'].str.contains('Jammu', case=False, na=False)]
        map_data = pd.concat([map_data, jk_data], ignore_index=True)
    
    # Remove any rows with NaN deaths
    map_data = map_data.dropna(subset=['Deaths'])
    
    return map_data

def create_india_map(df, year):
    """Create India choropleth map focused ONLY on India"""
    map_data = prepare_map_data(df, year)
    
    try:
        # Use India-specific GeoJSON and create choropleth
        fig = px.choropleth(
            map_data,
            geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
            featureidkey='properties.ST_NM',
            locations='State',
            color='Deaths',
            hover_data={'Original_State': True, 'Deaths': ':,'},
            color_continuous_scale='Reds',
            title=f'🇮🇳 Cancer Mortality by State - {year}',
            labels={'Deaths': 'Cancer Deaths', 'Original_State': 'State/UT'}
        )
        
        # Configure INDIA ONLY - no world map background
        fig.update_geos(
            # Hide everything except India
            showcoastlines=False,
            showland=False,
            showocean=False, 
            showlakes=False,
            showcountries=False,
            showsubunits=False,
            showframe=False,
            # Fit bounds to geojson (India only)
            fitbounds="geojson",
            visible=False,  # Hide the base map completely
        )
        
        fig.update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=600,
            margin=dict(l=0, r=0, t=50, b=0),
            title_x=0.5,
            # Ensure no world map shows
            geo=dict(
                showframe=False,
                showcoastlines=False,
                projection=dict(type='natural earth'),
                bgcolor='rgba(0,0,0,0)'
            )
        )
        
        return fig
        
    except Exception as e:
        # Fallback to alternative India-only map
        return create_alternative_india_map(df, year)

def create_alternative_india_map(df, year):
    """Alternative India-ONLY map using scatter plot on India coordinates"""
    # India state coordinates (approximate centers) - COMPLETE LIST
    state_coords = {
        'Andhra Pradesh': [15.9129, 79.7400],
        'Arunachal Pradesh': [28.2180, 94.7278],
        'Assam': [26.2006, 92.9376],
        'Bihar': [25.0961, 85.3131],
        'Chhattisgarh': [21.2787, 81.8661],
        'Goa': [15.2993, 74.1240],
        'Gujarat': [23.0225, 72.5714],
        'Haryana': [29.0588, 76.0856],
        'Himachal Pradesh': [31.1048, 77.1734],
        'Jharkhand': [23.6102, 85.2799],
        'Karnataka': [15.3173, 75.7139],
        'Kerala': [10.8505, 76.2711],
        'Madhya Pradesh': [22.9734, 78.6569],
        'Maharashtra': [19.7515, 75.7139],
        'Manipur': [24.6637, 93.9063],
        'Meghalaya': [25.4670, 91.3662],
        'Mizoram': [23.1645, 92.9376],
        'Nagaland': [26.1584, 94.5624],
        'Odisha': [20.9517, 85.0985],
        'Orissa': [20.9517, 85.0985],  # Alternative name
        'Punjab': [31.1471, 75.3412],
        'Rajasthan': [27.0238, 74.2179],
        'Sikkim': [27.5330, 88.5122],
        'Tamil Nadu': [11.1271, 78.6569],
        'Telangana': [18.1124, 79.0193],
        'Tripura': [23.9408, 91.9882],
        'Uttar Pradesh': [26.8467, 80.9462],
        'Uttarakhand': [30.0668, 79.0193],
        'Uttaranchal': [30.0668, 79.0193],  # Alternative name
        'West Bengal': [22.9868, 87.8550],
        'Delhi': [28.7041, 77.1025],
        # Multiple variations for Jammu & Kashmir
        'Jammu & Kashmir': [34.0837, 74.7973],
        'Jammu and Kashmir': [34.0837, 74.7973],
        'J&K': [34.0837, 74.7973],
        # Union Territories
        'Chandigarh': [30.7333, 76.7794],
        'Dadra & Nagar Haveli': [20.1809, 73.0169],
        'Daman': [20.3974, 72.8328],
        'Lakshadweep': [10.5667, 72.6417],
        'Puducherry': [11.9416, 79.8083],
        'Pondicherry': [11.9416, 79.8083],  # Alternative name
        'Andaman & Nicobar Islands': [11.7401, 92.6586],
    }
    
    # Prepare data with coordinates
    map_data = []
    for _, row in df.iterrows():
        state_name = row['State']
        
        # Try to find coordinates for this state (try multiple variations)
        coords = None
        for coord_key in [state_name, state_name.strip(), 
                         'Jammu & Kashmir' if 'Jammu' in state_name else None,
                         'Odisha' if state_name == 'Orissa' else None,
                         'Uttarakhand' if state_name == 'Uttaranchal' else None]:
            if coord_key and coord_key in state_coords:
                coords = state_coords[coord_key]
                break
        
        if coords:
            map_data.append({
                'State': state_name,
                'Latitude': coords[0],
                'Longitude': coords[1],
                'Deaths': row[str(year)],
                'Size': min(max(row[str(year)] / 5000, 5), 50)  # Better scaling for bubble size
            })
    
    map_df = pd.DataFrame(map_data)
    
    # Create scatter map focused ONLY on India
    fig = px.scatter_geo(
        map_df,
        lat='Latitude',
        lon='Longitude',
        size='Size',
        color='Deaths',
        hover_name='State',
        hover_data={'Deaths': ':,', 'Latitude': False, 'Longitude': False, 'Size': False},
        color_continuous_scale='Reds',
        title=f'🇮🇳 Cancer Mortality by State - {year} (India Only)',
        size_max=35
    )
    
    # Configure to show ONLY India - no world background
    fig.update_geos(
        projection_type="mercator",
        # Hide all world features
        showland=False,
        showocean=False,
        showlakes=False,
        showcountries=False,
        showcoastlines=False,
        showframe=False,
        # Set tight bounds for India only
        lonaxis_range=[68, 98],  # India longitude range
        lataxis_range=[6, 38],   # India latitude range  
        bgcolor='rgba(0,0,0,0)'  # Transparent background
    )
    
    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=600,
        margin=dict(l=0, r=0, t=50, b=0),
        title_x=0.5
    )
    
    return fig

def create_state_comparison(df, states, years):
    """Create state comparison chart"""
    # Filter data for selected states and years
    state_data = df[df['State'].isin(states)]
    
    fig = go.Figure()
    
    colors = px.colors.qualitative.Set3
    
    for i, state in enumerate(states):
        state_row = state_data[state_data['State'] == state].iloc[0]
        values = [state_row[str(year)] for year in years]
        
        fig.add_trace(go.Scatter(
            x=years,
            y=values,
            mode='lines+markers',
            name=state,
            line=dict(width=3, color=colors[i % len(colors)]),
            marker=dict(size=8)
        ))
    
    fig.update_layout(
        title='Cancer Mortality Trends - State Comparison',
        xaxis_title='Year',
        yaxis_title='Deaths',
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=500,
        hovermode='x unified'
    )
    
    return fig

def create_top_states_chart(df, year, top_n=10):
    """Create top states bar chart"""
    year_data = df[['State', str(year)]].copy()
    year_data = year_data.sort_values(str(year), ascending=False).head(top_n)
    
    fig = px.bar(
        year_data,
        x='State',
        y=str(year),
        title=f'Top {top_n} States by Cancer Mortality - {year}',
        color=str(year),
        color_continuous_scale='Reds',
        text=str(year)
    )
    
    # Format text on bars
    fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    
    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=500,
        xaxis_tickangle=-45,
        xaxis_title="State/UT",
        yaxis_title="Deaths",
        showlegend=False
    )
    
    return fig

def create_trend_analysis(df):
    """Create overall trend analysis"""
    # Calculate yearly totals
    years = ['2018', '2019', '2020', '2021', '2022', '2023', '2024']
    yearly_totals = []
    
    for year in years:
        total = df[year].sum()
        yearly_totals.append(total)
    
    # Calculate year-over-year change
    yoy_change = []
    for i in range(1, len(yearly_totals)):
        change = ((yearly_totals[i] - yearly_totals[i-1]) / yearly_totals[i-1]) * 100
        yoy_change.append(change)
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Total Cancer Deaths Over Time', 'Year-over-Year Change (%)'),
        vertical_spacing=0.1
    )
    
    # Total deaths trend
    fig.add_trace(
        go.Scatter(
            x=years,
            y=yearly_totals,
            mode='lines+markers',
            name='Total Deaths',
            line=dict(color=DANGER_COLOR, width=3),
            marker=dict(size=10)
        ),
        row=1, col=1
    )
    
    # YoY change
    colors = [SUCCESS_COLOR if x < 0 else DANGER_COLOR for x in yoy_change]
    fig.add_trace(
        go.Bar(
            x=years[1:],
            y=yoy_change,
            name='YoY Change %',
            marker_color=colors
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=700,
        showlegend=False
    )
    
    return fig, yearly_totals, yoy_change

def format_number(num):
    """Format numbers with commas"""
    if pd.isna(num):
        return "N/A"
    return f"{int(num):,}"

def calculate_statistics(df, year):
    """Calculate key statistics for the selected year"""
    year_data = df[str(year)]
    
    total_deaths = year_data.sum()
    avg_deaths = year_data.mean()
    max_deaths = year_data.max()
    min_deaths = year_data.min()
    std_deaths = year_data.std()
    
    # Find states with max and min deaths
    max_state = df[df[str(year)] == max_deaths]['State'].iloc[0]
    min_state = df[df[str(year)] == min_deaths]['State'].iloc[0]
    
    return {
        'total': total_deaths,
        'average': avg_deaths,
        'max': max_deaths,
        'min': min_deaths,
        'std': std_deaths,
        'max_state': max_state,
        'min_state': min_state
    }

def generate_insights(df, year, stats, yoy_change):
    """Generate AI insights"""
    insights = []
    
    # Total deaths insight
    insights.append(f"**Total Deaths in {year}**: {format_number(stats['total'])} people across India")
    
    # Highest and lowest states
    insights.append(f"**Highest Impact**: {stats['max_state']} with {format_number(stats['max'])} deaths")
    insights.append(f"**Lowest Impact**: {stats['min_state']} with {format_number(stats['min'])} deaths")
    
    # Year-over-year trend
    if len(yoy_change) > 0:
        latest_change = yoy_change[-1]
        if latest_change > 0:
            insights.append(f"**Concerning Trend**: {latest_change:.1f}% increase from previous year")
        else:
            insights.append(f"**Positive Trend**: {abs(latest_change):.1f}% decrease from previous year")
    
    # Regional distribution
    high_mortality_states = df[df[str(year)] > stats['average'] * 2]['State'].tolist()
    if high_mortality_states:
        insights.append(f"**High Risk States**: {len(high_mortality_states)} states have mortality rates above twice the national average")
    
    # Regional analysis
    north_states = ['Punjab', 'Haryana', 'Himachal Pradesh', 'Uttaranchal', 'Uttar Pradesh', 'Delhi', 'Jammu & Kashmir', 'Chandigarh']
    south_states = ['Karnataka', 'Tamil Nadu', 'Andhra Pradesh', 'Telangana', 'Kerala', 'Goa']
    east_states = ['West Bengal', 'Orissa', 'Bihar', 'Jharkhand', 'Assam']
    west_states = ['Maharashtra', 'Gujarat', 'Rajasthan', 'Madhya Pradesh', 'Chhattisgarh']
    
    regional_data = {
        'North India': df[df['State'].isin(north_states)][str(year)].sum(),
        'South India': df[df['State'].isin(south_states)][str(year)].sum(),
        'East India': df[df['State'].isin(east_states)][str(year)].sum(),
        'West India': df[df['State'].isin(west_states)][str(year)].sum()
    }
    
    highest_region = max(regional_data, key=regional_data.get)
    insights.append(f"**Regional Impact**: {highest_region} has the highest mortality with {format_number(regional_data[highest_region])} deaths")
    
    return insights

def create_regional_analysis(df, year):
    """Create regional analysis chart"""
    # Define regions
    regions = {
        'North India': ['Punjab', 'Haryana', 'Himachal Pradesh', 'Uttaranchal', 'Uttar Pradesh', 'Delhi', 'Jammu & Kashmir', 'Chandigarh'],
        'South India': ['Karnataka', 'Tamil Nadu', 'Andhra Pradesh', 'Telangana', 'Kerala', 'Goa'],
        'East India': ['West Bengal', 'Orissa', 'Bihar', 'Jharkhand', 'Assam', 'Tripura', 'Meghalaya', 'Manipur', 'Mizoram', 'Nagaland', 'Arunachal Pradesh', 'Sikkim'],
        'West India': ['Maharashtra', 'Gujarat', 'Rajasthan', 'Madhya Pradesh', 'Chhattisgarh', 'Daman', 'Dadra & Nagar Haveli'],
        'Islands & Others': ['Lakshadweep', 'Andaman & Nicobar Islands', 'Pondicherry']
    }
    
    regional_data = []
    for region, states in regions.items():
        total_deaths = df[df['State'].isin(states)][str(year)].sum()
        regional_data.append({'Region': region, 'Deaths': total_deaths})
    
    regional_df = pd.DataFrame(regional_data)
    
    fig = px.pie(
        regional_df,
        values='Deaths',
        names='Region',
        title=f'Regional Distribution of Cancer Deaths - {year}',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=500
    )
    
    return fig

# Main application
def main():
    # Header
    st.image("clg logo.jpg")
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <h1 style='color: #00d4aa; font-size: 3em; margin-bottom: 0;'>🇮🇳 India Cancer Mortality Dashboard</h1>
        <p style='color: #cccccc; font-size: 1.2em;'>Interactive State-wise Cancer Mortality Analysis (2018-2024)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    if df is None:
        st.error("Unable to load data. Please check the file path.")
        return
    
    # Sidebar controls
    with st.sidebar:
        st.markdown("### 🎛️ Dashboard Controls")
        
        # Year selector
        years = [2018, 2019, 2020, 2021, 2022, 2023, 2024]
        selected_year = st.selectbox(
            'Select Year',
            years,
            index=len(years)-1
        )
        
        st.markdown("### Map Options")
        show_map = st.checkbox("Show Interactive Map", value=True)
        
        st.markdown("### 📊 Analysis Options")
        show_comparison = st.checkbox("Show State Comparison", value=True)
        show_top_states = st.checkbox("Show Top States", value=True)
        show_trends = st.checkbox("Show Trend Analysis", value=True)
        
        if show_comparison:
            st.markdown("#### Compare States")
            available_states = df['State'].tolist()
            selected_states = st.multiselect(
                "Select states to compare:",
                available_states,
                default=available_states[:5]
            )
        
        if show_top_states:
            top_n = st.slider("Number of top states to show:", 5, 20, 10)
        
        st.markdown("### 📥 Export Options")
        if st.button("📊 Download Full Dataset"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"india_cancer_mortality_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    # Calculate statistics and trends
    stats = calculate_statistics(df, selected_year)
    _, yearly_totals, yoy_change = create_trend_analysis(df)
    
    # Key metrics
    st.markdown("### 📈 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: {DANGER_COLOR};">Total Deaths</h3>
            <h2>{format_number(stats['total'])}</h2>
            <p>Across all states in {selected_year}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: {PRIMARY_COLOR};">Average per State</h3>
            <h2>{format_number(stats['average'])}</h2>
            <p>Mean mortality rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: {WARNING_COLOR};">Highest Impact</h3>
            <h2>{stats['max_state']}</h2>
            <p>{format_number(stats['max'])} deaths</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if len(yoy_change) > 0:
            latest_change = yoy_change[-1]
            trend_color = SUCCESS_COLOR if latest_change < 0 else DANGER_COLOR
            trend_icon = "📉" if latest_change < 0 else "📈"
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: {trend_color};">YoY Change</h3>
                <h2>{trend_icon} {latest_change:+.1f}%</h2>
                <p>From previous year</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: {PRIMARY_COLOR};">Lowest Impact</h3>
                <h2>{stats['min_state']}</h2>
                <p>{format_number(stats['min'])} deaths</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Quick Statistics Summary
    st.markdown("### 📊 Quick Statistics Summary")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="summary-box">
            <h4>Statistical Overview</h4>
            <p><strong>Standard Deviation:</strong> {format_number(stats['std'])}</p>
            <p><strong>Median Deaths:</strong> {format_number(df[str(selected_year)].median())}</p>
            <p><strong>Range:</strong> {format_number(stats['min'])} - {format_number(stats['max'])}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Calculate percentiles
        percentile_75 = df[str(selected_year)].quantile(0.75)
        percentile_25 = df[str(selected_year)].quantile(0.25)
        above_avg = len(df[df[str(selected_year)] > stats['average']])
        
        st.markdown(f"""
        <div class="summary-box">
            <h4>Distribution Analysis</h4>
            <p><strong>75th Percentile:</strong> {format_number(percentile_75)}</p>
            <p><strong>25th Percentile:</strong> {format_number(percentile_25)}</p>
            <p><strong>Above Average:</strong> {above_avg} states/UTs</p>
        </div>
        """, unsafe_allow_html=True)

    # AI Insights
    st.markdown("### 🤖 AI-Generated Insights")
    insights = generate_insights(df, selected_year, stats, yoy_change)
    for insight in insights:
        # Use st.markdown() directly so **bold** syntax works properly
        st.markdown(insight)
    
    # Main visualizations
    if show_map:
        st.markdown("### 🗺️ Interactive India Map (India Only)")
        
        # Debug info for Jammu & Kashmir visibility
        jk_data = df[df['State'].str.contains('Jammu', case=False, na=False)]
        if not jk_data.empty:
            jk_deaths = jk_data[str(selected_year)].iloc[0]
            jk_state_name = jk_data['State'].iloc[0]
            st.success(f"**{jk_state_name} Found**: {format_number(jk_deaths)} deaths in {selected_year}")
        else:
            st.warning("Jammu & Kashmir data not detected - checking state names...")
            st.write("Available states:", df['State'].tolist()[:10], "...")
        
        with st.spinner("Loading India-only map visualization..."):
            try:
                map_fig = create_india_map(df, selected_year)
                st.plotly_chart(map_fig, use_container_width=True)
                st.success("�️ **India Choropleth Map**: Showing only Indian states and UTs")
            except Exception as e:
                st.warning("🗺️ Choropleth map unavailable. Loading India bubble map...")
                try:
                    alt_map = create_alternative_india_map(df, selected_year)
                    st.plotly_chart(alt_map, use_container_width=True)
                    st.success("�️ **India Bubble Map**: Showing only Indian territories")
                except Exception as e2:
                    st.error(f"Map visualization error: {str(e2)}")
                    st.info("Please check the other tabs for detailed state analysis")
    
    # Tabbed interface for additional charts
    tab1, tab2, tab3, tab4 = st.tabs(["State Rankings", "Trend Analysis", "Regional Analysis", "State Comparison"])
    
    with tab1:
        if show_top_states:
            st.plotly_chart(create_top_states_chart(df, selected_year, top_n), use_container_width=True)
        
        # State details table
        st.markdown(f"### 📋 Detailed State Data - {selected_year}")
        display_df = df[['State', str(selected_year)]].copy()
        display_df = display_df.sort_values(str(selected_year), ascending=False)
        display_df[str(selected_year)] = display_df[str(selected_year)].apply(lambda x: format_number(x))
        display_df.columns = ['State', f'Deaths ({selected_year})']
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    with tab2:
        if show_trends:
            trend_fig, _, _ = create_trend_analysis(df)
            st.plotly_chart(trend_fig, use_container_width=True)
    
    with tab3:
        st.plotly_chart(create_regional_analysis(df, selected_year), use_container_width=True)
        
        # Regional comparison table
        st.markdown("### Regional Statistics")
        regions = {
            'North India': ['Punjab', 'Haryana', 'Himachal Pradesh', 'Uttaranchal', 'Uttar Pradesh', 'Delhi', 'Jammu & Kashmir', 'Chandigarh'],
            'South India': ['Karnataka', 'Tamil Nadu', 'Andhra Pradesh', 'Telangana', 'Kerala', 'Goa'],
            'East India': ['West Bengal', 'Orissa', 'Bihar', 'Jharkhand', 'Assam', 'Tripura', 'Meghalaya', 'Manipur', 'Mizoram', 'Nagaland', 'Arunachal Pradesh', 'Sikkim'],
            'West India': ['Maharashtra', 'Gujarat', 'Rajasthan', 'Madhya Pradesh', 'Chhattisgarh', 'Daman', 'Dadra & Nagar Haveli'],
            'Islands & Others': ['Lakshadweep', 'Andaman & Nicobar Islands', 'Pondicherry']
        }
        
        regional_stats = []
        for region, states in regions.items():
            region_df = df[df['State'].isin(states)]
            total_deaths = region_df[str(selected_year)].sum()
            num_states = len([s for s in states if s in df['State'].values])
            avg_deaths = total_deaths / num_states if num_states > 0 else 0
            regional_stats.append({
                'Region': region,
                'Total Deaths': format_number(total_deaths),
                'Number of States/UTs': num_states,
                'Average per State': format_number(avg_deaths)
            })
        
        regional_stats_df = pd.DataFrame(regional_stats)
        st.dataframe(regional_stats_df, use_container_width=True, hide_index=True)
    
    with tab4:
        if show_comparison and 'selected_states' in locals() and selected_states:
            comparison_fig = create_state_comparison(df, selected_states, years)
            st.plotly_chart(comparison_fig, use_container_width=True)
        else:
            st.info("Please select states in the sidebar to enable comparison.")
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; color: #888888; padding: 20px;'>
        <p><strong>Data Source</strong>: Cancer Mortality Data (2018-2024)</p>
        <p><strong>Last Updated</strong>: {datetime.now().strftime("%Y-%m-%d")}</p>
        <p><strong>Dashboard created for Data Analytics Club</strong></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Application Error: {str(e)}")
        st.info("Please refresh the page or contact support if the issue persists.")