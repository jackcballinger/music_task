from pathlib import Path
import pickle

import pandas as pd

from artist_recordings import get_artist_recordings, format_artist_recordings
from artist_works import get_works, format_works
from artists import get_matched_artists, format_artists
from utils import write_data_to_sql, write_object_to_s3

write_mode = False
# read artists to match file
artists_to_match = pd.read_csv(Path(__file__).parent / 'artists_to_match.csv')

# match artists
matched_artists = get_matched_artists(artists_to_match)
artist_outputs = format_artists(matched_artists)

# corresponding recordings
# artist_recordings = get_artist_recordings(artist_outputs['DimArtist'])

with open(Path(__file__).parent.parent / 'artist_recordings.pkl', 'rb') as f:
    artist_recordings = pickle.load(f)

recording_outputs = format_artist_recordings(artist_recordings)

# corresponding works
# artist_works = get_works(recording_outputs['DimRecord'])

with open(Path(__file__).parent / 'work_metadata.pkl', 'rb') as f:
    artist_works = pickle.load(f)
work_outputs = format_works(artist_works)

# with open(Path(__file__).parent.parent / 'all_outputs.pkl', 'rb') as f:
#     all_outputs = pickle.load(f)

# write_data_to_sql(all_outputs, if_exists='replace', index=False)

write_data_to_sql({**artist_outputs, **recording_outputs, **work_outputs}, if_exists='replace', index=False)
