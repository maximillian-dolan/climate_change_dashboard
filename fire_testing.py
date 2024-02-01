#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  9 12:29:47 2023

@author: maxdolan
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import cartopy.crs as ccrs
import cartopy.feature as cfeature

#import data
fires = pd.read_csv('Documents/climate_change_dashboard/modis_2015_United_States.csv')
fires_df = pd.DataFrame(fires)


# Convert date into days

epoch_time = datetime(2015, 1, 1)   #Set first day

#Turn date format in CSV file to one readable by datetime module
dates = np.array(fires_df['acq_date'])
date_format = '%Y-%m-%d'

date_days = []

for i in range(len(dates)):
    date_days.append(datetime.strptime(dates[i], date_format))

#Work out days since first day of the year
days = []
for i in date_days:
    days.append((i-epoch_time).days)

fires_df['acq_date'] = days


#Set minimum confidence rating for whole USA map
confident_fires = fires_df[fires_df['confidence']>=95]


#Plot fires within whole USA
fig, ax = plt.subplots(1,2,figsize=(20, 20), subplot_kw={"projection": ccrs.PlateCarree()})
ax[0].add_feature(cfeature.STATES, zorder=3, linewidth=1.5, edgecolor='black')
ax[0].set_extent([-67, -130, 23, 50], crs=ccrs.PlateCarree())
ax[0].scatter(confident_fires['longitude'],confident_fires['latitude'], s = 0.1, alpha = 0.5, c = confident_fires['acq_date'],cmap = 'hot')

#Plot fires just within california
california_fires = fires_df[fires_df['latitude'] < 42][fires_df['latitude']>33][fires_df['longitude']<-115]

#fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={"projection": ccrs.PlateCarree()})
ax[1].add_feature(cfeature.STATES, zorder=3, linewidth=1.5, edgecolor='black')
ax[1].set_extent([-110, -130, 30, 45], crs=ccrs.PlateCarree())
ax[1].scatter(california_fires['longitude'],california_fires['latitude'], s = 0.1, alpha = 0.5, c = california_fires['acq_date'],cmap = 'hot')
plt.colorbar(confident_fires['acq_date'])
plt.show()








