"""
Report generation utilities for flat-level water consumption analysis.
Handles Excel export and data formatting.
"""

import pandas as pd
from io import BytesIO
from typing import Dict


class FlatReportGenerator:
    """Generates Excel reports for flat analysis."""

    def __init__(self):
        self.format_currency = "₹{:.0f}"
        self.format_percentage = "{:.1f}%"

    def create_comprehensive_report(self, merged_data: pd.DataFrame,
                                   categories: Dict[str, pd.DataFrame],
                                   metrics: Dict,
                                   block_summary: pd.DataFrame,
                                   include_block_summary: bool = True) -> BytesIO:
        """
        Create a comprehensive Excel report with all analysis data.

        Args:
            merged_data: Main comparison data
            categories: Categorized flat data
            metrics: Key metrics
            block_summary: Block-wise summary
            include_block_summary: Whether to include block summary sheet

        Returns:
            BytesIO object containing Excel file
        """
        output = BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Main flat-level comparison (primary data) - Remove index
            self._write_main_analysis(writer, merged_data)

            # Individual flat analyses - Remove index from all
            self._write_category_analyses(writer, categories)

            # Summary sheet with flat-level statistics
            self._write_summary_sheet(writer, metrics, categories)

            # Optional block-wise summary for management
            if include_block_summary and len(merged_data) > 0:
                self._write_block_summary(writer, block_summary)

        output.seek(0)
        return output

    def _write_main_analysis(self, writer, merged_data: pd.DataFrame):
        """Write the main flat analysis sheet."""
        export_merged = merged_data.copy().round(2)

        # Add block column for reference but keep flat as primary
        export_merged["Block"] = export_merged["Flat"].str.extract(r'^([A-Z])', expand=False)

        # Reorder columns to show Flat first, then Block
        cols = ["Flat", "Block"] + [col for col in export_merged.columns if col not in ["Flat", "Block"]]
        export_merged = export_merged[cols]

        # Rename columns for clarity
        column_mapping = {
            "Amount_last_month": "Last Month Amount",
            "Amount_this_month": "This Month Amount",
            "Change_Amount": "Change (₹)",
            "Change_Percent": "Change (%)"
        }
        export_merged = export_merged.rename(columns=column_mapping)

        export_merged.to_excel(writer, sheet_name="Flat Analysis", index=False)

    def _write_category_analyses(self, writer, categories: Dict[str, pd.DataFrame]):
        """Write individual category analysis sheets."""
        category_sheet_names = {
            "major_increases": "Flats - Major Increases",
            "major_decreases": "Flats - Major Decreases",
            "zero_consumption": "Flats - Zero Usage",
            "new_consumers": "Flats - New Consumers",
            "high_consumers": "Flats - High Consumers"
        }

        column_mapping = {
            "Amount_last_month": "Last Month Amount",
            "Amount_this_month": "This Month Amount",
            "Change_Amount": "Change (₹)",
            "Change_Percent": "Change (%)"
        }

        for category_name, df in categories.items():
            if not df.empty and category_name in category_sheet_names:
                df_export = df.copy().round(2)
                df_export = df_export.rename(columns=column_mapping)
                sheet_name = category_sheet_names[category_name]
                df_export.to_excel(writer, sheet_name=sheet_name, index=False)

    def _write_summary_sheet(self, writer, metrics: Dict, categories: Dict[str, pd.DataFrame]):
        """Write the summary statistics sheet."""
        summary_data = {
            "Metric": [
                "Total Flats",
                "Active Flats",
                "Zero Usage Flats",
                "New Consumer Flats",
                "Major Increase Flats",
                "Major Decrease Flats",
                "Total Revenue Change",
                "Average Change per Flat"
            ],
            "Value": [
                metrics['total_flats'],
                metrics['active_flats'],
                metrics['zero_usage_flats'],
                len(categories['new_consumers']),
                len(categories['major_increases']),
                len(categories['major_decreases']),
                f"₹{metrics['total_change']:,.0f}",
                f"₹{metrics['avg_change']:.0f}"
            ]
        }

        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name="Flat Summary", index=False)

    def _write_block_summary(self, writer, block_summary: pd.DataFrame):
        """Write the block summary sheet."""
        block_stats = block_summary.copy()
        block_stats.columns = [
            "Block",
            "Total_Flats",
            "Total_Amount",
            "Avg_Per_Flat",
            "Total_Change"
        ]

        # Rename columns for clarity
        column_mapping = {
            "Total_Flats": "Number of Flats",
            "Total_Amount": "Total Amount (₹)",
            "Avg_Per_Flat": "Average per Flat (₹)",
            "Total_Change": "Total Change (₹)"
        }
        block_stats = block_stats.rename(columns=column_mapping)

        block_stats.to_excel(writer, sheet_name="Block Summary", index=False)

    def format_dataframe_for_display(self, df: pd.DataFrame, columns: list) -> pd.DataFrame:
        """Format dataframe for display with proper currency formatting."""
        df_formatted = df[columns].copy()

        # Apply formatting to currency columns
        currency_columns = [col for col in df_formatted.columns if "Amount" in col or "Change" in col and "Percent" not in col]
        percentage_columns = [col for col in df_formatted.columns if "Percent" in col]

        formatting = {}
        for col in currency_columns:
            formatting[col] = self.format_currency

        for col in percentage_columns:
            formatting[col] = self.format_percentage

        if formatting:
            return df_formatted.style.format(formatting)
        else:
            return df_formatted