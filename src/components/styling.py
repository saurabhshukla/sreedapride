"""
Styling Component
Custom CSS styles for the billing management system.
"""

import streamlit as st


class StylingComponent:
    """Component for custom CSS styling."""

    @staticmethod
    def apply_custom_tab_styling():
        """Apply minimal custom styling to make selected tabs blue instead of red."""
        st.markdown("""
        <style>
        /* Tab button styling with horizontal padding and rounded top corners */
        .stTabs [data-baseweb="tab"] {
            padding-left: 20px !important;
            padding-right: 20px !important;
            border-radius: 8px 8px 0px 0px !important;
        }

        /* Simple blue selected tab styling */
        .stTabs [aria-selected="true"] {
            background-color: #1f77b4 !important;
            color: white !important;
        }
        </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def apply_enhanced_tab_styling():
        """Apply enhanced custom styling with borders and effects."""
        st.markdown("""
        <style>
        /* Enhanced tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
        }

        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #f0f2f6;
            border-radius: 4px 4px 0px 0px;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
            border: 1px solid #d6d6d6;
        }

        /* Selected tab styling - Blue theme */
        .stTabs [aria-selected="true"] {
            background-color: #1f77b4 !important;
            color: white !important;
            border-bottom: 2px solid #1f77b4 !important;
        }

        /* Hover effect for tabs */
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #e6f3ff;
            color: #1f77b4;
        }

        /* Tab content panel */
        .stTabs [data-baseweb="tab-panel"] {
            background-color: white;
            border: 1px solid #d6d6d6;
            border-top: none;
            padding: 20px;
            border-radius: 0px 0px 4px 4px;
        }
        </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def apply_general_styling():
        """Apply general custom styling to the application."""
        st.markdown("""
        <style>
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Custom styling for metrics */
        .metric-container {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }

        /* Custom styling for info boxes */
        .stAlert > div {
            border-radius: 8px;
        }

        /* Custom styling for buttons - match selected tab blue */
        .stButton > button {
            border-radius: 8px;
            border: 1px solid #1f77b4;
            background-color: #1f77b4 !important;
            color: white !important;
            font-weight: 500;
        }

        .stButton > button:hover {
            background-color: #0066cc !important;
            border-color: #0066cc !important;
            transform: translateY(-1px);
            box-shadow: 0 2px 4px rgba(31, 119, 180, 0.3);
        }

        /* Primary button styling to match tab blue */
        .stButton > button[kind="primary"] {
            background-color: #1f77b4 !important;
            border-color: #1f77b4 !important;
            color: white !important;
        }

        .stButton > button[kind="primary"]:hover {
            background-color: #0066cc !important;
            border-color: #0066cc !important;
        }

        /* Disabled button styling */
        .stButton > button:disabled {
            background-color: #e9ecef !important;
            border-color: #dee2e6 !important;
            color: #6c757d !important;
            cursor: not-allowed !important;
            transform: none !important;
            box-shadow: none !important;
        }

        .stButton > button[kind="primary"]:disabled {
            background-color: #e9ecef !important;
            border-color: #dee2e6 !important;
            color: #6c757d !important;
        }

        /* Flexbox container for button-warning combinations */
        .button-warning-container {
            display: flex !important;
            align-items: center !important;
            gap: 15px !important;
            flex-wrap: wrap !important;
            min-height: 56px !important;
        }

        /* Target the columns within the container */
        .button-warning-container .stColumn {
            display: flex !important;
            align-items: center !important;
            height: 56px !important;
        }

        /* Target button and warning elements within the container */
        .button-warning-container .stButton,
        .button-warning-container .stAlert {
            height: 56px !important;
            display: flex !important;
            align-items: center !important;
        }

        /* Legacy class for backward compatibility */
        .button-warning-flex {
            display: flex !important;
            align-items: center !important;
            gap: 15px !important;
            flex-wrap: wrap !important;
            min-height: 48px !important;
        }

        /* Styles for new container */
        .button-warning-container .stButton {
            flex: 0 0 auto !important;
            margin-bottom: 0 !important;
            width: auto !important;
        }

        .button-warning-container .stAlert {
            flex: 1 !important;
            margin-bottom: 0 !important;
            min-width: 200px !important;
            height: 56px !important;
            display: flex !important;
            align-items: center !important;
        }

        .button-warning-container .stAlert > div {
            padding: 8px 12px !important;
            margin: 0 !important;
            height: 100% !important;
            display: flex !important;
            align-items: center !important;
            font-size: 14px !important;
            line-height: 1.2 !important;
        }

        .button-warning-container .stButton > button {
            width: auto !important;
            min-width: auto !important;
            height: 56px !important;
            display: flex !important;
            align-items: center !important;
            padding: 0.5rem 1rem !important;
        }

        /* Legacy styles for backward compatibility */
        .button-warning-flex .stButton {
            flex: 0 0 auto !important;
            margin-bottom: 0 !important;
            width: auto !important;
        }

        .button-warning-flex .stAlert {
            flex: 1 !important;
            margin-bottom: 0 !important;
            min-width: 200px !important;
            height: 48px !important;
            display: flex !important;
            align-items: center !important;
        }

        .button-warning-flex .stAlert > div {
            padding: 8px 12px !important;
            margin: 0 !important;
            height: 100% !important;
            display: flex !important;
            align-items: center !important;
            font-size: 14px !important;
            line-height: 1.2 !important;
        }

        /* Make buttons inside flex containers auto-size */
        .button-warning-flex .stButton > button {
            width: auto !important;
            min-width: auto !important;
            height: 48px !important;
            display: flex !important;
            align-items: center !important;
            padding: 0.5rem 1rem !important;
        }
        </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def apply_minimal_styling():
        """Apply minimal styling (just blue tabs, no other changes)."""
        StylingComponent.apply_custom_tab_styling()

    @staticmethod
    def apply_all_styling():
        """Apply all custom styling (enhanced tabs + general)."""
        StylingComponent.apply_enhanced_tab_styling()
        StylingComponent.apply_general_styling()

    @staticmethod
    def apply_no_styling():
        """Apply no custom styling - use default Streamlit appearance."""
        pass