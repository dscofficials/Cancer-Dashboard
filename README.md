# India Cancer Mortality Dashboard - Features & Usage Guide

## 🌟 Overview
This comprehensive Streamlit dashboard provides interactive visualization and analysis of cancer mortality data across all Indian states from 2018-2024 using the synthetic dataset `CANCER-MORTALITY-2018-2024-SYNTHETIC.csv`.

## 📁 Project Structure
```
Cancer-Dashboard/
├── app.py                                    # Main Streamlit application
├── setup.bat                                # Automated setup script (Windows)
├── requirements.txt                          # Python dependencies
├── README.md                                # Project documentation
├── clg logo.jpg                            # College logo for dashboard
├── CANCER-MORTALITY-2018-2024-SYNTHETIC.csv # Main dataset
├── CANCER (2018-2024).csv                  # Additional dataset
├── CANCER MORTALITY (2018-2022).csv        # Historical data
└── cancer/                                  # Virtual environment (created by setup)
    ├── Scripts/                            # Environment activation scripts
    ├── Lib/                               # Installed packages
    └── Include/                           # Header files
```

## 🚀 Key Features

### 1. 🗺️ Interactive Indian Map Visualization
- **Choropleth Map**: Interactive map showing cancer mortality by state with color-coded intensity
- **Hover Information**: Detailed state-wise data on hover
- **Geographic Context**: Proper Indian state boundaries and geographic projection

### 2. 📊 Comprehensive Analytics Dashboard

#### Key Performance Indicators (KPIs)
- **Total Deaths**: Aggregate mortality across all states
- **Average per State**: Mean mortality rate calculation
- **Highest Impact State**: State with maximum deaths
- **Year-over-Year Change**: Trend analysis with percentage change

#### Advanced Visualizations
1. **State Rankings Chart**: Top N states by mortality (configurable)
2. **Trend Analysis**: Multi-year progression with YoY percentage changes
3. **Regional Analysis**: North/South/East/West India regional breakdown
4. **State Comparison**: Multi-state trend comparison over time

### 3. 🤖 AI-Powered Insights
- **Automated Analysis**: Smart insights based on data patterns
- **Regional Trends**: Identification of regional patterns and hotspots
- **Risk Assessment**: Highlighting high-risk states and regions
- **Trend Alerts**: Year-over-year change notifications

### 4. 📈 Interactive Controls

#### Sidebar Features
- **Year Selection**: Choose any year from 2018-2024
- **Map Toggle**: Enable/disable interactive map
- **Analysis Options**: Customizable chart displays
- **State Comparison**: Multi-select for comparing specific states
- **Export Functionality**: Download complete dataset as CSV

#### Tabbed Interface
1. **📊 State Rankings**: Top states and detailed data table
2. **📈 Trend Analysis**: Overall mortality trends and changes
3. **🗺️ Regional Analysis**: Geographic distribution and regional statistics
4. **🔍 State Comparison**: Side-by-side state trend analysis

### 5. 🎨 Professional Design
- **Dark Theme**: Modern, professional appearance
- **Color Coding**: Intuitive color schemes for different data types
- **Responsive Layout**: Adapts to different screen sizes
- **Clean Typography**: Easy-to-read fonts and spacing

## 📊 Data Features

### State Coverage
- **36+ States/UTs**: Complete coverage of Indian states and union territories
- **Standardized Names**: Proper mapping for visualization compatibility
- **Clean Data**: Processed and validated mortality figures

### Regional Classification
- **North India**: Punjab, Haryana, Himachal Pradesh, Uttarakhand, UP, Delhi, J&K, Chandigarh
- **South India**: Karnataka, Tamil Nadu, Andhra Pradesh, Telangana, Kerala, Goa
- **East India**: West Bengal, Odisha, Bihar, Jharkhand, Assam, Northeast states
- **West India**: Maharashtra, Gujarat, Rajasthan, Madhya Pradesh, Chhattisgarh
- **Islands & Others**: Lakshadweep, Andaman & Nicobar, Puducherry

### Time Series Analysis
- **7-Year Coverage**: 2018-2024 comprehensive data
- **Year-over-Year Trends**: Percentage change calculations
- **Growth Patterns**: Identification of increasing/decreasing trends

## 🛠️ Technical Implementation

### Libraries Used
- **Streamlit**: Web application framework
- **Plotly**: Interactive visualizations and maps
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations

### Map Implementation
- **GeoJSON Integration**: Indian state boundaries from trusted sources
- **Choropleth Mapping**: Color-coded state-wise data visualization
- **Interactive Features**: Hover tooltips and zoom capabilities

### Performance Optimizations
- **Caching**: `@st.cache_data` for efficient data loading
- **Lazy Loading**: Maps load only when requested
- **Responsive Charts**: Optimized for different screen sizes

## 🎯 Use Cases

### Healthcare Policy Analysis
- **Resource Allocation**: Identify states needing more healthcare resources
- **Trend Monitoring**: Track progress of healthcare interventions
- **Regional Planning**: Understand geographic distribution of cancer mortality

### Research & Academia
- **Data Exploration**: Interactive tool for cancer epidemiology research
- **Comparative Studies**: Cross-state and regional analysis capabilities
- **Trend Analysis**: Historical pattern identification

### Public Health Monitoring
- **Early Warning Systems**: Identify concerning trends early
- **Regional Disparities**: Understand geographic health inequalities
- **Progress Tracking**: Monitor improvements over time

## 📱 User Experience Features

### Intuitive Navigation
- **Single Page Design**: All features accessible without page changes
- **Sidebar Controls**: Centralized configuration panel
- **Tabbed Interface**: Organized content presentation

### Interactive Elements
- **Dynamic Filtering**: Real-time updates based on selections
- **Hover Details**: Additional information on demand
- **Zoom & Pan**: Map exploration capabilities

### Export & Sharing
- **CSV Export**: Full dataset download capability
- **Screenshot Ready**: High-quality visualizations for reports
- **URL Sharing**: Direct links to specific views

## 🔧 Setup & Installation

### 🚀 Quick Start with setup.bat (Recommended)

For **Windows users**, the easiest way to get started is using the automated setup script:

```batch
# Simply double-click or run in Command Prompt:
setup.bat
```

**What setup.bat does:**
1. **Creates Python Virtual Environment**: Isolates project dependencies
2. **Activates Environment**: Sets up the proper Python environment
3. **Upgrades pip**: Ensures latest package manager version
4. **Installs Dependencies**: Automatically installs all required packages from `requirements.txt`
5. **Provides Run Instructions**: Shows you exactly how to start the dashboard

**Features of setup.bat:**
- ✅ **Error Handling**: Stops if any step fails with clear error messages
- ✅ **Progress Tracking**: Shows which step is currently executing ([1/4], [2/4], etc.)
- ✅ **User Friendly**: Clear instructions and professional formatting
- ✅ **Complete Instructions**: Provides final run commands and URL

### 📋 Manual Setup (Alternative Method)

If you prefer manual setup or are on Linux/Mac:

#### Prerequisites
- **Python 3.7+**: Make sure Python is installed and added to PATH
- **pip**: Python package manager (comes with Python)

#### Required Packages
```bash
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.17.0
numpy>=1.24.0
altair>=5.0.0
```

#### Step-by-Step Installation
```bash
# 1. Create virtual environment
python -m venv cancer

# 2. Activate virtual environment
# On Windows:
cancer\Scripts\activate
# On Linux/Mac:
source cancer/bin/activate

# 3. Upgrade pip
pip install --upgrade pip

# 4. Install dependencies
pip install -r requirements.txt
```

### 🎯 Running the Dashboard

After setup completion:

```bash
# 1. Activate environment (if not already active)
cancer\Scripts\activate

# 2. Run the dashboard
streamlit run app.py --server.port 8502
```

### 🌐 Access URLs
- **Local Access**: http://localhost:8502
- **Network Access**: Available on local network for sharing
- **Default Browser**: Opens automatically when started

### 🛠️ Troubleshooting Setup

#### Common Issues & Solutions

1. **Python Not Found**
   ```
   Error: 'python' is not recognized...
   ```
   **Solution**: Install Python and add to system PATH

2. **Virtual Environment Creation Failed**
   ```
   Error: Failed to create virtual environment
   ```
   **Solution**: Check Python installation and permissions

3. **Package Installation Failed**
   ```
   Error: Failed to install requirements
   ```
   **Solution**: Check internet connection and pip version

4. **Permission Issues (Windows)**
   ```
   Error: Execution of scripts is disabled...
   ```
   **Solution**: The setup.bat automatically handles this with PowerShell execution policy

#### 🔍 Verification Steps

To verify successful installation:
```bash
# Check Python version
python --version

# Check installed packages
pip list

# Verify Streamlit installation
streamlit version
```

## 📈 Future Enhancements

### Planned Features
1. **Predictive Analytics**: Machine learning models for trend forecasting
2. **Comparative Benchmarking**: Compare with national/international standards
3. **Real-time Updates**: Integration with live data sources
4. **Advanced Filters**: Age groups, cancer types, demographic breakdowns
5. **Mobile Optimization**: Enhanced mobile user experience

### Scalability
- **Database Integration**: Support for larger datasets
- **Cloud Deployment**: AWS/Azure deployment options
- **API Integration**: External data source connectivity

## 💡 Benefits

### Decision Making
- **Data-Driven Insights**: Evidence-based policy decisions
- **Visual Clarity**: Complex data made understandable
- **Comprehensive View**: Multiple perspectives on the same data

### Accessibility
- **No Technical Skills Required**: Intuitive interface for all users
- **Interactive Exploration**: Users can explore data independently
- **Professional Presentation**: Ready for stakeholder meetings

### Efficiency
- **Rapid Analysis**: Quick insights from large datasets
- **Automated Processing**: Reduces manual data analysis time
- **Standardized Reporting**: Consistent visualization formats

This dashboard represents a comprehensive solution for cancer mortality analysis in India, combining powerful data visualization with user-friendly design to support healthcare decision-making and research activities.