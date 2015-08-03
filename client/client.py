#!/bin/python

import subprocess
import re
from time import sleep

ip = 'daviddworken.com'
port = '8545'

def getTemperature():
    try:
	temp = getAMDTemp()
    except:
	try:
	    temp = getNvidiaTemp()
   	except:
	    return -1
    return temp

def getRPCOutput(ipaddr, port, command, params):
    formattedParams = "["
    for item in params:
	if item == True or item == False:
	    if item == True:
		formattedParams += "true, "
	    if item == False:
		formattedParams += "false, "
	else:
	    formattedParams += ("\"" + item + "\", ")
	if params.index(item) + 1 == len(params):
	    formattedParams = formattedParams[:-2]
    formattedParams += "]"
    command = command.replace('.','_')
    try:
	out = run("curl --silent -X POST --data '{\"jsonrpc\":\"2.0\",\"method\":\"" + command + "\",\"params\":" + formattedParams + ",\"id\":67}' " + ipaddr + ":" + port)
    except:
	out = -1
    return out

def run(command):
    return subprocess.check_output(command, shell=True)

#def getAMDTemp():

def getNvidiaTemp():
    out = ' '.join(run('nvidia-smi').splitlines())
    return re.findall(r'\d+C', out)[0] #only return first temperature until we decide on how to do the API for multiple GPUs

def getLastKnownBlockNumber():
    return int(getRPCOutput(ip, port,'eth.blockNumber' , []).splitlines()[3].split('"')[3], 16)

def getLastKnownBlockHash():
    lastBlockHex = hex(getLastKnownBlockNumber())
    return getRPCOutput(ip, port, 'eth.getBlockByNumber', [lastBlockHex, False]).splitlines()[5].split('"')[3]

def submitData(dict, address):
    print dict
    run('curl --silent -X POST --data ' + str(dict) + " " + address)

while True:
    submitData({'blockHash':getLastKnownBlockHash(), 'blockNumber':getLastKnownBlockNumber(), 'temperature': getTemperature()}, "http://daviddworken.com")
    sleep(3)
