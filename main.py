import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import global_var
import global_fun
# easier to reload ...
import importlib
importlib.reload(global_var)
importlib.reload(global_fun)
from global_var import *
from global_fun import *

# %%
fullds = pd.read_csv('All Activities by project.csv')
fullds = fullds.sort_values(by=['Start Date'])

fullds['Score'] = [proj_prod[x] for x in fullds['Project'].to_numpy()]
fullds.fillna('', inplace=True)

fullds = fullds[fullds['Project']!='(No Project)']

fullds = fullds.reset_index()
fullds_mod = fullds.copy().drop(['index'],axis=1)

# combine the same project as long as they are at most dt_connect apart
# ignore the difference in title at the moment
idx_drop = []
startIdx = 0
for idx, row in fullds.iterrows():
    if idx == 0:
        continue

    dt = get_dt(fullds, idx-1, idx)
    l_same_proj = fullds.loc[idx-1,'Project']==fullds.loc[idx,'Project']

    if not l_same_proj or dt >= dt_connect:
        startIdx = idx

    if dt < dt_connect and dt >= 0 and l_same_proj:
        idx_drop.append(idx)
        fullds_mod.loc[startIdx,'End Date'] = fullds_mod.loc[idx,'End Date']
        fullds_mod.loc[startIdx,'Duration'] += fullds_mod.loc[idx,'Duration']
        if fullds_mod.loc[startIdx,'Title'] != fullds_mod.loc[idx,'Title']:
            if fullds_mod.loc[idx,'Title'] not in fullds_mod.loc[startIdx,'Title']:
                fullds_mod.loc[startIdx,'Title'] += '. ' + fullds_mod.loc[idx,'Title']

compres_ds = fullds_mod.drop(idx_drop).reset_index()
compres_ds

# find the indices of "breaks"
# only a break if a "work session" already started in dt_workbreak_interval
compres_ds['isBreak'] = False
workIdx = np.nan
for idx, row in compres_ds.iterrows():
    if idx == 0: continue
    if compres_ds.loc[idx, 'Score'] > 0.5:
        workIdx = idx
        continue
    if np.isnan(workIdx):
        compres_ds.loc[idx, 'isBreak'] = True
        continue

    dt = get_dt(compres_ds, workIdx, idx, t2stamp='End Date')
    if dt > dt_workbreak_interval:
        continue
    else:
        if compres_ds.loc[idx, 'Score'] <= 0.5:
            compres_ds.loc[idx, 'isBreak'] = True

compres_ds[-25:]
