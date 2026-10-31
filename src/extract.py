import csv
from pathlib import Path

#Locate the project directory
PROJECT_ROOT = Path(__file__).resolve().parents[1]

#Define the raw data file
SOURCE_FILE = PROJECT_ROOT / "data" / "raw" / "sales.csv"


def extract_sales_data():
    """
    Extract sales records from the source CSV file.
    """
    
    records = []

    #Open the CSV file
    with open(
        SOURCE_FILE,
        mode = "r",
        encoding = "utf-8-sig",
        newline = ""
    ) as file:

        reader = csv.DictReader(file)

        #Read every row into a dictionary
        for row in reader:
            records.append(row)

    return records

if __name__ =="__main__":

    sales_data = extract_sales_data()

    print("JIMA RETAIL - DATA EXTRACTION")
    print("-------------------------------")

    print(f"Total records : {len(sales_data)}")

    # print("\nFirst three records:")

    #Inspect every record
    for record in sales_data:
        print(record)

    #Inspect every record
    print("\nAvailable columns:")

    print(list(sales_data[0].keys()))