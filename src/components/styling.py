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

        /* Custom styling for buttons */
        .stButton > button {
            border-radius: 8px;
            border: 1px solid #1f77b4;
            background-color: #1f77b4;
            color: white;
        }

        .stButton > button:hover {
            background-color: #0066cc;
            border-color: #0066cc;
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