import re
from pathlib import Path

from musicie.exercise_3_artist_recording_universe.artist_recordings import get_artist_recordings, format_artist_recordings
from musicie.exercise_3_artist_recording_universe.artist_works import get_works, format_works
from musicie.exercise_3_artist_recording_universe.artists import get_matched_artists, format_artists
from musicie.utils import write_data_to_sql, read_data_from_excel

def format_table(input_table_name, input_table_data):
    input_table_data.columns = [col.replace('-','_') for col in input_table_data.columns]
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

def format_tables_for_sql(input_tables_dict):
    return {table_name: format_table(table_name, table_data) for table_name, table_data in input_tables_dict.items()}

def run_exercise(input_folder, write_mode=False):
    artists_to_match = read_data_from_excel(
        Path(input_folder) / 'Artists to match_vF.xlsx'
    )

    # match artists
    matched_artists = get_matched_artists(artists_to_match)
    artist_outputs = format_artists(matched_artists)

    # corresponding recordings
    artist_recordings = get_artist_recordings(artist_outputs['DimArtist'])
    recording_outputs = format_artist_recordings(artist_recordings)

    # corresponding works
    artist_works = get_works(recording_outputs['DimRecord'])  
    work_outputs = format_works(artist_works)

    if write_mode:
        # write data to sql
        write_data_to_sql(format_tables_for_sql({**artist_outputs, **recording_outputs, **work_outputs}), if_exists='replace', index=False)
