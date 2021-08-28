import pandas as pd

import musicbrainzngs

# musicbrainzngs auth and setup
musicbrainzngs.auth("test_application", "xqL4RTKh@7#9P4cG")
musicbrainzngs.set_useragent("test_application", "0.1", "http://example.com/music")

def get_work(work_id):
    return musicbrainzngs.get_work_by_id(work_id, includes=['artist-rels'])

def get_work_ids(input_df):
    return list(set(input_df['id']))

def get_works(input_df):
    return {work_id: get_work(work_id) for work_id in get_work_ids(input_df)}

def format_work_attributes(input_df):
    return pd.concat(
        [
            input_df.reset_index(drop=True).drop(columns=['attribute-list']),
            pd.json_normalize(input_df['attribute-list'])
        ], axis=1
    ).dropna().drop_duplicates(subset=['id','attribute']).reset_index(drop=True).rename(columns={'attribute': 'attribute.name'})

def format_work_creators(input_df):
    return (
        input_df[['id','artist.id','artist.role-id']].dropna().reset_index(drop=True),
        input_df[['artist.role-id','artist.role']].dropna().drop_duplicates().reset_index(drop=True)
    )

def format_works(input_works):
    works_df = pd.DataFrame([work['work'] for work in input_works.values()]).explode('artist-relation-list').reset_index(drop=True)
    works_df_exploded = pd.concat(
        [
            works_df,
            pd.json_normalize(works_df['artist-relation-list'])[['type','type-id','target','artist.id','artist.type','artist.name']].rename(columns={'type': 'artist.role', 'type-id': 'artist.role-id'})
        ], axis=1
    ).drop(columns=['iswc-list','artist-relation-list'])
    work_attribute_mapping = format_work_attributes(works_df_exploded[['id','attribute-list']].explode('attribute-list'))
    work_creator_mapping, work_creator_role_mapping = format_work_creators(works_df_exploded.drop(columns=['attribute-list']))
    return {
        'DimWork': works_df[['id','type','title','language','iswc','disambiguation']].drop_duplicates().reset_index(drop=True),
        'DimWorkCreator': work_creator_role_mapping,
        'MappingWorkAttribute': work_attribute_mapping,
        'MappingWorkCreator': work_creator_mapping
    }