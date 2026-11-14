from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def main():
    modis_file = PROCESSED_DIR / "modis_punjab_haryana.csv"
    viirs_file = PROCESSED_DIR / "viirs_punjab_haryana.csv"

    modis = pd.read_csv(modis_file)
    viirs = pd.read_csv(viirs_file)

    # MODIS: high confidence is represented by numeric values >= 80.
    modis_confidence = pd.to_numeric(
        modis["confidence"], errors="raise"
    )
    modis_high = modis[modis_confidence >= 80].copy()

    # VIIRS: high confidence is represented by the category "h".
    viirs_confidence = viirs["confidence"].astype(str).str.strip().str.lower()
    viirs_high = viirs[viirs_confidence == "h"].copy()

    # Save the filtered datasets without changing their columns.
    modis_output = PROCESSED_DIR / "modis_punjab_haryana_high.csv"
    viirs_output = PROCESSED_DIR / "viirs_punjab_haryana_high.csv"

    modis_high.to_csv(modis_output, index=False)
    viirs_high.to_csv(viirs_output, index=False)

    print("\nHIGH-CONFIDENCE DATA GENERATION")
    print("=" * 45)
    print(f"MODIS high-confidence records: {len(modis_high)}")
    print(f"VIIRS high-confidence records: {len(viirs_high)}")
    print(f"\nSaved: {modis_output}")
    print(f"Saved: {viirs_output}")


if __name__ == "__main__":
    main()