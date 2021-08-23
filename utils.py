from datetime import datetime as dt
import json
from io import StringIO
import os

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
