#!/bin/python

import subprocess  # used to call into curl to talk to the RPC server
import re  # used to parse out the temperature
from time import sleep
import json

ip = '127.0.0.1'  # the IP address of the RPC server
port = '8545'  # the port of the RPC server
apiIP = 'http://daviddworken.com:80'  # placeholder for what the IP of the API will end up being


def getTemperature():  # returns the temperature of the GPU no matter what brand
    try:
        temp = getAMDTemp()
    except:
        try:
            temp = getNvidiaTemp()
        except:
            print "Error: Could not detect a GPU. Do you have a GPU installed? If so, do you have either nvidia-smi or aticonfig installed?"
            return -1
    return temp[0]  # only return the first GPU temp until we decide on the API for multiple GPUs


def submitData(dict, address):  # submits the json to the server at address
    cmd = 'curl --silent -X POST --data \'%s\' %s' % (dict, address)
    print cmd
    return run(cmd)


def getRPCOutput(ipaddr, port, command, params):
    command = command.replace('.', '_')  # repalce . with _ because that is how the RPC server wants to get commands

    post_data = json.dumps({'jsonrpc': '2.0', 'method': command, 'params': params, 'id': 67})

    try:
        return submitData(post_data, '%s:%s' % (ipaddr, port))
    except:
        print "Error: Could not connect to the RPC Server. If you have it running somewhere other than localhost port 8545 please change the constants defined in this file. "
        return None


def run(command):  # just a simple wrapper around subprocess.check_output
    return subprocess.check_output(command, shell=True)


def getAMDTemp():  # parses ati-config to get GPU temps
    out = ' '.join(run('aticonfig --odgt').splitlines())
    return re.findall(r'\d+\.\d+ C',
                      out)  # matches any number of digits followed by a period followed by any number of digits followed by a C


def getNvidiaTemp():  # parses nvidia-smi to get GPU temps
    out = ' '.join(run('nvidia-smi').splitlines())  # makes it all 1 line so only 1 regex execution needed
    return re.findall(r'\d+C', out)  # matches any number of digits followed by a C


def getLastKnownBlockNumber():
    res = json.loads(getRPCOutput(ip, port, 'eth.blockNumber', []))['result']
    return int(res, 16)


def getLastKnownBlockHash(lastBlockNumber):
    lastBlockHex = hex(lastBlockNumber)  # eth.getBlockByNumber wants the block number in hex not base 10
    res = json.loads(getRPCOutput(ip, port, 'eth.getBlockByNumber', [lastBlockHex, False]))['result']['hash']
    return res


while True:
    lastBlockNumber = getLastKnownBlockNumber()
    lastBlockHash = getLastKnownBlockHash(lastBlockNumber)
    data = {'lastBlockNumber': lastBlockNumber,
            'lastBlockHash': lastBlockHash,
            'temperature': getTemperature()}
    print data
    # submitData(json.dumps(data), apiIP)
    sleep(10)
