from datetime import datetime, timedelta
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
