"""

A script to download data from US Census website
and organise into database

"""

import pandas as pd
import geopandas as gpd
import numpy as np
from census import Census
import us
import ConfigParser
import urllib
import zipfile
import pickle

print 'Loading census'
# loading the census api key
config = ConfigParser.ConfigParser()
config.read('census_api.ini')
census_api_key = config.get('census_api', 'key')
# setting up a census object
c = Census(census_api_key, year=2013)

print '2013 American Community Survey data'
print 'Constructing variables'

## collecting variables to match the 
## at risk groups as defined by the cdc
vars_acs_block = {}
vars_acs_block['m_u5'] = 'B01001_003E'
vars_acs_block['f_u5'] = 'B01001_027E'

# year structure was built
vars_acs_block['built_total'] = 'B25034_001E'
vars_acs_block['built_1970s'] = 'B25034_006E'
vars_acs_block['built_1960s'] = 'B25034_007E'
vars_acs_block['built_1950s'] = 'B25034_008E'
vars_acs_block['built_1940s'] = 'B25034_009E'
vars_acs_block['built_before_1940'] = 'B25034_010E'

"""
young children in 'racial-ethnic minority groups'

I don't know what the CDC mean by this statement. 
I could not find evidence of specific groups.

After discussions with colleagues I selected children 
under 5 identified as black, indigenous or latin.
"""

# backgrounds of children
vars_acs_tract = {}
vars_acs_tract['m_u5_black'] = 'B01001B_003E'
vars_acs_tract['f_u5_black'] = 'B01001B_027E'
vars_acs_tract['m_u5_indig'] = 'B01001C_003E'
vars_acs_tract['f_u5_indig'] = 'B01001C_027E'
vars_acs_tract['m_u5_latin'] = 'B01001H_003E'
vars_acs_tract['f_u5_latin'] = 'B01001H_027E'

# young children born overseas
vars_acs_tract['foreign_parents_u6'] = 'B05009_007E'
vars_acs_tract['one_foreign_parent_one_us_parent_u6_foreign'] = 'B05009_012E'
vars_acs_tract['foreign_parents_u6_foreign'] = 'B05009_009E'
vars_acs_tract['one_foreign_parent_u6_foreign'] = 'B05009_019E'
vars_acs_tract['foreign_born_child'] = 'B05009_005E'

# poverty level
vars_acs_tract['poverty_level_u100'] = 'B06012_002E'
vars_acs_tract['poverty_level_u149_o100'] = 'B06012_003E'

# intersection of poverty and foreign born
vars_acs_tract['poverty_level_u100_foreign'] = 'B06012_018E'
vars_acs_tract['poverty_level_u149_o100_foreign'] = 'B06012_019E'

print 'Downloading and storing database'

# getting state fips
df_states = pd.DataFrame(c.acs5.state( 'NAME', Census.ALL))
state_dict = us.states.mapping('fips', 'name')
state_fips = [a for a in state_dict.keys() if a != None]

print 'Downloading data for', state_dict[state_fips[0]]
# initialising the database with the first state
df_tmp = pd.DataFrame(
        c.acs5.state_county(
            vars_acs_block.values(),
            state_fips[0],
            Census.ALL))

tmp_county_fips = df_tmp['county']

df_blocks = pd.DataFrame(
        c.acs5.state_county_blockgroup(
            vars_acs_block.values(),
            state_fips[0],
            tmp_county_fips[0],
            Census.ALL))

df_tracts = pd.DataFrame(
        c.acs5.state_county_tract(
            vars_acs_tract.values(),
            state_fips[0],
            tmp_county_fips[0],
            Census.ALL))

# looping through other counties in the first state
for county_fip in tmp_county_fips[1:]:
    # blocks
    df_tmp = pd.DataFrame(
            c.acs5.state_county_blockgroup(
                vars_acs_block.values(),
                state_fips[0],
                county_fip,
                Census.ALL))
    df_blocks = pd.concat([df_blocks, df_tmp])
    # tracts
    df_tmp = pd.DataFrame(
            c.acs5.state_county_tract(
                vars_acs_tract.values(),
                state_fips[0],
                county_fip,
                Census.ALL))
    df_tracts = pd.concat([df_tracts, df_tmp])

# now looping through the rest of the counties in the rest of the states
for state_fip in state_fips[1:]:
    print 'downloading data for', state_dict[state_fip]
    if state_dict[state_fip] == 'Kansas':
        pass
    df_tmp = pd.DataFrame(
        c.acs5.state_county(
            vars_acs_block.values(),
            state_fips[0],
            Census.ALL))
    try:
        tmp_county_fips = df_tmp['county']
        # looping through counties
        for county_fip in tmp_county_fips:
            # blocks
            df_tmp = pd.DataFrame(
                c.acs5.state_county_blockgroup(
                    vars_acs_block.values(),
                    state_fip,
                    county_fip,
                    Census.ALL))
            df_blocks = pd.concat([df_blocks, df_tmp])
            # tracts
            df_tmp = pd.DataFrame(
                c.acs5.state_county_tract(
                    vars_acs_tract.values(),
                    state_fip,
                    county_fip,
                    Census.ALL))
            df_tracts = pd.concat([df_tracts, df_tmp])
    except KeyError:
        pass

# swapping keys and values of dictionary for dataframe relabeling
vars_acs_tract = {y:x for x, y in vars_acs_tract.iteritems()}
vars_acs_block = {y:x for x, y in vars_acs_block.iteritems()}

df_tracts.rename(columns = vars_acs_tract, inplace=True)
df_blocks.rename(columns = vars_acs_block, inplace=True)

print 'Merging databases'
df = pd.merge(df_blocks, df_tracts,
        on = ['state', 'county', 'tract'],
        how = 'outer')

df.rename(columns = {'block group': 'blockgroup'}, inplace = True)

print 'Creating new variables'

old_houses = df.built_1970s + df.built_1960s + df.built_1950s + df.built_1940s+\
            df.built_before_1940

df['old_houses'] = old_houses

minority_children = df.f_u5_indig + df.m_u5_indig + \
                    df.f_u5_black + df.m_u5_black + \
                    df.f_u5_latin + df.m_u5_latin

df['minority_children'] = minority_children

u6_foreign = df.foreign_parents_u6_foreign + \
        df.one_foreign_parent_u6_foreign + \
        df.one_foreign_parent_one_us_parent_u6_foreign \

df['foreign'] = u6_foreign

povlvl = df.poverty_level_u100 + df.poverty_level_u149_o100
povlvl_f = df.poverty_level_u100_foreign + df.poverty_level_u149_o100_foreign

df['poverty_level'] = povlvl
df['poverty_level_foreign'] = povlvl_f

print 'Saving dataframe to csv'
df.to_csv('lead_ranking_data.csv')

print 'Getting shapefiles'

# getting base url strings
base_url = us.states.NY.shapefile_urls()['blockgroup']
base, end = base_url.split('36')

urls = []
for fip in state_fips:
    urls.append( base + fip + end)

def download_data(url):
    """
    input:
        url string
    output:
        none. extracts downloaded zipfile into
        a folder called 'shapefiles'
    """
    spatialfile = 'spatialfile.zip'
    urllib.urlretrieve(url, spatialfile)
    zfile = zipfile.ZipFile(spatialfile)
    zfile.extractall('shapefiles/')
    return 0

print 'downloading and extracting shapefiles'
map(lambda x: download_data(x), urls)
print 'Done'

print 'merging shapefiles with database'
# basic download

def shape_file_merger(fip, df):
    """
    merges a state's shape file with the database
    input:
        fip: string, state fip code
        df: pandas dataframe
    output:
        df: merged dataframe
    """""
    gdp_tmp = gpd.GeoDataFrame.from_file(
                    'shapefiles/tl_2010_%s_bg10.shp' % fip)
    gdp_tmp.rename(columns = {
                'COUNTYFP10' : 'county',
                'TRACTCE10' : 'tract',
                'BLKGRPCE10' : 'blockgroup' }, inplace = True)
    # creating state var for merging
    gdp_tmp['state'] = int(fip)
    # converting key values to integers
    gdp_tmp.county = gdp_tmp.county.astype(int)
    gdp_tmp.tract = gdp_tmp.tract.astype(int)
    gdp_tmp.blockgroup = gdp_tmp.blockgroup.astype(int)
    df = pd.merge(df, gdp_tmp, on = ['state', 'county',
                'tract', 'blockgroup'], how = 'left')
    return df

df.rename(columns = {'block group' : 'blockgroup'}, inplace = True)

for fip in state_fips:
    print 'downloading shapefile for', state_dict[fip]
    df = shape_file_merger(fip, df)

print 'Saving spatial dataframe to pickle'
pickle.dump(df, open('lead_ranking_data_shp.p', 'wb'))
print 'Done. Good job!'

