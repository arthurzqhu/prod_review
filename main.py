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
    # fullds = fullds.drop(['index'],axis=1)
    return fullds

# combine the same project as long as they are at most dt_connect apart
# ignore the difference in title at the moment
def combine_proj(df_in):
    df_in = df_in.reset_index().drop(['index'],axis=1)
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


def drop_df_idx(df, idx):
    compressed = df.drop(idx)
    # compressed = compressed.drop(['index'],axis=1)
    return compressed

# find the indices of "breaks"
# only a break if a "work session" already started in dt_workbreak_interval
compres_ds[-15:-3].reset_index().drop(['index'],axis=1)

def break_analysis(compressed):
    compressed = compressed.reset_index().drop(['index'],axis=1)
    break_list = []
    compres_ds['isBreak'] = False
    do_start_count = False
    for idx, row in compressed.iterrows():
        if idx == 0: continue


        if do_start_count: dt = get_dt(compressed, workIdx, idx)

        if row['Score'] > 0.5:
            workIdx = idx
            if not do_start_count:
                do_start_count = True
                continue

        if not do_start_count: continue

        if dt > dt_workbreak_interval:
            continue
        else:
            if idx == len(compressed)-1: break

            is_consecutive_work_session = compressed.loc[idx-1, 'Score'] > 0.5 and row['Score'] > 0.5
            if is_consecutive_work_session and dt >= dt_afk_min:
                brk = Break()

                brk.addBreak('AFK', dt, 'AFK', afk_score, row['Start Date'])
                brk.break_eff = calc_break_effect(compressed, idx, is_AFK=True)
                break_list.append(brk)

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
                # had to do this since the whether or not the next one is
                # break is not known yet
                dt_next = get_dt(compressed, idx, idx+1, t2stamp='Start Date')
                if dt_next > dt_workbreak_interval or compressed.loc[idx+1,'Score'] > 0.5:
                    brk.break_eff = calc_break_effect(compressed, idx)
                    break_list.append(brk)
    return break_list

# %% bare with me not putting this into a main function atm
fullds = preproc('All Activities by project.csv')
idx_drop, fullds_mod = combine_proj(fullds)
compres_ds = drop_df_idx(fullds_mod, idx_drop)
break_list = break_analysis(compres_ds)


len(break_list)
len(break_list)

# %% plot
%matplotlib inline
brk_dur = [sum(x.proj_dur) for x in break_list]
brk_scr = [x.break_eff for x in break_list]
# plt.scatter(brk_dur, brk_scr, alpha=0.05)
# _, brk_dur_binedges = np.histogram(brk_dur)
# _, brk_scr_binedges = np.histogram(brk_scr)
# plt.hist(brk_dur, brk_dur_binedges)
# plt.hist(brk_scr, brk_scr_binedges)

brk_dur_list = np.arange(0,dt_workbreak_interval+1,30)
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
plt.ylabel('Break Effectiveness')
