import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

# easier to reload ...
import importlib
import global_var
importlib.reload(global_var)
from global_var import *

# %%
fullds = pd.read_csv('All Activities by project.csv')
fullds = fullds.sort_values(by=['Start Date'])

fullds['Score'] = [proj_prod[x] for x in fullds['Project'].to_numpy()]
fullds.fillna('', inplace=True)

fullds = fullds[fullds['Project']!='(No Project)']

fullds = fullds.reset_index()
fullds_mod = fullds.copy().drop(['index'],axis=1)

# combine the same project as long as they are at most delta_t_threshold apart
# ignore the difference in title at the moment
idx_drop = []
startIdx = 0
for idx, row in fullds.iterrows():
    if idx == 0:
        continue

    t1, t2 = fullds.iloc[idx-1]['End Date'], fullds.iloc[idx]['Start Date']
    dt = (datetime.fromisoformat(t2)-datetime.fromisoformat(t1)).total_seconds()
    l_same_proj = fullds.iloc[idx-1]['Project']==fullds.iloc[idx]['Project']

    if not l_same_proj or dt >= delta_t_threshold:
        startIdx = idx

    if dt < delta_t_threshold and dt >= 0 and l_same_proj:
        idx_drop.append(idx)
        fullds_mod.loc[startIdx,'End Date'] = fullds_mod.loc[idx,'End Date']
        fullds_mod.loc[startIdx,'Duration'] += fullds_mod.loc[idx,'Duration']
        if fullds_mod.loc[startIdx,'Title'] != fullds_mod.loc[idx,'Title']:
            if fullds_mod.loc[idx,'Title'] not in fullds_mod.loc[startIdx,'Title']:
                fullds_mod.loc[startIdx,'Title'] += '. ' + fullds_mod.loc[idx,'Title']
