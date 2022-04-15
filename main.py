# %%
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
from global_var import *
from global_fun import *


# %% read data
activities_dat = pd.read_csv('compressed_activities.csv')
break_dat = pd.read_csv('break_down.csv')

# %% some processing

ndat = len(break_dat)
brk_dur_seperated = [np.fromstring(break_dat['proj_dur'][ievent][1:-1],
                                   dtype=float, sep=',') for ievent in range(ndat)]
brk_dur = [sum(ievent) for ievent in brk_dur_seperated]
brk_cat = [break_dat['proj_name'][ievent][2:-2].split("\', \'") for ievent in range(ndat)]
brk_eff = break_dat['break_eff']
brk_app = [break_dat['proj_app'][ievent][2:-2].split("\', \'") for ievent in range(ndat)]
brk_end = [datetime.fromisoformat(break_dat['end_time'][ievent][2:-2].split("\', \'")[-1])
           for ievent in range(ndat)]


# %%
# %matplotlib inline

brk_dur_mean, score_mean, score_std = \
    get_mean_std(brk_dur, brk_eff, 30, x_min=0, x_max=dt_workbreak_interval)

# %% break effectiveness vs break length
plt.figure(figsize=(5, 4), dpi=144)
plt.plot(brk_dur_mean, score_mean, linewidth=1)
plt.fill_between(brk_dur_mean, score_mean - score_std, score_mean + score_std, alpha=.3)
plt.xlabel('Break length [s]')
plt.ylabel('Break Effectiveness')

count = 0
while count < 100:
    print(count)
    count += 1
# %% break effectiveness over time

brk_endtime_mean, brk_et_scr_mean, brk_et_scr_std = \
    get_mean_std(np.array(brk_end), brk_eff, timedelta(days=7))

# %% plot
plt.figure(figsize=(6, 4), dpi=144)
plt.plot_date(brk_endtime_mean, brk_et_scr_mean, lw=1, ls='-', markersize=0)
plt.fill_between(brk_endtime_mean, brk_et_scr_mean - brk_et_scr_std,
                 brk_et_scr_mean + brk_et_scr_std, alpha=.3)
plt.xlabel('Time')
plt.ylabel('Break Effectiveness')
plt.xticks(rotation=45)

# %%
