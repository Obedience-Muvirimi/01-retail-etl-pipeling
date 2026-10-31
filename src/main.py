from extract import extract_sales_data
from transform import transform_sales_data
from load import load_clean_data, load_rejected_data
from logger_config import setup_logger

def run_pipeline():

    logger = setup_logger()

    logger.info("JIMA RETAIL ETL PIPELINE STARTED")
    

    try:
        #Step 1 :EXTRACT
        logger.info("STEP 1: Extracting data")

        sales_data = extract_sales_data()

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
        

        #STEP 3: LOAD
        logger.info("STEP 3: Loading data")

        clean_file = load_clean_data(valid_records)
        rejected_file = load_rejected_data(rejected_records)

        logger.info("Clean data saved to: %s" ,clean_file)
        logger.info("Rejected data saved to: %s", rejected_file)

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

        logger.info("PIPELINE COMPLETED SUCCESSFULLY")

    except Exception:
        logger.exception("PIPELINE FAILED")
        raise


if __name__ == "__main__":
    run_pipeline()
