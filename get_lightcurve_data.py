#!/usr/bin/python

#Get lightcurve points and periods.

import json
import os

MPC_SPINS="mpc_spins"
LIGHTCURVE_DIR="lightcurves"
DATASET_FILE="LIGHTCURVE_DATASET"
ERROR_FILE="light_errors"

def get_spins_dict():
    data = []
    with open(MPC_SPINS) as f:
        data = json.load(f)

    return dict((d['number'], d['spin_period']) for d in data)

# XXX: Possible place of optimization
def parse_lightcurve_file(filename):
    # {'number': , 'observations': [
    #                 {'reducemags':,
    #                  'ucormag': ,
    #                  'data': [('julian date', 'magnitude', '..')]
    #               ]}}
    data = {}
    i = 0
    with open(filename, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            if line.startswith('OBJECTNUMBER=') and not data.get('number'):
                data['number'] = int(line.split('=')[1])
                data['observations'] = []

            def __add_observation(data):
                if not data.get('observations'):
                    data['observations'] = []
                if len(data['observations']) - 1 < i:
                    data['observations'].append([])
                    data['observations'][i] = {}

            # REDUCEMAGS and UCORMAG are presented in one example
            # for each metadata
            # Arrgh, need to use this in calculations
            for param in ('reducemags', 'ucormag'):
                if param.upper() + '=' in line:
                    __add_observation(data)
                    observs = data['observations'][i]
                    observs[param] = float(line.split('=')[1])
                    if not observs.get('data'):
                        observs['data'] = []

            # DATA BLOCK
            if line.startswith('DATA='):
                data['observations'][i]['data'].append(line.split('=')[1])

            if 'ENDDATA' in line:
                i += 1
    return data

def is_data_for_analyze(data, period):
    # get number of periods per observation
    MAX_PERIODS = 2.0
    threshold = 10
    points = [d.split('|') for d in data]
    if len(points) < threshold:
        return False
    time_beg = float(points[0][0])
    time_end = float(points[-1][0])
    obs_time = (time_end - time_beg) * 60 * 60 * 24
    period_in_sec = period * 60 * 60
    if period_in_sec > obs_time:
        return False
    count_periods = obs_time / period_in_sec
    print len(points), obs_time, period_in_sec, count_periods
    if (len(points) / count_periods < threshold) or \
            count_periods < MAX_PERIODS:
        return False
    return True


def get_observation_points(data, period):
    return_obs = {}
    good_points = []
    for observation in data['observations']:
        if is_data_for_analyze(observation['data'], period):
            if len(good_points) < len(observation['data']):
                good_points.append(observation['data'][:])
    if good_points:
        return_obs['number'] = data['number']
        return_obs['points'] = good_points
        # period in hours
        return_obs['spin_period'] = period

    return return_obs


def dump_dataset(data_set):
    with open(DATASET_FILE, 'w') as f:
        json.dump(data_set, f)

def dump_desig_name(filename):
    with open(ERROR_FILE, 'a') as f:
        f.write('Bad filename: %s\n' % filename)

def main():
    spins_dict = get_spins_dict()
    print len(spins_dict)

    # Clean the error file
    with open(ERROR_FILE, 'w') as f:
        f.write('')

    dump_data = []
    for _, _, files in os.walk(LIGHTCURVE_DIR):
        for i, curve_file in enumerate(files):
            try:
                aster_number = int(curve_file.split('_')[1])
            except ValueError:
                dump_desig_name(curve_file)
                continue
            if aster_number in spins_dict and spins_dict[aster_number] < 11.0:
                print curve_file
                spin_period = spins_dict[aster_number]
                # dump data
                filename = os.path.join(LIGHTCURVE_DIR, curve_file)
                light_data = parse_lightcurve_file(filename)

                data_set = get_observation_points(light_data, spin_period)
                if data_set:
                    dump_data.append(data_set)
        break
    dump_dataset(dump_data)
    print len(dump_data)


if __name__ == '__main__':
    main()
