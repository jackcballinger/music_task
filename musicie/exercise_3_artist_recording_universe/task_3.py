from pathlib import Path

from musicie.exercise_3_artist_recording_universe.artist_recordings import get_artist_recordings, format_artist_recordings
from musicie.exercise_3_artist_recording_universe.artist_works import get_works, format_works
from musicie.exercise_3_artist_recording_universe.artists import get_matched_artists, format_artists
from musicie.utils import write_data_to_sql, read_data_from_excel


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
        write_data_to_sql({**artist_outputs, **recording_outputs, **work_outputs}, if_exists='replace', index=False)
