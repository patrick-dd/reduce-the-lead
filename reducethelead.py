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
import readline

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

    def complete(self, text, complete_state):
        """
        tab completion for county names
        """
        for cty in self.counties:
            if cty.startswith(text):
                if not complete_state:
                    return cty
                else:
                    complete_state -= 1

    def complete_tract(self, text, complete_state):
        """
        tab completion for county names
        """
        for tr in self.tracts:
            if tr.startswith(text):
                if not complete_state:
                    return tr
                else:
                    complete_state -= 1


    def county_name_dict(self):
        """
        creates a dictionary of county names to fips
        """
        df_tmp = pd.read_csv('county_fips.txt')
        df_tmp = df_tmp[df_tmp.state_fips==self.state_fip]
        self.county_dict = \
                df_tmp.set_index('county_name')['county_fips'].to_dict()
        self.counties = self.county_dict.keys()
        return 0


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
            self.df_tmp = df[df['state'] == self.state_fip]
        elif self.geo_level == 'D':
            self.state_key = raw_input('Which State (two letter code):').upper()
            self.state_fip = int(self.state_dict[self.state_key])
            self.county_name_dict()
            readline.parse_and_bind("tab: complete")
            readline.set_completer(self.complete)
            self.county_name = raw_input('What is the County name (tab complete):')
            self.county_fip = int(self.county_dict[self.county_name])
            self.key = ['tract']
            self.df_tmp = self.df[(self.df['state'] == self.state_fip) & \
                            (self.df['county']==self.county_fip)][\
                            self.explanatory_vars + self.key]
        elif self.geo_level == 'E':
            self.state_key = raw_input('Which State (two letter code):').upper()
            self.state_fip = int(self.state_dict[self.state_key])
            self.county_name_dict()
            readline.parse_and_bind("tab: complete")
            readline.set_completer(self.complete)
            self.county_name = raw_input('What is the County name (tab complete):')
            self.county_fip = int(self.county_dict[self.county_name])
            self.key = 'blockgroup'
            print self.df.columns.values
            self.df_tmp = self.df[(self.df['state'] == self.state_fip) & \
                            (self.df['county']==self.county_fip)][\
                            self.explanatory_vars + [self.key]\
                            + ['state', 'county', 'tract']]
        elif self.geo_level == 'F':
            self.state_key = raw_input('Which State (two letter code):').upper()
            self.state_fip = int(self.state_dict[self.state_key])
            self.county_name_dict()
            readline.parse_and_bind("tab: complete")
            readline.set_completer(self.complete)
            self.county_name = raw_input('What is the County name (tab complete):')
            self.county_fip = int(self.county_dict[self.county_name])
            self.tracts = self.df[(self.df['state']==self.state_fip) &\
                            (self.df['county']==self.county_fip)][\
                            'tract'].unique()
            print self.tracts
            readline.parse_and_bind("tab: complete")
            readline.set_completer(self.complete_tract)
            self.tract_fip = int(raw_input('What is the Tract FIPS code:'))
            self.key = 'blockgroup'
            print df['tract'].head()
            print self.tract_fip
            self.df_tmp = self.df[(self.df['state'] == self.state_fip) & \
                            (self.df['county']==self.county_fip) & \
                            (self.df['tract']==self.tract_fip)][\
                            self.explanatory_vars + [self.key]\
                            + ['state', 'county', 'tract']]
        if self.key != 'blockgroup':
            self.df_tmp = self.df_tmp.groupby(self.key)
        else:
            self.df_tmp.set_index(['state', 'county', 'tract', 'blockgroup'])


if __name__=="__main__":
    df = pd.read_csv('lead_ranking_data.csv')
    a = reduceTheLead(df)
    a.group_data()
    a.principal_component()
    savefile = raw_input('Do you want to save the file (Y/N):').upper()
    if savefile == 'Y':
        filename = raw_input('Name the file:')
        a.x.to_csv(filename + '.csv')
        print 'File saved as ' + filename+'.csv'


