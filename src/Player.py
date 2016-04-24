
class Player(object):
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.height = 72
        self.weight = 200

    def run(self):
        print ("starting Player thread...")
        

class Bot(Player):
    def __init__(self):
        pass

    def run(self):
        print ("starting Bot thread...")

class Brain(Player):
    def __init__(self):
        pass

    def run(self):
        print ("starting Brain thread...")
        
class PostOffice(Player):
    def __init__(self):
        pass

    def run(self):
        print ("starting PostOffice thread...")

class PlayerMapper(Player):
    def __init__(self):
        pass

    def run(self):
        print ("starting PlayerMapper thread...")

class FirstAide(Player):
    def __init__(self):
        pass

    def run(self):
        print ("starting FirstAide thread...")

class Sensor(Player):
    def __init__(self):
        pass

    def run(self):
        print ("starting Sensor thread...")




        
