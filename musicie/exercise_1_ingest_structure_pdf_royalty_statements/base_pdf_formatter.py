from collections import defaultdict
import logging
import re

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__file__)


class BasePDFFormatter:
    def __init__(self, config):
        self._config = config
        self._ignore_tables = self._config.get("ignore_tables", 0)
        self._table_config = self._config["tables"]
        self._func_list = {
            table: [FUNC_DICT[k] for k in functions if k != "enhance_table_data"]
            for table, functions in self._table_config.items()
        }

    def apply_table_formatting(self, input_df: pd.DataFrame, table_name: str) -> dict:
        """
        Functionto apply any table formatting required, as set in the config
        """
        formatted_df = input_df.copy()
        _LOGGER.info("formatting pdf tables")
        for func, args in zip(
            self._func_list[table_name],
            [
                v
                for k, v in self._table_config[table_name].items()
                if k != "enhance_table_data"
            ],
        ):
            if isinstance(args, bool):
                formatted_df = func(formatted_df)
            elif isinstance(args, (str, int, float)):
                formatted_df = func(formatted_df, args)
            elif isinstance(args, dict):
                formatted_df = func(formatted_df, **args)
        return {
            "table_name": table_name,
            "df": formatted_df.reset_index(drop=True),
        }

    def enhance_table_data():
        raise NotImplementedError

    def format_pdf_data():
        raise NotImplementedError


def drop_first_rows(input_df, n):
    return input_df[n:]


def drop_last_rows(input_df, n):
    return input_df[:-n]


def replace_values(input_df, replace_config):
    for k, v in replace_config.items():
        if k != "cols":
            input_df = input_df.replace(k, v, regex=True)
    return input_df


def col_types(input_df, type_mappings):
    return input_df.astype(type_mappings)


def fill_na_values(input_df, how):
    for col, method in how.items():
        input_df[col] = input_df[col].fillna(method=method)
    return input_df


def query_df(input_df, query_string=None):
    return input_df.query(query_string, engine="python")


def normalize_column_names(input_df):
    input_df.columns = [
        re.sub("([a-z0-9])([A-Z])", r"\1_\2", col)
        .lower()
        .strip()
        .replace(" ", "_")
        .replace("\r", "_")
        for col in input_df.columns
    ]
    return input_df


FUNC_DICT = {
    "drop_last_rows": drop_last_rows,
    "drop_first_rows": drop_first_rows,
    "col_types": col_types,
    "fillna": fill_na_values,
    "replace_values": replace_values,
    "query": query_df,
    "normalize_column_names": normalize_column_names,
}


def format_front_page(schema_type, front_page_text):
    return front_page_parsing_dict[schema_type](front_page_text)


def format_wc_music_corp(input_text):
    front_page_split = input_text.splitlines()
    front_page = front_page_split[:1] + front_page_split[5:]

    # join sentences
    formatted_front_page = []
    for i, row in enumerate(front_page):
        if i + 1 <= len(front_page) - 1 and front_page[i + 1][0].islower():
            formatted_front_page.append(row + " " + front_page[i + 1])
            continue
        if not row[0].islower():
            formatted_front_page.append(row)

    # get any obvious key value pairs
    front_page_dict = {
        x.split(":")[0]: x.split(":")[1].strip()
        for x in formatted_front_page
        if ":" in x
    }

    other_front_page_info = [x for x in formatted_front_page if ":" not in x]

    # get closing balance and amount due digits
    closing_balance_amount_due_dict = {
        re.match(r"(Closing Balance|Amount Due)\s(\d+(?:,\d+(?:.\d+)))", x).group(
            1
        ): float(
            re.match(r"(Closing Balance|Amount Due)\s(\d+(?:,\d+(?:.\d+)))", x)
            .group(2)
            .replace(",", "")
        )
        for x in other_front_page_info
        if re.match(r"(Closing Balance|Amount Due)\s(\d+(?:,\d+(?:.\d+)))", x)
    }

    # get date of document
    date_dict = {
        "date": pd.Timestamp(x)
        for x in formatted_front_page
        if re.match(r"\d{4}-\d{2}-\d{2}", x)
    }
    unique_id = (
        front_page_dict["Statement/Invoice No"].replace("/", "").replace(" ", "_")
        + "_"
        + date_dict["date"].strftime("%Y%m%d")
    )
    return {
        **front_page_dict,
        **closing_balance_amount_due_dict,
        **date_dict,
        **{"unique_id": unique_id},
    }


front_page_parsing_dict = {"wc_music_corp": format_wc_music_corp}
