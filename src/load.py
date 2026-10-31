import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def load_clean_data(records):
    """
    Save valid sales records to a CSV file
    """

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    output_file = PROCESSED_DIR / "sales_clean.csv"

    if not records:
        raise ValueError("No valid records available to load")

    fieldnames = list(records[0].keys())

    with open(
        output_file,
        mode = "w",
        encoding = "utf-8",
        newline = ""
    ) as file:

        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(records)

    return output_file

def load_rejected_data(records):
    """
    Save rejected sales records and all rejection reasons.
    """

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    output_file = PROCESSED_DIR / "sales_rejected.csv"

    if not records:
        raise ValueError("No rejected records available to load")

    original_fields = list(records[0]["record"].keys())

    fieldnames = original_fields + ["rejection_reasons"]

    with open(
        output_file,
        mode = "w",
        encoding = "utf-8",
        newline = ""
    ) as file:

        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()

        for item in records:

            output_record = item["record"].copy()

            output_record["rejection_reasons"] = "; ".join(
                item["rejection_reasons"]
            )

            writer.writerow(output_record)

    return output_file