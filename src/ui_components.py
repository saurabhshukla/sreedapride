"""
UI components for the flat-level water consumption analysis app.
Contains all Streamlit UI elements and display functions.
"""

import streamlit as st
import pandas as pd
from typing import Dict
from io import BytesIO


class FlatAnalysisUI:
    """Handles all UI components for flat analysis."""

    def __init__(self):
        self.display_columns = ["Flat", "Previous Month", "Current Month", "Change Amount", "Change %"]

    def show_header(self):
        """Display the main header and introduction."""
        st.title("Flat-Level Water Consumption Analysis 💧")
        st.write("Upload **last month** and **this month** Excel files to analyze water consumption for individual flats (A101, B101, C101, etc.)")

        st.info("🏠 **Individual Flat Analysis**: This tool analyzes consumption at the apartment level.")

    def show_file_uploaders(self):
        """Display file upload widgets."""
        col1, col2 = st.columns(2)
        with col1:
            last_month_file = st.file_uploader("Upload Last Month File", type=["xls", "xlsx"])
        with col2:
            this_month_file = st.file_uploader("Upload This Month File", type=["xls", "xlsx"])

        return last_month_file, this_month_file

    def show_processing_status(self, last_success: bool, this_success: bool):
        """Display processing status."""
        if last_success and this_success:
            st.success("✅ Both files processed successfully!")
        else:
            if not last_success:
                st.error("❌ Could not process last month file")
            if not this_success:
                st.error("❌ Could not process this month file")

    def show_data_summary(self, df_last: pd.DataFrame, df_this: pd.DataFrame):
        """Display data summary for both months."""
        with st.expander("📊 Flat-Level Data Summary"):
            col1, col2 = st.columns(2)

            with col1:
                st.write("**Last Month (Individual Flats):**")
                st.write(f"- Total flats: {len(df_last)}")
                st.write(f"- Total amount: ₹{df_last['Amount'].sum():,.0f}")
                st.write(f"- Average per flat: ₹{df_last['Amount'].mean():.0f}")
                st.write("**Sample flat data:**")
                st.dataframe(df_last.head())

            with col2:
                st.write("**This Month (Individual Flats):**")
                st.write(f"- Total flats: {len(df_this)}")
                st.write(f"- Total amount: ₹{df_this['Amount'].sum():,.0f}")
                st.write(f"- Average per flat: ₹{df_this['Amount'].mean():.0f}")
                st.write("**Sample flat data:**")
                st.dataframe(df_this.head())

    def show_key_metrics(self, metrics: Dict):
        """Display key metrics."""
        st.subheader("🏠 Individual Flat Metrics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Individual Flats", metrics["total_flats"], help="Total number of apartment units analyzed")
        with col2:
            st.metric("Active Flats", metrics["active_flats"], f"{metrics['active_percentage']:.1f}%", help="Flats with consumption this month")
        with col3:
            st.metric("Total Revenue Change", f"₹{metrics['total_change']:,.0f}", help="Combined change across all flats")
        with col4:
            st.metric("Zero Usage Flats", metrics["zero_usage_flats"], f"{metrics['zero_percentage']:.1f}%", help="Flats with no consumption this month")

    def show_analysis_tabs(self, categories: Dict[str, pd.DataFrame]):
        """Display analysis results in tabs."""
        st.subheader("🔍 Detailed Analysis")

        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📈 Major Increases", "📉 Major Decreases", "⭕ Zero Usage",
            "🆕 New Consumers", "🏆 High Consumers", "🔻 Low Consumers"
        ])

        with tab1:
            self._show_category_data(categories["major_increases"], "significant increases")

        with tab2:
            self._show_category_data(categories["major_decreases"], "significant decreases")

        with tab3:
            self._show_zero_usage_data(categories["zero_consumption"])

        with tab4:
            self._show_new_consumers_data(categories["new_consumers"])

        with tab5:
            self._show_high_consumers_data(categories["high_consumers"])

        with tab6:
            self._show_low_consumers_data(categories["low_consumers"])

    def _show_category_data(self, df: pd.DataFrame, category_name: str):
        """Show data for a specific category."""
        if not df.empty:
            st.write(f"**{len(df)} flats with {category_name}:**")

            # Prepare display data with renamed columns
            display_df = df.copy()
            display_df = display_df.rename(columns={
                "Amount_last_month": "Previous Month",
                "Amount_this_month": "Current Month",
                "Change_Amount": "Change Amount",
                "Change_Percent": "Change %"
            })

            st.dataframe(
                display_df[self.display_columns].style.format({
                    "Previous Month": "₹{:.0f}",
                    "Current Month": "₹{:.0f}",
                    "Change Amount": "₹{:.0f}",
                    "Change %": "{:.1f}%"
                }),
                use_container_width=True
            )
        else:
            st.info(f"No {category_name} found")

    def _show_zero_usage_data(self, df: pd.DataFrame):
        """Show zero usage specific data."""
        if not df.empty:
            st.write(f"**{len(df)} flats went from active to zero usage:**")

            display_df = df.copy()
            display_df = display_df.rename(columns={
                "Amount_last_month": "Previous Month",
                "Change_Amount": "Change Amount"
            })

            display_cols = ["Flat", "Previous Month", "Change Amount"]
            st.dataframe(
                display_df[display_cols].style.format({
                    "Previous Month": "₹{:.0f}",
                    "Change Amount": "₹{:.0f}"
                }),
                use_container_width=True
            )
        else:
            st.info("No flats went from active to zero usage")

    def _show_new_consumers_data(self, df: pd.DataFrame):
        """Show new consumers specific data."""
        if not df.empty:
            st.write(f"**{len(df)} new active flats:**")

            display_df = df.copy()
            display_df = display_df.rename(columns={
                "Amount_this_month": "Current Month",
                "Change_Amount": "Change Amount"
            })

            display_cols = ["Flat", "Current Month", "Change Amount"]
            st.dataframe(
                display_df[display_cols].style.format({
                    "Current Month": "₹{:.0f}",
                    "Change Amount": "₹{:.0f}"
                }),
                use_container_width=True
            )
        else:
            st.info("No new consumers found")

    def _show_high_consumers_data(self, df: pd.DataFrame):
        """Show high consumers specific data."""
        if not df.empty:
            high_threshold = df["Amount_this_month"].min() if not df.empty else 0
            st.write(f"**Top 10% consumers (≥₹{high_threshold:.0f}):**")

            display_df = df.copy()
            display_df = display_df.rename(columns={
                "Amount_this_month": "Current Month",
                "Change_Amount": "Change Amount",
                "Change_Percent": "Change %"
            })

            display_cols = ["Flat", "Current Month", "Change Amount", "Change %"]
            st.dataframe(
                display_df[display_cols].style.format({
                    "Current Month": "₹{:.0f}",
                    "Change Amount": "₹{:.0f}",
                    "Change %": "{:.1f}%"
                }),
                use_container_width=True
            )

    def _show_low_consumers_data(self, df: pd.DataFrame):
        """Show low consumers specific data."""
        if not df.empty:
            low_threshold = df["Amount_this_month"].max() if not df.empty else 0
            st.write(f"**Bottom 10% consumers (≤₹{low_threshold:.0f}):**")

            display_df = df.copy()
            display_df = display_df.rename(columns={
                "Amount_this_month": "Current Month",
                "Change_Amount": "Change Amount",
                "Change_Percent": "Change %"
            })

            display_cols = ["Flat", "Current Month", "Change Amount", "Change %"]
            st.dataframe(
                display_df[display_cols].style.format({
                    "Current Month": "₹{:.0f}",
                    "Change Amount": "₹{:.0f}",
                    "Change %": "{:.1f}%"
                }),
                use_container_width=True
            )
        else:
            st.info("No low consumers found")

    def show_executive_summary(self, metrics: Dict, categories: Dict[str, pd.DataFrame], block_summary: pd.DataFrame):
        """Display executive summary."""
        st.header("📋 Executive Summary")

        summary_text = f"""
        **Monthly Water Consumption Analysis Summary - Flat Level Report**

        **Overall Trends:**
        - Total individual flats analyzed: {metrics['total_flats']}
        - Active flats this month: {metrics['active_flats']} ({metrics['active_percentage']:.1f}%)
        - Total revenue change: ₹{metrics['total_change']:,.0f} ({'+' if metrics['total_change'] >= 0 else ''}{(metrics['total_change']/max(1, metrics['total_flats'])*100):.1f}% per flat avg)
        - Average change per flat: ₹{metrics['avg_change']:.0f}

        **Block-wise Overview:**"""

        for _, row in block_summary.iterrows():
            block = row['Block']
            flats = int(row['Total_Flats'])
            amount = int(row['Block_Amount'])
            avg = int(row['Avg_Per_Flat'])
            change = int(row['Block_Change'])
            summary_text += f"\n        - Block {block}: {flats} flats, ₹{amount:,} total amount (₹{avg} avg/flat), ₹{change:,} change"

        summary_text += f"""

        **Key Findings (Individual Flats):**
        - {len(categories['major_increases'])} flats had significant amount increases
        - {len(categories['major_decreases'])} flats had significant amount decreases
        - {len(categories['zero_consumption'])} flats went from active to zero usage
        - {len(categories['new_consumers'])} flats became newly active
        - {len(categories['high_consumers'])} flats are in the top 10% of consumers
        - {len(categories['low_consumers'])} flats are in the bottom 10% of consumers

        **Action Items for Individual Flats:**
        - Follow up on {len(categories['zero_consumption'])} flats with zero usage for vacancy status
        - Investigate {len(categories['major_increases'])} flats with major increases for potential leaks
        - Verify meter readings for flats with >100% consumption changes
        - Welcome {len(categories['new_consumers'])} new active residents
        - Review {len(categories['low_consumers'])} low-consuming flats for potential maintenance savings
        """

        st.markdown(summary_text)

    def show_download_section(self, merged_data: pd.DataFrame, categories: Dict[str, pd.DataFrame],
                            metrics: Dict, block_summary: pd.DataFrame):
        """Display download section with options."""
        st.header("📥 Download Complete Analysis")

        # Report options
        _, col2 = st.columns([3, 1])
        with col2:
            include_block_summary = st.checkbox("Include Block Summary", value=True,
                                              help="Add a sheet with block-level aggregation for management overview")

        # Create Excel file
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Main flat-level comparison (primary data) - Remove index
            export_merged = merged_data.copy().round(2)
            export_merged["Block"] = export_merged["Flat"].str.extract(r'^([A-Z])', expand=False)

            # Reorder columns to show Flat first, then Block
            cols = ["Flat", "Block"] + [col for col in export_merged.columns if col not in ["Flat", "Block"]]
            export_merged = export_merged[cols]

            export_merged.to_excel(writer, sheet_name="Flat Analysis", index=False)

            # Individual flat analyses - Remove index from all
            for category_name, df in categories.items():
                if not df.empty:
                    sheet_name = f"Flats - {category_name.replace('_', ' ').title()}"
                    df.round(2).to_excel(writer, sheet_name=sheet_name, index=False)

            # Summary sheet with flat-level statistics
            summary_data = {
                "Metric": ["Total Flats", "Active Flats", "Zero Usage Flats", "New Consumer Flats",
                          "Major Increase Flats", "Major Decrease Flats", "Total Revenue Change", "Average Change per Flat"],
                "Value": [metrics['total_flats'], metrics['active_flats'], metrics['zero_usage_flats'], len(categories['new_consumers']),
                         len(categories['major_increases']), len(categories['major_decreases']),
                         f"₹{metrics['total_change']:,.0f}", f"₹{metrics['avg_change']:.0f}"]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name="Flat Summary", index=False)

            # Optional block-wise summary for management
            if include_block_summary and len(merged_data) > 0:
                block_stats = block_summary.copy()
                block_stats.columns = ["Block", "Total_Flats", "Total_Amount", "Avg_Per_Flat", "Total_Change"]
                block_stats.to_excel(writer, sheet_name="Block Summary", index=False)

        st.download_button(
            label="📥 Download Comprehensive Analysis Report",
            data=output.getvalue(),
            file_name=f"flat_consumption_analysis_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


    def show_error_message(self, message: str):
        """Display error message."""
        st.error(f"❌ {message}")

    def show_success_message(self, message: str):
        """Display success message."""
        st.success(f"✅ {message}")

