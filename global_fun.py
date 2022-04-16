from datetime import datetime, timedelta
from matplotlib.pyplot import broken_barh
import numpy as np
from global_var import *

def get_dt(dataset, idx1, idx2, t1stamp='End Date', t2stamp='Start Date'):
    """
    get_dt(dataset, idx1, idx2)
    Get the difference in time between the end time ('End Date') of `idx1` and
    start time ('Start Date') of `idx2` in a Dataframe `dataset`
    Return is a floating number in seconds
    """
    if idx2 <= idx1:
        raise ValueError('First argument must be strictly smaller than the second one')
    t1, t2 = dataset.loc[idx1, t1stamp], dataset.loc[idx2, t2stamp]
    dt = (datetime.fromisoformat(t2)-datetime.fromisoformat(t1)).total_seconds()
    return dt

def calc_break_effect(compressed, curr_idx, is_AFK=False):
    # calculate the score potential of this break
    # cut off an activity if it starts before the scoring ends but stops after
    # what if nothing is recorded after the break?
    # set to afk_score?
    score_span = {}
    if not is_AFK:
        assess_end_dt = datetime.fromisoformat(compressed.loc[curr_idx, 'End Date']) + \
                        timedelta(seconds = prod_assess_span)
    else:
        assess_end_dt = datetime.fromisoformat(compressed.loc[curr_idx, 'Start Date']) + \
                        timedelta(seconds = prod_assess_span)

    act_idx = curr_idx + 1

    while act_idx < len(compressed) and \
          datetime.fromisoformat(compressed.loc[act_idx, 'Start Date']) <= assess_end_dt:
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
    # fill default value
    if not score_span or sum(score_span.values())==0: score_span = {afk_score: 1}
    break_effect = np.average(list(score_span.keys()),
                     weights=list(score_span.values()))
    return break_effect

# %%
def get_mean_std(x_scatter, y_scatter, interval, x_min=np.nan, x_max=np.nan):
    if np.isnan(x_min): x_min = min(x_scatter)
    if np.isnan(x_max): x_max = max(x_scatter)
    # + interval to include x_max
    if not isinstance(x_scatter[0], datetime):
        x_edges = np.arange(x_min, x_max + interval, interval) 
        x_mean = np.arange(x_min + interval/2., x_max - interval/2., interval) 
    else:
        # since np.arange does not preserve timezone offset ...
        nelem = int(np.ceil((x_scatter[-1] - x_scatter[0]) / interval)) + 1
        x_edges = np.zeros(nelem).astype(datetime)
        x_mean = np.zeros(nelem - 1).astype(datetime)
        for i in range(nelem):
            x_edges[i] = x_scatter[0] + interval * i
            if i == nelem - 1: break
            x_mean[i] = x_scatter[0] + interval * (i + 0.5)

    y_mean, y_std = np.zeros(len(x_mean)), np.zeros(len(x_mean))
    for idx in range(len(x_mean)):
        if not isinstance(x_scatter[0], datetime):
            vidx = np.argwhere(np.logical_and(x_scatter >= x_edges[idx],
                            x_scatter < x_edges[idx+1]))
            vidx = vidx[:,0]
        else:
            idx_s = np.searchsorted(x_scatter, x_edges[idx])
            idx_e = np.searchsorted(x_scatter, x_edges[idx + 1])
            vidx = np.arange(idx_s, idx_e)

        if vidx.size == 0:
            y_mean[idx] = np.nan
        else:
            y_mean[idx] = np.mean(y_scatter[vidx])
            y_std[idx] = np.std(y_scatter[vidx])
    return x_mean, y_mean, y_std

# %%
