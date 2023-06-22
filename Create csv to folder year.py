#!/usr/bin/env python
# coding: utf-8

# In[126]:


import pandas as pd
import numpy as np
import re
from pathlib import Path
pd.options.mode.chained_assignment = None
df = pd.read_csv("HPI_AT_metro.csv", header=None)
unique_years = df[df.columns[2]].unique()


# In[27]:


# Create folders
results_path = Path.cwd() / 'results'
results_path.mkdir(exist_ok=True)
for year in unique_years:
    (results_path / str(year)).mkdir(exist_ok=True)


# In[3]:


posebni_sumlev = df.loc[df[0].str.contains('MSAD') == True][1].unique()
print(posebni_sumlev)


# In[28]:


for year in unique_years:
    hpi1 = df.loc[( (df[df.columns[3]] == 1) & (df[df.columns[2]] == year) )][4].reset_index(drop=True).replace('-', np.NaN)
    hpi2 = df.loc[( (df[df.columns[3]] == 2) & (df[df.columns[2]] == year) )][4].reset_index(drop=True).replace('-', np.NaN)
    hpi3 = df.loc[( (df[df.columns[3]] == 3) & (df[df.columns[2]] == year) )][4].reset_index(drop=True).replace('-', np.NaN)
    hpi4 = df.loc[( (df[df.columns[3]] == 4) & (df[df.columns[2]] == year) )][4].reset_index(drop=True).replace('-', np.NaN)
    hpi1, hpi2, hpi3, hpi4 = hpi1.astype(float), hpi2.astype(float), hpi3.astype(float), hpi4.astype(float)
    
    output_df = pd.DataFrame()
    output_df = pd.concat([pd.Series(df[1].unique()), hpi1, hpi2, hpi3, hpi4, \
                     pd.Series(index=range(hpi1.shape[0]), data='SL310'), \
                     pd.Series(dtype='float64'), pd.Series(dtype='float64'), pd.Series(dtype='float64')], axis=1, \
                    keys=['GeoID', 'HPI1', 'HPI2', 'HPI3', 'HPI4', 'SUMLEV', 'HPI_min', 'HPI_max', 'HPI_avg'])
    output_df['HPI_min'] = output_df[['HPI1', 'HPI2', 'HPI3', 'HPI4']].min(axis=1, numeric_only=True)
    output_df['HPI_max'] = output_df[['HPI1', 'HPI2', 'HPI3', 'HPI4']].max(axis=1, numeric_only=True)
    output_df['HPI_avg'] = output_df[['HPI1', 'HPI2', 'HPI3', 'HPI4']].mean(axis=1, numeric_only=True)
    
    for key, value in output_df['GeoID'].iteritems():
        if value in posebni_sumlev:
            output_df['SUMLEV'][key] = 'SL314'
    
    output_df.to_csv(results_path / str(year) / ('HPI_' + str(year) + '.csv'), index=False)


# In[155]:


for year in unique_years:
    st1 = df.loc[( (df[df.columns[3]] == 1) & (df[df.columns[2]] == year) )][5].reset_index(drop=True)
    st2 = df.loc[( (df[df.columns[3]] == 2) & (df[df.columns[2]] == year) )][5].reset_index(drop=True)
    st3 = df.loc[( (df[df.columns[3]] == 3) & (df[df.columns[2]] == year) )][5].reset_index(drop=True)
    st4 = df.loc[( (df[df.columns[3]] == 4) & (df[df.columns[2]] == year) )][5].reset_index(drop=True)
    st1 = '-' + st1.apply(lambda x: re.sub(r'[^0-9.]', '', x)).replace('', np.NaN)
    st2 = '-' + st2.apply(lambda x: re.sub(r'[^0-9.]', '', x)).replace('', np.NaN)
    st3 = '-' + st3.apply(lambda x: re.sub(r'[^0-9.]', '', x)).replace('', np.NaN)
    st4 = '-' + st4.apply(lambda x: re.sub(r'[^0-9.]', '', x)).replace('', np.NaN)
    st1, st2, st3, st4 = st1.astype(float), st2.astype(float), st3.astype(float), st4.astype(float)
    
    output_error_df = pd.DataFrame()
    output_error_df = pd.concat([pd.Series(df[1].unique()), st1, st2, st3, st4, \
                     pd.Series(index=range(hpi1.shape[0]), data='SL310')], \
                     keys=['GeoID', 'St_Error1', 'St_Error2', 'St_Error3', 'St_Error4', 'SUMLEV'], axis=1)
    
    for key, value in output_error_df['GeoID'].iteritems():
        if value in posebni_sumlev:
            output_error_df['SUMLEV'][key] = 'SL314'
    
    output_error_df.to_csv(results_path / str(year) / ('HPI_St_Error_' + str(year) + '.csv'), index=False)

