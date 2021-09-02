import logging
from pathlib import Path
import pathlib
import re

import yaml

from musicie.exercise_1_ingest_structure_pdf_royalty_statements.base_pdf_reader import (
    determine_document_schema_type,
)
from musicie.utils import write_data_to_sql, write_data_to_csv, write_data_to_s3

# logging
logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__file__)

# Global variables
with open(Path(__file__).parent / "config.yaml", 'r', encoding='utf-8') as file:
    CONFIG = yaml.load(file, Loader=yaml.FullLoader)


def get_class(document_schema_type: str, class_type: str) -> type:
    """
    Function to obtain the correct class for the exercise
    """
    try:
        mod = __import__(
            "musicie.exercise_1_ingest_structure_pdf_royalty_statements."
            + document_schema_type,
            fromlist=[
                document_schema_type.title().replace("_", "") + class_type.title()
            ],
        )
        return getattr(
            mod, document_schema_type.title().replace("_", "") + class_type.title()
        )
    except AttributeError:
        mod = __import__(
            "musicie.exercise_1_ingest_structure_pdf_royalty_statements.base_pdf_"
            + class_type,
            fromlist=["BasePDF" + class_type.title()],
        )
        return getattr(mod, "BasePDF" + class_type.title())


def get_input_pdf_files(input_folder: str) -> list:
    """
    Function to retrieve all pdf files in the input folder
    """
    input_folder = Path(input_folder)
    return list(Path(input_folder).glob("*.pdf"))


def format_table(input_table_data: list) -> list:
    """
    Function to format the input table prior to writing to sql
    """
    input_table_data.columns = [
        "".join([x.title() for x in col.split("_")]) for col in input_table_data.columns
    ]
    return input_table_data


def format_tables_for_download(pdf_id: str, pdf_data: dict, file_in_name=False) -> dict:
    """
    Function for preparing data for writing to sql
    """
    return {
        pdf_id + '/' + "".join([x.title() for x in table_name.split("_")]) if file_in_name else "".join([x.title() for x in table_name.split("_")]): format_table(
            table_data
        ).assign(UniqueId=pdf_id)
        for table_name, table_data in pdf_data.items()
    }


def run_exercise(
    input_folder: pathlib.Path,
    output_folder: str,
    write_mode=False,
    database_config=None,
    aws_config=None
) -> None:
    """
    Function to run the code for the exercise
    """
    exercise_number = re.search(r".*(\d+).*", Path(__file__).parent.name).group(1)
    _LOGGER.info(f"Running Exercise {exercise_number}")
    input_pdf_files = get_input_pdf_files(input_folder)

    formatted_data = {}
    for pdf_file in input_pdf_files:
        document_schema_type, front_page_data = determine_document_schema_type(pdf_file)
        pdf_config = CONFIG[document_schema_type]
        reader_cls = get_class(document_schema_type, "reader")
        formatter_cls = get_class(document_schema_type, "formatter")
        validator_cls = get_class(document_schema_type, "validator")
        page_data, page_table_numbers, no_pages = reader_cls(pdf_file).get_page_data()
        formatted_pdf_data, formatted_page_table_numbers = formatter_cls(
            pdf_config["format_pdf_config"]
        ).format_pdf_data(page_data, page_table_numbers)
        validator_cls(
            pdf_config["validate_pdf_config"],
            Path(output_folder)
            / Path(__file__).parent.name
            / front_page_data["unique_id"],
            formatted_pdf_data,
            formatted_page_table_numbers,
            front_page_data,
            no_pages,
        ).validate_data()
        formatted_data[front_page_data["unique_id"]] = formatted_pdf_data

    if write_mode:
        # write data to csv
        for pdf_file_id, pdf_table_data in formatted_data.items():
            write_data_to_csv(
                pdf_table_data,
                Path(output_folder) / Path(__file__).parent.name / pdf_file_id,
                index=False,
                encoding='utf-8-sig'
            )
            if aws_config is not None:
                write_data_to_s3(
                    format_tables_for_download(pdf_file_id, pdf_table_data, file_in_name=True),
                    index=False,
                    encoding='utf-8-sig'
                )
            if database_config is not None:
                # write data to sql
                write_data_to_sql(
                    format_tables_for_download(pdf_file_id, pdf_table_data),
                    if_exists="replace",
                    index=False,
                )
