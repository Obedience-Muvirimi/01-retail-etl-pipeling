from src.extract import extract_sales_data
from src.transform import transform_sales_data
from src.load import load_clean_data, load_rejected_data, write_csv_atomically
import csv
import pytest
import json
import src.load as load_module


def test_load_clean_data():

    #Arrange
    records = extract_sales_data()
    valid_records, rejected_records = transform_sales_data(records)

    #Act
    output_file = load_clean_data(valid_records)

    #Assert
    assert output_file.exists()
    assert output_file.name == "sales_clean.csv"

    with open(
        output_file,
        mode = "r",
        encoding = "utf-8",
        newline = ""
    ) as file:

        reader = csv.DictReader(file)
        loaded_records = list(reader)

        assert len(loaded_records) == 10
        assert len(loaded_records) == len(valid_records)

        for record in loaded_records:
            assert record["customer_id"] != ""
            assert int(record["quantity"]) > 0

def test_load_rejected_data():

    #Arrange
    records = extract_sales_data()
    valid_records, rejected_records = transform_sales_data(records)

    #Act
    output_file = load_rejected_data(rejected_records)

    #Assert
    assert output_file.exists()
    assert output_file.name == "sales_rejected.csv"

    with open(
        output_file,
        mode="r",
        encoding="utf-8",
        newline=""
    ) as file:

        reader = csv.DictReader(file)
        loaded_records = list(reader)

    assert len(loaded_records) == 3
    for record in loaded_records:
        assert record["rejection_reasons"] != ""


def test_load_empty_clean_data():
    #Arrange
    fieldnames = [
        "order_id",
        "order_date",
        "customer_id",
        "product",
        "category",
        "quantity",
        "unit_price",
        "city"
    ]

    output_file = load_clean_data(
        [],
        fieldnames=fieldnames
        )

    assert output_file.exists()

    with open(
        output_file,
        mode="r",
        encoding="utf-8",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        assert reader.fieldnames == fieldnames
        assert list(reader) == []

def test_load_empty_rejected_data():
    #Arrange
    fieldnames = [
        "order_id",
        "order_date",
        "customer_id",
        "product",
        "category",
        "quantity",
        "unit_price",
        "city"
    ]

    output_file = load_rejected_data(
        [],
        original_fieldnames=fieldnames
    )

    assert output_file.exists()

    with open(
        output_file,
        mode="r",
        encoding="utf-8",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        assert reader.fieldnames == fieldnames + ["rejection_reasons"]
        assert list(reader) == []

def test_atomic_csv_write(tmp_path):
    #Arrange
    records = [
        {
            "order_id": "1001",
            "customer_id": "C001",
        }
    ]

    fieldnames = ["order_id", "customer_id"]

    output_file = tmp_path / "sales.csv"

    #Act
    result = write_csv_atomically(
        records,
        fieldnames,
        output_file
    )

    #Assert
    assert result.exists()
    assert result == output_file
    assert list(tmp_path.iterdir()) == [output_file]

    with open(
        output_file,
        mode="r",
        encoding="utf-8",
        newline=""
    ) as file:

        reader = csv.DictReader(file)
        loaded_records = list(reader)

    assert len(loaded_records) == 1
    assert loaded_records[0]["order_id"] == "1001"

def test_failed_atomic_write_preserves_existing_file(tmp_path):
    #Arrange
    output_file = tmp_path / "sales.csv"

    original_content = "order_id,customer_id\n1001,C001\n"
    output_file.write_text(
        original_content,
        encoding="utf-8"
        )

    records = [
        {
            "order_id": "1002",
            "customer_id": "C002",
        }
    ]

    fieldnames = ["order_id", "customer_id"]

    #Act and Assert
    with pytest.raises(ValueError):

        write_csv_atomically(
            records,
            ["order_id"],
            output_file
        )

    #Verify that the original file is unchanged
    assert output_file.read_text(encoding="utf-8") == original_content

    #Verify temporary files were cleaned up
    assert list(tmp_path.iterdir()) == [output_file]

def test_publish_batch_successfully(tmp_path, monkeypatch):
    monkeypatch.setattr(load_module, "PROCESSED_DIR", tmp_path)

    valid_records = [
        {
            "order_id": "1001",
            "customer_id": "C001",
        }
    ]

    rejected_records = [
        {
            "record": {"order_id": "1002", "customer_id": ""},
            "rejection_reasons": ["Missing customer_id"]
        }
    ]

    source_fieldnames = ["order_id", "customer_id"]

    batch_dir = load_module.publish_batch(
        valid_records,
        rejected_records,
        source_fieldnames
    )

    # 1.Verify batch directory and ouput files
    assert batch_dir.exists()
    assert (batch_dir / "sales_clean.csv").exists()
    assert (batch_dir / "sales_rejected.csv").exists()
    assert (batch_dir / "manifest.json").exists()

    # 2. Read manifest
    with open(batch_dir / "manifest.json", "r", encoding="utf-8") as manifest_file:
        manifest = json.load(manifest_file)

    # 4, Verify manifest metadata
    assert manifest["batch_id"] == batch_dir.name
    assert manifest["pipeline_version"] == "1.0.0"
    assert manifest["source_file"] == "sales.csv"
    assert manifest["status"] == "COMPLETED"

    # 4. Verify record counts in manifest
    assert manifest["total_records"] == 2
    assert manifest["valid_records"] == 1
    assert manifest["rejected_records"] == 1

    # 5. Verify output filenames in manifest
    assert manifest["outputs"]["clean_file"] == "sales_clean.csv"
    assert manifest["outputs"]["rejected_file"] == "sales_rejected.csv"

    #6. Verify actual CSV records counts
    assert load_module.count_csv_records(batch_dir / "sales_clean.csv") == 1
    assert load_module.count_csv_records(batch_dir / "sales_rejected.csv") == 1

    #7. Verify only one CSV record counts
    assert len(list(tmp_path.glob("batch_*"))) == 1
    assert not list(tmp_path.glob("staging_*"))


def test_publish_batch_failure_preserves_batch(tmp_path, monkeypatch):
    monkeypatch.setattr(load_module, "PROCESSED_DIR", tmp_path)

    valid_records = [
        {
            "order_id": "1001",
            "customer_id": "C001",
        }
    ]

    rejected_records = [
        {
            "record": {"order_id": "1002", "customer_id": ""},
            "rejection_reasons": ["Missing customer_id"]
        }
    ]

    source_fieldnames = ["order_id", "customer_id"]

    # First publish a successful batch.
    previous_batch = load_module.publish_batch(
        valid_records,
        [],
        source_fieldnames
    )

    orignal_writer = load_module.write_csv_atomically
    call_count = 0

    def failing_writer(records, fieldnames, output_file):
        nonlocal call_count
        call_count += 1

        if call_count == 2:
            raise OSError("Simulated failure writing rejected records")

        return orignal_writer(records, fieldnames, output_file)
    monkeypatch.setattr(load_module, "write_csv_atomically", failing_writer)

    # The next batch should fail.
    with pytest.raises(OSError):
        load_module.publish_batch(
            valid_records,
            rejected_records,
            source_fieldnames
        )

    # The earlier successful batch must remain untouched.
    assert previous_batch.exists()
    assert (previous_batch / "manifest.json").exists()

    with open(
        previous_batch / "manifest.json",
        encoding="utf-8"
    ) as file:
        previous_manifest = json.load(file)

    assert previous_manifest["status"] == "COMPLETED"

    #The failed batch must be recorded separately.
    failed_batches = list((tmp_path / "failed").iterdir())

    assert len(failed_batches) == 1

    with open(
        failed_batches[0] / "manifest.json",
        encoding="utf-8"
    ) as file:
        failed_manifest = json.load(file)

    assert failed_manifest["status"] == "FAILED"
    assert failed_manifest["error_type"] == "OSError"


    assert not list(tmp_path.glob(".staging_*"))
