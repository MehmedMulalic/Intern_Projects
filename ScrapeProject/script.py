from hashlib import new
from os import dup
from difflib import get_close_matches
import pandas as pd
import jellyfish

# DATA processing
all_df = pd.read_csv("fudo_mehmed_data - edited.csv", low_memory=False)
df = pd.read_csv("fudo_mehmed_data - edited.csv", low_memory=False)

nanbg = all_df[all_df['block_group_2020_fips'].isna()]
nansm = all_df[all_df['sub_market'].isna()]
# nanbg.to_csv("NaN_BG.csv") ###CSV###
# nansm.to_csv("NaN_SM.csv") ###CSV###
nanbg = nanbg[['block_group_2020_fips', 'sub_market', 'market']]
nansm = nansm[['block_group_2020_fips', 'sub_market', 'market']]
all_df.dropna(subset=['block_group_2020_fips', 'sub_market'], inplace=True)

df.fillna(value={"zcta5_fips": 0, "block_group_2020_fips": 0}, inplace=True)
df.fillna("???", inplace=True)
df.sort_values(by=['block_group_2020_fips'], inplace=True)

# SUBMARKET MAPPING
filtered = df.value_counts(subset=['sub_market', 'block_group_2020_fips'], dropna=False).sort_index(level=1)
mapping = pd.DataFrame()
red1 = pd.DataFrame()
red2 = pd.DataFrame()
duplicateBG = []

for i in range(filtered.count()):
    a1 = pd.Series(filtered.index[i][1])
    a2 = pd.Series(filtered.index[i][0])
    red1 = pd.concat([red1, a1.to_frame().T], ignore_index=True)
    red2 = pd.concat([red2, a2.to_frame().T], ignore_index=True)

mapping = pd.concat([mapping, red1, red2], ignore_index=True, axis=1)
mapping.columns = ['block_group_2020_fips', 'sub_market']

# with open("Submarket_mapping.csv", 'w') as outputf:               ###CSV###
#     mapping.to_csv(outputf, index=False, line_terminator='\n')    ###CSV###

# check for incorrect sub_market to market mapping
kopije = all_df.value_counts(subset=['sub_market', 'market']).sort_index(level=0)
vriM = pd.Series(kopije.index.droplevel()) #samo markets
vriSM = pd.Series(kopije.index.droplevel(1)) #samo submarkets
vriSMIndex = vriSM[vriSM.duplicated(keep=False) == True] #samo duplicate submarkets
vriMIndex = vriM.loc[vriM.index.isin(vriSMIndex.index)] #markets with matching submarket ids
multipleSMs = pd.DataFrame()
multipleSMs = pd.concat([multipleSMs, vriSMIndex, vriMIndex], axis=1) #submarkets which have multiple markets; debug_csv
ovo = pd.merge(all_df, multipleSMs, on=['market', 'sub_market'], how='inner')
# ovo.drop_duplicates(subset=['market', 'sub_market']).to_csv("Submarket-market_mapping.csv")    ###CSV###

# indexing duplicates
duplicates = mapping['block_group_2020_fips'].duplicated()
for d in range(duplicates.shape[0]):
    if duplicates[d] == True:
        duplicateBG.append(mapping.iloc[d][0])
all_df.index += 2 #zbog index 0 i headera

# duplicates ids needed
duplicate_final = pd.DataFrame( all_df.loc[ all_df['block_group_2020_fips'].isin(duplicateBG) ].sort_values(by=['block_group_2020_fips', 'sub_market']) )
# duplicate_final.to_csv("Duplicates.csv") ###CSV###

# Fuadov kod u 3 linije umjesto ovog
valsCheck = all_df[['sub_market', 'block_group_2020_fips']].value_counts().sort_index(level=1) #vrijednosti
bgSeries = pd.Series(valsCheck.index.droplevel()) #samo fips
dupChecked = bgSeries.duplicated(keep=False) #ako ima duplicate fips
finalChecked = pd.Series(dupChecked[dupChecked == True].index) #get ids ako jesu duplicate
rez = bgSeries[bgSeries.index.isin(finalChecked)] #fips sa istim ids kao gore
uniqueRez = pd.Series(rez.unique()) #samo uniques

# bad values
final = pd.DataFrame(all_df.loc[all_df['block_group_2020_fips'].isin(uniqueRez)].sort_values(by=['block_group_2020_fips', 'sub_market']))
trebazakraj = final.copy()
trebazakraj = trebazakraj[['block_group_2020_fips', 'sub_market', 'market']]
trebazakraj.drop_duplicates(inplace=True)
# final.to_csv("Final_bad.csv") ###CSV###
final.drop_duplicates(subset=['sub_market', 'block_group_2020_fips'], inplace=True)
# final.to_csv("Final_bad_nodp.csv") ###CSV###

# vrijednosti preko 2 u svoj file (znaci samo da su parovi)
finalBGvc = final['block_group_2020_fips'].value_counts()
# finalBGvc.to_csv("valc check over two.csv")   ###CSV###
customfips = finalBGvc[finalBGvc.values != 2].index
# final[final['block_group_2020_fips'].isin(customfips)].to_csv("Check manually.csv")   ###CSV###
final2 = final[~final['block_group_2020_fips'].isin(customfips)]

tmp = final2['sub_market']
autocheck = pd.DataFrame()
proba1 = pd.Series((tmp.iloc[::2]).values) #svaki drugi row
proba2 = pd.Series((tmp.iloc[1::2]).values) #svaki drugi row pocevsi od prvog
autocheck = pd.concat([autocheck, proba1, proba2], axis=1)
autocheck.columns = ['first_SM', 'second_SM']
# autocheck.to_csv("Check automatically.csv")   ###CSV###

# levenshtein distance
lista = []
for i in range(autocheck.shape[0]):
    lista.append( jellyfish.damerau_levenshtein_distance(autocheck.iloc[i,0], autocheck.iloc[i, 1]) )
autocheck = pd.concat([autocheck, pd.Series(lista)], axis=1)
# autocheck.to_csv("Similarity.csv")    ###CSV###

# good values
all_df = all_df.loc[~all_df['block_group_2020_fips'].isin(uniqueRez)].sort_values(by=['block_group_2020_fips'])
# all_df.to_csv("Final_good.csv")   ###CSV###
all_df = all_df[['block_group_2020_fips', 'sub_market', 'market']]
all_df.drop_duplicates(inplace=True)

# sve u jedan file
all = pd.DataFrame()
all = pd.concat([all, all_df, nanbg, nansm, trebazakraj])
all.to_csv("Gotovo.csv", index=False)  ###CSV### zadnji