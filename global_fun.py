from datetime import datetime

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
