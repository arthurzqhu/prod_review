import numpy as np

proj_prod = {'Media': 0.25,
             'piano': 0.25,
             'Misc': 0.25,
             'Finance': 0.5,
             'Gaming': 0.,
             'Communication': 0.5,
             'News & Procrastination': 0.,
             'Studying': 1.,
             'Work': 1.,
             'Development': 1.,
             'Office & Business': 1.,
             'Reading & Writing': 1.,
             'File Management': 0.5,
             'Graphics': 0.75,
             'Web Browsing': 0.5,
             'Web Browsing ▸ Social Media': 0.,
             'Web Browsing ▸ Shopping & Travel': 0.,
             '(No Project)': np.nan
            }

dt_connect = 300 # seconds. connect the two projects if they're less than 300 s apart
dt_workbreak_interval = 1800 # seconds. used to find the breaks in between work sessions
dt_afk = 300 # minimum dt between work session that'll be considered AFK, in which case afk_score
             # is used
prod_assess_span = 3600 # seconds. time span over which average score is calculated
afk_score = 0.5
