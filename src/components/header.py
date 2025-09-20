"""
Header Component
Component for displaying headers and navigation.
"""

import streamlit as st


class HeaderComponent:
    """Component for displaying headers and navigation."""

    @staticmethod
    def show_main_header():
        """Display the main application header."""
        st.title("🏢 Apartment Billing Management System")
        st.write("Comprehensive billing and analysis solution for apartment management")

    @staticmethod
    def show_tab_header(title: str, description: str, icon: str = ""):
        """
        Display a header for a specific tab.

        Args:
            title: The tab title
            description: Description of the tab functionality
            icon: Optional icon for the header
        """
        st.header(f"{icon} {title}" if icon else title)
        st.write(description)

    @staticmethod
    def show_section_header(title: str, subtitle: str = "", level: int = 2):
        """
        Display a section header with optional subtitle.

        Args:
            title: The section title
            subtitle: Optional subtitle text
            level: Header level (1-6, where 1 is largest)
        """
        if level == 1:
            st.title(title)
        elif level == 2:
            st.header(title)
        elif level == 3:
            st.subheader(title)
        else:
            st.write(f"**{title}**")

        if subtitle:
            st.write(subtitle)

    @staticmethod
    def show_page_header(title: str, description: str = "", icon: str = ""):
        """
        Display a full page header with title, description and optional icon.

        Args:
            title: Page title
            description: Page description
            icon: Optional icon
        """
        full_title = f"{icon} {title}" if icon else title
        st.title(full_title)
        if description:
            st.markdown(f"*{description}*")
        st.divider()