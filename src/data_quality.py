def calculate_quality_metrics(total_records, valid_records, rejected_records):
    """
    Calculate data quality metrics for an ETL batch
    """

    if total_records <= 0:
        raise ValueError("Total records must be greater than zero")

    if valid_records < 0 or rejected_records < 0 :
        raise ValueError("Record cannot be negative")

    if valid_records + rejected_records != total_records:
        raise ValueError("Record reconciliation failed")

    valid_rate = (valid_records / total_records) * 100

    rejected_rate = (rejected_records / total_records) * 100

    metrics = {
        "total_records": total_records,
        "valid_records": valid_records,
        "rejected_records": rejected_records,
        "valid_rate": round(valid_rate, 2),
        "rejected_rate": round(rejected_rate, 2)
    }

    return metrics

def calculate_rejection_breakdown(rejected_records):
    """
    Count how frequently each rejection reason occurs.
    """

    rejection_breakdown = {}

    for rejected_record in rejected_records:

        for reason in rejected_record["rejection_reasons"]:

            if reason in rejection_breakdown:
                rejection_breakdown[reason] += 1
            else:
                rejection_breakdown[reason] = 1

    return rejection_breakdown

def generate_data_quality_report( total_records, valid_records, rejected_records):
    """
    Generate a data quality report for an ETL batch.
    """


    metrics = calculate_quality_metrics(
        total_records,
        len(valid_records),
        len(rejected_records)
        )

    rejection_breakdown = calculate_rejection_breakdown(
        rejected_records
        )

    report = {
        "metrics": metrics,
        "rejection_breakdown": rejection_breakdown
    }

    return report
