import threading
import time
import json
#from asyncio.windows_events import NULL

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
        self.PMThread = PlayerMapper(self)
        self.threadPool = [self.brainThread]

    def start(self):
        print ("starting Player...")
        

    def fromJSON(self):
        p = Player()
        for (k,v) in self.items():
            p.__dict__[k] = v
        #p.__dict__ = self
        return p
    
    

    

class PlayerThread(threading.Thread):
    def testThreading(self):
        print (self.player.x)

    def __init__(self, player):
        super(PlayerThread, self).__init__()
        self.player = player
        self.napTime = player.napTime
        
    
    def runTasks(self):
        """runTasks: overload in subclasses to carry out needed tasks."""
        raise NotImplementedError("Must override runTasks")

    

    

class Brain(PlayerThread):
    def __init__(self, player):
        super(Brain, self).__init__(player)

    def run(self):
        print ("starting Brain..." + self.player.name)
        while True:
            if not self.player.PMThread.isAlive():
                    self.player.PMThread.start()
            print ("Brain is running..." + self.player.name)
            time.sleep(self.napTime)
            
            
    #def runTasks(self):
    #    """runTasks: overload in subclasses to carry out needed tasks."""
    #    print("This is runTasks() in the Brain thread!!")
        
class PostOffice(PlayerThread):
    def __init__(self, player):
        super(PostOffice, self).__init__(player)

    def run(self):
        print ("starting PostOffice..." + self.player.name)
        

class PlayerMapper(PlayerThread):
    def __init__(self, player):
        super(PlayerMapper, self).__init__(player)

    def run(self):
        print ("starting PlayerMapper..." + self.player.name)
        while True:
            print ("PlayerMapper is running..." + self.player.name)
            time.sleep(self.napTime*3)
            
class FirstAide(PlayerThread):
    def __init__(self, player):
        super(FirstAide, self).__init__(player)

    def run(self):
        print ("starting FirstAide..." + self.player.name)
        

class Sensor(PlayerThread):
    def __init__(self, player):
        super(Sensor, self).__init__(player)

    def run(self):
        print ("starting Sensor..." + self.player.name)
        



class Bot(Player):
    def __init__(self, player):
        super(Bot, self).__init__(player)
        
    def run(self):
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



