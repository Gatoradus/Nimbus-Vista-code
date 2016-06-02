#!/usr/bin/env python3

import sys, getopt
import json
from Player import *

def main(argv):
    inputfile = ''
    #outputdir = ''
    try:
        (opts, args) = getopt.getopt(sys.argv[1:], "hi:", ["ifile="])
        #
    except getopt.GetoptError:
        print ('runplayer.py -i <inputfile>')
        
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('bot_factory.py -i <inputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        
    print ('Input file is "' + inputfile + '"')
    
    
    #players = []
    #args = 0 # Just gets rid of annoying unused var message in Eclipse.
    fp = open(inputfile,'r')
    
    ##for line in fp:
    ##    p = json.loads(line,object_hook=Player.fromJSON)
    ##    players.append(p)
    ##    print(p.name)
    
    dictStr = fp.read()
    
    fp.close()
    
    configDict = json.loads(dictStr)
    #multicast_group = configDict["multicast_group"]
    server_address = (configDict["server_address"][0],configDict["server_address"][1])
    #napTime = configDict["napTime"]
    configDict["server_address"] = server_address
    
    #(receiverAddress,startingPort) = server_address
    p = Player(pd=configDict)
    
    
    for key,val in p.__dict__.items():
        #print(key + ":" + str(type(val)))
        try:
            print(key + ":" + str(val))
        except: 
            print (Exception)
            
    p.brainThread.start()
    
if __name__ == "__main__":
#    print("HEHH")
    main(sys.argv[1:])
    
        
        