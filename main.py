import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from global_var import *
from datetime import datetime


# %%
fullds = pd.read_csv('All Activities by project.csv')
fullds = fullds.sort_values(by=['Start Date'])

fullds['Score'] = [proj_prod[x] for x in fullds['Project'].to_numpy()]

fullds['Project']
fullds = fullds[fullds['Project']!='(No Project)']
test1 = fullds.iloc[0]['End Date']
test2 = fullds.iloc[1]['Start Date']
dt = datetime.fromisoformat(test2)-datetime.fromisoformat(test1)
dt.total_seconds()
