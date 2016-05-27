import threading
import time
import json
#from asyncio.windows_events import NULL
import socket
import struct
import sys

class Player(object):
    def __init__(self,pd=dict()):
        if pd:
            self.__dict__ = pd
            self.multicast_group = (self.multicast_group_ip, self.server_address[1])
        else:
            self.x = 0
            self.y = 0
            self.z = 0
            self.height = 72
            self.weight = 200
            self.name = "UNNAMED"
        
        self.lastx = self.x
        self.lasty = self.y
        self.lastz = self.z
           
        self.outbox = []
        self.inbox = []
        self.brainThread = Brain(self)
        self.PMThread = PlayerMapper(self)
        self.POThread = PostOffice(self)
        self.brainThread.setName("{}[{}]".format(self.id,"brain"))
        self.POThread.setName("{}[{}]".format(self.id,"post_office"))
        self.threadPool = [self.brainThread,self.PMThread,self.POThread]

    def start(self):
        print ("starting Player...")

    def fromJSON(self):
        p = Player()
        for (k,v) in self.items():
            p.__dict__[k] = v
        #p.__dict__ = self
        return p
    
    def hasMoved(self):
        if (self.lastx != self.x or
            self.lasty != self.y or
            self.lastz != self.z):
            return True
        return False

class PlayerThread(threading.Thread):
    """PlayerThread: superclass of all threads used by Player."""
    def testThreading(self):
        print (self.player.x)

    def __init__(self, player):
        super(PlayerThread, self).__init__()
        self.player = player
        self.napTime = player.napTime
        
    
   
    
class Brain(PlayerThread):
    def __init__(self, player):
        
        super(Brain, self).__init__(player)

    def run(self):
        print ("starting Brain..." + self.player.name)
        while True:
            # This will generate the "threads can only be started once" error if the message
            # goes out more than once.
            if not self.player.PMThread.isAlive():
                    self.player.PMThread.start()
                    
            if not self.player.POThread.isAlive():
                    self.player.POThread.start()
                    
            #print ("Brain is running..." + self.player.name)
            self.player.x+=1
            if self.player.hasMoved():            
                if self.player.sender:
                    message = dict()
                    message['x'] = self.player.x
                    message['y'] = self.player.y
                    message['z'] = self.player.z
                    message['subject'] = "L" # 'L' is for location messages
                    message['playerID'] = self.player.id
                    
                    self.player.outbox.append(message)
                    
                    
                
            time.sleep(self.napTime)
        
class PostOffice(PlayerThread):
    def __init__(self, player):
        self.senderSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.senderSock.settimeout(20)
        # Set the time-to-live for messages to 1 so they do not go past the
        # local network segment.
        ttl = struct.pack('b', 1)
        self.senderSock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

        super(PostOffice, self).__init__(player)
        
        if self.player.receiver:

            self.receiverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Bind to the server address
            self.receiverSock.bind(self.player.server_address)
    
    # Tell the operating system to add the socket to the multicast group
    # on all interfaces.
            self.group = socket.inet_aton(self.player.multicast_group_ip)
            self.mreq = struct.pack('4sL', self.group, socket.INADDR_ANY)
            self.receiverSock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, self.mreq)

# Receive/respond loop

    def listen(self):
        currentThread = threading.current_thread()
        threadName = currentThread.getName()
        print (threadName + ':waiting to receive message')
        data, address = self.receiverSock.recvfrom(1024)
    
        print (threadName + ':received %s bytes from %s' % (len(data), address))
        
        data = data.decode('utf-8')
        print ('Raw data:' + data)
        messageDict = json.loads(data)
        
        for key,val in messageDict.items():
            print(threadName + "\t:KEY: " + key + ", VAL: " + str(val))
            
        print (threadName + ':sending acknowledgement to', address)
        self.receiverSock.sendto(bytes('ack','UTF-8'), address)
        print (threadName + ':Adding message to inbox' )
        self.player.inbox.append(messageDict)
        print (threadName + ":Returning from 'listen(self,threadName)'")


    def processMail(self):
        currentThread = threading.current_thread()
        threadName = currentThread.getName()
        if len(self.player.outbox) > 0:
            message = self.player.outbox.pop()
            messageString = json.dumps(message)
            print (threadName + ":Trying to send my location...")       
            
            
            
            try:
                # Send data to the multicast group
                print (threadName + ':sending "%s"' % messageString)
                sent = self.senderSock.sendto(bytes(messageString,'UTF-8'), self.player.multicast_group)
                
                # Look for responses from all recipients
                while True:
                    print ('waiting to receive')
                    try:
                        data, server = self.senderSock.recvfrom(16)
                    except socket.timeout:
                        self.player.outbox.append(message)
                        print ('timed out, no more responses')
                        break
                    else:
                        
                        print ('received "%s" from %s' % (data,server))
    
            finally:
                print (threadName + ':closing socket')
                self.senderSock.close()   
            
            print (threadName + ":Returning from 'processMail(self,threadName)'")


    def run(self):
        print ("starting PostOffice..." + self.player.name)
        while True:
            if self.player.receiver:
                self.listen()
            self.processMail()
        

class PlayerMapper(PlayerThread):
    def __init__(self, player):
        super(PlayerMapper, self).__init__(player)

    def run(self):
        while True:
            #print ("PlayerMapper.run()" + self.player.name)
            time.sleep(self.napTime)

            
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



