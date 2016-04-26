#!/usr/bin/python

# Get NEOWISE data

import os
import time
import json
import requests

MPC_SPIN_PROC = "mpc_spins_proc"
NEOWISE_DIR = "neowise_stat"
NEOWISE_SKIP = "neowise_skip_objs"

data = []
with open(MPC_SPIN_PROC, 'r') as f:
    data = json.load(f)

url = 'http://irsa.ipac.caltech.edu/cgi-bin/Gator/nph-query?searchForm=MO' \
      '&spatial=cone&catalog=allsky_4band_p1bs_psd&mobj=smo&outfmt=1' \
      '&mobjstr=%s'

def save_to_file(obj_name, stat):
    with open(NEOWISE_DIR + '/' + obj_name, 'w') as f:
        f.write(stat)

def execute_request(request_url):
    retries = 1
    i = 0
    text = ''
    try:
        while (i < retries):
            r = requests.get(request_url)
            # Very bad
            if r.text.startswith("[struct stat=\"ERROR\""):
                print "Retry: ", request_url
                time.sleep(1)
            else:
                text = r.text
                break
            i += 1
    except:
        text = ''
    return text

def stat_file_exists(obj_name):
    return os.path.exists(NEOWISE_DIR + '/' + obj_name)

def get_objs_to_skip():
    if os.path.exists(NEOWISE_SKIP):
        with open(NEOWISE_SKIP, 'r') as f:
            return f.read().split()
    else:
        return []

def add_obj_to_skip(obj_name):
    with open(NEOWISE_SKIP, 'a') as f:
        f.write(obj_name + ' ')

if not os.path.exists(NEOWISE_DIR):
    os.mkdir(NEOWISE_DIR)

print "Total: ", len(data)
skip_objs = get_objs_to_skip()
print "Not uploaded objs: ", skip_objs
for i in range(0, len(data)):
    mobjstr = ''
    for n in ('name', 'number', 'designation'):
        if data[i].get(n):
            mobjstr = data[i].get(n)
    if not mobjstr or stat_file_exists(str(mobjstr)) or\
                      str(mobjstr) in skip_objs:
        continue
    mobjstr = str(mobjstr)
    print "Processing: %s - %s" % (i, mobjstr)
    stat = execute_request(url%mobjstr)
    if stat:
        save_to_file(mobjstr, stat)
    else:
        add_obj_to_skip(mobjstr)

