import logging
from pathlib import Path
import pathlib
import re

import pandas as pd

from musicie.exercise_3_artist_recording_universe.artist_recordings import (
    get_artist_recordings,
    format_artist_recordings,
)
from musicie.exercise_3_artist_recording_universe.artist_works import (
    get_works,
    format_works,
)
from musicie.exercise_3_artist_recording_universe.artists import (
    get_matched_artists,
    format_artists,
)
from musicie.utils import write_data_to_s3, write_data_to_sql, read_data_from_excel, write_data_to_csv

# logging
logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__file__)


def format_table(input_table_name: str, input_table_data: pd.DataFrame) -> pd.DataFrame:
    """
    Function to format the input table prior to writing to sql
    """
    input_table_data.columns = [
        col.replace("-", "_") for col in input_table_data.columns
    ]
    if re.match(r"^Dim.*", input_table_name):
        input_table_data.rename(
            columns={
                **{
                    input_table_data.columns[0]: "Id"
                },
                **{
                    col: col.split('.')[-1].title().replace('_','') if '.' in col else col.title().replace('_','') for col in input_table_data.columns[1:]
                }    
            }, inplace=True
        )
    elif re.match(r"^Mapping.*", input_table_name):
        input_table_data.rename(
            columns={
                **{
                    input_table_data.columns[0]: (re.findall(
                        "[A-Z][^A-Z]*", input_table_name
                    )[1].lower()
                    + "_"
                    + input_table_data.columns[0]).replace('id','key').title().replace('_','')
                },
                **{
                    col: (re.findall("[A-Z][^A-Z]*", input_table_name)[2].lower()
                    + "_"
                    + col.split(".")[-1]).replace('id','key').title().replace('_','')
                    if "." in col
                    else (re.findall("[A-Z][^A-Z]*", input_table_name)[2].lower()
                    + "_"
                    + col).replace('id','key').title().replace('_','')
                    for col in input_table_data.columns[1:]
                },
            },
            inplace=True,
        )
    return input_table_data


def format_tables_for_download(input_tables_dict: dict) -> dict:
    """
    Function to format all tables prior to writing to sql
    """
    return {
        table_name: format_table(table_name, table_data)
        for table_name, table_data in input_tables_dict.items()
    }


def run_exercise(
    input_folder: pathlib.Path,
    output_folder: str,
    write_mode=False,
    database_config=None,
    aws_config=None
) -> None:
    """
    Function to run the code for the exercise
    """
    exercise_number = re.search(r".*(\d+).*", Path(__file__).parent.name).group(1)
    _LOGGER.info(f"Running Exercise {exercise_number}")
    artists_to_match = read_data_from_excel(
        Path(input_folder) / "Artists to match_vF.xlsx"
    )

    # match artists
    matched_artists = get_matched_artists(artists_to_match)
    artist_outputs = format_artists(matched_artists)

    # # corresponding recordings
    artist_recordings = get_artist_recordings(artist_outputs["DimArtist"])
    recording_outputs = format_artist_recordings(artist_recordings)

    # corresponding works
    artist_works = get_works(recording_outputs['MappingRecordWork'])
    work_outputs = format_works(artist_works)

    if write_mode:
        # write data to csv
        write_data_to_csv(
            format_tables_for_download(
                {**artist_outputs, **recording_outputs, **work_outputs}
            ),
            Path(output_folder) / Path(__file__).parent.name,
            index=False,
            encoding='utf-8-sig'
        )
        if aws_config is not None:
            write_data_to_s3(
                format_tables_for_download(
                    {**artist_outputs, **recording_outputs, **work_outputs}
                ),
                index=False,
                encoding='utf-8-sig'
            )
        if database_config is not None:
            # write data to sql
            write_data_to_sql(
                format_tables_for_download(
                    {**artist_outputs, **recording_outputs, **work_outputs}
                ),
                if_exists="replace",
                index=False,
            )
