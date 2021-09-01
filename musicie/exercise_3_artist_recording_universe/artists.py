from collections import defaultdict
from itertools import chain
import time

import logging

import pandas as pd

import musicbrainzngs

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__file__)

# musicbrainzngs auth and setup
musicbrainzngs.auth("test_application", "xqL4RTKh@7#9P4cG")
musicbrainzngs.set_useragent("test_application", "0.1", "http://example.com/music")

# musicbrainz functions
def search_recordings(track: str, **kwargs) -> dict:
    """
    Function to search for recordings using the musicbrainszngs api
    """
    return musicbrainzngs.search_recordings(query=track, **kwargs)


def search_artists(artist: str, **kwargs) -> dict:
    """
    Function to search for arists using the musicbrainszngs api
    """
    return musicbrainzngs.search_artists(query=artist, **kwargs)


def browse_recordings(artist: str, **kwargs) -> dict:
    """
    Function to broswse recordings for a specific artist using the musicbrainszngs api
    """
    return musicbrainzngs.browse_recordings(artist=artist, **kwargs)


# formatting functions
def format_search_recording_response(input_recording_response: dict) -> dict:
    """
    Function to format the search recording response
    """
    recording_list = input_recording_response["recording-list"]
    artist_recordings_dict = defaultdict(list)
    for recording in recording_list:
        for artist in recording["artist-credit"]:
            if isinstance(artist, dict):
                artist_recordings_dict[
                    (artist["artist"]["id"], artist["artist"]["name"])
                ].append(recording["id"])
    return {
        k[0]: {"name": k[1], "records": v} for k, v in artist_recordings_dict.items()
    }


def format_search_artist_response(input_artist_response: dict) -> dict:
    """
    Function to format the search artist response
    """
    return {x["id"]: x for x in input_artist_response["artist-list"]}


def format_browse_recordings_response(input_recording_response: dict) -> list:
    """
    Function to format the browse recordings by artist response
    """
    return input_recording_response["recording-list"]


def get_recordings(input_track: str, input_artist: str, **kwargs) -> dict:
    """
    Function to get and format recordings given an input track and artist
    """
    recordings_search_response = search_recordings(
        input_track, artist=input_artist, **kwargs
    )
    return format_search_recording_response(recordings_search_response)


def get_artists(artist_name: str, **kwargs) -> dict:
    """
    Function to get and format artists given an input artist_name
    """
    artist_search_response = search_artists(artist_name, **kwargs)
    return format_search_artist_response(artist_search_response)


def get_artist_recordings(artist_id: str, **kwargs) -> dict:
    """
    Function to get and format artist recordings given an input artist_id
    """
    n_records = browse_recordings(artist_id)["recording-count"]
    recordings = []
    for page in range(int(n_records / 100) + 1):
        recordings.append(
            format_browse_recordings_response(
                browse_recordings(artist_id, limit=100, offset=page * 100, **kwargs)
            )
        )
    return {
        recording["id"]: recording["title"]
        for recording in list(chain.from_iterable(recordings))
    }


def match_artists(input_artist: str, input_track: str) -> tuple(list, str):
    """
    Function that attempts to match input artists and tracks to an artist in the
    musicbrainz ecosystem
    """
    # first attempt
    artist_response_dict = get_artists(input_artist)
    recordings_response_dict = get_recordings(input_track, input_artist)
    cross_validated_artists = set(artist_response_dict).intersection(
        recordings_response_dict
    )
    if len(cross_validated_artists) == 1:
        return [
            artist_response_dict[list(cross_validated_artists)[0]]
        ], "1_cross_validation"

    if len(cross_validated_artists) == 0:
        # if no valid result is returned from the first iteration, introduce the strict=True
        # argument this will reduce down the number of search results, and will hopefully
        # narrow down to the correct song/artist combination
        recordings_response_dict = get_recordings(input_track, input_artist, strict=True)

        cross_validated_artists = set(artist_response_dict).intersection(
            recordings_response_dict
        )
        if len(cross_validated_artists) == 1:
            return [
                artist_response_dict[list(cross_validated_artists)[0]]
            ], "2_cross_validation_strict"

        if len(cross_validated_artists) == 0:
            raise KeyError(f"Unable to match {input_artist}: {input_track}")

    # check to see if the artists are part of the same recording, otherwise we'll miss 'featured'
    # artists etc
    cross_validated_artist_recordings = {
        x: set(recordings_response_dict[x]["records"]) for x in cross_validated_artists
    }
    if (
        len(
            list(cross_validated_artist_recordings.values())[0].intersection(
                *list(cross_validated_artist_recordings.values())
            )
        )
        > max({len(v) for v in cross_validated_artist_recordings.values()}) / 2
    ):
        return [
            artist_response_dict[artist] for artist in cross_validated_artist_recordings
        ], "3_featuring_artists"

    # look at ext:score to further narrow down artist output
    cross_validated_artists_ext = {
        artist
        for artist in cross_validated_artists
        if artist_response_dict[artist]["ext:score"] == "100"
    }
    if len(cross_validated_artists_ext) == 1:
        return [
            artist_response_dict[list(cross_validated_artists_ext)[0]]
        ], "4_ext:score"

    # at this point, we still have more than one possible artist
    # get all recordings for the artist and see if they match
    all_artist_recordings = {
        potential_artist: get_artist_recordings(potential_artist)
        for potential_artist in cross_validated_artists
    }

    n_matching_recordings = {
        artist: len([k for k, v in recordings.items() if v == input_track.title()])
        for artist, recordings in all_artist_recordings.items()
    }
    return [
        artist_response_dict[max(n_matching_recordings, key=n_matching_recordings.get)]
    ], "5_matching_recordings"


def get_matched_artists(input_df: pd.DataFrame) -> list:
    """
    Function to match artists and songs from an input df to musicbrainz ids
    """
    matched_artists = pd.DataFrame()
    for i, (input_artist, input_song) in enumerate(
        zip(input_df["input_artist"], input_df["input_song_name"])
    ):
        _LOGGER.info(
            f"{i+1}/{len(input_df)} - retrieving data for {input_artist}: {input_song}"
        )
        matched_artist, matching_method = match_artists(input_artist, input_song)
        matched_artists = matched_artists.append(
            pd.DataFrame(matched_artist).assign(
                input_artist=input_artist,
                input_song=input_song,
                matching_method=matching_method,
            ),
            ignore_index=True,
        )
        time.sleep(1)
    return matched_artists


def format_area(input_df: pd.DataFrame) -> tuple(pd.DataFrame, pd.DataFrame):
    """
    Function to format the area column of the input dataframe
    """
    artist_area_mapping = (
        pd.concat(
            [
                input_df["id"],
                pd.json_normalize(input_df["area"])
                .drop(columns=["sort-name", "life-span.ended"])
                .rename(
                    columns={"id": "area.id", "type": "area.type", "name": "area.name"}
                ),
            ],
            axis=1,
        )
        .dropna()
        .reset_index(drop=True)
    )
    return (
        artist_area_mapping,
        artist_area_mapping[["area.id", "area.type", "area.name"]]
        .dropna()
        .drop_duplicates()
        .sort_values(by=["area.type", "area.name"])
        .reset_index(drop=True)
    )


def format_artist_alias(input_df: pd.DataFrame) -> pd.DataFrame:
    """
    Function to format the artist-alias column of the input dataframe
    """
    return (
        pd.concat(
            [
                input_df["id"],
                pd.json_normalize(input_df["alias-list"])
                .drop(columns=["sort-name"])
                .rename(columns={"alias": "name"}),
            ],
            axis=1,
        )
        .dropna()
        .reset_index(drop=True)
    )


def format_artists(input_df: pd.DataFrame) -> dict:
    """
    Function to format any information related to artists and return a dictionary of
    relevant tables
    """
    artist_area_mapping, area_metadata = format_area(input_df)
    artist_alias_mapping = format_artist_alias(
        input_df[["id", "alias-list"]].explode("alias-list").reset_index(drop=True)
    )
    return {
        "DimArtist": pd.concat(
            [
                input_df[["id", "type", "name", "country", "disambiguation", "gender"]],
                pd.json_normalize(input_df["life-span"]),
            ],
            axis=1,
        ),
        "DimArea": area_metadata,
        "MappingArtistArea": artist_area_mapping,
        "MappingArtistAlias": artist_alias_mapping,
        "MappingArtistIsni": input_df[["id", "isni-list"]]
        .explode("isni-list")
        .reset_index(drop=True)
        .rename(columns={"isni-list": "isni.value"}),
        "MappingArtistIpi": input_df[["id", "ipi-list"]]
        .explode("ipi-list")
        .dropna()
        .reset_index(drop=True)
        .rename(columns={"ipi-list": "ipi.value"}),
        "MappingInputtrackInputartist": input_df[
            ["input_song", "input_artist", "name", "id"]
        ].rename(columns={"input_song": "track", "input_artist": "artist"}),
    }
