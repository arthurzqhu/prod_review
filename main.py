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

# %% functions
def preproc(filedir):
    fullds = pd.read_csv(filedir)
    fullds = fullds.sort_values(by=['Start Date'])
    fullds['Score'] = [proj_prod[x] for x in fullds['Project'].to_numpy()]
    fullds.fillna('', inplace=True)

    fullds = fullds[fullds['Project']!='(No Project)']

    fullds = fullds.reset_index()
    fullds = fullds.drop(['index'],axis=1)
    return fullds

# combine the same project as long as they are at most dt_connect apart
# ignore the difference in title at the moment
def combine_proj(df_in):
    idx_drop = []
    startIdx = 0
    df_out = df_in.copy()
    for idx, row in df_in.iterrows():
        if idx == 0:
            continue

        dt = get_dt(df_in, idx-1, idx)
        l_same_proj = df_in.loc[idx-1,'Project']==row['Project']
        if not l_same_proj or dt >= dt_connect:
            startIdx = idx

        if dt < dt_connect and l_same_proj:
            idx_drop.append(idx)
            df_out.loc[startIdx,'End Date'] = row['End Date']
            df_out.loc[startIdx,'Duration'] += df_out.loc[idx,'Duration']
            if df_out.loc[startIdx,'Title'] != df_out.loc[idx,'Title']:
                if df_out.loc[idx,'Title'] not in df_out.loc[startIdx,'Title']:
                    df_out.loc[startIdx,'Title'] += '. ' + df_out.loc[idx,'Title']
    return idx_drop, df_out


#
def drop_df_idx(df, idx):
    compressed = df.drop(idx).reset_index()
    compressed = compressed.drop(['index'],axis=1)
    return compressed

# find the indices of "breaks"
# only a break if a "work session" already started in dt_workbreak_interval
def break_analysis(compressed):
    break_list = []
    compres_ds['isBreak'] = False
    workIdx = np.nan
    for idx, row in compressed.iterrows():
        if idx == 0: continue

        # start remembering idx when it's "productive"
        if row['Score'] > 0.5:
            workIdx = idx
            continue

        if np.isnan(workIdx):
            continue

        dt = get_dt(compressed, workIdx, idx, t2stamp='End Date')

        if dt > dt_workbreak_interval:
            continue
        else:
            if row['Score'] <= 0.5:
                compressed.loc[idx, 'isBreak'] = True

                # create a new break obj if the previous activity is not a break
                if not compressed.loc[idx-1, 'isBreak']:
                    brk = Break()

                if compressed.loc[idx-1, 'Project'] == row['Project']:
                    brk.extendBreak(row['Duration'], row['End Date'])
                else:
                    brk.addBreak(row['Project'], row['Duration'],
                                 row['Application'], row['Score'], row['End Date'])

                # if the next item is not break:
                # but had to do this since the whether or not the next one is
                # break is not known yet
                dt_next = get_dt(compressed, idx, idx+1, t2stamp='Start Date')
                if dt_next > dt_workbreak_interval or compressed.loc[idx+1,'Score'] > 0.5:
                    # calculate the score potential of this break and append to the list
                    # cut off an activity if it starts before the scoring ends but stops after
                    # what if nothing is recorded after the break?
                    # set to default_phone_scrolling_score?
                    score_span = {}
                    assess_end_dt = datetime.fromisoformat(row['End Date']) + \
                                 timedelta(seconds = prod_assess_span)
                    act_idx = idx + 1

                    while datetime.fromisoformat(compressed.loc[act_idx, 'Start Date']) <= assess_end_dt:
                        curr_score = compressed.loc[act_idx, 'Score']

                        # cut off the process if it lasts after the end of assessment time
                        if datetime.fromisoformat(compressed.loc[act_idx, 'End Date']) <= assess_end_dt:
                            curr_dur = compressed.loc[act_idx, 'Duration']
                        else:
                            curr_dur = (assess_end_dt - datetime.fromisoformat(compressed.loc[act_idx, 'Start Date'])).total_seconds()

                        if curr_score not in score_span:
                            score_span[curr_score] = curr_dur
                        else:
                            score_span[curr_score] += curr_dur

                        act_idx += 1
                        if act_idx == len(compressed):
                            break
                    # fill default value
                    if not score_span or sum(score_span.values())==0: score_span = {no_record_score: 1}
                    brk.prod_score = np.average(list(score_span.keys()),
                                     weights=list(score_span.values()))
                    break_list.append(brk)
    return break_list


# %% bare with me not putting this into a main function atm
fullds = preproc('All Activities by project.csv')
idx_drop, fullds_mod = combine_proj(fullds)
compres_ds = drop_df_idx(fullds_mod, idx_drop)
break_list = break_analysis(compres_ds)

# %% plot
%matplotlib inline
brk_dur = [sum(x.proj_dur) for x in break_list]
brk_scr = [x.prod_score for x in break_list]
# plt.scatter(brk_dur, brk_scr, alpha=0.05)
# _, brk_dur_binedges = np.histogram(brk_dur)
# _, brk_scr_binedges = np.histogram(brk_scr)
# plt.hist(brk_dur, brk_dur_binedges)
# plt.hist(brk_scr, brk_scr_binedges)

brk_dur_list = np.arange(0,dt_workbreak_interval+1,10)
brk_dur_list_mid = (brk_dur_list[:-1] + brk_dur_list[1:])/2
mean_score = np.zeros(len(brk_dur_list_mid))
mean_std = np.zeros(len(brk_dur_list_mid))
for idx, val in enumerate(brk_dur):
    vidx = np.argwhere(np.logical_and(np.array(brk_dur) > brk_dur_list[idx],
                       np.array(brk_dur) <= brk_dur_list[idx+1]))
    if vidx.size == 0:
        mean_score[idx] = np.nan
    else:
        mean_score[idx] = np.mean(np.array(brk_scr)[vidx[:,0]])
        mean_std[idx] = np.std(np.array(brk_scr)[vidx[:,0]])
    if idx == len(brk_dur_list_mid)-1:
        break
# %% plot
plt.figure(figsize=(5,4), dpi=144)
plt.plot(brk_dur_list_mid, mean_score, linewidth=1)
plt.fill_between(brk_dur_list_mid, mean_score-mean_std, mean_score+mean_std, alpha=.3)
plt.xlabel('break length [s]')
plt.ylabel('productivity score')
