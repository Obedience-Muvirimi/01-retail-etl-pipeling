import csv
import json
import tempfile
from datetime import datetime, timezone
from uuid import uuid4
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

PIPELINE_VERSION = "1.0.0"

def write_csv_atomically(records, fieldnames, output_file):
    """
    Write CSV data to a temporary file and replace
    the destination only after the write succeeds.
    """

    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    temporary_file = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            dir=output_file.parent,
            suffix=".tmp",
            delete=False
        ) as file:

            temporary_file = Path(file.name)

            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)

            file.flush()

        temporary_file.replace(output_file)

    except Exception:
        if temporary_file is not None:
            temporary_file.unlink(missing_ok=True)

        raise

    return output_file

def load_clean_data(records, fieldnames=None):
    """
    Save valid sales records to a CSV file

    Supports empty datasets when fieldnames are supplied.
    """

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    output_file = PROCESSED_DIR / "sales_clean.csv"

    if records:
        fieldnames = list(records[0].keys())

    elif not fieldnames:

        raise ValueError(
            "Fieldnames are required when loading an empty clean data"
            )

    return write_csv_atomically(
                records,
                 fieldnames,
                 output_file
)

def load_rejected_data(records, original_fieldnames=None):
    """
    Save rejected sales records and all rejection reasons.

    Supports empty datasets when original_fieldnames are supplied.
    """

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    output_file = PROCESSED_DIR / "sales_rejected.csv"

    if records:
        original_fieldnames = list(records[0]["record"].keys())

    elif not original_fieldnames:

            raise ValueError(
                "Original fieldnames are required when loading an empty rejected data"
            )

    fieldnames = list(original_fieldnames) + ["rejection_reasons"]

    output_records = []

    for item in records:

        output_record = item["record"].copy()

        output_record["rejection_reasons"] = "; ".join(
            item["rejection_reasons"]
        )

        output_records.append(output_record)

    return write_csv_atomically(
        output_records,
        fieldnames,
        output_file
    )

def create_batch_id():
    """
    Genetate a unique ID for each ETL batch.
    """

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    unique_suffix = uuid4().hex[:8]

    return f"batch_{timestamp}_{unique_suffix}"

def count_csv_records(csv_file):
    """
    Count data rows in a CSV file, excluding the header.
    """

    with open(
        csv_file,
        mode="r",
        encoding="utf-8",
        newline=""
    ) as file:
        reader = csv.DictReader(file)
        return sum(1 for _ in reader)


def publish_batch(valid_records, rejected_records, source_fieldnames):
    """
    Publish a complete ETL batch.

    Both CSV files are written and verified in a staging directory.
    The staging directory is renamed to its final batch directory
    only after all outputs and the manifest are ready.

    Failed runs are moved to the failed directory when possible.
    """

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    batch_id = create_batch_id()

    staging_dir = PROCESSED_DIR / f"staging_{batch_id}"
    final_dir = PROCESSED_DIR / batch_id

    if final_dir.exists() or staging_dir.exists():
        raise FileExistsError(
            f"Batch directory already exists: {batch_id}"
        )

    staging_dir.mkdir()

    clean_file = staging_dir / "sales_clean.csv"
    rejected_file = staging_dir / "sales_rejected.csv"
    manifest_file = staging_dir / "manifest.json"

    total_records = len(valid_records) + len(rejected_records)

    rejected_fieldnames = (
        list(source_fieldnames) + ["rejection_reasons"]
    )

    rejected_output_records = []

    for item in rejected_records:

        output_record = item["record"].copy()

        output_record["rejection_reasons"] = "; ".join(
            item["rejection_reasons"]
        )

        rejected_output_records.append(output_record)

    try:
        #Step 1: Write both datasets into staging.
        write_csv_atomically(
            valid_records,
            source_fieldnames,
            clean_file
        )

        write_csv_atomically(
            rejected_output_records,
            rejected_fieldnames,
            rejected_file
        )

        #Step 2: Verify both output files.
        if not clean_file.exists() or not rejected_file.exists():
            raise RuntimeError("One or more batch output files are missing")

        clean_count = count_csv_records(clean_file)
        rejected_count = count_csv_records(rejected_file)

        if clean_count != len(valid_records):
            raise RuntimeError("Clean records count verification failed")

        if rejected_count != len(rejected_output_records):
            raise RuntimeError("Rejected records count verification failed")

        if clean_count + rejected_count != total_records:
            raise RuntimeError("Batch reconciliation failed")

        #Step 3: Create the complete batch manifest.
        manifest = {
            "batch_id": batch_id,
            "pipeline_version": PIPELINE_VERSION,
            "source_file": "sales.csv",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "COMPLETED",
            "total_records": total_records,
            "valid_records": clean_count,
            "rejected_records": rejected_count,
            "outputs": {
                "clean_file": "sales_clean.csv",
                "rejected_file": "sales_rejected.csv"
            }
        }

        with open(
            manifest_file,
            mode="w",
            encoding="utf-8"
        ) as file:
            json.dump(manifest, file, indent=4)

        #Step 4: Publish the entire batch directory.
        staging_dir.replace(final_dir)

        return final_dir

    except Exception as error:

        # Record the failure without modifying earlier successful batches.
        failed_manifest = {
            "batch_id": batch_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "FAILED",
            "total_records": total_records,
            "valid_records": len(valid_records),
            "rejected_records": len(rejected_records),
            "error_type": type(error).__name__,
            "error_message": str(error)
        }

        try:
            # Step 1: Write the failure manifest.
            with open(
                manifest_file,
                mode="w",
                encoding="utf-8"
            ) as file:
                json.dump(failed_manifest, file, indent=4)

            # Step 2: Close the manifest before moving the directory.
            failed_root = PROCESSED_DIR / "failed"
            failed_root.mkdir(parents=True, exist_ok=True)

            failed_dir = failed_root / batch_id
            staging_dir.replace(failed_dir)

        except OSError:
            # Preserve the original pipeline error if failure recording fails.
            pass

        raise
