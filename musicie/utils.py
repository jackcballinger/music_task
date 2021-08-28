from datetime import datetime as dt
import json
from io import StringIO
import os
import re

import boto3
import pandas as pd
import sqlalchemy
import yaml

with open(r'postgres_config.yaml') as file:
    creds = yaml.load(file, Loader=yaml.FullLoader)

engine = sqlalchemy.create_engine(f'postgresql://{creds["username"]}:{creds["password"]}@localhost:5432/{creds["database"]}')

def write_object_to_s3(input_df, state, dataset_name, file_type):
    s3 = boto3.client('s3')
    # csv_buffer = StringIO()
    # input_df.to_csv(csv_buffer, index=False)
    key = get_s3_key(state, dataset_name, file_type)
    s3.put_object(Bucket='music-task', Key=key, Body=json.dumps(input_df.to_dict(orient='records')))

def write_dataframe_to_sql(df, table_name, cols=None, **kwargs):
    if cols is not None:
        df[cols].assign(datestamp=dt.utcnow()).to_sql(table_name, engine, **kwargs)
    else:
        df.assign(datestamp=dt.utcnow()).to_sql(table_name, engine, **kwargs)

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

def format_sql_table(input_table_name, input_table_data):
    input_table_data.columns = [col.replace('-','_') for col in input_table_data.columns]
    # if input_table_name == 'MappingArtistAlias':
    #     print('here')
    if re.match(r'^Dim.*', input_table_name):
        input_table_data.rename(
            columns={
                input_table_data.columns[0]: 'id'
            }, inplace=True
        )
    elif re.match(r'^Mapping.*', input_table_name):
        input_table_data.rename(
            columns={
                **{input_table_data.columns[0]: re.findall('[A-Z][^A-Z]*', input_table_name)[1].lower() + '_' + input_table_data.columns[0]},
                **{col: re.findall('[A-Z][^A-Z]*', input_table_name)[2].lower() + '_' + col.split('.')[-1] if '.' in col else re.findall('[A-Z][^A-Z]*', input_table_name)[2].lower() + '_' + col for col in input_table_data.columns[1:]}
            }, inplace=True
        )
        
    return input_table_data

def write_data_to_sql(input_tables_dict, **kwargs):
    formatted_tables = {table_name: format_sql_table(table_name, table_data) for table_name, table_data in input_tables_dict.items()}
    for formatted_table_name, formatted_table in formatted_tables.items():
        write_dataframe_to_sql(formatted_table, formatted_table_name, **kwargs)
