# -- coding: utf-8 --
import os
from time import sleep
import pandas as pd
import numpy as np

# read data
dataset = pd.read_csv('/data/Alibaba_requests_up_5min.csv')

requests_data = dataset['requests']
requests_data = requests_data.values
state_cur = []
# pull requests via jmeter
for i in range(200, 220):
    k = requests_data[i]
    os.system("jmeter -n -t /data/testjmt.jmx -l f:/jmeter_rawdata_adjust/jmeter_rawdata_%s.csv -JthreadNum=%s -JloopNum=1 -JrampupTime=300" % (i, k))
    jmeter = pd.read_csv('f:/jmeter_rawdata_adjust/jmeter_rawdata_%s.csv' % i)
    elapsed = np.array(jmeter['elapsed'])
    timeStamp = jmeter['timeStamp']
    success = np.array(jmeter['success'].astype('int'))
    latency = np.array(jmeter['Latency'])
    connect = np.array(jmeter['Connect'])
    lenth = len(timeStamp)
    timeStamp_len = timeStamp[lenth-1] - timeStamp[0]
    # QoS: version 3
    state_cur_val = (np.mean(elapsed) * 0.05 + np.mean(latency) * 0.1 + np.mean(connect) * 0.05 + (
                1 - np.mean(success)) * 2 + (timeStamp_len-300000)/300000)/8
    if state_cur_val > 4:
        state_cur_val = 4
    state_cur.append(round(state_cur_val))
    csv = pd.DataFrame(data=state_cur)
    names = ['state']
    csv.columns = names
    csv.to_csv('/data/state_adjust.csv', mode='w')
    # run requests_server.py
    if i > 204:
        with open('/serving_model/requests_server.py', 'r') as f:
            exec(f.read())