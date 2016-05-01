#!/usr/bin/env python3

import sys, getopt
import json
#from Player import *

def main(argv):
    inputfile = ''
    outputdir = ''
    try:
        (opts, args) = getopt.getopt(sys.argv[1:], "hi:d:", ["ifile=", "dir="])
        #
    except getopt.GetoptError:
        print ('bot_factory.py -i <inputfile> -d <outputdir>')
        
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('bot_factory.py -i <inputfile> -o <outputdir>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-d", "--dir"):
            outputdir = arg
    print ('Input file is "' + inputfile + '"')
    print ('Output dir is "' + outputdir + '"')
    
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
    multicast_group = configDict["multicast_group"]
    server_address = (configDict["server_address"][0],configDict["server_address"][1])
    napTime = configDict["napTime"]
    
    (receiverAddress,startingPort) = server_address
    
    for pd in configDict["players"]:    
        pd["multicast_group"] = multicast_group
        pd["server_address"] = (receiverAddress,startingPort)
        pd["napTime"] = napTime
        fp = open(outputdir + '/' + pd["name"] + '.json', 'w')
        pstr = json.dumps(pd)
        fp.write(pstr)
        fp.close()
        
        
        
        

if __name__ == "__main__":
    main(sys.argv[1:])
