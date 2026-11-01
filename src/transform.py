from datetime import datetime


def standardise_date(date_value):
    """
    Accept approved date formats and return YYYY-MM-DD.
    """

    accepted_formats = [
        "%Y-%m-%d",
        "%d/%m/%Y"
    ]

    for date_format in accepted_formats:
        try:
            parsed_date = datetime.strptime(
                date_value.strip(),
                date_format
            )

            return parsed_date.strftime("%Y-%m-%d")

        except ValueError:
            continue

    raise ValueError(
        f"Unsupported date format: {date_value}"
    )


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
        standardise_date(record["order_date"])

    except ValueError:
        errors.append(
            "Order date must be a valid and use an approved format"
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
        transformed_record = record.copy()

        if not errors:
            transformed_record["order_date"] = standardise_date(
                record["order_date"]
            )

            valid_records.append(transformed_record)
        else:
            rejected_records.append({
                "record": record,
                "rejection_reasons": errors
            })


    return valid_records, rejected_records