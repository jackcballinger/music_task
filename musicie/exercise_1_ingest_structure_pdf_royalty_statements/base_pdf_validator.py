import codecs
from datetime import datetime
from itertools import chain
from pathlib import Path
import pathlib

from jinja2 import Template
import pandas as pd
import pdfkit

with codecs.open(Path(__file__).parent / "testing_template.html") as f:
    template_code = f.read()

TEMPLATE = Template(template_code)

class BasePDFValidator:
    """
    Class to validate input pdf
    """
    def __init__(
        self,
        config: dict,
        output_folder: pathlib.Path,
        pdf_data: list,
        page_table_numbers: dict,
        front_page_data: dict,
        no_pages: int,
    ):
        self._config = config
        self._output_folder = output_folder
        self._table_config = self._config["tables"]
        self._pdf_data = pdf_data
        self._page_table_numbers = page_table_numbers
        self._front_page_data = front_page_data
        self._no_pages = no_pages
        self._template = TEMPLATE
        self._css_files = [
            Path(__file__).parent
            / "static"
            / "bootstrap-4.1.3-dist"
            / "css"
            / "bootstrap.css",
        ]

    def write_validation_data(self, input_validation_data: dict, test_definitions: dict) -> None:
        """
        Function to write the validation data to an output pdf as specified in the config
        """
        document_result = all(
            x["Result"] == "Pass"
            for x in list(
                chain.from_iterable(
                    chain.from_iterable(list(input_validation_data.values()))
                )
            )
        )
        failures = (
            list(
                chain.from_iterable(
                    chain.from_iterable(
                        [
                            [
                                [
                                    result
                                    for result in test_type
                                    if result["Result"] == "Fail"
                                ]
                                for test_type in v
                            ]
                            for k, v in input_validation_data.items()
                        ]
                    )
                )
            )
            if not document_result
            else []
        )

        template_vars = {
            "title": "Quality Validation Report",
            "document_result": '<h4 style="color:green">Document Result: PASS<h4>'
            if document_result
            else '<h4 style="color:red">Document Result: FAIL<h4>',
            "whole_document_tests": self.format_whole_document_html(
                input_validation_data["whole_document_results"][0]
            ),
            "table_tests": self.format_table_html(
                pd.DataFrame(
                    list(chain.from_iterable(input_validation_data["table_results"]))
                )
                .pivot(index="Test Type", columns="Table Name", values="Result")
                .reset_index()
            ),
            "test_failures": self.format_failures(failures)
            if failures
            else "WOOO NO FAILURES!",
            "test_definitions": test_definitions,
            "document_id": self._front_page_data["unique_id"],
            "date_generated": datetime.today().date().strftime("%d/%m/%Y"),
        }
        html_out = self._template.render(template_vars)
        pdfkit.from_string(
            html_out,
            self._output_folder / self._config["report_output_name"],
            configuration=pdfkit.configuration(
                wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
            ),
            css=self._css_files,
        )

    @staticmethod
    def format_whole_document_html(input_table: list) -> str:
        """
        Function to format the whole document tests into html
        """
        html_string = f"""{pd.DataFrame(input_table).to_html(
            index=False,
            col_space=50,
            justify='left',
            classes=['table']
        ).replace('border="1"','border="0"')}"""
        return html_string

    @staticmethod
    def format_table_html(input_table: list) -> str:
        """
        Function to format the table tests into html
        """
        input_table = input_table.rename_axis(None, axis=1).fillna("Not Applicable")
        html_string = f"""{input_table.to_html(
            index=False,
            col_space=50,
            justify='left',
            classes=['table']
        ).replace('border="1"','border="0"')}"""
        return html_string

    @staticmethod
    def format_failure_dfs(input_failure_dfs: list) -> str:
        """
        Function to format the failure dataframes into html
        """
        if not input_failure_dfs:
            return ""
        formatted_input_failure_dfs = [
            {k.lower().replace(" ", "_"): v for k, v in x.items()}
            for x in input_failure_dfs
        ]
        failure_html_string = "".join(
            [
                f"""<li><p><b>Table Name</b>: {table['table_name']}<p><b>Test Type</b>:
                {table['test_type']}<p><b>Test Calculation</b>: {table['calculation'].to_html(
            index=False,
            col_space=50,
            justify='left',
            classes=['table']
        ).replace('border="1"','border="0"')}</li>"""
                for table in formatted_input_failure_dfs
            ]
        )
        failure_template = Template(
            f"""<div>
                        <ul>
                        {failure_html_string}
                        </ul>
                    </div>"""
        )
        return failure_template.render()

    @staticmethod
    def format_failure_strings(input_failure_strings: list):
        """
        Function to format the failure strings into html
        """
        if not input_failure_strings:
            return ""
        return ""

    def format_failures(self, input_failure: list) -> str:
        """
        Function to format the failure dataframes and strings
        """
        failure_dfs = self.format_failure_dfs(
            [
                failure
                for failure in input_failure
                if isinstance(failure["Calculation"], pd.DataFrame)
            ]
        )
        failure_strings = self.format_failure_strings(
            [
                failure
                for failure in input_failure
                if isinstance(failure["Calculation"], str)
            ]
        )
        return failure_dfs + failure_strings

    @staticmethod
    def validate_data():
        """
        Function to validate the data. Must be overridden
        """
        raise NotImplementedError
