from src.transform import validate_record, is_duplicate
from src.extract import extract_sales_data
from src.transform import transform_sales_data, standardise_date

def test_standardise_date():
    assert standardise_date("2026-10-30") == "2026-10-30"

    assert standardise_date("30/10/2026") == "2026-10-30"


def test_valid_record():

    #Arrange
    record = {
        "order_id": "2001",
        "order_date": "2026-10-31",
        "customer_id": "C020",
        "product": "Laptop",
        "category": "Electronics",
        "quantity": "2",
        "unit_price": "8500.00",
        "city": "Cape Town"
    }

    #Act
    errors = validate_record(record)

    #Assert
    assert errors == []


def test_missing_customer_id():
    record = {
        "order_id": "2002",
        "order_date": "2026-10-31",
        "customer_id": "",
        "product": "Mouse",
        "category": "Accessories",
        "quantity": "2",
        "unit_price": "250.00",
        "city": "Cape Town"
    }

    errors = validate_record(record)

    assert "Missing customer_id" in errors


def test_negative_quantity():
    
    record = {
        "order_id": "2003",
        "order_date": "2026-10-31",
        "customer_id": "C021",
        "product": "Keyboard",
        "category": "Accessories",
        "quantity": "-2",
        "unit_price": "450.00",
        "city": "Durban"
    }

    errors = validate_record(record)

    assert "Quantity must be greater than zero" in errors

def test_invalid_date():

    record = {
         "order_id": "2004",
        "order_date": "2026-15-45",
        "customer_id": "C022",
        "product": "Monitor",
        "category": "Electronics",
        "quantity": "1",
        "unit_price": "3200.00",
        "city": "Pretoria"
    }

    errors = validate_record(record)

    assert "Order date must be a valid and use an approved format" in errors


def test_first_record_is_not_duplicate():
    record = {
         "order_id": "3001",
        "product": "Mouse",
        "quantity": "2"
    }

    seen_records = set()

    result = is_duplicate(record, seen_records)

    assert result is False


def test_repeated_record_is_duplicate():

    record = {
        "order_id": "3002",
        "product": "Keyboard",
        "quantity": "1"
    }

    seen_records = set()

    first_result = is_duplicate(record, seen_records)
    second_result = is_duplicate(record, seen_records)

    assert first_result is False
    assert second_result is True

def test_full_dataset_reconciliation():

    #Arrange
    records = extract_sales_data()

    #Act
    valid_records,rejected_records = transform_sales_data(records)

    #Assert
    assert len(records) == 13
    assert len(valid_records) == 10
    assert len(rejected_records) == 3

    assert len(valid_records) + len(rejected_records) == len(records)

def test_multiple_validation_errors():

    record = {
        "order_id": "4001",
        "order_date": "2026-10-31",
        "customer_id": "",
        "product": "Laptop",
        "category": "Electronics",
        "quantity": "-2",
        "unit_price": "-8500.00",
        "city": "Cape Town"
    }

    errors = validate_record(record)

    assert len(errors) == 3
    assert "Missing customer_id" in errors
    assert "Quantity must be greater than zero" in errors
    assert "Unit price must be greater than zero" in errors

def test_transform_standardises_dates():

    record = {
         "order_id": "2001",
        "order_date": "30/10/2026",
        "customer_id": "C020",
        "product": "Laptop",
        "category": "Electronics",
        "quantity": "1",
        "unit_price": "8500.00",
        "city": "Cape Town"
    }

    valid_records, rejected_records = transform_sales_data([record])

    assert len(valid_records) == 1
    assert len(rejected_records) == 0

    assert valid_records[0]["order_date"] == "2026-10-30"

    #confirming original sources record was not modified
    assert record["order_date"] == "30/10/2026"