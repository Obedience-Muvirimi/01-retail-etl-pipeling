import pytest
from src.extract import extract_sales_data
from src.data_quality import calculate_quality_metrics,calculate_rejection_breakdown, generate_data_quality_report
from src.transform import transform_sales_data


def test_calculate_quality_metrics():

    records = {
        "extracted_records": 2500,
        "valid_records":2350,
        "rejected_records":150
    }

    records_metrics = calculate_quality_metrics(records["extracted_records"], records["valid_records"], records["rejected_records"])

    assert records_metrics["valid_rate"] == 94
    assert records_metrics["rejected_rate"] == 6


def test_zero_total_records():

    records = {
            "extracted_records": 0,
            "valid_records":2350,
            "rejected_records":150
        }

    with pytest.raises(ValueError):
         calculate_quality_metrics(records["extracted_records"], records["valid_records"], records["rejected_records"])

def test_reconciliation_failure():

    records = {
                "extracted_records": 2500,
                "valid_records":2350,
                "rejected_records":100
            }

    with pytest.raises(ValueError):

        calculate_quality_metrics(records["extracted_records"], records["valid_records"], records["rejected_records"])

def test_negative_record_counts():
    records = {
                    "extracted_records": 2500,
                    "valid_records":2600,
                    "rejected_records":-100
                }
    with pytest.raises(ValueError):
        calculate_quality_metrics(records["extracted_records"], records["valid_records"], records["rejected_records"])


def test_multiple_rejection_reasons():
    rejected_records = [
    {
        "record": {"order_id": "1011"},
        "rejection_reasons": [
            "Missing customer_id"
        ]
    },
    {
        "record": {"order_id": "1012"},
        "rejection_reasons": [
            "Quantity must be greater than zero"
        ]
    },
    {
        "record": {"order_id": "1002"},
        "rejection_reasons": [
            "Duplicate record detected"
        ]
    },
    {
        "record": {"order_id": "1013"},
        "rejection_reasons": [
            "Missing customer_id",
            "Quantity must be greater than zero"
        ]
    }
]

    rejection_breakdown = {
    "Missing customer_id": 2,
    "Quantity must be greater than zero": 2,
    "Duplicate record detected": 1
}

    assert calculate_rejection_breakdown(rejected_records) == rejection_breakdown

def test_empty_rejected_records():
    rejected_records = []

    assert calculate_rejection_breakdown(rejected_records) == {}


def test_generate_data_quality_report():


    #Arrange
    records = extract_sales_data()

    #Act
    valid_records,rejected_records = transform_sales_data(records)

    report = generate_data_quality_report(len(records),valid_records, rejected_records)

    assert report["metrics"]["total_records"] == 13
    assert report["metrics"]["valid_rate"] == 76.92
    assert report["metrics"]["rejected_rate"] == 23.08
    assert report["rejection_breakdown"]["Missing customer_id"] == 1
    assert report["rejection_breakdown"]["Quantity must be greater than zero"] == 1
    assert report["rejection_breakdown"]["Duplicate record detected"] == 1

def test_generate_data_quality_report_reconciliation_failure():

    valid_records = [{} for _ in range(10)]
    rejected_records = [
        {"rejection_reasons": ["Missing customer_id"]}
    ]

    with pytest.raises(ValueError):
        generate_data_quality_report(
            13,
            valid_records,
            rejected_records
        )
