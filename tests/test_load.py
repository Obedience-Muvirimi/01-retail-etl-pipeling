from src.extract import extract_sales_data
from src.transform import transform_sales_data
from src.load import load_clean_data, load_rejected_data
import csv


# def test_load_clean_data():

#     records = extract_sales_data()

#     valid_records,rejected_records = transform_sales_data(records)

#     output_file = load_clean_data(valid_records)

#     assert output_file.exists()
#     assert output_file.name == "sales_clean.csv"

def test_load_clean_data():

    #Arrange
    records = extract_sales_data()
    valid_records, rejected_records = transform_sales_data(records)

    #Act
    output_file = load_clean_data(valid_records)

    #Assert
    assert output_file.exists
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