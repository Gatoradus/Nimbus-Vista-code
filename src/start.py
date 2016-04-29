#!/usr/bin/env python3

print ("hello")

import json
from Player import *

#playerFile = 'players.json'
playerFile = 'players2.json'


players = []

fp = open(playerFile,'r')

##for line in fp:
##    p = json.loads(line,object_hook=Player.fromJSON)
##    players.append(p)
##    print(p.name)

dictStr = fp.read()

fp.close()

configDict = json.loads(dictStr)
multicast_group = configDict["multicast_group"]

for pd in configDict["players"]:
    pd["multicast_group"] = multicast_group
    p = Player(pd)
    players.append(p)
    

for p in players:
    [print(k,v) for k,v in p.__dict__.items() if True]
    #print(p.__dict__.keys())
    p.brainThread.start()





