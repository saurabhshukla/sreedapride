"""
Flat-Level Water Consumption Analysis App
Clean, modular Streamlit application for analyzing apartment water consumption.
"""

import streamlit as st
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent))

from data_processor import FlatDataProcessor, FlatAnalyzer
from ui_components import FlatAnalysisUI


def main():
    """Main application function."""
    # Initialize components
    data_processor = FlatDataProcessor()
    analyzer = FlatAnalyzer()
    ui = FlatAnalysisUI()

    # Show header
    ui.show_header()

    # File upload section
    last_month_file, this_month_file = ui.show_file_uploaders()

    if last_month_file and this_month_file:
        try:
            with st.spinner("🔄 Processing multi-sheet Excel files..."):
                # Process both files
                df_last = data_processor.load_flat_data(last_month_file)
                df_this = data_processor.load_flat_data(this_month_file)

            # Show processing status
            ui.show_processing_status(df_last is not None, df_this is not None)

            if df_last is not None and df_this is not None:

                # Show data summary
                ui.show_data_summary(df_last, df_this)

                # Analyze the data
                analysis_results = analyzer.analyze_consumption_changes(df_last, df_this)

                # Display main analytics dashboard
                st.header("📈 Advanced Analytics Dashboard")

                # Show key metrics
                ui.show_key_metrics(analysis_results["metrics"])

                # Show detailed analysis in tabs
                ui.show_analysis_tabs(analysis_results["categories"])

                # Create block summary for executive summary
                block_summary = analyzer.create_block_summary(analysis_results["merged_data"])

                # Show executive summary
                ui.show_executive_summary(
                    analysis_results["metrics"],
                    analysis_results["categories"],
                    block_summary
                )

                # Download section
                ui.show_download_section(
                    analysis_results["merged_data"],
                    analysis_results["categories"],
                    analysis_results["metrics"],
                    block_summary
                )

            else:
                ui.show_error_message("Could not extract flat data from one or both files")
                ui.show_troubleshooting()

        except Exception as e:
            ui.show_error_message(f"Error processing files: {str(e)}")
            ui.show_troubleshooting()

    # Show instructions
    ui.show_instructions()


if __name__ == "__main__":
    # Set page config
    st.set_page_config(
        page_title="Flat Water Analysis",
        page_icon="💧",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    main()