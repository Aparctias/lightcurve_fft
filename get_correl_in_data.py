#!/usr/bin/python

#Get some correlations in data

import numpy as np
import json
import pprint as pp

SPIN_FILE = "mpc_spins"
SPIN_FILE_PROCESSED = "mpc_spins_proc"

data = []
with open(SPIN_FILE, "r") as f:
    data = json.load(f)

check_attrs = ('spin_period', 'absolute_magnitude', 'period', 'semimajor_axis',
               'aphelion_distance', 'perihelion_distance',
               'argument_of_perihelion', 'ascending_node', 'inclination',
               'eccentricity', 'mean_anomaly',)# 'phase_slope', 'orbit_type',
               #'delta_v', 'h_neowise')

process_data = data[:]
for d in data:
    for attr in check_attrs:
        if not d.get(attr):
            process_data.remove(d)
            break

with open(SPIN_FILE_PROCESSED, 'w') as f:
    json.dump(process_data, f)

print "For data len: ", len(data)

cor_check = []
for attr in check_attrs:
    cor_check.append([float(d[attr]) for d in process_data])
correlation = np.corrcoef(cor_check)
for i in range(0, len(check_attrs)):
    print "----------"
    print check_attrs[i], ":"
    for j in range(0, len(check_attrs)):
        print "\t", check_attrs[j], ":", correlation[i][j]
