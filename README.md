# 📊 India E-Commerce Sales Analytics Dashboard

> **Advanced Analytics Platform with Predictive Intelligence, Anomaly Detection & Seasonality Analysis**

A professional, enterprise-grade Streamlit-based dashboard for comprehensive analysis of Indian e-commerce sales data. Features real-time analytics, predictive forecasting, anomaly detection, and advanced time-series analysis.

---

## ✨ Key Features

### 📈 **7 Comprehensive Tabs**

1. **Overview Tab** - Dashboard KPIs and key metrics
2. **Predictions Tab** - Sales forecasting with multiple scenarios
3. **Profitability Tab** - Profit margin analysis by region and category
4. **Analysis Tab** - Advanced insights with heatmaps
5. **Time-Series Tab** - MoM/YoY growth, seasonal patterns, decomposition
6. **Anomalies Tab** - Statistical anomaly detection with Z-score analysis
7. **Supply & Demand Tab** - Product demand scoring and supplier metrics

### 🎯 **Advanced Filtering System**

- 📅 **Date Range Filter** - Analyze specific time periods
- 🏙️ **City Multi-Select** - Choose one or multiple cities
- 📦 **Category Filter** - Filter by product categories
- 💰 **Profit Margin Range** - Set margin thresholds
- 🛍️ **Discount Range** - Filter by discount percentage
- 📊 **Quantity Range** - Filter by order quantity
- 💵 **Sales Range** - Filter by sales amount
- **Live Record Counter** - Shows filtered vs total records in real-time

### 📊 **Analytics Capabilities**

| Feature | Description |
|---------|-------------|
| **Sales Forecasting** | Linear regression-based predictions (7-90 days) |
| **Seasonal Analysis** | Day-of-week & monthly patterns |
| **Decomposition** | Trend, seasonal, and residual components |
| **MoM Analysis** | Month-over-month growth metrics |
| **Anomaly Detection** | Z-score based outlier identification |
| **Demand Scoring** | Product demand ranking system |
| **City Heatmaps** | Sales intensity by city and category |
| **Profit Analysis** | Detailed profitability metrics |

---

## 📦 Dataset Overview

**India E-Commerce Sales Data**

| Metric | Value |
|--------|-------|
| **Records** | 1,500+ transactions |
| **Date Range** | 12-15 months |
| **Cities** | 20+ Indian cities |
| **Categories** | 5+ product categories |
| **Total Sales** | ₹200M+ |
| **Total Profit** | ₹50M+ |

---

## 🚀 Getting Started

### Quick Start (3 Steps)

**Step 1: Install Dependencies**
```bash
pip install -r requirements.txt
pip install statsmodels
```

**Step 2: Run Dashboard**
```bash
python -m streamlit run src/app.py
```

**Step 3: Open Browser**
```
http://localhost:8501
```

### Alternative Launch Methods

**Windows Batch File:**
```bash
double-click run_dashboard.bat
```

**PowerShell:**
```powershell
.\run_dashboard.ps1
```

---

## 📋 Requirements

```
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.17.0
openpyxl>=3.10.0
scikit-learn>=1.3.0
statsmodels>=0.14.0
numpy>=1.24.0
scipy>=1.11.0
```

---

## 📁 Project Structure

```
Good_Dashboard-main/
├── src/
│   └── app.py                       # Main dashboard application
├── data/
│   └── India_ECommerce_Sales.xlsx   # Dataset
├── .streamlit/
│   └── config.toml                  # Streamlit configuration
├── run_dashboard.bat                # Windows batch launcher
├── run_dashboard.ps1                # PowerShell launcher
├── requirements.txt                 # Python dependencies
├── README.md                        # Overview (this file)
├── INSTALLATION.md                  # Detailed setup guide
├── USER_GUIDE.md                    # How to use features
├── ARCHITECTURE.md                  # Technical details
└── FEATURES.md                      # Complete feature list
```

---

## 📖 Documentation Files

- **README.md** (this file) - Project overview and quick start
- **INSTALLATION.md** - Detailed installation instructions
- **USER_GUIDE.md** - How to use each feature
- **ARCHITECTURE.md** - Technical architecture and design
- **FEATURES.md** - Complete feature documentation
- **PROJECT_STRUCTURE.md** - Directory organization

---

## 🎓 How to Use

See **USER_GUIDE.md** for detailed instructions on:
- Applying filters
- Navigating each tab
- Interpreting charts
- Exporting data
- Common workflows

---

## 🔧 Technical Details

See **ARCHITECTURE.md** for:
- Code structure
- Key functions
- Technologies used
- Data flow
- Configuration details

---

## ⚙️ Installation Help

See **INSTALLATION.md** for:
- Python setup
- Dependency installation
- Troubleshooting
- Configuration
- Environment setup

---

## 📊 Feature Details

See **FEATURES.md** for:
- Complete feature list
- Advanced filtering options
- Time-series analysis
- Anomaly detection
- Supplier metrics

---

## 🔍 Key Insights

With this dashboard, you can discover:

- 📈 **Seasonal Trends** - Peak buying seasons
- 🏙️ **Regional Performance** - Best cities
- 📦 **Product Demand** - Top sellers
- 💰 **Profit Margins** - Margin by category
- 🚨 **Anomalies** - Unusual patterns
- 📊 **Growth Rates** - MoM performance
- 🔮 **Forecasts** - Future predictions
- 💵 **Discount Impact** - Pricing analysis

---

## 🌟 Highlights

✅ **Production Ready** - Fully tested and optimized  
✅ **Easy to Use** - Intuitive interface with helpful filters  
✅ **Comprehensive** - 7 analysis tabs with 50+ metrics  
✅ **Fast** - Optimized data loading and caching  
✅ **Well Documented** - Multiple guide files  
✅ **Professional** - Enterprise-grade analytics  

---

## 📞 Getting Help

1. **Installation Issues?** → See `INSTALLATION.md`
2. **How to use features?** → See `USER_GUIDE.md`
3. **Technical questions?** → See `ARCHITECTURE.md`
4. **Feature details?** → See `FEATURES.md`
5. **Directory structure?** → See `PROJECT_STRUCTURE.md`

---

**Version:** 2.0 | **Status:** ✅ Production Ready | **Last Updated:** November 18, 2025
