"""
Apartment Billing Management System
Comprehensive billing and analysis solution for apartment management.
"""

import streamlit as st
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent))

from components import HeaderComponent, StylingComponent
from tabs.billing_tab import show_billing_tab
from tabs.analysis_tab import show_analysis_tab


def main():
    """Main application function."""
    # Apply minimal styling (just blue tabs, clean look)
    # Options: apply_minimal_styling(), apply_all_styling(), apply_no_styling()
    StylingComponent.apply_minimal_styling()

    # Show main header
    HeaderComponent.show_main_header()

    # Create main tabs
    billing_tab, analysis_tab = st.tabs(["💰 Billing Management", "📊 Analysis"])

    # Billing Tab
    with billing_tab:
        show_billing_tab()

    # Analysis Tab
    with analysis_tab:
        show_analysis_tab()


if __name__ == "__main__":
    # Set page config
    st.set_page_config(
        page_title="Apartment Billing System",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    main()