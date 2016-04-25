
class Player(object):
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.height = 72
        self.weight = 200

    def start(self):
        print ("starting Player...")

class PlayerThread(object):
    def __init__(self, player):
        self.player = player

class Brain(PlayerThread):
    def __init__(self, player):
        super().__init__()

    def run(self):
        print ("starting Brain PlayerThread...")
        
class PostOffice(PlayerThread):
    def __init__(self):
        super().__init__()

    def run(self):
        print ("starting PostOffice PlayerThread...")

class PlayerMapper(PlayerThread):
    def __init__(self):
        super().__init__()

    def run(self):
        print ("starting PlayerMapper PlayerThread...")

class FirstAide(PlayerThread):
    def __init__(self):
        super().__init__()

    def run(self):
        print ("starting FirstAide PlayerThread...")

class Sensor(PlayerThread):
    def __init__(self):
        super().__init__()

    def run(self):
        print ("starting Sensor PlayerThread...")



class Bot(Player):
    def __init__(self):
        super().__init__()

    def start(self):
        print ("starting Bot ...")
        
