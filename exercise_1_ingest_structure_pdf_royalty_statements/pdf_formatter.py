import logging
import re

import pandas as pd

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__file__)

class PDFFormatter:
    def __init__(self, config):
        self._config = config
        self._func_list = [FUNC_DICT[k] for k in self._config if k != 'add_song_titles']

    def format_pdf_tables(self, input_dfs: list, input_text: dict):
        formatted_df = pd.concat(input_dfs, ignore_index=True)
        _LOGGER.info('formatting pdf tables')
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

def extract_track_titles(input_df):
    input_df['track_information'] = input_df['Income Type'][input_df['Statement Id'].isna()]
    input_df['track_title'] = input_df['track_information'].fillna(method='ffill').str.split('-').str[0].replace('\s+', ' ', regex=True)
    track_totals = input_df['track_information'].str.extractall(r'(\d+\.\d{3})').unstack()
    track_totals.columns = track_totals.columns.droplevel()
    output_df = pd.concat(
        [
            input_df, 
            track_totals.rename(
                columns={
                    0: 'track_amount_received',
                    1: 'track_amount_paid'
                }
            )
        ], axis=1
    )
    output_df[['track_amount_received', 'track_amount_paid']] = output_df[['track_amount_received', 'track_amount_paid']].fillna(method='ffill')
    return output_df
        
def drop_first_rows(input_df, n):
    return input_df[n:]

def drop_last_rows(input_df, n):
    return input_df[:-n]

def replace_values(input_df, replace_config):
    for k, v in replace_config.items():
        if k != 'cols':
            input_df = input_df.replace(k, v, regex=True) 
    return input_df

def col_types(input_df, type_mappings):
    return input_df.astype(
        type_mappings
    )

def fill_na_values(input_df, how):
    for col, method in how.items():
        input_df[col] = input_df[col].fillna(method=method)
    return input_df
    
def query_df(input_df, query_string=None):
    return input_df.query(query_string, engine='python')

def normalize_column_names(input_df):
    input_df.columns = [re.sub("([a-z0-9])([A-Z])", r"\1_\2", col).lower().strip().replace(" ","_").replace("\r", '_') for col in input_df.columns]
    return input_df

FUNC_DICT = {
    'extract_track_titles': extract_track_titles,
    'drop_last_rows': drop_last_rows,
    'drop_first_rows': drop_first_rows,
    'col_types': col_types,
    'fillna': fill_na_values,
    'replace_values': replace_values,
    'query': query_df,
    'normalize_column_names': normalize_column_names
}