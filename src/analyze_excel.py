import pandas as pd
import numpy as np
import os
import re

def analyze_excel_file(file_path, file_name):
    """Analyze an Excel file and return detailed information about its sheets"""
    print(f"\n{'='*60}")
    print(f"ANALYZING: {file_name}")
    print(f"{'='*60}")

    try:
        # Read all sheet names
        xl_file = pd.ExcelFile(file_path)
        sheet_names = xl_file.sheet_names

        print(f"\nTotal sheets found: {len(sheet_names)}")
        print("Sheet names:")
        for i, sheet in enumerate(sheet_names, 1):
            print(f"  {i}. {sheet}")

        sheet_analysis = {}

        # Analyze each sheet
        for sheet_name in sheet_names:
            print(f"\n{'─'*40}")
            print(f"SHEET: {sheet_name}")
            print(f"{'─'*40}")

            try:
                # Read the sheet
                df = pd.read_excel(file_path, sheet_name=sheet_name)

                # Basic info
                rows, cols = df.shape
                print(f"Dimensions: {rows} rows × {cols} columns")

                # Column names
                print(f"Columns: {list(df.columns)}")

                # Look for flat-related columns
                flat_columns = []
                for col in df.columns:
                    if any(keyword in str(col).lower() for keyword in ['flat', 'unit', 'apartment', 'block']):
                        flat_columns.append(col)

                print(f"Potential flat-related columns: {flat_columns}")

                # Sample data from first few rows
                print(f"\nFirst 3 rows of data:")
                if not df.empty:
                    print(df.head(3).to_string())

                # Look for flat patterns (like A103, B201, C401)
                flat_patterns = []
                unique_flats = set()

                for col in df.columns:
                    if df[col].dtype == 'object':  # String columns
                        sample_values = df[col].dropna().head(20).astype(str).tolist()

                        # Check for flat number patterns
                        flat_like_values = []
                        for val in sample_values:
                            # Pattern for flat numbers like A103, B201, etc.
                            if re.match(r'^[A-Z]\d{3}$', val) or re.match(r'^[A-Z]\d{2}$', val) or re.match(r'^[A-Z]-\d+$', val):
                                flat_like_values.append(val)
                                unique_flats.add(val)

                        if flat_like_values:
                            flat_patterns.extend(flat_like_values)
                            print(f"Found flat patterns in column '{col}': {flat_like_values[:10]}")

                # Count unique values in potential flat columns
                for col in flat_columns:
                    if col in df.columns:
                        unique_vals = df[col].nunique()
                        print(f"Unique values in '{col}': {unique_vals}")

                        # Show sample values
                        sample_vals = df[col].dropna().unique()[:10]
                        print(f"Sample values: {list(sample_vals)}")

                # Store analysis results
                sheet_analysis[sheet_name] = {
                    'rows': rows,
                    'cols': cols,
                    'columns': list(df.columns),
                    'flat_columns': flat_columns,
                    'flat_patterns': list(set(flat_patterns)),
                    'unique_flats_found': len(unique_flats),
                    'sample_data': df.head(2).to_dict() if not df.empty else {}
                }

                print(f"Unique flat numbers identified: {len(unique_flats)}")
                if unique_flats:
                    print(f"Sample flat numbers: {list(unique_flats)[:10]}")

            except Exception as e:
                print(f"Error reading sheet '{sheet_name}': {str(e)}")
                sheet_analysis[sheet_name] = {'error': str(e)}

        return sheet_analysis

    except Exception as e:
        print(f"Error opening file: {str(e)}")
        return {}

def main():
    aug_file = "/Users/saurabhshukla/poc-workspace/sreedapride/BillingAll_Blocks_Aug-2025_04092025.xlsx"
    jul_file = "/Users/saurabhshukla/poc-workspace/sreedapride/BillingAll_Blocks_Jul-2025_10082025.xlsx"

    # Analyze both files
    aug_analysis = analyze_excel_file(aug_file, "August 2025 Billing")
    jul_analysis = analyze_excel_file(jul_file, "July 2025 Billing")

    # Summary comparison
    print(f"\n{'='*60}")
    print("SUMMARY COMPARISON")
    print(f"{'='*60}")

    print("\nSheets with individual flat data (likely candidates):")

    for file_name, analysis in [("August", aug_analysis), ("July", jul_analysis)]:
        print(f"\n{file_name} file:")
        for sheet_name, data in analysis.items():
            if 'error' not in data:
                flat_count = data.get('unique_flats_found', 0)
                if flat_count > 0 and flat_count < 100:  # Reasonable range for individual flats
                    print(f"  ✓ {sheet_name}: {flat_count} unique flats")
                elif flat_count > 100:
                    print(f"  ⚠ {sheet_name}: {flat_count} entries (might be duplicated data)")
                else:
                    print(f"  - {sheet_name}: No clear flat patterns found")

if __name__ == "__main__":
    main()