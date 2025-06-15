import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import spatial

# heritage heights
# read saved telemetry data (use telemetry.py to create)
df_border = pd.read_csv("20230209_180752_telemetry_reference_2left4right6fast.csv")
df_wrong = pd.read_csv("20230217_103423_telemetry_reference_wrong_side.csv")
df_wrong_overpass = pd.read_csv("20230223_110216_telemetry_overpass.csv")
np.floor(df_border.min())
np.ceil(df_border.max())

# write references lap to disk
df_reference = df_border[df_border["lap"].isin([2, 4, 6])].copy()
# map so that lap 0 = reference, 1 = left, 2 = right, 3=wrong
df_reference["lap"] = df_reference["lap"].map({6:0, 2:1, 4:2})
# drop duplicates (recording framerate 1000fps, higher than game framerate -> duplicates)
df_reference.drop_duplicates(subset = ["x", "y", "z", "lap"],
                             keep="first", inplace=True, ignore_index=True)

# get wrong side data
df_wrong.drop_duplicates(subset = ["x", "y", "z", "lap"],
                             keep="first", inplace=True, ignore_index=True)
df_wrong["lap"] = df_wrong["lap"].map({1:3})

# get wrong overpass
df_wrong_overpass.drop_duplicates(subset = ["x", "y", "z", "lap"],
                             keep="first", inplace=True, ignore_index=True)
df_wrong_overpass["lap"] = df_wrong_overpass["lap"].map({1:3})

# concat with reference
df_reference = pd.concat([df_reference, df_wrong, df_wrong_overpass])

# safe for later use
df_reference.to_csv("data/reference_telemetry.csv", index=False)

# omega
# read saved telemetry data (use telemetry.py to create)
df_border = pd.read_csv("20230316_200833_telemetry.csv")
#df_wrong = pd.read_csv("20230217_103423_telemetry_reference_wrong_side.csv")
#df_wrong_overpass = pd.read_csv("20230223_110216_telemetry_overpass.csv")
np.floor(df_border.min())
np.ceil(df_border.max())

# write references lap to disk
df_reference = df_border[df_border["lap"].isin([2, 4, 6])].copy()
# map so that lap 0 = reference, 1 = left, 2 = right, 3=wrong
df_reference["lap"] = df_reference["lap"].map({6:0, 2:1, 4:2})
# drop duplicates (recording framerate 1000fps, higher than game framerate -> duplicates)
df_reference.drop_duplicates(subset = ["x", "y", "z", "lap"],
                             keep="first", inplace=True, ignore_index=True)

# safe for later use
df_reference.to_csv("data/reference_telemetry_omega.csv", index=False)
