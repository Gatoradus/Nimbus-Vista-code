import threading
import time
import json

class Player(object):
    def __init__(self,pd=dict()):
        if pd:
            self.__dict__ = pd
        else:
            self.x = 0
            self.y = 0
            self.z = 0
            self.height = 72
            self.weight = 200
            self.name = "UNNAMED"
        self.brainThread = Brain(self)
        self.threadPool = [self.brainThread]

    def start(self):
        print ("starting Player...")
        

    def fromJSON(d):
        p = Player()
        for (k,v) in d.items():
            p.__dict__[k] = v
        #p.__dict__ = d
        return p

    

class PlayerThread(threading.Thread):
    def testThreading(self):
        print (self.player.x)

    def __init__(self, player):
        super(PlayerThread, self).__init__()
        self.player = player

    def run(self):
        while True:
            print ("run..." + self.player.name)
            time.sleep(5)

class Brain(PlayerThread):
    def __init__(self, player):
        super(Brain, self).__init__(player)

    def run(self):
        print ("starting Brain PlayerThread..." + self.player.name)
        super().run()
        
class PostOffice(PlayerThread):
    def __init__(self):
        super().__init__()

    def run(self):
        print ("starting PostOffice PlayerThread..." + self.player.name)

class PlayerMapper(PlayerThread):
    def __init__(self):
        super().__init__()

    def run(self):
        print ("starting PlayerMapper PlayerThread..." + self.player.name)

class FirstAide(PlayerThread):
    def __init__(self):
        super().__init__()

    def run(self):
        print ("starting FirstAide PlayerThread..." + self.player.name)

class Sensor(PlayerThread):
    def __init__(self):
        super().__init__()

    def run(self):
        print ("starting Sensor PlayerThread..." + self.player.name)



class Bot(Player):
    def __init__(self):
        super().__init__()

    def start(self):
        print ("starting Bot ..." + self.player.name)

class PlayerFactory(object):
    def __init__(self, numPlayers, baseName):
        self.numPlayers = numPlayers
        self.baseName = baseName

    def makePlayers(self,fileName):
        fp = open(fileName, 'w')
        
        for i in range(0,self.numPlayers):
            suffix = '{:04d}'.format(i)
            name = self.baseName + suffix
            p = Player()
            p.name = name
            pstr = json.dumps(p,default=toJSON)
            fp.write(pstr + '\n')
        fp.close()
            

class PlayerModuleEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Player):
            return obj.__dict__
        else:
            return json.JSONEncoder.default(self,obj)

class PlayerModuleDecoder(json.JSONDecoder):
    def default(self, s):
        #d = super().default(s)
        p = Player()
        #p.__dict__ = d
        return p
        

def toJSON(p):
    d = {k: v for k, v in p.__dict__.items() if not (k == 'brainThread' or k == 'threadPool')}
    return d



