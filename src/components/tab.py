"""
Tab Component
Component for creating and managing tabs in the application.
"""

import streamlit as st
from typing import Tuple, Any


class TabComponent:
    """Component for creating and managing tabs in the application."""

    @staticmethod
    def create_main_tabs() -> Tuple[Any, Any]:
        """
        Create the main application tabs (Billing and Analysis).

        Returns:
            Tuple of tab containers (billing_tab, analysis_tab)
        """
        billing_tab, analysis_tab = st.tabs(["💰 Billing Management", "📊 Analysis"])
        return billing_tab, analysis_tab

    @staticmethod
    def create_custom_tabs(tab_names: list) -> list:
        """
        Create custom tabs with specified names.

        Args:
            tab_names: List of tab names/labels

        Returns:
            List of tab containers
        """
        return st.tabs(tab_names)

    @staticmethod
    def create_analysis_subtabs():
        """
        Create sub-tabs for analysis functionality.

        Returns:
            Tuple of analysis sub-tab containers
        """
        return st.tabs([
            "📈 Major Increases", "📉 Major Decreases", "⭕ Zero Usage",
            "🆕 New Consumers", "🏆 High Consumers", "🔻 Low Consumers"
        ])