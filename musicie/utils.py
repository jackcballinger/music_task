from datetime import datetime as dt
from io import StringIO
import json
import logging
import os
import pathlib

import boto3
import pandas as pd
import sqlalchemy
import yaml

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__file__)

with open(r"postgres_config.yaml", "r", encoding="utf-8") as file:
    creds = yaml.load(file, Loader=yaml.FullLoader)

engine = sqlalchemy.create_engine(
    f'postgresql://{creds["username"]}:{creds["password"]}@localhost:5432/{creds["database"]}'
)

def list_of_dicts_to_dict(input_list_of_dicts: list) -> dict:
    """
    Function to convert a list of dictionaries to a dictionary
    """
    return dict((key, d[key]) for d in input_list_of_dicts for key in d)

def write_object_to_s3(
    input_df: pd.DataFrame, state: str, dataset_name: str, file_type: str, **kwargs
) -> None:
    """
    Function to write an input object to the correct location in S3
    """
    s3 = boto3.client("s3")
    key = get_s3_key(state, dataset_name, file_type)
    csv_buffer = StringIO()
    input_df.to_csv(csv_buffer, **kwargs)
    s3.put_object(
        Bucket="music-task",
        Key=key,
        Body=csv_buffer.getvalue(),
    )


def get_s3_key(state: str, dataset_name: str, file_type: str) -> str:
    """
    Function to create a valid s3 key given various inputs
    """
    date = dt.utcnow()
    date_path = os.path.join(
        date.strftime("%Y"),
        date.strftime("%m"),
        date.strftime("%d"),
        date.strftime("%H%M%S"),
    )
    return os.path.join(
        state, dataset_name, date_path, dataset_name + "." + file_type
    ).replace("\\", "/")


def write_dataframe_to_sql(
    df: pd.DataFrame, table_name: str, cols=None, **kwargs
) -> None:
    """
    Function to write an input dataframe to a configured sql database
    """
    if cols is not None:
        df[cols].assign(Datestamp=dt.utcnow()).to_sql(table_name, engine, **kwargs)
    else:
        df.assign(Datestamp=dt.utcnow()).to_sql(table_name, engine, **kwargs)


def write_dataframe_to_csv(
    input_df: pd.DataFrame,
    df_name: str,
    output_folder: pathlib.Path,
    cols=None,
    **kwargs,
):
    """
    Function to write an input dataframe to a configured output folder
    """
    output_folder.mkdir(parents=True, exist_ok=True)
    if cols is not None:
        input_df[cols].assign(Datestamp=dt.utcnow()).to_csv(
            output_folder / (df_name + ".csv"), **kwargs
        )
    else:
        input_df.assign(Datestamp=dt.utcnow()).to_csv(
            output_folder / (df_name + ".csv"), **kwargs
        )


def read_data_from_sql(table: str, cols: list) -> pd.DataFrame:
    """
    Function to read data from an sql table
    """
    sql_query = f"""
    SELECT  {','.join(cols)}
    FROM    {table}
    """
    return pd.read_sql(sql_query, con=engine.connect())


def read_data_from_excel(input_path: str, **kwargs) -> pd.DataFrame:
    """
    Function to read data from a specified excel spreadsheet
    """
    return pd.read_excel(input_path, engine="openpyxl", **kwargs)


def write_data_to_sql(input_formatted_tables: dict, **kwargs) -> None:
    """
    Function to iterate through input tables and write data to sql
    """
    _LOGGER.info(f"writing data to sql database")
    for formatted_table_name, formatted_table in input_formatted_tables.items():
        write_dataframe_to_sql(formatted_table, formatted_table_name, **kwargs)


def write_data_to_csv(input_data_tables: dict, output_folder: pathlib.Path, **kwargs) -> None:
    """
    Function to iterate through input tables and write data to csv files
    """
    _LOGGER.info(f"writing data to csv in location {output_folder}")
    for df_name, df in input_data_tables.items():
        write_dataframe_to_csv(df, df_name, output_folder, **kwargs)

def write_data_to_s3(input_data_tables: dict, **kwargs) -> None:
    for df_name, df in input_data_tables.items():
        write_object_to_s3(df, 'trans', df_name, 'csv', **kwargs)
