#!/usr/bin/python
import json

DATA_COUNT = 10000
MPC_IN_FILE = "mpc_data"
MPC_CUT_FILE = "mpc_data%s" % DATA_COUNT

with open(MPC_IN_FILE, "r") as f:
    data = json.load(f)

print "Total asteroids in base: ", len(data)

certain_data = []
with open(MPC_CUT_FILE, "w") as f:
    for d in data:
        if int(d['orbit_uncertainty']) in [0, 1]:
            certain_data.append(d)
    print "Certain asteroids count: ", len(certain_data)
    json.dump(certain_data[:DATA_COUNT], f)
