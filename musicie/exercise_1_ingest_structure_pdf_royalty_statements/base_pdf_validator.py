from itertools import chain
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, Template
import pandas as pd
import pdfkit

TEMPLATE = Template("""
<html>
<head lang="en">
    <meta charset="UTF-8">
    <title>{{ title }}</title>
</head>
<body>
    <h2>Whole Document Results</h2>
     {{ whole_document_tests }}
     <br>
    <h2>Table Results</h2>
     {{ table_tests }}
</body>
</html>
""")

class BasePDFValidator:
    def __init__(self, config, pdf_data, page_table_numbers, front_page_data, no_pages):
        self._config = config
        self._table_config = self._config['tables']
        self._pdf_data = pdf_data
        self._page_table_numbers = page_table_numbers
        self._front_page_data = front_page_data
        self._no_pages = no_pages
        # self._env = Environment(loader=FileSystemLoader(searchpath="."))
        self._template = TEMPLATE

    def write_validation_data(self, input_validation_data):
        template_vars = {
            "title" : "Quality Validation Report",
            "whole_document_tests": pd.DataFrame(list(chain.from_iterable(input_validation_data['whole_document_results']))).to_html(),
            "table_tests": pd.DataFrame(list(chain.from_iterable(input_validation_data['table_results']))).to_html()
        }
        html_out = self._template.render(template_vars)
        pdfkit.from_string(
            html_out,
            self._config['report_output_name'],
            configuration=pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'),
            css=Path(__file__).parent / 'bootstrap.min.css'
         )


    def validate_data(self):
        raise NotImplementedError

