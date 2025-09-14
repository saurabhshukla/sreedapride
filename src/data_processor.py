"""
Data processing module for flat-level water consumption analysis.
Handles Excel file reading, data cleaning, and analysis.
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple, Dict, List


class FlatDataProcessor:
    """Processes flat-level water consumption data from Excel files."""

    def __init__(self):
        self.priority_sheets = ["Final allocation monthly", "final allocation", "allocation"]
        self.exclude_keywords = ["wegot", "charges", "chart", "input", "dues_tmpt"]

    def load_flat_data(self, file) -> Optional[pd.DataFrame]:
        """
        Load flat-level data from Excel file.

        Args:
            file: Excel file (file-like object or path)

        Returns:
            DataFrame with flat data or None if failed
        """
        try:
            # Get all sheet names
            xl_file = pd.ExcelFile(file)
            sheet_names = xl_file.sheet_names

            # Determine processing order
            processing_order = self._get_processing_order(sheet_names)

            # Process sheets in priority order
            for sheet_name in processing_order:
                flat_data = self._process_sheet(file, sheet_name)
                if flat_data is not None:
                    return flat_data

            return None

        except Exception:
            return None

    def _get_processing_order(self, sheet_names: List[str]) -> List[str]:
        """Determine the order to process sheets, prioritizing billing sheets."""
        processing_order = []

        # Add priority sheets first
        for priority in self.priority_sheets:
            for sheet_name in sheet_names:
                if priority in sheet_name.lower():
                    processing_order.append(sheet_name)
                    break

        # Add remaining sheets (excluding problematic ones)
        for sheet_name in sheet_names:
            if (sheet_name not in processing_order and
                not any(exclude in sheet_name.lower() for exclude in self.exclude_keywords)):
                processing_order.append(sheet_name)

        return processing_order

    def _process_sheet(self, file, sheet_name: str) -> Optional[pd.DataFrame]:
        """Process a single sheet to extract flat data."""
        try:
            # Load sheet data
            raw = pd.read_excel(file, sheet_name=sheet_name, header=None)

            if raw.empty:
                return None

            # Process based on sheet type
            if "allocation" in sheet_name.lower():
                return self._process_allocation_sheet(file, sheet_name, raw)
            elif "dues_tmpt" in sheet_name.lower():
                return self._process_billing_sheet(file, sheet_name, raw)
            else:
                return self._process_standard_sheet(file, sheet_name, raw)

        except Exception:
            return None

    def _process_billing_sheet(self, file, sheet_name: str, raw: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Process billing sheets with Block+Flat structure."""
        # Find header row
        header_row = self._find_billing_header(raw)
        if header_row is None:
            return None

        # Load with proper header
        df = pd.read_excel(file, sheet_name=sheet_name, header=header_row)
        df.columns = [str(c).strip().replace('\n', ' ').replace('\r', ' ') for c in df.columns]

        # Find required columns
        block_col, flat_col, amount_col = self._find_billing_columns(df)
        if not all([block_col, flat_col, amount_col]):
            return None

        # Process the data
        return self._create_flat_data(df, block_col, flat_col, amount_col)

    def _find_billing_header(self, raw: pd.DataFrame) -> Optional[int]:
        """Find the header row in billing sheet."""
        for i in range(min(10, len(raw))):
            row = raw.iloc[i]
            row_str = row.astype(str).str.lower()
            row_text = ' '.join(row_str.values)

            has_block = "block" in row_text
            has_flat = "flat" in row_text
            has_amount = any(keyword in row_text for keyword in ["amount", "due", "bill"])

            if has_block and has_flat and has_amount:
                return i

        return None

    def _find_billing_columns(self, df: pd.DataFrame) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Find Block, Flat, and Amount columns in billing sheet."""
        block_col = None
        flat_col = None
        amount_col = None

        for col in df.columns:
            col_lower = str(col).lower()
            if "block" in col_lower and block_col is None:
                block_col = col
            elif "flat" in col_lower and "square" not in col_lower and flat_col is None:
                flat_col = col
            elif any(keyword in col_lower for keyword in ["amount*", "amount", "currentdue", "due"]) and amount_col is None:
                amount_col = col

        return block_col, flat_col, amount_col

    def _create_flat_data(self, df: pd.DataFrame, block_col: str, flat_col: str, amount_col: str) -> pd.DataFrame:
        """Create clean flat data from billing sheet."""
        # Extract relevant columns
        df_clean = df[[block_col, flat_col, amount_col]].copy()
        df_clean.columns = ["Block", "FlatNum", "Amount"]

        # Clean Block and Flat data - remove brackets
        df_clean["Block"] = df_clean["Block"].astype(str).str.strip().str.replace('<', '').str.replace('>', '')
        df_clean["FlatNum"] = df_clean["FlatNum"].astype(str).str.strip().str.replace('<', '').str.replace('>', '')

        # Combine Block + Flat to create proper flat identifiers
        df_clean["Flat"] = df_clean["Block"] + df_clean["FlatNum"]

        # Clean amount data
        df_clean["Amount"] = pd.to_numeric(df_clean["Amount"], errors='coerce').fillna(0)

        # Remove invalid rows
        df_clean = df_clean[
            df_clean["Block"].notna() &
            df_clean["FlatNum"].notna() &
            (df_clean["Block"] != "") &
            (df_clean["FlatNum"] != "") &
            (df_clean["Block"] != "nan") &
            (df_clean["FlatNum"] != "nan") &
            (~df_clean["Block"].str.lower().str.contains("total|sum|grand", na=False))
        ]

        # Select final columns with proper names
        df_final = df_clean[["Flat", "Amount"]].copy()

        return df_final

    def _process_allocation_sheet(self, file, sheet_name: str, raw: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Process allocation sheets with Apartment and Total columns."""
        # Find header row for allocation sheets
        header_row = self._find_allocation_header(raw)
        if header_row is None:
            return None

        # Load with proper header
        df = pd.read_excel(file, sheet_name=sheet_name, header=header_row)
        df.columns = [str(c).strip().replace('\n', ' ').replace('\r', ' ') for c in df.columns]

        # Find required columns
        apartment_col, total_col = self._find_allocation_columns(df)
        if not all([apartment_col, total_col]):
            return None

        # Process the data
        return self._create_allocation_data(df, apartment_col, total_col)

    def _find_allocation_header(self, raw: pd.DataFrame) -> Optional[int]:
        """Find the header row in allocation sheet."""
        for i in range(min(15, len(raw))):
            row = raw.iloc[i]
            row_str = row.astype(str).str.lower()
            row_text = ' '.join(row_str.values)

            has_apartment = any(keyword in row_text for keyword in ["apartment", "apartm", "flat"])
            has_total = "total" in row_text
            has_owner = "owner" in row_text

            if has_apartment and has_total and has_owner:
                return i

        return None

    def _find_allocation_columns(self, df: pd.DataFrame) -> Tuple[Optional[str], Optional[str]]:
        """Find Apartment and Total columns in allocation sheet."""
        apartment_col = None
        total_col = None

        for col in df.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in ["apartment", "apartm", "flat"]) and apartment_col is None:
                apartment_col = col
            elif "total" in col_lower and total_col is None:
                total_col = col

        return apartment_col, total_col

    def _create_allocation_data(self, df: pd.DataFrame, apartment_col: str, total_col: str) -> pd.DataFrame:
        """Create clean flat data from allocation sheet."""
        # Extract relevant columns
        df_clean = df[[apartment_col, total_col]].copy()
        df_clean.columns = ["Flat", "Amount"]

        # Clean flat identifiers - handle different formats
        df_clean["Flat"] = df_clean["Flat"].astype(str).str.strip()

        # Clean amount data
        df_clean["Amount"] = pd.to_numeric(df_clean["Amount"], errors='coerce').fillna(0)

        # Remove invalid rows
        df_clean = df_clean[
            df_clean["Flat"].notna() &
            (df_clean["Flat"] != "") &
            (df_clean["Flat"] != "nan") &
            (df_clean["Flat"] != "None") &
            (~df_clean["Flat"].str.lower().str.contains("total|sum|grand", na=False))
        ]

        # Select final columns
        df_final = df_clean[["Flat", "Amount"]].copy()

        return df_final

    def _process_standard_sheet(self, file, sheet_name: str, raw: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Process standard sheets with apartment column."""
        # This would be implemented for other sheet types if needed
        # Parameters kept for interface compatibility
        _ = file, sheet_name, raw
        return None


class FlatAnalyzer:
    """Analyzes flat-level water consumption data."""

    def __init__(self):
        self.increase_threshold = 200
        self.percentage_threshold = 25

    def analyze_consumption_changes(self, df_last: pd.DataFrame, df_this: pd.DataFrame) -> Dict:
        """
        Analyze consumption changes between two months.

        Args:
            df_last: Last month's data with columns ['Flat', 'Amount']
            df_this: This month's data with columns ['Flat', 'Amount']

        Returns:
            Dictionary containing analysis results
        """
        # Merge data with clear column names
        merged = pd.merge(df_last, df_this, on="Flat", how="outer", suffixes=("_last_month", "_this_month"))
        merged = merged.fillna(0)

        # Calculate changes with clear column names
        merged["Change_Amount"] = merged["Amount_this_month"] - merged["Amount_last_month"]
        merged["Change_Percent"] = np.where(
            merged["Amount_last_month"] > 0,
            (merged["Change_Amount"] / merged["Amount_last_month"]) * 100,
            np.where(merged["Amount_this_month"] > 0, 100, 0)
        )

        # Calculate key metrics
        metrics = self._calculate_metrics(merged)

        # Categorize flats
        categories = self._categorize_flats(merged)

        return {
            "merged_data": merged,
            "metrics": metrics,
            "categories": categories
        }

    def _calculate_metrics(self, merged: pd.DataFrame) -> Dict:
        """Calculate key metrics from merged data."""
        total_change = merged["Change_Amount"].sum()
        avg_change = merged["Change_Amount"].mean()
        active_flats = len(merged[merged["Amount_this_month"] > 0])
        zero_usage = len(merged[merged["Amount_this_month"] == 0])


        return {
            "total_flats": len(merged),
            "active_flats": active_flats,
            "zero_usage_flats": zero_usage,
            "total_change": total_change,
            "avg_change": avg_change,
            "active_percentage": (active_flats / len(merged)) * 100 if len(merged) > 0 else 0,
            "zero_percentage": (zero_usage / len(merged)) * 100 if len(merged) > 0 else 0
        }

    def _categorize_flats(self, merged: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Categorize flats based on consumption patterns."""
        categories = {}

        # Major increases
        categories["major_increases"] = merged[
            ((merged["Change_Amount"] > self.increase_threshold) |
             (merged["Change_Percent"] > self.percentage_threshold)) &
            (merged["Change_Amount"] > 0)
        ].sort_values("Change_Amount", ascending=False)

        # Major decreases
        categories["major_decreases"] = merged[
            ((merged["Change_Amount"] < -self.increase_threshold) |
             (merged["Change_Percent"] < -self.percentage_threshold)) &
            (merged["Change_Amount"] < 0)
        ].sort_values("Change_Amount")

        # Zero consumption (previously active)
        categories["zero_consumption"] = merged[
            (merged["Amount_this_month"] == 0) &
            (merged["Amount_last_month"] > 0)
        ].sort_values("Amount_last_month", ascending=False)

        # New consumers
        categories["new_consumers"] = merged[
            (merged["Amount_last_month"] == 0) &
            (merged["Amount_this_month"] > 0)
        ].sort_values("Amount_this_month", ascending=False)

        # High consumers (top 10%)
        high_threshold = merged["Amount_this_month"].quantile(0.9)
        categories["high_consumers"] = merged[
            merged["Amount_this_month"] >= high_threshold
        ].sort_values("Amount_this_month", ascending=False)

        # Low consumers (bottom 10% of active flats)
        active_flats = merged[merged["Amount_this_month"] > 0]
        if len(active_flats) > 0:
            low_threshold = active_flats["Amount_this_month"].quantile(0.1)
            categories["low_consumers"] = active_flats[
                active_flats["Amount_this_month"] <= low_threshold
            ].sort_values("Amount_this_month", ascending=True)
        else:
            categories["low_consumers"] = pd.DataFrame()

        return categories

    def create_block_summary(self, merged: pd.DataFrame) -> pd.DataFrame:
        """Create block-wise summary from flat-level data."""
        merged_summary = merged.copy()
        merged_summary["Block"] = merged_summary["Flat"].str.extract(r'^([A-Z])', expand=False).fillna('Unknown')

        block_summary = merged_summary.groupby("Block").agg({
            "Flat": "count",
            "Amount_this_month": ["sum", "mean"],
            "Change_Amount": "sum"
        }).round(0)

        block_summary.columns = ["Total_Flats", "Block_Amount", "Avg_Per_Flat", "Block_Change"]
        return block_summary.reset_index()