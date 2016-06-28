import threading
import time
import json
#from asyncio.windows_events import NULL
import socket
import struct
#import sys
import datetime
import queue
import random
import logging
#logging.basicConfig(filename='example.log',level=logging.DEBUG)
#logging.debug('This message should go to the log file')
#logging.info('So should this')
#logging.warning('And this, too')

class Player(object):
    def __init__(self,pd=dict(),fname=None,mapped=False):
        if pd:
            self.__dict__ = pd
            #self.multicast_group = (self.multicast_group_ip, self.server_address[1])
            if hasattr(self, 'multicast_group_ip') and hasattr('self,sender_port'):
                self.multicast_group = (self.multicast_group_ip, self.sender_port)
        elif fname is not None:
            print ("fname found:" + fname)
            fp = open(fname,'r') 
            dictStr = fp.read()   
            
            print ("fname found")      
               
            configDict = json.loads(dictStr)        
            #server_address = (configDict["server_address"][0],configDict["server_address"][1])
            
            #server_address = (configDict["multicast_group_ip"],configDict["server_address"][1])        
            server_address = ('',configDict["server_address"][1])
            configDict["server_address"] = server_address
            self.__dict__ = configDict
            print ("fname found:" + self.multicast_group_ip,)
            print ('configDict["server_address"]' + str(configDict["server_address"] ))
            fp.close()
            
            self.multicast_group = (self.multicast_group_ip, self.sender_port)
                     
        else:
            self.x = 0
            self.y = 0
            self.z = 0
            self.height = 72
            self.weight = 200
            self.name = "UNNAMED"
            self.id = 0
        self.uniqueMessageNumber = 0
        self.lastx = self.x
        self.lasty = self.y
        self.lastz = self.z
        self.outboxLock = threading.Lock()
        self.inboxLock = threading.Lock()
        self.playerMap = dict()
        self.inboxq = queue.Queue(100)
        self.outboxq = queue.Queue(100)
           
        #self.outbox = []
        #self.inbox = []
        if not mapped:
            self.brainThread = Brain(self)
            self.PMThread = PlayerMapper(self)
            self.POThread = PostOffice(self)
            self.brainThread.setName("{}[{}]".format(self.id,"BR"))
            self.POThread.setName("{}[{}]".format(self.id,"PO"))
            self.threadPool = [self.brainThread,self.PMThread,self.POThread]
            self.longName = self.name + "-" + str(self.id)
            self.logger = logging.getLogger(self.longName)
            self.logger.setLevel(logging.INFO)
            self.fh = logging.FileHandler(self.longName + '.log')
            self.fh.setLevel(logging.WARNING)
            self.logger.addHandler(self.fh)
            self.minX = 2
            self.minY = 2
            self.maxX = 110
            self.maxY = 100

    def bindSockets(self):
        self.loopCount = 0
        self.senderSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Might help with servers on PC.
        self.senderSock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.senderSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.senderSock.settimeout(0.1)
        #self.senderSock.setblocking()
        # Set the time-to-live for messages to 1 so they do not go past the
        # local network segment.
        ttl = struct.pack('b', 1)
        self.senderSock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
        if self.receiver:
            
            self.receiverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.receiverSock.settimeout(0.1)
    # Bind to the server address
            self.senderSock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            self.senderSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            self.receiverSock.bind(self.server_address)
    
    # Tell the operating system to add the socket to the multicast group
    # on all interfaces.
            self.group = socket.inet_aton(self.multicast_group_ip)
            self.mreq = struct.pack('4sL', self.group, socket.INADDR_ANY)
            self.receiverSock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, self.mreq)




    def start(self):
        print ("starting Player...")
        
    def messageStamp(self):
        self.uniqueMessageNumber+=1
    
    def stmpPrint(self,*args, logLevel=logging.INFO):
        return
        currentThread = threading.current_thread()
        threadName = currentThread.getName()
        messageNumber = self.uniqueMessageNumber
        
        s = '{}:{}:{}:'.format(threadName,str(messageNumber).zfill(6),datetime.datetime.now())
        
        for a in args:
            s = s + str(a)
        #print(self.messageStamp()+s)
        if logLevel == logging.WARNING:
            self.logger.warning(s)
            #self.fh.warning(s)
        elif logLevel == logging.INFO:
            self.logger.info(s)
            #self.fh.info(s)
        elif logLevel == logging.ERROR:
            self.logger.error(s)
            #self.fh.error(s)
        elif logLevel == logging.DEBUG:
            self.logger.debug(s)
            #self.fh.debug(s)
        elif logLevel == logging.CRITICAL:
            self.logger.critical(s)
            #self.fh.critical(s)

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
    
    def listen(self):
        
        self.stmpPrint ('listen():waiting to receive message')
        #(data, address) = ('','')
        try:
            data, address = self.receiverSock.recvfrom(1024)
        except socket.timeout:
            #self.player.outbox.append(message)
            self.stmpPrint ('timed out, no more responses')
            
        else:
            self.stmpPrint ('received "%s" from %s' % (data,address))
            self.stmpPrint (':received %s bytes from %s' % (len(data), address))
            
            data = data.decode('utf-8')
            self.stmpPrint ('Raw data:' + data)
            messageDict = json.loads(data)
            
            p = Player(pd=messageDict,mapped=True)
            if 'id' in messageDict:
                    self.playerMap[messageDict['id']] = p
                    self.messageStamp()
                    self.stmpPrint("Found Player!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!:" + str(p.id),logging.WARNING)
                    self.stmpPrint("Found Player!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!:" + str(len(self.playerMap)),logging.WARNING)
                
            
            
            for key,val in messageDict.items():
                self.stmpPrint("\t:KEY: " + key + ", VAL: " + str(val),logging.WARNING)
                
            self.stmpPrint (':sending acknowledgement to', address)
            self.receiverSock.sendto(bytes('ack','UTF-8'), address)
            #self.player.stmpPrint (':Adding message to inbox' )
            #self.player.inbox.append(messageDict)
            self.inboxLock.acquire()
            #self.player.inboxq.put_nowait(messageDict)
            self.inboxLock.release()
        
        
        
    
        
        self.stmpPrint (":Returning from 'listen(self,threadName)'")


    def sendStatus(self):
        
        self.outboxLock.acquire()       
        
        if not self.outboxq.empty():            
            message = self.outboxq.get()
            self.outboxLock.release()
            messageString = json.dumps(message)
            self.stmpPrint (":Trying to send my location...")       
            
            
            
            try:
                # Send data to the multicast group
                self.stmpPrint (':sending "%s"' % messageString)
                sent = self.senderSock.sendto(bytes(messageString,'UTF-8'), self.multicast_group)
                
                # Look for responses from all recipients
#                while True:
 #                   self.stmpPrint ('waiting to receive')
  #                  try:
   #                     data, server = self.senderSock.recvfrom(16)
    #                except socket.timeout:
     #                   #self.player.outbox.append(message)
      #                  self.stmpPrint ('timed out, no more responses')
       #                 break
        #            else:
                        
         #               self.stmpPrint ('received "%s" from %s' % (data,server))
    
            finally:
                pass
                self.stmpPrint (':Executing finally clause.')
                #self.senderSock.close()   
            
            self.stmpPrint (":Returning from 'sendStatus(self,threadName)'")
        else:
            self.outboxLock.release()

class PlayerThread(threading.Thread):
    """PlayerThread: superclass of all threads used by Player."""
    def testThreading(self):
        print (self.player.x)

    def __init__(self, player):
        super(PlayerThread, self).__init__()
        self.player = player
        if hasattr(player,'napTime'):
            self.napTime = player.napTime
        else:
            self.napTime = 5 #FIXME
        
    
   
    
class Brain(PlayerThread):
    def __init__(self, player):
        
        super(Brain, self).__init__(player)

    def run(self):
        print ("starting Brain..." + self.player.name)
        while True:
            self.player.lastx = self.player.x
            self.player.lasty = self.player.y
            self.player.lastz = self.player.z
            self.player.stmpPrint("There are " + str(self.player.inboxq.qsize()) + " inbound messages.")
            #if self.player.inboxq.qsize() > 0:                
                # assume for now that this message is a player's location.
            #    locDict = self.player.inboxq.get()
            #    self.player.stmpPrint('INBOX:' + str(locDict))
            #    p = Player(pd=locDict,mapped=True)
            #    if 'id' in locDict:
            #        self.player.playerMap[locDict['id']] = p
                    
            #        self.player.stmpPrint("Found Player!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!:" + str(p.id))
            #        self.player.stmpPrint("Found Player!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!:" + str(len(self.player.playerMap)))
                
            self.player.stmpPrint("There are " + str(self.player.outboxq.qsize()) + " outbound messages.")
            # This will generate the "threads can only be started once" error if the message
            # goes out more than once.
            if not self.player.PMThread.isAlive():
                    self.player.PMThread.start()
                    
            if not self.player.POThread.isAlive():
                    self.player.POThread.start()
                    
            #print ("Brain is running..." + self.player.name)
            
            xr = random.randint(-2,2)*0.1
            yr = random.randint(-2,2)*0.1
            
            newX = self.player.x+xr
            newY = self.player.y+yr
            if  not (newX > self.player.maxX or newY > self.player.maxY
                      or newX < self.player.minX or newY < self.player.minY):
                self.player.x=newX
                self.player.y=newY
                
            if self.player.hasMoved():            
                if self.player.sender:
                    message = dict()
                    message['x'] = self.player.x
                    message['y'] = self.player.y
                    message['z'] = self.player.z
                    message['subject'] = "L" # 'L' is for location messages
                    message['id'] = self.player.id
                    
                    #self.player.outbox.append(message)
                    self.player.outboxLock.acquire()
                    if self.player.outboxq.qsize() > 0:
                        self.player.outboxq.get()
                        #throw away the message on top so we don't let them pile up!
                    
                    self.player.outboxq.put_nowait(message)
                    self.player.outboxLock.release()
                    
            self.player.stmpPrint('NAPPING:',self.player.napTime*10, logging.WARNING)    
            time.sleep(self.player.napTime*2)
        
class PostOffice(PlayerThread):
    
    
    
    def __init__(self, player):
        super(PostOffice, self).__init__(player)
# Receive/respond loop

    


   

    def run(self):
        self.player.stmpPrint ("starting PostOffice..." + self.player.name)
        self.player.bindSockets()
        while True:
            self.player.stmpPrint("LOOP COUNT:" + str(self.player.loopCount))
            if self.player.receiver:
                self.player.listen()
            if self.player.loopCount >= self.player.sendingDelay:
                self.player.stmpPrint("Starting to SEND!!!!!\n\n")
                self.player.sendStatus()
            self.player.loopCount+=1
            self.player.stmpPrint('NAPPING:',self.player.napTime, logging.WARNING)
            time.sleep(self.player.napTime)
        

class PlayerMapper(PlayerThread):
    def __init__(self, player):
        super(PlayerMapper, self).__init__(player)

    def run(self):
        while True:
            #print ("PlayerMapper.run()" + self.player.name)
            #self.player.stmpPrint('NAPPING:',self.napTime)
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



