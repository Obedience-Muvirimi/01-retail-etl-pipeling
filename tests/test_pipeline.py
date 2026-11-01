import logging
import csv
import json
import pytest

import src.main as main_module
import src.load as load_module


def test_pipeline_runs_successfully(monkeypatch, tmp_path):

    #Arrange: provide a small dataset
    sample_records = [
        {
            "order_id": "2001",
            "order_date": "2026-11-01",
            "customer_id": "C101",
            "product": "Laptop",
            "category": "Electronics",
            "quantity": "2",
            "unit_price": "8500.00",
            "city": "Cape Town"
        },
        {
            "order_id": "2002",
            "order_date": "2026-11-01",
            "customer_id": "",
            "product": "Mouse",
            "category": "Accessories",
            "quantity": "1",
            "unit_price": "250.00",
            "city": "Johannesburg"
        }
    ]

    #Use a temporary directory instead of the real output directory
    monkeypatch.setattr(
        load_module,
        "PROCESSED_DIR",
        tmp_path
    )

    #Prevent tests from writting to the real log file
    test_logger = logging.getLogger("test_pipeline")
    test_logger.handlers.clear()
    test_logger.addHandler(logging.NullHandler())

    monkeypatch.setattr(
        main_module,
        "setup_logger",
        lambda: test_logger
    )

    monkeypatch.setattr(
        main_module,
        "extract_sales_data",
        lambda: sample_records
    )

    # Act: execute the complete pipeline
    batch_dir = main_module.run_pipeline()

    # Assert: verify the published batch
    assert batch_dir.exists()
    assert (batch_dir / "sales_clean.csv").exists()
    assert (batch_dir / "sales_rejected.csv").exists()
    assert (batch_dir / "manifest.json").exists()

    # Verify the manifest
    with open(
        batch_dir / "manifest.json",
        encoding="utf-8"
    ) as file:
        manifest = json.load(file)

    assert manifest["status"] == "COMPLETED"
    assert manifest["total_records"] == 2
    assert manifest["valid_records"] == 1
    assert manifest["rejected_records"] == 1

    # Verify the clean CSV
    with open(batch_dir / "sales_clean.csv",
               encoding="utf-8",
               newline=""
    ) as file:
        clean_records = list(csv.DictReader(file))

    assert len(clean_records) == 1
    assert clean_records[0]["order_id"] == "2001"

    # Verify the rejected CSV
    with open(
        batch_dir / "sales_rejected.csv",
        encoding="utf-8",
        newline=""
    ) as file:

        rejected_records = list(csv.DictReader(file))

    assert len(rejected_records) == 1
    assert rejected_records[0]["order_id"] == "2002"


def test_pipeline_fails_when_source_is_empty(monkeypatch):

    # Arrange
    test_logger = logging.getLogger("test_pipeline_empty")
    test_logger.handlers.clear()
    test_logger.addHandler(logging.NullHandler())

    monkeypatch.setattr(
        main_module,
        "setup_logger",
        lambda: test_logger
    )

    monkeypatch.setattr(
        main_module,
        "extract_sales_data",
        lambda: []
    )

    def unexpected_publish(*args, **kwargs):
        pytest.fail("Pipeline should not publish an empty batch")

    monkeypatch.setattr(
        main_module,
        "publish_batch",
        unexpected_publish
    )

    # Act and Assert
    with pytest.raises(
        ValueError,
        match="Source CSV contains no sales records"
    ):
        main_module.run_pipeline()


def test_pipeline_fails_when_transformation_fails(monkeypatch):

    # Arrange
    test_logger = logging.getLogger("test_pipeline_transform")
    test_logger.handlers.clear()
    test_logger.addHandler(logging.NullHandler())

    monkeypatch.setattr(
        main_module,
        "setup_logger",
        lambda: test_logger
    )

    monkeypatch.setattr(
        main_module,
        "extract_sales_data",
        lambda: [{"order_id": "2001"}]
    )

    def fail_transformation(records):
        raise RuntimeError("Simulated transformation failure")

    monkeypatch.setattr(
        main_module,
        "transform_sales_data",
        fail_transformation
    )

    def unexpected_publish(*args, **kwargs):
        pytest.fail("Publishing should not happen after transformation failure")

    monkeypatch.setattr(
        main_module,
        "publish_batch",
        unexpected_publish
    )

    # Act and Assert
    with pytest.raises(
        RuntimeError,
        match="Simulated transformation failure"
    ):
        main_module.run_pipeline()



def test_pipeline_fails_when_publication_fails(monkeypatch):

    # Arrange
    test_logger = logging.getLogger("test_pipeline_load")
    test_logger.handlers.clear()
    test_logger.addHandler(logging.NullHandler())

    monkeypatch.setattr(
        main_module,
        "setup_logger",
        lambda: test_logger
    )

    sample_records = [
        {
            "order_id": "2001",
            "order_date": "2026-11-01",
            "customer_id": "C101",
            "product": "Laptop",
            "category": "Electronics",
            "quantity": "2",
            "unit_price": "8500.00",
            "city": "Cape Town"
        }
    ]

    monkeypatch.setattr(
        main_module,
        "extract_sales_data",
        lambda: sample_records
    )

    def fail_publication(*args, **kwargs):
        raise OSError("Simulated storage failure")

    monkeypatch.setattr(
        main_module,
        "publish_batch",
        fail_publication
    )

    # Act and Assert
    with pytest.raises(
        OSError,
        match="Simulated storage failure"
    ):
        main_module.run_pipeline()


def test_previous_batch_is_preserved_after_later_failure(monkeypatch, tmp_path):

    # Arrange: use an isolated output directory
    monkeypatch.setattr(
        load_module,
        "PROCESSED_DIR",
        tmp_path
    )

    test_logger = logging.getLogger("test_pipeline_preservation")
    test_logger.handlers.clear()
    test_logger.addHandler(logging.NullHandler())

    monkeypatch.setattr(
        main_module,
        "setup_logger",
        lambda: test_logger
    )

    sample_records = [
        {
            "order_id": "2001",
            "order_date": "2026-11-01",
            "customer_id": "C101",
            "product": "Laptop",
            "category": "Electronics",
            "quantity": "2",
            "unit_price": "8500.00",
            "city": "Cape Town"
        }
    ]

    monkeypatch.setattr(
        main_module,
        "extract_sales_data",
        lambda: sample_records
    )

    # First run: publish successfully
    first_batch = main_module.run_pipeline()

    assert first_batch.exists()

    original_manifest = (
        first_batch / "manifest.json"
    ).read_text(encoding="utf-8")

    # Second run: simulate a transformation failure
    def fail_transformation(records):
        raise RuntimeError("Simulated second-run failure")

    monkeypatch.setattr(
        main_module,
        "transform_sales_data",
        fail_transformation
    )

    with pytest.raises(
        RuntimeError,
        match="Simulated second-run failure"
    ):
        main_module.run_pipeline()

    # Assert: the original batch remains intact
    assert first_batch.exists()

    current_manifest = (
        first_batch / "manifest.json"
    ).read_text(encoding="utf-8")

    assert current_manifest == original_manifest
