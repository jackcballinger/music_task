from collections import defaultdict
import logging
from musicie.exercise_1_ingest_structure_pdf_royalty_statements.pdf_formatter import format_front_page
import re
import tempfile
from tqdm import tqdm

import pdfplumber
from PyPDF2 import PdfFileReader, PdfFileWriter
import tabula

logging.basicConfig(level=logging.INFO)
logging.getLogger('pdfminer').setLevel(logging.WARNING)
_LOGGER = logging.getLogger(__file__)

class PDFReader:
    def __init__(self, config, pdf_path):
        self._config = config
        self._ignore_tables = config.get('ignore_tables',[])
        self._tables = self._config['tables']
        self._pdf_path = pdf_path
        self._pdf = PdfFileReader(open(self._pdf_path,'rb'))
        self._pdf_writer = PdfFileWriter()

    def get_all_pdf_tables(self):
        return tabula.read_pdf(
            self._pdf_path,
            multiple_tables=True,
            pages='all'
        )

    def get_consolidated_tables(self):
        all_tables = self.get_pdf_tables()
        all_table_schemas = [table.columns.tolist() for table in all_tables]
        schema_dict = defaultdict(list)
        for i, schema in enumerate(all_table_schemas):
            schema_dict[tuple(schema)].append(i)
        return {schema: range(min(pages)+1, max(pages)+1) if min(pages)!=max(pages) else min(pages) for i, (schema, pages) in enumerate(schema_dict.items()) if i not in self._ignore_tables}

    def get_pdf_tables(self, multiple_tables=True, pages='all'):
        _LOGGER.info('retrieving pdf tables')
        return tabula.read_pdf(
            self._pdf_path,
            multiple_tables=multiple_tables,
            pages=pages
        )
    
    def get_pdf_text(self, table_config):
        _LOGGER.info('retrieving pdf text')
        with pdfplumber.open(self._pdf_path) as f:
            pdf_pages = f.pages[
                int(table_config['pages'].split('-')[0])-1: int(table_config['pages'].split('-')[1])
            ] if isinstance(table_config['pages'], str) else f.pages[table_config['pages']]
            if isinstance(pdf_pages, list):
                return [
                    {
                        'page_no': i,
                        'text': page.extract_text().splitlines()[:table_config['n_rows'] if isinstance(table_config['n_rows'], int) else table_config['n_rows']['first_page'] if i == 0 else table_config['n_rows']['other_pages']]
                    } for i, page in tqdm(enumerate(pdf_pages))
                ]
            return [{'page_no': 0, 'text': pdf_pages.extract_text().splitlines()[:table_config['n_rows']]}]

    def read_tables(self, table_name, pages):
        if table_name == 'music_royalties':
            self._tables[table_name].update({'pages': f"{min(pages)}-{max(pages)}" if isinstance(pages, range) else pages+1})
        else:
            self._tables[table_name].update({'pages': f"{min(pages)}-{max(pages)+1}" if isinstance(pages, range) else pages+1})
        return self.get_pdf_text(self._tables[table_name]), self.get_pdf_tables(**{k:v for k, v in self._tables[table_name].items() if k != 'n_rows'})

def extract_front_page_text(input_pdf):
    pdf_file_writer = PdfFileWriter()
    pdf_front_page = input_pdf if input_pdf.get('/Rotate') == 0 else input_pdf.rotateClockwise(360+input_pdf.get('/Rotate'))
    pdf_file_writer.addPage(pdf_front_page)
    temp_file = tempfile.TemporaryFile()
    pdf_file_writer.write(temp_file)
    with pdfplumber.open(temp_file) as f:
        return f.pages[0].extract_text()

def determine_document_schema_type(input_pdf_path):
    front_page_text = extract_front_page_text(PdfFileReader(open(input_pdf_path, 'rb')).getPage(0))
    potential_structures = [structure_name for regex, structure_name in pdf_structure_regex_dict.items() if re.match(re.compile(regex, re.DOTALL), front_page_text)]
    if len(potential_structures) == 1:
        front_page_data = format_front_page(potential_structures[0], front_page_text)
        return potential_structures[0], front_page_data

pdf_structure_regex_dict = {
    r'.*WC Music Corp\..*': 'wc_music_corp'
}
