import re

import pandas as pd

class PDFFormatter:
    def __init__(self, config):
        self._config = config
        self._func_list = [FUNC_DICT[k] for k in self._config]

    def format_pdf_tables(self, input_dfs: list, input_text: dict):
        formatted_df = pd.concat(input_dfs, ignore_index=True)
        for func, args in zip(self._func_list, self._config.values()):
            if isinstance(args, bool):
                formatted_df = func(formatted_df)
            elif isinstance(args, (str, int, float)):
                formatted_df = func(formatted_df, args)
            elif isinstance(args, dict):
                formatted_df = func(formatted_df, **args)
        return {
            'df': formatted_df.reset_index(drop=True),
            'metadata': input_text
        }
        
        
def drop_last_row(input_df, n):
    return input_df[:-n]

def replace_values(input_df, replace_config):
    for k, v in replace_config.items():
        if k != 'cols':
            return input_df.replace(k, v, regex=True) 

def col_types(input_df, type_mappings):
    return input_df.astype(
        type_mappings
    )

def fill_na_values(input_df, how):
    for col, method in how.items():
        input_df[col] = input_df[col].fillna(method=method)
    return input_df
    
def query_df(input_df, includes_query=None, not_query=None):
    if includes_query is not None:
        input_df = input_df.query(not_query, engine='python')
    if not_query is not None:
        input_df = input_df.query(not_query, engine='python')
    return input_df

def normalize_column_names(input_df):
    input_df.columns = [re.sub("([a-z0-9])([A-Z])", r"\1_\2", col).lower().strip().replace(" ","_") for col in input_df.columns]
    return input_df

FUNC_DICT = {
    'drop_last_rows': drop_last_row,
    'col_types': col_types,
    'fillna': fill_na_values,
    'replace_values': replace_values,
    'query': query_df,
    'normalize_column_names': normalize_column_names
}