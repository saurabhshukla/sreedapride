# Sreeda Pride Apartments - Flat-Level Water Consumption Analysis

## ✅ Updated App Features

### 🔻 **Low Consumers Tab Added**
- 6 analysis tabs: Major Increases, Major Decreases, Zero Usage, New Consumers, High Consumers, **Low Consumers**
- Bottom 10% identification for potential savings

### 📊 **Clear Column Names**
- Table headers: "Previous Month", "Current Month", "Change Amount", "Change %"
- No more confusing `Consumption_this` names

### 🚫 **Removed Logging Clutter**
- Clean interface with simple status messages
- No verbose processing logs

### ✅ **Fixed Core Issues**
- Exactly 76 flats (not 1931)
- Proper flat IDs: A101, B201, C401
- Clean Excel exports without row numbers

## Quick Start

```bash
# Create (if needed) and activate a virtual environment
# Create a venv (run once)
# Use `python3` if `python` on your system refers to Python 2 or is missing
python3 -m venv venv

# Activate the venv
# - macOS / Linux (bash, zsh)
source venv/bin/activate
# - fish shell
# source venv/bin/activate.fish
# - csh/tcsh
# source venv/bin/activate.csh
# - Windows PowerShell
# .\venv\Scripts\Activate.ps1
# - Windows Command Prompt
# .\venv\Scripts\activate.bat

# Install dependencies (run inside the activated venv)
# Use `pip` (or `pip3` if your system requires it)
pip install -r requirements.txt

# Run the app locally
streamlit run src/app.py

# For Streamlit Cloud (uses streamlit_app.py automatically)
streamlit run streamlit_app.py

# Test everything
python tests/test_app.py
```

## File Structure

```
├── src/                    # Source code
│   ├── app.py             # Main application
│   ├── data_processor.py  # Data processing logic
│   ├── ui_components.py   # UI components
│   └── report_generator.py # Excel report generation
├── data/                  # Excel data files
│   ├── BillingAll_Blocks_Aug-2025_04092025.xlsx
│   └── BillingAll_Blocks_Jul-2025_10082025.xlsx
├── tests/                 # Test files
│   └── test_app.py       # Test suite
├── docs/                  # Documentation (future)
├── venv/                  # Virtual environment
├── streamlit_app.py      # Streamlit Cloud entry point
├── requirements.txt       # Dependencies
└── README.md             # This file
```
