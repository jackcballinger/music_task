import logging

import pandas as pd

import musicbrainzngs

logging.basicConfig(level=logging.INFO)
logging.getLogger("musicbrainzngs").setLevel(logging.WARNING)
_LOGGER = logging.getLogger(__file__)

# musicbrainzngs auth and setup
musicbrainzngs.auth("test_application", "xqL4RTKh@7#9P4cG")
musicbrainzngs.set_useragent("test_application", "0.1", "http://example.com/music")


def browse_artist_recordings(input_artist_id, **kwargs):
    no_recordings = musicbrainzngs.browse_recordings(artist=input_artist_id)[
        "recording-count"
    ]
    _LOGGER.info(f"Paginating: {no_recordings} found")
    recordings = pd.DataFrame()
    for page in range(int(no_recordings / 100) + 1):
        recordings = recordings.append(
            pd.DataFrame(
                musicbrainzngs.browse_recordings(
                    artist=input_artist_id, offset=page * 100, **kwargs
                )["recording-list"]
            ),
            ignore_index=True,
        ).assign(artist_id=input_artist_id)
    return recordings


def get_artist_recordings(artist_id_df):
    artist_recordings = pd.DataFrame()
    for i, (artist_id, name) in enumerate(
        zip(artist_id_df["id"], artist_id_df["name"])
    ):
        _LOGGER.info(
            f"{i+1}/{len(artist_id_df)} - retrieving data for {artist_id}: {name}"
        )
        artist_recordings = artist_recordings.append(
            browse_artist_recordings(
                artist_id,
                includes=["isrcs", "artist-rels", "work-rels", "label-rels"],
                limit=100,
            ).assign(artist_id=artist_id),
            ignore_index=True,
        )
    return artist_recordings


def format_artist_relations(input_df):
    artist_relation_df = pd.concat(
        [
            input_df["id"],
            pd.json_normalize(input_df["artist-relation-list"])[
                ["type", "type-id", "artist.id", "artist.type", "artist.name"]
            ].rename(columns={"type": "artist.role", "type-id": "artist.role-id"}),
        ],
        axis=1,
    )
    return (
        input_df[["id", "artist_id"]]
        .dropna()
        .drop_duplicates()
        .reset_index(drop=True)
        .rename(columns={"artist_id": "artist.id"}),
        artist_relation_df[["id", "artist.id", "artist.role-id"]]
        .dropna()
        .drop_duplicates()
        .reset_index(drop=True),
        artist_relation_df[["artist.role-id", "artist.role"]]
        .dropna()
        .drop_duplicates()
        .reset_index(drop=True),
    )


def format_record_works(input_df):
    record_work_relations = pd.concat(
        [
            input_df.reset_index(drop=True).drop(columns=["work-relation-list"]),
            pd.json_normalize(input_df["work-relation-list"]),
        ],
        axis=1,
    )
    return (
        record_work_relations[["id", "work.id"]]
        .dropna()
        .drop_duplicates()
        .reset_index(drop=True)
    )


def format_record_label(input_df):
    label_relation_df = pd.concat(
        [input_df["id"], pd.json_normalize(input_df["label-relation-list"])], axis=1
    )
    return (
        label_relation_df[["id", "type-id", "label.id", "begin", "end", "ended"]]
        .drop_duplicates()
        .reset_index(drop=True),
        label_relation_df[["label.id", "label.type", "label.name", "label.label-code"]]
        .drop_duplicates()
        .reset_index(drop=True),
        label_relation_df[["type-id", "type"]]
        .dropna()
        .drop_duplicates()
        .reset_index(drop=True),
    )


def format_artist_recordings(input_df):
    (
        record_artist_mapping,
        record_creator_mapping,
        record_creator_role_mapping,
    ) = format_artist_relations(
        input_df.explode("artist-relation-list").reset_index(drop=True)
    )
    record_work_mapping = format_record_works(
        input_df[["id", "work-relation-list"]].explode("work-relation-list")
    )
    record_label_mapping, label_metadata, label_type_mapping = format_record_label(
        input_df[["id", "label-relation-list"]]
        .explode("label-relation-list")
        .dropna()
        .reset_index(drop=True)
    )
    return {
        "DimRecord": input_df[["id", "title", "disambiguation", "video"]],
        "DimLabel": label_metadata,
        "DimLabelType": label_type_mapping,
        "DimRecordCreatorType": record_creator_role_mapping,
        "MappingRecordIsrc": input_df[["id", "isrc-list"]]
        .dropna()
        .explode("isrc-list")
        .reset_index(drop=True)
        .rename(columns={"isrc-list": "isrc.value"}),
        "MappingRecordWork": record_work_mapping,
        "MappingRecordArtist": record_artist_mapping,
        "MappingRecordCreator": record_creator_mapping,
        "MappingRecordLabel": record_label_mapping,
    }
