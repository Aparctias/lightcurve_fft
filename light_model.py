#!/usr/bin/python

# Analyze data from lightcurves gor from constraints
# Based on FFT. Check wavelet series.


import os
import json
import math
import numpy as np
import matplotlib.pyplot as mplt
import scipy.interpolate as sinter
import scipy.fftpack as fftpack
from get_lightcurve_data import DATASET_FILE

FOUR_OBS_DIR="light_four_data"

# Probably, this could be done automatically. Need to check further
# Any good filter or smth like that
FEATURES_NUMB = 110
UPPER_LIM = 90 # harmonics to skip
EXCEPT_HARM = 1 # lower limit

def load_light_dataset():
    with open(DATASET_FILE, 'r') as f:
        return json.load(f)

def dump_for_fourier_analyze(light_dataset):
    if not os.path.exists(FOUR_OBS_DIR):
        os.mkdir(FOUR_OBS_DIR)
    for d in light_dataset:
        if len(d['points']) > 1:
            print d['number'], d['spin_period']
            for i, points in enumerate(d['points']):
                name = str(d['number']) + '_' + str(i)
                filename = os.path.join(FOUR_OBS_DIR, name)
                with open(filename, 'w') as f:
                    dump = [o.split('|')[:2] for o in points]
                    for o in dump:
                        f.write(o[0] + ' ' + o[1] + '\n')


def print_plot(yf, period, aster_number):
    time_inter = np.linspace(0.0, period * 2, FEATURES_NUMB)
    xf = []
    for t in time_inter[EXCEPT_HARM:]:
        xf.append(t - time_inter[EXCEPT_HARM])
    xf = np.array(xf)
    mplt.plot(xf[:-UPPER_LIM], yf)


def get_fourier_series(observations, period):
    # Period and times are counted in hours
    points = [observ.split('|')[:2] for observ in observations]
    # p[0] - time, p[1] - magnitude
    points = [[float(p[0]), float(p[1])] for p in points]
    # Normalize time
    norm_value = points[0][0]
    for i in range(0, len(points)):
        points[i][0] -= norm_value

    times = np.array([p[0] * 24 for p in points])
    magnitudes = np.array([p[1] for p in points])
    # Normalize
    min_mag = np.min(magnitudes)
    max_mag = np.max(magnitudes)
    magnitudes = np.array([(m - min_mag)/(max_mag - min_mag) \
                           for m in magnitudes])

    # Points for interpolation
    time_inter = np.linspace(0.0, period * 2, FEATURES_NUMB)
    EXCEPT_HARM = 1 # lower limit
    f = sinter.PchipInterpolator(times, magnitudes)
    yf = fftpack.fft(f(time_inter))
    return np.abs(yf[EXCEPT_HARM:-UPPER_LIM])

def get_norm_vector(data):
    mx = max(data)
    mn = min(data)
    for i in range(len(data)):
        data[i] = (data[i] - mn) / (mx - mn)
    return data

def sqe(obj, fourier_coeffs):
    s = 0
    for i in range(len(fourier_coeffs)):
        for j in range(len(fourier_coeffs[i])):
            s += (obj[j] - fourier_coeffs[i][j])**2
    # XXX: Need to check for better approach
    return s/len(fourier_coeffs)


def get_probs(obj, known_objs):
    sqes = []
    p = []
    s = 0
    for i in range(len(known_objs)):
        sqes.append(sqe(obj, known_objs[i]))
        s += math.exp(-sqes[i])
    for i in range(len(known_objs)):
        p.append(math.exp(-sqes[i])/s)
    return p


def is_recent_observ(observ1, observ2):
    #XXX: Another constraints: Probable effects are caused by spin plane
    #orientation towards us. Also phase angle matters.
    #This should be corrected after!
    threshold = 42.0 # Days
    if float(observ2[0][0]) - float(observ1[-1][0]) < threshold:
        return True
    return False


def main():
    light_dataset = load_light_dataset()
    data = []
    # XXX: Temporary
    #dump_for_fourier_analyze(light_dataset)

    MAX = 20
    i = 0
    print "Total light dataset: ", len(light_dataset)
    prev_points = []
    prev_fs = []
    for d in light_dataset:
        if i == MAX:
            break
        dataset = {}
        for observations in d['points']:
            fs = get_fourier_series(observations, d['spin_period'])
            fs = get_norm_vector(fs)
            if prev_points and is_recent_observ(prev_points, observations):
                if not dataset.get('number'):
                    dataset['number'] = d['number']
                    dataset['spin_period'] = d['spin_period']
                if not dataset.get('fourier_coef'):
                    dataset['fourier_coef'] = []
                    dataset['fourier_coef'].append(prev_fs)
                dataset['fourier_coef'].append(fs)
            prev_points = observations[:]
            prev_fs = fs[:]

        if dataset:
            data.append(dataset)
        prev_points = []
        i += 1

    control_data = []
    check_data = []
    aster_numbers = []
    if data:
        for astero in data:
            # Get check set
            if len(astero['fourier_coef']) > 2:
                aster_numbers.append(astero['number'])
                control_data.append(astero['fourier_coef'][:-1])
                check_data.append(astero['fourier_coef'][-1])

    #        print astero['number'], len(astero['fourier_coef'])
    #        # XXX: UNcomment this to print plots
    #        mplt.figure()
    #        mplt.title("Fourier for astero number: %s" % astero['number'])
    #        for fs in astero.get('fourier_coef'):
    #            print_plot(fs, astero['spin_period'], astero['number'])
    #        mplt.show()

    # Check results
    # Clustering, sqe, similar..
    for i, check in enumerate(check_data):
        probs = get_probs(check, control_data)
        print "---------------"
        print "For aster: ", aster_numbers[i]
        for j, prob in enumerate(probs):
            print aster_numbers[j], ": ", prob


    # Use some kind of polling
    #result_index = {}
    #for i, aster_number in enumerate(aster_numbers):
    #    result_index[aster_number] = {}
    #    def __print_probs(probs):
    #        for j, prob in enumerate(probs):
    #            print "check aster: ", aster_numbers[j], " - ", prob

    #    def __set_max(probs, result_index):
    #        max_index = 0
    #        max_prob = 0
    #        for i in range(0, len(probs)):
    #            if probs[i] > max_prob:
    #                max_prob = probs[i]
    #                max_index = i
    #        result = result_index[aster_number]
    #        if not result.get(aster_numbers[max_index]):
    #            result[aster_numbers[max_index]] = 1
    #        result[aster_numbers[max_index]] += 1

    #    print "Probabilities per astero: ", aster_number
    #    print "_______________"
    #    for j in range(0, len(control_data[i])):
    #        # XXX: Rewrite this!
    #        probs = sqe.prob(control_data[i][j], check_data)
    #        __set_max(probs, result_index)
    #        #__print_probs(probs)
    #    print result_index


if __name__ == '__main__':
    main()

