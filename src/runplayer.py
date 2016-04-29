#!/usr/bin/env python3

import json
from Player import *


print ("Starting Player...")

# tasks:
# 1) Serialize/deserialize
# 2) Create Thread class and get working w/ Player class


p = Player()

p.x = 1005

pf = PlayerFactory(10,'Player-')

pstr = json.dumps(p,default=toJSON)

#pstr = pe.dumps(p)

print (pstr)

ploaded = json.loads(pstr,object_hook=Player.fromJSON)

print(ploaded)



p.start()
fp = open("player.json", 'w')
p_json = json.dumps(p.__dict__,fp)
fp.write(p_json)
fp.close()


