import threading
import time
import json
#from asyncio.windows_events import NULL
import socket
import struct
import sys
import datetime
import queue

class Player(object):
    def __init__(self,pd=dict(),fname=None):
        if pd:
            self.__dict__ = pd
            #self.multicast_group = (self.multicast_group_ip, self.server_address[1])
            self.multicast_group = (self.multicast_group_ip, self.sender_port)
        elif fname is not None:
            print ("fname found:" + fname)
            fp = open(fname,'r') 
            dictStr = fp.read()   
            
            print ("fname found")      
               
            configDict = json.loads(dictStr)        
            server_address = (configDict["server_address"][0],configDict["server_address"][1])        
            configDict["server_address"] = server_address
            self.__dict__ = configDict
            print ("fname found:" + self.multicast_group_ip,)
            
            #print ("dictStr:" + dictStr)
            
    
            
    #multicast_group = configDict["multicast_group"]
            
    #napTime = configDict["napTime"]
            
            fp.close()
            
            self.multicast_group = (self.multicast_group_ip, self.sender_port)
                     
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
        self.outboxLock = threading.Lock()
        self.inboxLock = threading.Lock()
        self.inboxq = queue.Queue(10)
        self.outboxq = queue.Queue(10)
           
        self.outbox = []
        self.inbox = []
        self.brainThread = Brain(self)
        self.PMThread = PlayerMapper(self)
        self.POThread = PostOffice(self)
        self.brainThread.setName("{}[{}]".format(self.id,"BR"))
        self.POThread.setName("{}[{}]".format(self.id,"PO"))
        self.threadPool = [self.brainThread,self.PMThread,self.POThread]

    def start(self):
        print ("starting Player...")
        
    def messageStamp(self):
        currentThread = threading.current_thread()
        threadName = currentThread.getName()
        return '{}{}:'.format(threadName,datetime.datetime.now())
    
    def stmpPrint(self,*s):
        print(self.messageStamp()+str(s))

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
            self.player.stmpPrint("There are " + str(self.player.outboxq.qsize()) + " outgoing messages.")
            self.player.stmpPrint("There are " + str(self.player.inboxq.qsize()) + " inbound messages.")
            # This will generate the "threads can only be started once" error if the message
            # goes out more than once.
            if not self.player.PMThread.isAlive():
                    self.player.PMThread.start()
                    
            if not self.player.POThread.isAlive():
                    self.player.POThread.start()
                    
            #print ("Brain is running..." + self.player.name)
            self.player.x=self.player.x+1
            if self.player.hasMoved():            
                if self.player.sender:
                    message = dict()
                    message['x'] = self.player.x
                    message['y'] = self.player.y
                    message['z'] = self.player.z
                    message['subject'] = "L" # 'L' is for location messages
                    message['playerID'] = self.player.id
                    
                    self.player.outbox.append(message)
                    self.player.outboxLock.acquire()
                    self.player.outboxq.put(message)
                    self.player.outboxLock.release()
                    
                
            time.sleep(self.napTime*10)
        
class PostOffice(PlayerThread):
    
    def bindSockets(self):
        self.loopCount = 0
        self.senderSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.senderSock.settimeout(2)
        #self.senderSock.setblocking()
        # Set the time-to-live for messages to 1 so they do not go past the
        # local network segment.
        ttl = struct.pack('b', 1)
        self.senderSock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
        if self.player.receiver:
            
            self.receiverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.receiverSock.settimeout(1)
    # Bind to the server address
            self.receiverSock.bind(self.player.server_address)
    
    # Tell the operating system to add the socket to the multicast group
    # on all interfaces.
            self.group = socket.inet_aton(self.player.multicast_group_ip)
            self.mreq = struct.pack('4sL', self.group, socket.INADDR_ANY)
            self.receiverSock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, self.mreq)

    
    
    def __init__(self, player):
        super(PostOffice, self).__init__(player)
# Receive/respond loop

    def listen(self):
        
        self.player.stmpPrint ('listen():waiting to receive message')
        #(data, address) = ('','')
        try:
            data, address = self.receiverSock.recvfrom(1024)
        except socket.timeout:
            #self.player.outbox.append(message)
            self.player.stmpPrint ('timed out, no more responses')
            
        else:
            self.player.stmpPrint ('received "%s" from %s' % (data,address))
            self.player.stmpPrint (':received %s bytes from %s' % (len(data), address))
            
            data = data.decode('utf-8')
            self.player.stmpPrint ('Raw data:' + data)
            messageDict = json.loads(data)
            
            for key,val in messageDict.items():
                self.player.stmpPrint("\t:KEY: " + key + ", VAL: " + str(val))
                
            self.player.stmpPrint (':sending acknowledgement to', address)
            self.receiverSock.sendto(bytes('ack','UTF-8'), address)
            self.player.stmpPrint (':Adding message to inbox' )
            self.player.inbox.append(messageDict)
            self.player.inboxLock.acquire()
            self.player.inboxq.put(messageDict)
            self.player.inboxLock.release()
        
        
        
    
        
        self.player.stmpPrint (":Returning from 'listen(self,threadName)'")


    def sendStatus(self):
        
        self.player.outboxLock.acquire()       
        
        if not self.player.outboxq.empty():            
            message = self.player.outboxq.get()
            self.player.outboxLock.release()
            messageString = json.dumps(message)
            self.player.stmpPrint (":Trying to send my location...")       
            
            
            
            try:
                # Send data to the multicast group
                self.player.stmpPrint (':sending "%s"' % messageString)
                sent = self.senderSock.sendto(bytes(messageString,'UTF-8'), self.player.multicast_group)
                
                # Look for responses from all recipients
                while True:
                    self.player.stmpPrint ('waiting to receive')
                    try:
                        data, server = self.senderSock.recvfrom(16)
                    except socket.timeout:
                        #self.player.outbox.append(message)
                        self.player.stmpPrint ('timed out, no more responses')
                        break
                    else:
                        
                        self.player.stmpPrint ('received "%s" from %s' % (data,server))
    
            finally:
                pass
                self.player.stmpPrint (':Executing finally clause.')
                #self.senderSock.close()   
            
            self.player.stmpPrint (":Returning from 'sendStatus(self,threadName)'")
        else:
            self.player.outboxLock.release()

    def run(self):
        self.player.stmpPrint ("starting PostOffice..." + self.player.name)
        self.bindSockets()
        while True:
            self.player.stmpPrint("LOOP COUNT:" + str(self.loopCount))
            if self.player.receiver:
                self.listen()
            if self.loopCount >= self.player.sendingDelay:
                self.player.stmpPrint("\n\nStarting to SEND!!!!!\n\n")
                self.sendStatus()
            self.loopCount+=1
            time.sleep(self.napTime)
        

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



