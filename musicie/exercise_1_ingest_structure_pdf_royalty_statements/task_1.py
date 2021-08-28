import logging
import pickle
from pathlib import Path

import yaml

from musicie.exercise_1_ingest_structure_pdf_royalty_statements.pdf_reader import PDFReader, determine_document_schema_type
from musicie.exercise_1_ingest_structure_pdf_royalty_statements.pdf_formatter import PDFFormatter

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__file__)


def run_exercise(input_folder, write_mode=False):
    input_folder = Path(input_folder)
    input_pdf_files = [x for x in Path(input_folder).glob('*.pdf')]

    with open(Path(__file__).parent /'config.yaml') as file:
        config = yaml.load(file, Loader=yaml.FullLoader)  

    for pdf_file in input_pdf_files:
        document_schema_type = determine_document_schema_type(pdf_file)
        pdf_config = config[document_schema_type]
        pdf_reader = PDFReader(pdf_config['read_pdf_config'], pdf_file)
        pdf_formatter = PDFFormatter(pdf_config['format_pdf_config'])
        table_schema_page_dict = pdf_reader.get_consolidated_tables()
        pdf_file_output_tables = {}
        for table, pages in zip(pdf_config['read_pdf_config']['tables'].keys(), table_schema_page_dict.values()):
            _LOGGER.info(f"Running table {table}")
            pdf_text, pdf_tables = pdf_reader.read_tables(table, pages)
            pdf_file_output_tables[table] = pdf_formatter.format_pdf_tables(table, pdf_tables, pdf_text)

        if write_mode:
            with open('pdf_output.pkl', 'wb') as f:
                pickle.dump(pdf_file_output_tables, f, protocol=pickle.HIGHEST_PROTOCOL)