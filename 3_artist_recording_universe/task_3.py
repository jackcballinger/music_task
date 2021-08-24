from pathlib import Path

import pandas as pd

from match_artists import get_matched_artists
from artist_recordings import get_artist_recordings
from utils import write_dataframe_to_sql, write_object_to_s3, read_data_from_sql

write_mode = False
# read artists to match file
artists_to_match = pd.read_csv(Path(__file__).parent / 'artists_to_match.csv')

# match artists
matched_artists = get_matched_artists(artists_to_match)
if write_mode:
    write_object_to_s3(
        matched_artists,
        'raw',
        'artist_mapping',
        'json')

# corresponding recordings
artist_recordings = get_artist_recordings(matched_artists[['id','name']])
if write_mode:
    write_object_to_s3(
        artist_recordings,
        'raw',
        'recordings',
        'json')

pass
