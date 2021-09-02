from collections import defaultdict
import logging
import pathlib
import re
import tempfile
from tqdm import tqdm

import pandas as pd
import pdfplumber
from PyPDF2 import PdfFileReader, PdfFileWriter
import tabula

from musicie.exercise_1_ingest_structure_pdf_royalty_statements.base_pdf_formatter import (
    format_front_page,
)

logging.basicConfig(level=logging.INFO)
logging.getLogger("pdfminer").setLevel(logging.WARNING)
_LOGGER = logging.getLogger(__file__)


class BasePDFReader:
    """
    Class to read the correct data from the pdf specified by the pdf_path
    """
    def __init__(self, pdf_path):
        self._pdf_path = pdf_path

    def get_pdf_tables(self, multiple_tables=True, pages="all") -> list:
        """
        Function to return any tables on the specified pages
        """
        return tabula.read_pdf(
            self._pdf_path, multiple_tables=multiple_tables, pages=pages
        )

    def get_table_pages(self) -> dict:
        """
        Function to get the tables and the corresponding pages for those tables
        """
        all_tables = self.get_pdf_tables()
        all_table_schemas = [table.columns.tolist() for table in all_tables]
        schema_dict = defaultdict(list)
        for i, schema in enumerate(all_table_schemas):
            schema_dict[tuple(schema)].append(i)
        return {
            schema: range(min(pages) + 1, max(pages) + 1)
            if min(pages) != max(pages)
            else min(pages)
            for schema, pages in schema_dict.items()
        }

    def get_pdf_text(self, page: int) -> dict:
        """
        Function to extract any text from the specified page
        """
        with pdfplumber.open(self._pdf_path) as f:
            pdf_page = f.pages[page - 1]
            return {"page_no": page, "text": pdf_page.extract_text().splitlines()}

    def get_page_data(self) -> tuple:
        """
        Function to get all data corresponding to each page of the input document
        """
        _LOGGER.info('obtaining pdf page data')
        pdf = PdfFileReader(open(self._pdf_path, "rb"))
        no_pages = pdf.getNumPages()
        return (
            [
                {
                    "page_number": page_no,
                    "page_tables": self.get_pdf_tables(pages=page_no),
                    "page_text": self.get_pdf_text(page=page_no),
                }
                for page_no in tqdm(range(1, no_pages + 1))
            ],
            self.get_table_pages(),
            no_pages,
        )


def extract_front_page_text(input_pdf: pd.DataFrame) -> str:
    """
    Function to extract text from the front page, rotating if necessary
    """
    pdf_file_writer = PdfFileWriter()
    pdf_front_page = (
        input_pdf
        if input_pdf.get("/Rotate") == 0
        else input_pdf.rotateClockwise(360 + input_pdf.get("/Rotate"))
    )
    pdf_file_writer.addPage(pdf_front_page)
    temp_file = tempfile.TemporaryFile()
    pdf_file_writer.write(temp_file)
    with pdfplumber.open(temp_file) as f:
        return f.pages[0].extract_text()


def determine_document_schema_type(input_pdf_path: pathlib.Path) -> tuple:
    """
    Function to return the correct schema type of the document, as well as the front page data
    """
    front_page_text = extract_front_page_text(
        PdfFileReader(open(input_pdf_path, "rb")).getPage(0)
    )
    potential_structures = [
        structure_name
        for regex, structure_name in pdf_structure_regex_dict.items()
        if re.match(re.compile(regex, re.DOTALL), front_page_text)
    ]
    assert len(potential_structures) == 1, 'narrow down regexes as picking up more than one schema'
    front_page_data = format_front_page(potential_structures[0], front_page_text)
    return potential_structures[0], front_page_data


pdf_structure_regex_dict = {r".*WC Music Corp\..*": "wc_music_corp"}
