# JIMA RETAIL - End-to-End ETL Data Pipeline

## Project Overview

JIMA RETAIL is a Python-based ETL (Extract, Transform, Load) pipeline developed to demonstrate practical data engineering principles using a sample retail sales dataset.

The pipeline extracts sales records from a CSV source, validates and transforms the data, separates valid and rejected records, generates data-quality metrics, reconciles record counts, and publishes outputs into uniquely identified batch directories.

The project emphasizes data integrity, error handling, traceability, and reliable batch publication.

## Architecture

```text
Raw Sales CSV
      |
      v
   EXTRACT
      |
      v
  TRANSFORM
      |
      +-------------------+
      |                   |
      v                   v
 Valid Records       Rejected Records
      |                   |
      +---------+---------+
                |
                v
       DATA QUALITY REPORT
                |
                v
          RECONCILIATION
                |
                v
          BATCH PUBLISHING
                |
       +--------+--------+
       |                 |
       v                 v
  Clean CSV          Rejected CSV
       |                 |
       +--------+--------+
                |
                v
          Batch Manifest
```

## Technologies

- Python 3.14
- CSV processing
- Python logging
- pathlib and tempfile
- pytest
- Git and GitHub

## Project Structure

```text
01-retail-etl-pipeling/
|
+-- data/
|   +-- raw/
|   |   +-- sales.csv
|   |
|   +-- processed/
|       +-- Generated batch outputs (not tracked by Git)
|
+-- src/
|   +-- __init__.py
|   +-- extract.py
|   +-- transform.py
|   +-- data_quality.py
|   +-- load.py
|   +-- logger_config.py
|   +-- main.py
|
+-- tests/
|   +-- test_transform.py
|   +-- test_data_quality.py
|   +-- test_load.py
|   +-- test_pipeline.py
|
+-- logs/ (generated at runtime)
+-- .gitignore
+-- requirements.txt
+-- README.md
```

## Pipeline Features

### 1. Data Extraction

- Reads retail sales records from a CSV source.
- Uses Python's CSV module.
- Preserves the original source data.

### 2. Data Transformation and Validation

- Validates required fields.
- Checks date formats and numeric values.
- Rejects invalid quantities and prices.
- Detects exact duplicate records.
- Standardises accepted dates.
- Records rejection reasons for investigation.

### 3. Data Quality

- Calculates total, valid, and rejected record counts.
- Calculates valid and rejected percentages.
- Produces a breakdown of rejection reasons.
- Checks that record counts reconcile.

### 4. Batch Publishing

- Publishes outputs into uniquely identified batch directories.
- Writes clean and rejected CSV files.
- Generates a JSON manifest containing batch metadata.
- Uses temporary files and atomic replacement for CSV writes.
- Verifies output record counts before publishing a completed batch.
- Preserves previously published batches when a later pipeline execution fails.

### 5. Logging and Error Handling

- Records pipeline execution stages.
- Logs pipeline failures and exceptions.
- Captures exception tracebacks.
- Propagates failures rather than silently reporting success.

## Sample Dataset

The sample dataset contains 13 sales records.

It intentionally includes:

- A record with a missing customer ID.
- A record with a negative quantity.
- An exact duplicate record.

Expected processing results:

| Metric | Result |
|---|---:|
| Total records | 13 |
| Valid records | 10 |
| Rejected records | 3 |
| Valid rate | 76.92% |
| Rejected rate | 23.08% |

## Installation and Setup

### Prerequisites

- Python 3.14 or a compatible version.
- Git.

### 1. Clone the repository

```bash
git clone https://github.com/Obedience-Muvirimi/01-retail-etl-pipeling.git
```

### 2. Navigate into the project

```bash
cd 01-retail-etl-pipeling
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
python -m pip install -r requirements.txt
```

## Running the Pipeline

Run from the project root:

```bash
python -m src.main
```

The pipeline reads the raw sales data and publishes a new batch under:

```text
data/processed/
```

Each completed batch contains:

```text
batch_<timestamp>_<unique_id>/
+-- sales_clean.csv
+-- sales_rejected.csv
+-- manifest.json
```

Runtime logs are written to:

```text
logs/pipeline.log
```

Generated outputs and logs are excluded from version control.

## Running Tests

Run the complete test suite:

```bash
python -m pytest -v
```

The test suite covers:

- Record validation and transformation.
- Duplicate detection.
- Data-quality calculations.
- Atomic CSV writing.
- Batch publication and failure handling.
- End-to-end pipeline execution.
- Preservation of previously published batches.

## Current Test Results

The project currently has **31 automated tests passing**.

## Engineering Principles Demonstrated

- Separation of concerns.
- Data validation and quality assurance.
- Reconciliation and completeness checks.
- Atomic file operations.
- Batch-level traceability.
- Structured logging.
- Exception handling.
- Unit and integration testing.
- Reproducible project setup.

## Future Development

Potential extensions include:

- PostgreSQL data warehouse integration.
- SQL-based transformations.
- dbt data modelling.
- Apache Airflow orchestration.
- Docker-based deployment.
- Automated data-quality monitoring.
- Cloud storage integration.

---

**Project:** JIMA RETAIL - End-to-End ETL Data Pipeline
**Language:** Python
**Status:** Initial ETL implementation and automated test suite completed.
