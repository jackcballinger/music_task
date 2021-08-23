from pathlib import Path

import pandas as pd

from match_artists import get_matched_artists

# read artists to match file
artists_to_match = pd.read_csv(Path(__file__).parent / 'artists_to_match.csv')

# match artists
matched_artists = get_matched_artists(artists_to_match)

