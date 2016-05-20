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
        self.brainThread = Brain(self)
        self.PMThread = PlayerMapper(self)
        self.POThread = PostOffice(self)
        self.threadPool = [self.brainThread,self.PMThread,self.POThread]

    def start(self):
        print ("starting Player...")
        

    def fromJSON(self):
        p = Player()
        for (k,v) in self.items():
            p.__dict__[k] = v
        #p.__dict__ = self
        return p
    
    

    

class PlayerThread(threading.Thread):
    """PlayerThread: superclass of all threads used by Player."""
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
            # This will generate the "threads can only be started once" error if the message
            # goes out more than once.
            if not self.player.PMThread.isAlive():
                    self.player.PMThread.start()
                    
            if not self.player.POThread.isAlive():
                    self.player.POThread.start()
                    
            print ("Brain is running..." + self.player.name)
            if self.player.sender:
                message = dict()
                message['x'] = self.player.x
                message['y'] = self.player.y
                message['z'] = self.player.z
                message['subject'] = "L" # 'L' is for location messages
                message['playerID'] = self.player.id
                messageString = json.dumps(message)
                self.player.POThread.sendMessage(messageString)
             
            time.sleep(self.napTime)
            
         
    #def runTasks(self):
    #    """runTasks: overload in subclasses to carry out needed tasks."""
    #    print("This is runTasks() in the Brain thread!!")
        
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
        while True:
            print ('\nwaiting to receive message')
            data, address = self.receiverSock.recvfrom(1024)
        
            print ('received %s bytes from %s' % (len(data), address))
            print (data)
    
            print ('sending acknowledgement to', address)
            self.receiverSock.sendto(bytes('ack','UTF-8'), address)



    def sendMessage(self, message):
        try:
            # Send data to the multicast group
            print ('sending "%s"' % message)
            sent = self.senderSock.sendto(bytes(message,'UTF-8'), self.player.multicast_group)
            
            # Look for responses from all recipients
            while True:
                print ('waiting to receive')
                try:
                    data, server = self.senderSock.recvfrom(16)
                except socket.timeout:
                    print ('timed out, no more responses')
                    break
                else:
                    print ('received "%s" from %s' % (data,server))

        finally:
            print ('closing socket')
            self.senderSock.close()   

    def run(self):
        print ("starting PostOffice..." + self.player.name)
        if self.player.receiver:
            self.listen()
        

class PlayerMapper(PlayerThread):
    def __init__(self, player):
        super(PlayerMapper, self).__init__(player)

    def run(self):
        print ("starting PlayerMapper..." + self.player.name)
#         sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         #Bind to the server address
#         sock.bind(self.player.server_address)
#         print(self.player.server_address)
#         #sock.bind(('', 10000))
#         #Tell the operating system to add the socket to the multicast group
#         #on all interfaces.
#         group = socket.inet_aton(self.player.multicast_group)
#         mreq = struct.pack('4sL', group, socket.INADDR_ANY)
#         sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
#         if self.player.receiver:
#             while True:
#                 print ("PlayerMapper is running..." + self.player.name)
#                 print ('\nwaiting to receive message')
#                 data, address = sock.recvfrom(1024)
#                  
#                 print ('received %s bytes from %s' % (len(data), address))
#                 print (data)
#              
#                 print ('sending acknowledgement to', address)
#                 sock.sendto(bytes('ack','UTF-8'), address)
#                 time.sleep(self.napTime*3)
#         else:
#             while True:
#                 print ("PlayerMapper is running..." + self.player.name)
#                 print ('\nActually every Player should be a receiver, brain thread is supposed to send...')
#                 time.sleep(self.napTime*3)
            
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



