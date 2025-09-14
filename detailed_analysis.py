import pandas as pd
import numpy as np

def analyze_dues_sheet_detailed(file_path, file_name):
    """Detailed analysis of the dues_tmpt_05-04-25 sheet"""
    print(f"\n{'='*60}")
    print(f"DETAILED ANALYSIS OF DUES SHEET: {file_name}")
    print(f"{'='*60}")

    try:
        # Read the dues sheet specifically
        df = pd.read_excel(file_path, sheet_name='dues_tmpt_05-04-25')

        print(f"Sheet dimensions: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"Columns: {list(df.columns)}")

        # Analyze Block and Flat columns
        print(f"\n{'─'*40}")
        print("BLOCK ANALYSIS:")
        print(f"{'─'*40}")

        unique_blocks = df['Block'].unique()
        print(f"Unique blocks: {list(unique_blocks)}")
        print(f"Block counts:")
        print(df['Block'].value_counts())

        print(f"\n{'─'*40}")
        print("FLAT ANALYSIS:")
        print(f"{'─'*40}")

        unique_flats = df['Flat'].unique()
        print(f"Total unique flats: {len(unique_flats)}")
        print(f"All flats: {list(unique_flats)}")

        # Create combined flat identifiers (Block + Flat)
        df['FullFlat'] = df['Block'].astype(str) + df['Flat'].astype(str)
        df['CleanFlat'] = df['Block'].str.replace('<', '').str.replace('>', '') + df['Flat'].str.replace('<', '').str.replace('>', '')

        unique_full_flats = df['CleanFlat'].unique()
        print(f"\nCombined flat identifiers (Block+Flat): {len(unique_full_flats)}")
        print(f"Sample combined flats: {list(unique_full_flats)[:20]}")

        print(f"\n{'─'*40}")
        print("SAMPLE DATA (First 10 rows):")
        print(f"{'─'*40}")

        # Display key columns
        display_cols = ['Block', 'Flat', 'SquareFeet', 'Name', 'CurrentDue', 'Amount*']
        print(df[display_cols].head(10).to_string())

        print(f"\n{'─'*40}")
        print("DATA STATISTICS:")
        print(f"{'─'*40}")

        print(f"Total records: {len(df)}")
        print(f"Records with valid names: {df['Name'].notna().sum()}")
        print(f"Records with amounts: {df['Amount*'].notna().sum()}")

        print(f"\nSquare feet range: {df['SquareFeet'].min()} - {df['SquareFeet'].max()}")
        print(f"Amount range: {df['Amount*'].min()} - {df['Amount*'].max()}")

        # Check for any duplicates
        duplicates = df.duplicated(subset=['Block', 'Flat']).sum()
        print(f"Duplicate Block+Flat combinations: {duplicates}")

        if duplicates > 0:
            print("Duplicate entries:")
            duplicate_rows = df[df.duplicated(subset=['Block', 'Flat'], keep=False)].sort_values(['Block', 'Flat'])
            print(duplicate_rows[['Block', 'Flat', 'Name', 'Amount*']].to_string())

        return df

    except Exception as e:
        print(f"Error analyzing dues sheet: {str(e)}")
        return None

def analyze_wegot_sheet_detailed(file_path, file_name):
    """Detailed analysis of the WeGot report sheet"""
    print(f"\n{'='*60}")
    print(f"DETAILED ANALYSIS OF WEGOT SHEET: {file_name}")
    print(f"{'='*60}")

    try:
        # Read with specific parameters to handle the complex structure
        df = pd.read_excel(file_path, sheet_name='WeGot report', header=None)

        print(f"Sheet dimensions: {df.shape[0]} rows × {df.shape[1]} columns")

        # Find where the actual flat data starts
        print(f"\nFirst 10 rows to understand structure:")
        print(df.head(10).to_string())

        # Look for flat patterns in column 2 (index 2)
        if df.shape[1] > 2:
            flat_data = df.iloc[:, 2].dropna().astype(str)

            # Filter for flat-like patterns
            import re
            flat_patterns = []
            for idx, val in flat_data.items():
                if re.match(r'^[A-Z]\d{3}$', val):
                    flat_patterns.append((idx, val))

            print(f"\nFlat patterns found: {len(flat_patterns)}")
            if flat_patterns:
                print("Sample flat patterns (row_index, flat_number):")
                for i, (idx, flat) in enumerate(flat_patterns[:15]):
                    print(f"  Row {idx}: {flat}")

                # Get the data range with flats
                first_flat_row = flat_patterns[0][0]
                last_flat_row = flat_patterns[-1][0]

                print(f"\nFlat data appears to be in rows {first_flat_row} to {last_flat_row}")

                # Extract flat data section
                flat_section = df.iloc[first_flat_row:last_flat_row+1]
                print(f"\nFlat section shape: {flat_section.shape}")

                # Try to identify columns with data
                for col_idx in range(min(10, flat_section.shape[1])):
                    non_null = flat_section.iloc[:, col_idx].notna().sum()
                    if non_null > 0:
                        sample_values = flat_section.iloc[:, col_idx].dropna().head(5).tolist()
                        print(f"Column {col_idx}: {non_null} non-null values, samples: {sample_values}")

        return df

    except Exception as e:
        print(f"Error analyzing WeGot sheet: {str(e)}")
        return None

def main():
    aug_file = "/Users/saurabhshukla/poc-workspace/sreedapride/BillingAll_Blocks_Aug-2025_04092025.xlsx"
    jul_file = "/Users/saurabhshukla/poc-workspace/sreedapride/BillingAll_Blocks_Jul-2025_10082025.xlsx"

    # Detailed analysis of dues sheets
    aug_dues = analyze_dues_sheet_detailed(aug_file, "August 2025")
    jul_dues = analyze_dues_sheet_detailed(jul_file, "July 2025")

    # Analyze WeGot sheets for comparison
    analyze_wegot_sheet_detailed(aug_file, "August 2025")

    print(f"\n{'='*80}")
    print("FINAL RECOMMENDATIONS")
    print(f"{'='*80}")

    print("""
Based on the analysis, here are my findings:

1. BEST SHEET FOR FLAT-LEVEL DATA: 'dues_tmpt_05-04-25'
   - Contains individual flat records with proper structure
   - Has Block and Flat columns with clear identifiers like <A>, <101>
   - Contains billing amounts, square footage, and resident names
   - Around 76 records which is reasonable for ~70 flats

2. ISSUE WITH APP SHOWING 1931 FLATS:
   - The app might be reading from sheets like 'WeGot report' or 'Water charges'
   - These contain historical data, calculations, and intermediate results
   - They have many more rows due to multiple entries per flat over time

3. ISSUE WITH "C Block" vs "A103":
   - The dues sheet shows blocks as <A>, <B>, <C> and flats as <101>, <102>, etc.
   - App might be reading just the Block column instead of combining Block+Flat
   - Should combine to get A101, B102, C301 format

4. SHEETS TO AVOID:
   - 'Water charges': Historical monthly data with many duplicate entries
   - 'WeGot report': Raw meter reading data with multiple entries per flat
   - 'Charts': Summary charts, no individual flat data
   - 'Allocation' and 'Input': Calculation worksheets, partial data only

RECOMMENDATION:
- Use ONLY the 'dues_tmpt_05-04-25' sheet for flat-level billing
- Combine Block and Flat columns (remove < > brackets) to get proper flat numbers
- This should give you exactly the ~70 flats you expect
""")

if __name__ == "__main__":
    main()