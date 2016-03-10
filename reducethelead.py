"""

A script to rank regions

This is an interactive terminal ~experience~

"""

import pandas as pd
import numpy as np
import geopandas as gpd
import sys
import us
from sklearn.decomposition import PCA

class reduceTheLead():
    def __init__(self, df):
        self.df = df
        self.df_dropna = df.dropna(axis=0, how='any')
        self.explanatory_vars = ['old_houses', 'minority_children', 'foreign_u6',
                                'poverty_level', 'poverty_foreign']
        self.state_dict = us.states.mapping('abbr', 'fips')
        print 'Welcome to Reduce the Lead'
        print ''
        allowable_selection = {
                 'A': 'Nationwide across States',
                 'B': 'Nationwide across Counties',
                 'C': 'Statewide across Counties' ,
                 'D': 'Countywide across Census Tracts' ,
                 'E': 'Countywide across Census Block Groups',
                 'F': 'Census Tractwide across Census Block Groups' }
        print 'At what geographic level to you want to focus your testing?'
        print 'A:', allowable_selection['A']
        print 'B:', allowable_selection['B']
        print 'C:', allowable_selection['C']
        print 'D:', allowable_selection['D']
        print 'E:', allowable_selection['E']
        print 'F:', allowable_selection['F']
        print ''
        for i in range(3):
            self.geo_level = raw_input('Your selection: ')
            self.geo_level = self.geo_level.upper()
            if self.geo_level in allowable_selection:
                geo_level_ok = True
                break
            print 'SelectionError: not a valid input'
            geo_level_ok = False
        if geo_level_ok == False:
            sys.exit('Too many failed attempts. Goodbye!')

    def principal_component(self):
        """
        generates a single ranking of regions in the dataset
        uses the first principal component

        takes a dataframe

        adds a new column of the principal component
        """
        self.x = self.df_tmp[self.explanatory_vars]
        self.x = pd.DataFrame(self.x.sum())
        self.x.dropna(axis=0, how='any', inplace=True)
        pca = PCA(n_components=5, whiten=True)
        pca.fit(self.x.T)
        self.explained_var = pca.explained_variance_ratio_
        self.first_pc = pca.components_[0].T
        print 'The ranking variable explains'
        print '%f percent of the data' % self.explained_var[0]
        self.x['first_pca'] = self.first_pc
        self.x.sort(columns='first_pca', ascending=False, inplace=True)
        print self.x.head()

    def group_data(self):
        """
        groups the data into required groups
        """
        if self.geo_level == 'A':
            self.key = ['state']
            self.df_tmp = self.df[self.explanatory_vars + self.key]
        elif self.geo_level == 'B':
            self.key = ['state', 'county']
            self.df_tmp = self.df[self.explanatory_vars + self.key]
        elif self.geo_level == 'C':
            self.state_key = raw_input('Which State (two letter code):').upper()
            self.state_fip = int(self.state_dict[self.state_key])
            self.key = ['county']
            print self.state_fip
            print df.state.head()
            self.df_tmp = df[df['state'] == self.state_fip]
        elif self.geo_level == 'D':
            self.state_key = raw_input('Which State (two letter code):').upper()
            self.county_fip = raw_input('What is the County FIP code:')
            self.state_fip = int(self.state_dict[self.state_key])
            self.df_tmp = df[(df['state'] == self.state_fip) & \
                            (df['county']==self.county_fip)][\
                            self.explanatory_vars + self.key]
            self.key = ['tract']
        elif self.geo_level == 'E':
            self.state_key = raw_input('Which State (two letter code):').upper()
            self.county_fip = raw_input('What is the County FIP code:')
            self.state_fip = int(self.state_dict[self.state_key])
            self.df_tmp = df[(df['state'] == self.state_key) & \
                            (df['county']==self.county_key)][\
                            self.explanatory_vars + self.key]
            self.key = 'blocks'
        elif self.geo_level == 'F':
            self.state_key = raw_input('Which State (two letter code):').upper()
            self.county_fip = raw_input('What is the County FIP code:')
            self.tract_fip = raw_input('What is the Tract FIP code:')
            self.state_fip = int(self.state_dict[self.state_key])
            self.df_tmp = df[(df['state'] == self.state_fip) & \
                            (df['county']==self.county_fip) & \
                            (df['tract']==self.tract_fip)][\
                            self.explanatory_vars + self.key]
            self.key = 'blocks'
        if self.key != 'blocks':
            self.df_tmp = self.df_tmp.groupby(self.key)
        else:
            self.df_tmp.set_index(key=['state', 'county', 'tract', 'block'])

df = pd.read_csv('lead_ranking_data.csv')
a = reduceTheLead(df)
a.group_data()
a.principal_component()
savefile = raw_input('Do you want to save the file (Y/N):').upper()
if savefile == 'Y':
    filename = raw_input('Name the file:')
    self.x.to_csv(filename + '.csv', 'wb')
    print 'File saved as ' + filename+'.csv'


