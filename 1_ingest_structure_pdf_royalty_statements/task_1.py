import pickle
from pathlib import Path

import yaml

from pdf_formatter import PDFFormatter
from pdf_reader import PDFReader


pdf_path = Path(__file__).parent.parent / 'inputs/2H 2020_Anthony Johnson_US 065824000 001.pdf'

with open(Path(__file__).parent /'config.yaml') as file:
    pdf_config = yaml.load(file, Loader=yaml.FullLoader)

pdf_output_tables = {}

for table, table_config in pdf_config['tables'].items():
    pdf_reader = PDFReader(table_config['read_pdf_config'], pdf_path)
    pdf_text, pdf_tables = pdf_reader.read_tables()
    pdf_formatter = PDFFormatter(table_config['format_pdf_config'])
    pdf_output_tables[table] = pdf_formatter.format_pdf_tables(pdf_tables, pdf_text)

with open('pdf_output.pkl', 'wb') as f:
    pickle.dump(pdf_output_tables, f, protocol=pickle.HIGHEST_PROTOCOL)