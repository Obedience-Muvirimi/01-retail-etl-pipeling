from datetime import datetime


def validate_record(record):
    """
    Validate one sales record and collect all errors.
    """
    
    errors = []

    #Check required text fields
    required_fields = [
        "order_id",
        "order_date",
        "customer_id",
        "product",
        "category",
        "city"
    ]

    #Checking for missing required fields
    for field in required_fields:
        if not record[field].strip():
            errors.append(f"Missing {field}")

    #Validate quantity
    try:
        quantity = int(record["quantity"])

        if quantity <=0 :
            errors.append(
                "Quantity must be greater than zero"
                )
    except ValueError:
        errors.append("Quantity must be a valid integer")

    #Validate unit price
    try:
        unit_price = float(record["unit_price"])

        if unit_price <- 0:
            errors.append(
                "Unit price must be greater than zero"
            )
    except ValueError:
        errors.append("Unit price must be a valid number")

    #Validate order date
    try:
        datetime.strptime(
            record["order_date"],
            "%Y-%m-%d"
        )

    except ValueError:
        errors.append(
            "Order date must be a valid date in YYYY-MM-DD format"
        )

    return errors

def is_duplicate(record, seen_records):
    """
    Check whether an exact record has already been processed.
    """

    #Convert the record into a hashable tuple
    record_key = tuple(sorted(record.items()))

    if record_key in seen_records:
        return True

    seen_records.add(record_key)

    return False

def transform_sales_data(records):
    """
    Validate and transform all extracted sales records.
    Separate valid records from rejected records.
    """

    valid_records = []
    rejected_records = []
    seen_records = set()

    for record in records:

        #Collect validation errors
        errors = validate_record(record)

        #Check for exact duplicates
        if is_duplicate(record, seen_records):
            errors.append("Duplicate record detected")

        #Classify the record
        if errors:
            rejected_records.append({
                "record": record,
                "rejection_reasons": errors
            })
        else:
            valid_records.append(record)

    return valid_records, rejected_records