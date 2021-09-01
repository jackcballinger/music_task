from collections import defaultdict
import inspect
from itertools import chain
import logging
import re

import numpy as np
from math import isclose
import pandas as pd

from musicie.exercise_1_ingest_structure_pdf_royalty_statements.base_pdf_formatter import (
    BasePDFFormatter,
)
from musicie.exercise_1_ingest_structure_pdf_royalty_statements.base_pdf_validator import (
    BasePDFValidator,
)

logging.basicConfig(level=logging.INFO)
logging.getLogger("pdfminer").setLevel(logging.WARNING)
_LOGGER = logging.getLogger(__file__)


class WcMusicCorpValidator(BasePDFValidator):
    def __init__(
        self,
        config,
        output_folder,
        pdf_data,
        page_table_numbers,
        front_page_data,
        no_pages,
    ):
        super().__init__(
            config,
            output_folder,
            pdf_data,
            page_table_numbers,
            front_page_data,
            no_pages,
        )

        self._test_definitions = [
            {
                "test_name": "Number of Pages",
                "test_description": "Document test to check that the number of pages parsed is equal to the number of pages in the document",
            },
            {
                "test_name": "Amount Due",
                "test_description": "Table test to check that the amounts due in the various tables tally up with the amount on the front page",
            },
            {
                "test_name": "Scope Sum",
                "test_description": "Table test to check that the amounts paid in the Scope Summary table tally up with those in the Music Royalties table",
            },
            {
                "test_name": "Track Sum",
                "test_description": "Table test to check that the amounts received in the Music Royalties tables corresponding to each song tally with those stated in the document",
            },
        ]

    def validate_amount_due(self, table_data, table_name, col):
        amount_due = self._front_page_data["Amount Due"]
        amount_due_col = table_data[col].sum()
        return {
            "Table Name": table_name.title().replace("_", " "),
            "Test Type": "Amount Due",
            "Calculation": pd.DataFrame(
                [
                    {
                        "table_name": table_name,
                        "stated_amount_due": amount_due,
                        "calculated_amount_due": amount_due_col,
                    }
                ]
            ),
            "Result": "Pass"
            if isclose(amount_due, amount_due_col, abs_tol=10)
            else "Fail",
        }

    def validate_scope_sum(self, table_data, table_name, *args):
        scope_sum = self._pdf_data["scope_summary"][
            ["scope_name", "gross_payable"]
        ].to_dict(orient="records")
        return {
            "Table Name": table_name.title().replace("_", " "),
            "Test Type": "Scope Sum",
            "Calculation": pd.DataFrame(
                [
                    {
                        "table_name": table_name,
                        "scope_name": item["scope_name"],
                        "scope_stated_sum": table_data[
                            table_data["scope"] == item["scope_name"]
                        ]["amount_paid"].sum(),
                        "scope_calculated_sum": item["gross_payable"],
                    }
                    for item in scope_sum
                ]
            ),
            "Result": "Pass"
            if all(
                [
                    isclose(
                        table_data[table_data["scope"] == item["scope_name"]][
                            "amount_paid"
                        ].sum(),
                        item["gross_payable"],
                        abs_tol=10,
                    )
                    for item in scope_sum
                ]
            )
            else "Fail",
        }

    def validate_track_sum(self, table_data, table_name, *args):
        track_amount_received = table_data.groupby("track_title")[
            "amount_received"
        ].sum()
        return {
            "Table Name": table_name.title().replace("_", " "),
            "Test Type": "Track Sum",
            "Calculation": pd.DataFrame(
                [
                    {
                        "table_name": table_name,
                        "track_name": track_name,
                        "track_stated_sum": table_data[
                            table_data["track_title"] == track_name
                        ]["track_amount_received"]
                        .astype("float")
                        .unique()
                        .sum(),
                        "track_calculated_sum": track_sum,
                    }
                    for track_name, track_sum in track_amount_received.items()
                ]
            ),
            "Result": "Pass"
            if all(
                [
                    isclose(
                        table_data[table_data["track_title"] == track_name][
                            "track_amount_received"
                        ]
                        .astype("float")
                        .unique()
                        .sum(),
                        track_sum,
                        abs_tol=10,
                    )
                    for track_name, track_sum in track_amount_received.items()
                ]
            )
            else "Fail",
        }

    def validate_num_pages(self, table_data):
        return {
            "Test Type": "Number of Pages",
            "Calculation": f"{table_data['page_number'].max()} == {self._no_pages}",
            "Result": "Pass"
            if table_data["page_number"].max() == self._no_pages
            else "Fail",
        }

    def validate_table(self, table_name, table_data, table_funcs):
        return [
            func(
                self, table_data, table_name, self._table_config[table_name][func_name]
            )
            for func_name, func in table_funcs.items()
        ]

    def validate_data(self):
        tests_result = defaultdict(list)
        for table_name, table in self._pdf_data.items():
            table_funcs = {
                k: validation_dict[k] for k in self._table_config[table_name]
            }
            table_results = self.validate_table(table_name, table, table_funcs)
            tests_result["table_results"].append(table_results)
        document_results = [self.validate_num_pages(list(self._pdf_data.values())[-1])]
        tests_result["whole_document_results"].append(document_results)
        self.write_validation_data(tests_result, self._test_definitions)
        return tests_result


class WcMusicCorpFormatter(BasePDFFormatter):
    def __init__(self, config):
        super().__init__(config)

    def format_pdf_data(self, input_page_data, input_page_table_numbers):
        enhanced_tables_dict = self.match_correct_tables(
            input_page_data, input_page_table_numbers
        )
        formatted_tables = [
            self.apply_table_formatting(input_df, table_name)
            for table_name, input_df in enhanced_tables_dict.items()
        ]
        return {table["table_name"]: table["df"] for table in formatted_tables}, list(
            input_page_table_numbers.values()
        )[self._ignore_tables :]

    def match_correct_tables(self, input_page_data, input_page_table_numbers):
        pdf_tables = {}
        for page_table_numbers, (table_name, table_config) in zip(
            list(input_page_table_numbers.values())[self._ignore_tables :],
            self._table_config.items(),
        ):
            data_enhancements = table_config.get("enhance_table_data", None)
            if isinstance(page_table_numbers, int):
                page_table_numbers_list = [page_table_numbers + 1]
            elif isinstance(page_table_numbers, range):
                page_table_numbers_list = list(page_table_numbers) + [
                    max(page_table_numbers) + 1
                ]
            corresponding_page_data = [
                page
                for page in input_page_data
                if page["page_number"] in page_table_numbers_list
            ]
            if data_enhancements:
                pdf_tables[table_name] = pd.concat(
                    list(
                        chain.from_iterable(
                            [
                                page["page_tables"]
                                for page in self.enchance_table_data(
                                    corresponding_page_data,
                                    table_config["enhance_table_data"],
                                    pdf_tables,
                                )
                            ]
                        )
                    ),
                    ignore_index=True,
                )
            else:
                pdf_tables[table_name] = pd.concat(
                    list(
                        chain.from_iterable(
                            [page["page_tables"] for page in corresponding_page_data]
                        )
                    ),
                    ignore_index=True,
                )
        return pdf_tables

    def enchance_table_data(
        self, page_data_list, enhance_table_data_config, prev_tables
    ):
        output_table_data = page_data_list.copy()
        arg_mapping = {
            "input_page_data": output_table_data,
            "scope_table": prev_tables.get("scope_summary", None),
        }
        for enhancement in enhance_table_data_config:
            func = enhancement_dict[enhancement]
            input_args = {
                arg: (arg_mapping[arg] if arg in arg_mapping else None)
                for arg in inspect.getfullargspec(func).args
            }
            output_table_data = func(**input_args)
        return output_table_data


def add_page_numbers(input_page_data):
    for page in input_page_data:
        page["page_tables"] = [
            table.assign(page_number=page["page_number"])
            for table in page["page_tables"]
        ]
    return input_page_data


def add_scope(input_page_data, scope_table):
    for page in input_page_data:
        record_scope = set(scope_table["Scope Name"]).intersection(
            set(page["page_text"]["text"])
        )
        if len(record_scope) == 1:
            page["page_tables"] = [
                table.assign(scope=list(record_scope)[0])
                for table in page["page_tables"]
            ]
        else:
            page["page_tables"] = [
                table.assign(scope=np.nan) for table in page["page_tables"]
            ]
    return input_page_data


def extract_track_titles(input_page_data):
    for page in input_page_data:
        output_page_tables = []
        for page_table in page["page_tables"]:
            if not page_table.empty:
                page_table["track_information"] = page_table["Income Type"][
                    page_table["Statement Id"].isna()
                ]
                page_table["track_title"] = (
                    page_table["track_information"]
                    .fillna(method="ffill")
                    .str.split("-")
                    .str[0]
                    .replace("\s+", " ", regex=True)
                )
                page_table["track_title"] = page_table["track_title"].apply(
                    lambda x: x
                    if re.match(r"\b[A-Z][A-Z]+\b", x) and not "," in x
                    else None
                )
                track_totals = (
                    page_table["track_information"]
                    .str.replace(",", "")
                    .str.extractall(r"(\d+\.\d{3})")
                    .unstack()
                )
                track_totals.columns = track_totals.columns.droplevel()
                output_df = pd.concat(
                    [
                        page_table.drop(columns=["track_information"]),
                        track_totals.rename(
                            columns={0: "track_amount_received", 1: "track_amount_paid"}
                        ),
                    ],
                    axis=1,
                )
                output_df[["track_amount_received", "track_amount_paid"]] = output_df[
                    ["track_amount_received", "track_amount_paid"]
                ].fillna(method="ffill")
                output_page_tables.append(output_df)
        page["page_tables"] = output_page_tables
    return input_page_data


enhancement_dict = {
    "scope": add_scope,
    "track_titles": extract_track_titles,
    "add_page_numbers": add_page_numbers,
}

validation_dict = {
    "validate_amount_due": WcMusicCorpValidator.validate_amount_due,
    "validate_scope_sum": WcMusicCorpValidator.validate_scope_sum,
    "validate_track_sum": WcMusicCorpValidator.validate_track_sum,
}
