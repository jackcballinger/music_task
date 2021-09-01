import logging
import pickle
from pathlib import Path

import yaml

from musicie.exercise_1_ingest_structure_pdf_royalty_statements.base_pdf_reader import determine_document_schema_type
from musicie.utils import write_data_to_sql, write_data_to_csv

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__file__)

with open(Path(__file__).parent /'config.yaml') as file:
    CONFIG = yaml.load(file, Loader=yaml.FullLoader)  

def get_class(document_schema_type: str, class_type):
    try:
        mod = __import__(
            'musicie.exercise_1_ingest_structure_pdf_royalty_statements.' + document_schema_type,
            fromlist=[document_schema_type.title().replace('_','') + class_type.title()]
        )
        return getattr(mod, document_schema_type.title().replace('_','') + class_type.title())
    except AttributeError:
        mod = __import__(
            'musicie.exercise_1_ingest_structure_pdf_royalty_statements.base_pdf_' + class_type,
            fromlist=['BasePDF' + class_type.title()]
        )
        return getattr(mod, 'BasePDF' + class_type.title())

def get_input_pdf_files(input_folder):
    input_folder = Path(input_folder)
    return [x for x in Path(input_folder).glob('*.pdf')]

def format_table(input_table_data):
    input_table_data.columns = [''.join([x.title() for x in col.split('_')]) for col in input_table_data.columns]
    return input_table_data

def format_tables_for_sql(pdf_id, pdf_data):
    return {
        ''.join([x.title() for x in table_name.split('_')]):
        format_table(table_data).assign(UniqueId=pdf_id) for table_name, table_data in pdf_data.items()
    }

def run_exercise(input_folder, output_folder, write_mode=False, database_config=None):
    input_pdf_files = get_input_pdf_files(input_folder)

    formatted_data = {}
    for pdf_file in input_pdf_files:
        document_schema_type, front_page_data = determine_document_schema_type(pdf_file)
        pdf_config = CONFIG[document_schema_type]
    #     reader_cls = get_class(document_schema_type, 'reader')
    #     formatter_cls = get_class(document_schema_type, 'formatter')
        validator_cls = get_class(document_schema_type, 'validator')
    #     page_data, page_table_numbers, no_pages = reader_cls(pdf_file).get_page_data()
    #     formatted_pdf_data, formatted_page_table_numbers = formatter_cls(pdf_config['format_pdf_config']).format_pdf_data(page_data, page_table_numbers)       
        with open(Path(__file__).parent.parent.parent / 'formtted_data.pkl', 'rb') as f:
            formatted_pdf_data, formatted_page_table_numbers = pickle.load(f)
        no_pages = 1090
        validator_cls(pdf_config['validate_pdf_config'], Path(output_folder) / Path(__file__).parent.name / front_page_data['unique_id'], formatted_pdf_data, formatted_page_table_numbers, front_page_data, no_pages).validate_data()
    #     formatted_data[front_page_data['unique_id']] = formatted_pdf_data

    with open(Path(__file__).parent.parent.parent / 'formatted_page_data.pkl', 'rb') as f:
        formatted_data = pickle.load(f)

    if write_mode:
        # write data to csv
        for pdf_file_id, pdf_table_data in formatted_data.items():
            write_data_to_csv(pdf_table_data, Path(output_folder) / Path(__file__).parent.name / pdf_file_id, index=False)
            if database_config is not None:
                # write data to sql
                write_data_to_sql(format_tables_for_sql(pdf_file_id, pdf_table_data), if_exists='replace', index=False)
