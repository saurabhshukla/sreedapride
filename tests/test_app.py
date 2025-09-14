#!/usr/bin/env python3

"""
Test script for the updated app.py
"""

import sys
from pathlib import Path

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from data_processor import FlatDataProcessor, FlatAnalyzer
import pandas as pd


def test_updated_app():
    """Test the updated app functionality."""
    print("🧪 Testing Updated App...")

    processor = FlatDataProcessor()
    analyzer = FlatAnalyzer()

    # Test files (now in data directory)
    data_dir = Path(__file__).parent.parent / "data"
    files = [
        str(data_dir / "BillingAll_Blocks_Jul-2025_10082025.xlsx"),
        str(data_dir / "BillingAll_Blocks_Aug-2025_04092025.xlsx")
    ]

    # Load data
    df_last = processor.load_flat_data(files[0])
    df_this = processor.load_flat_data(files[1])

    if df_last is not None and df_this is not None:
        print(f"✅ Data loaded: {len(df_last)} vs {len(df_this)} flats")

        # Test analysis
        results = analyzer.analyze_consumption_changes(df_last, df_this)

        print("✅ Analysis Results:")
        print(f"   📊 Merged data: {len(results['merged_data'])} flats")
        print(f"   📋 Column names: {list(results['merged_data'].columns)}")

        # Check categories including low consumers
        for category, df in results['categories'].items():
            print(f"   📈 {category}: {len(df)} flats")

        # Verify low consumers exists
        if 'low_consumers' in results['categories']:
            print("✅ Low Consumers tab available")
            low_consumers = results['categories']['low_consumers']
            if len(low_consumers) > 0:
                print(f"   🔻 Found {len(low_consumers)} low consuming flats")
                print(f"   💰 Range: ₹{low_consumers['Amount_this_month'].min():.0f} - ₹{low_consumers['Amount_this_month'].max():.0f}")
            else:
                print("   ⚠️ No low consumers found in data")
        else:
            print("❌ Low Consumers tab missing")

        # Check column names
        bad_cols = [col for col in results['merged_data'].columns if 'Consumption_' in col]
        if not bad_cols:
            print("✅ No old 'Consumption_' column names")
        else:
            print(f"⚠️ Found old column names: {bad_cols}")

        print("\n🎉 APP READY - Run with: streamlit run app.py")
        return True
    else:
        print("❌ Failed to load test data")
        return False


if __name__ == "__main__":
    test_updated_app()