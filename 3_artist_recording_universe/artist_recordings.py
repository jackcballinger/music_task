import logging

import pandas as pd

import musicbrainzngs

from utils import read_data_from_sql

logging.basicConfig(level=logging.INFO)
logging.getLogger('musicbrainzngs').setLevel(logging.WARNING)
_LOGGER = logging.getLogger(__file__)

# musicbrainzngs auth and setup
musicbrainzngs.auth("test_application", "xqL4RTKh@7#9P4cG")
musicbrainzngs.set_useragent("test_application", "0.1", "http://example.com/music")

def browse_artist_recordings(input_artist_id, **kwargs):
    no_recordings = musicbrainzngs.browse_recordings(artist=input_artist_id)['recording-count']
    _LOGGER.info(f"Paginating: {no_recordings} found")
    recordings = pd.DataFrame()
    for page in range(int(no_recordings/100)+1):
        recordings = recordings.append(
            pd.DataFrame(
                musicbrainzngs.browse_recordings(
                    artist=input_artist_id,
                    offset=page*100,
                    **kwargs
                )['recording-list']
            ), ignore_index=True
        ).assign(artist_id=input_artist_id)
    return recordings

def get_artist_recordings(artist_id_df):
    artist_recordings = pd.DataFrame()
    for i, (artist_id, name) in enumerate(zip(artist_id_df['id'], artist_id_df['name'])):
        _LOGGER.info(f"{i+1}/{len(artist_id_df)} - retrieving data for {artist_id}: {name}")
        artist_recordings = artist_recordings.append(
            browse_artist_recordings(artist_id, includes=['isrcs', 'artist-rels', 'work-rels', 'label-rels'], limit=100).assign(artist_id=artist_id),
            ignore_index=True
        )
    return artist_recordings
