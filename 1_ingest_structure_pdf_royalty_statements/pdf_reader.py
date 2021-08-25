import logging
from tqdm import tqdm

import pdfplumber
import tabula

logging.basicConfig(level=logging.INFO)
logging.getLogger('pdfminer').setLevel(logging.WARNING)
_LOGGER = logging.getLogger(__file__)

class PDFReader:
    def __init__(self, config, pdf_path):
        self._config = config
        self._n_rows = self._config.get('n_rows', None)
        del self._config['n_rows']
        self._pdf_path = pdf_path

    def get_pdf_tables(self, multiple_tables=True, pages='all'):
        _LOGGER.info('retrieving pdf tables')
        return tabula.read_pdf(
            self._pdf_path,
            multiple_tables=multiple_tables,
            pages=pages
        )
    
    def get_pdf_text(self):
        _LOGGER.info('retrieving pdf text')
        with pdfplumber.open(self._pdf_path) as f:
            pdf_pages = f.pages[
                int(self._config['pages'].split('-')[0])-1: int(self._config['pages'].split('-')[1])
            ] if isinstance(self._config['pages'], str) else f.pages[self._config['pages']-1]
            if isinstance(pdf_pages, list):
                return [
                    {
                        'page_no': i,
                        'text': page.extract_text().splitlines()[:self._n_rows if isinstance(self._n_rows, int) else self._n_rows['first_page'] if i == 0 else self._n_rows['other_pages']]
                    } for i, page in tqdm(enumerate(pdf_pages))
                ]
            return [{'page_no': 0, 'text': pdf_pages.extract_text().splitlines()[:self._n_rows]}]

    def read_tables(self):
        return self.get_pdf_text(), self.get_pdf_tables(**self._config)