from src.extract import extract_sales_data
from src.transform import transform_sales_data
from src.load import publish_batch
from src.logger_config import setup_logger
from src.data_quality import generate_data_quality_report

def run_pipeline():

    logger = setup_logger()

    logger.info("JIMA RETAIL ETL PIPELINE STARTED")


    try:
        #Step 1 :EXTRACT
        logger.info("STEP 1: Extracting data")

        sales_data = extract_sales_data()

        if not sales_data:
            raise ValueError("Source CSV contains no sales records")

        source_fieldnames = list(sales_data[0].keys())

        logger.info(
            "Extracted %d records",
            len(sales_data)
        )


        #STEP 2:TRANSFORM
        logger.info("STEP 2: Transforming data")

        valid_records, rejected_records = transform_sales_data(sales_data)

        logger.info(
            "Valid records: %d",
            len(valid_records)
        )

        if rejected_records:
            logger.warning(
                "Rejected records: %d",
                len(rejected_records)
            )

        #STEP 3: DATA QUALITY REPORT
        logger.info("STEP 3: Generating data quality reports")

        quality_report = generate_data_quality_report(
            len(sales_data),
            valid_records,
            rejected_records
        )

        metrics = quality_report["metrics"]

        logger.info("DATA QUALITY REPORT")
        logger.info("Total records: %d", metrics["total_records"])
        logger.info("Valid records: %d", metrics["valid_records"])
        logger.info("Rejected records: %d", metrics["rejected_records"])
        logger.info("Valid rate: %.2f%%", metrics["valid_rate"])
        logger.info("Rejected rate: %.2f%%", metrics["rejected_rate"])

        logger.info("REJECTION BREAKDOWN")

        for reason, count in quality_report["rejection_breakdown"].items():
            logger.warning("%s: %d", reason, count)


        #STEP 4:RECONCILIATION
        logger.info("STEP 4: Reconciliation")

        total_processed = (
            len(valid_records) + len(rejected_records)
            )

        if len(sales_data) != total_processed:
            raise RuntimeError(
                "Data reconciliation failed"
            )

        logger.info(
            "Reconciliation successful: %d records accounted for",
            total_processed
        )

        #STEP 5: BATCH PUBLISHING
        logger.info("STEP 5: Publishing batch")

        batch_dir = publish_batch(
            valid_records,
            rejected_records,
            source_fieldnames
        )

        logger.info(
            "Batch published successfully: %s",
            batch_dir
        )

        logger.info("PIPELINE COMPLETED SUCCESSFULLY")

        return batch_dir

    except Exception:
        logger.exception("PIPELINE FAILED")
        raise


if __name__ == "__main__":
    run_pipeline()
