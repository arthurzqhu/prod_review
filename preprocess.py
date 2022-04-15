# %%

import pandas as pd
from global_var import *
from global_fun import *
from global_class import *


# %% functions
def preproc(fileloc):
    '''
    pre-preprocess input activity file
    '''
    fullds = pd.read_csv(fileloc)
    fullds = fullds.sort_values(by=['Start Date'])
    fullds['Score'] = [proj_prod[x] for x in fullds['Project'].to_numpy()]
    fullds.fillna('', inplace=True)
    fullds = fullds[fullds['Project'] != '(No Project)']
    return fullds


def combine_proj(df_in):
    '''
    combine the same project as long as they are at most dt_connect apart.
    ignore the difference in title at the moment 
    '''
    df_in = df_in.reset_index().drop(['index'], axis=1)
    idx_drop = []
    startIdx = 0
    df_out = df_in.copy()
    for idx, row in df_in.iterrows():
        if idx == 0:
            continue
        dt = get_dt(df_in, idx - 1, idx)
        l_same_proj = df_in.loc[idx - 1, 'Project'] == row['Project']
        if not l_same_proj or dt >= dt_connect:
            startIdx = idx
        if dt < dt_connect and l_same_proj:
            idx_drop.append(idx)
            df_out.loc[startIdx, 'End Date'] = row['End Date']
            df_out.loc[startIdx, 'Duration'] += df_out.loc[idx, 'Duration']
            if df_out.loc[startIdx, 'Title'] != df_out.loc[idx, 'Title']:
                if df_out.loc[idx, 'Title'] not in df_out.loc[startIdx, 'Title']:
                    df_out.loc[startIdx, 'Title'] += '. ' + df_out.loc[idx, 'Title']
    compressed = df_out.drop(idx_drop)
    return compressed


def break_analysis(compressed):
    '''
    find the indices of "breaks"
    only a break if a "work session" already started in dt_workbreak_interval
    '''
    compressed = compressed.reset_index().drop(['index'], axis=1)
    break_list = []
    compressed['isBreak'] = False
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
            is_consecutive_work_session = \
                compressed.loc[idx - 1, 'Score'] > 0.5 and row['Score'] > 0.5
            if is_consecutive_work_session and dt >= dt_afk_min:
                brk = Break()
                brk.addBreak('AFK', dt, 'AFK', afk_score, row['Start Date'])
                brk.break_eff = calc_break_effect(compressed, idx, is_AFK=True)
                break_list.append(brk)
            if row['Score'] <= 0.5:
                compressed.loc[idx, 'isBreak'] = True
                # create a new break obj if the previous activity has score > 0.5
                if compressed.loc[idx - 1, 'Score'] > 0.5:
                    brk = Break()
                if compressed.loc[idx - 1, 'Project'] == row['Project']:
                    brk.extendBreak(row['Duration'], row['End Date'])
                else:
                    brk.addBreak(row['Project'], row['Duration'],
                                 row['Application'], row['Score'], row['End Date'])
                # if the next item is not break:
                # had to do this since the whether or not the next one is
                # break is not known yet
                dt_next = get_dt(compressed, idx, idx + 1, t2stamp='Start Date')
                if dt_next > dt_workbreak_interval or compressed.loc[idx + 1, 'Score'] > 0.5:
                    brk.break_eff = calc_break_effect(compressed, idx)
                    break_list.append(brk)
    break_ds = pd.DataFrame([o.__dict__ for o in break_list])
    return break_ds


# %% run
# def preprocess():
fullds = preproc('All Activities by project.csv')
compres_ds = combine_proj(fullds)
break_ds = break_analysis(compres_ds)
compres_ds.to_csv('compressed_activities.csv')
break_ds.to_csv('break_down.csv')
