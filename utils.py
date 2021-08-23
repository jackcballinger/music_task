from datetime import datetime as dt

import pandas as pd
import sqlalchemy

with open(r'postgres_config.yaml') as file:
    creds = yaml.load(file, Loader=yaml.FullLoader)

engine = sqlalchemy.create_engine(f'postgresql://{creds["username"]}:{creds["password"]}@localhost:5432/{creds["database"]}')

def write_dataframe_to_sql(df, table_name, cols=None, **kwargs):
    if cols is not None:
        df[cols].to_sql(table_name, engine, **kwargs)
    else:
        df.to_sql(table_name, engine, **kwargs)    