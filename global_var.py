import numpy as np

proj_prod = {'Media': 0.25,
             'piano': 0.5,
             'Misc': 0.5,
             'Finance': 0.75,
             'Gaming': 0.,
             'Communication': 0.75,
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

delta_t_threshold = 300 # seconds
