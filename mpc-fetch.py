#!/usr/bin/python
# mpc-fetch.py -- fetches properties of all objects that match search params.

# Sample call to retrieve all Near-Earth-Objects with inclination <= 2 degrees
# and spin period >= 5 hours:
#  python mpc-fetch.py neo 1 inclination_max 2.0 spin_period_min 5.0 > data.xml

# For the list of possible search parameters, browse to:
# http://minorplanetcenter.net/web_service.html

# To get results in JSON format instead of xml, add 'json 1' to parameters.

# N.B. This script requires the 'requests' python module:
# $ pip install requests
# If you need pip, see: https://pypi.python.org/pypi/pip


import sys, requests

url = 'http://mpc.cfa.harvard.edu/ws/search'

params = {}
for i in range(1, len(sys.argv)):
  if (i % 2 == 1):
    params[sys.argv[i]] = sys.argv[i+1]

r = requests.post(url, params, auth = ('mpc_ws', 'mpc!!ws'))

print r.text
