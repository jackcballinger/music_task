from datetime import datetime as dt
import json
import os
from pathlib import Path

import boto3
import pandas as pd
import sqlalchemy
import yaml

with open(r'postgres_config.yaml') as file:
    creds = yaml.load(file, Loader=yaml.FullLoader)

engine = sqlalchemy.create_engine(f'postgresql://{creds["username"]}:{creds["password"]}@localhost:5432/{creds["database"]}')

def write_object_to_s3(input_df, state, dataset_name, file_type):
    s3 = boto3.client('s3')
    key = get_s3_key(state, dataset_name, file_type)
    s3.put_object(Bucket='music-task', Key=key, Body=json.dumps(input_df.to_dict(orient='records')))

def write_dataframe_to_sql(df, table_name, cols=None, **kwargs):
    if cols is not None:
        df[cols].assign(datestamp=dt.utcnow()).to_sql(table_name, engine, **kwargs)
    else:
        df.assign(datestamp=dt.utcnow()).to_sql(table_name, engine, **kwargs)

def write_dataframe_to_csv(input_df, df_name, output_folder, cols=None, **kwargs):
    output_folder.mkdir(parents=True, exist_ok=True)
    if cols is not None:
        input_df[cols].assign(datestamp=dt.utcnow()).to_csv(output_folder / (df_name + '.csv'), **kwargs)
    else:
        input_df.assign(datestamp=dt.utcnow()).to_csv(output_folder / (df_name + '.csv'), encoding='utf-8-sig', **kwargs)

def read_data_from_sql(table, cols):
    sql_query = f"""
    SELECT  {','.join(cols)}
    FROM    {table}
    """
    return pd.read_sql(sql_query, con=engine.connect())

def read_data_from_excel(input_path, **kwargs):
    return pd.read_excel(
        input_path, engine='openpyxl', **kwargs
    )

def get_s3_key(state, dataset_name, file_type):
    date = dt.utcnow()
    date_path = os.path.join(
        date.strftime('%Y'),
        date.strftime('%m'),
        date.strftime('%d'),
        date.strftime('%H%M%S')
    )
    return os.path.join(
        state,
        dataset_name,
        date_path,
        dataset_name + '.'+ file_type
    ).replace('\\', '/')

def write_data_to_sql(input_formatted_tables, **kwargs):
    for formatted_table_name, formatted_table in input_formatted_tables.items():
        write_dataframe_to_sql(formatted_table, formatted_table_name, **kwargs)

def write_data_to_csv(input_data_tables, output_folder, **kwargs):
    for df_name, df in input_data_tables.items():
        write_dataframe_to_csv(df, df_name, output_folder, **kwargs)