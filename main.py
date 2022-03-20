import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import global_var
import global_fun
import global_class
# easier to reload ...
import importlib
importlib.reload(global_var)
importlib.reload(global_fun)
importlib.reload(global_class)
from global_var import *
from global_fun import *
from global_class import *

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
    l_same_proj = fullds.loc[idx-1,'Project']==row['Project']

    if not l_same_proj or dt >= dt_connect:
        startIdx = idx

    if dt < dt_connect and l_same_proj:
        idx_drop.append(idx)
        fullds_mod.loc[startIdx,'End Date'] = row['End Date']
        fullds_mod.loc[startIdx,'Duration'] += fullds_mod.loc[idx,'Duration']
        if fullds_mod.loc[startIdx,'Title'] != fullds_mod.loc[idx,'Title']:
            if fullds_mod.loc[idx,'Title'] not in fullds_mod.loc[startIdx,'Title']:
                fullds_mod.loc[startIdx,'Title'] += '. ' + fullds_mod.loc[idx,'Title']

# %%
# think about how to identify and deal with parallel activities ...
fullds_mod[130250:130260]


compres_ds = fullds_mod.drop(idx_drop).reset_index()
compres_ds = compres_ds.drop(['index'],axis=1)

# find the indices of "breaks"
# only a break if a "work session" already started in dt_workbreak_interval
break_list = []
compres_ds['isBreak'] = False
workIdx = np.nan
for idx, row in compres_ds.iterrows():
    if idx == 0: continue
    if row['Score'] > 0.5:
        workIdx = idx
        continue
    if np.isnan(workIdx):
        continue

    dt = get_dt(compres_ds, workIdx, idx, t2stamp='End Date')
    if dt > dt_workbreak_interval:
        continue
    else:
        if row['Score'] <= 0.5:
            compres_ds.loc[idx, 'isBreak'] = True

            # create a new break obj if the previous activity is not a break
            if compres_ds.loc[idx-1, 'isBreak'] == False:
                brk = Break()

            if compres_ds.loc[idx-1, 'Project'] == row['Project']:
                brk.extendBreak(row['Duration'], row['End Date'])
            else:
                brk.addBreak(row['Project'], row['Duration'],
                             row['Application'], row['Score'], row['End Date'])

            if compres_ds.loc[idx+1, 'isBreak'] == False:
                # calculate the score potential of this break and append to the list
                # cut off an activity if it starts before the scoring ends but stops after
                # what if nothing is recorded after the break?
                # set to default_phone_scrolling_score?
                score_span = {}
                assess_end_dt = datetime.fromisoformat(row['End Date']) + \
                             timedelta(seconds = prod_assess_span)
                act_idx = idx + 1

                while datetime.fromisoformat(compres_ds.loc[act_idx, 'Start Date']) <= assess_end_dt:
                    curr_score = compres_ds.loc[act_idx, 'Score']

                    # cut off the process if it lasts after the end of assessment time
                    if datetime.fromisoformat(compres_ds.loc[act_idx, 'End Date']) <= assess_end_dt:
                        curr_dur = compres_ds.loc[act_idx, 'Duration']
                    else:
                        curr_dur = (assess_end_dt - datetime.fromisoformat(compres_ds.loc[act_idx, 'Start Date'])).total_seconds()

                    if curr_score not in score_span:
                        score_span[curr_score] = curr_dur
                    else:
                        score_span[curr_score] += curr_dur

                    act_idx += 1
                    if act_idx == len(compres_ds):
                        break
                # fill default value
                if not score_span or sum(score_span.values())==0: score_span = {no_record_score: 1}
                brk.prod_score = np.average(list(score_span.keys()), weights=list(score_span.values()))
                break_list.append(brk)

# %% plot
%matplotlib inline
brk_dur = [sum(x.proj_dur) for x in break_list]
brk_scr = [x.prod_score for x in break_list]
plt.scatter(brk_dur, brk_scr, alpha=0.05)
_, brk_dur_binedges = np.histogram(brk_dur)
_, brk_scr_binedges = np.histogram(brk_scr)
plt.hist(brk_dur, brk_dur_binedges)
plt.hist(brk_scr, brk_scr_binedges)

brk_dur_list = np.arange(0,dt_workbreak_interval+1,10)
brk_dur_list_mid = (brk_dur_list[:-1] + brk_dur_list[1:])/2
mean_score = np.zeros(len(brk_dur_list_mid))
mean_std = np.zeros(len(brk_dur_list_mid))
for idx, val in enumerate(brk_dur):
    vidx = np.argwhere(np.logical_and(np.array(brk_dur) > brk_dur_list[idx], np.array(brk_dur) <= brk_dur_list[idx+1]))
    if vidx.size == 0:
        mean_score[idx] = np.nan
    else:
        mean_score[idx] = np.mean(np.array(brk_scr)[vidx[:,0]])
        mean_std[idx] = np.std(np.array(brk_scr)[vidx[:,0]])
    if idx == len(brk_dur_list_mid)-1:
        break
# %% plot
plt.figure(figsize=(5,4), dpi=144)
plt.plot(brk_dur_list_mid, mean_score)
plt.fill_between(brk_dur_list_mid, mean_score-mean_std, mean_score+mean_std, alpha=.2)
plt.xlabel('break length [s]')
plt.ylabel('productivity score')
