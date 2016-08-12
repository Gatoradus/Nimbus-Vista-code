'''
Created on Aug 11, 2016

@author: gregory
'''

from random import random, randint

# Assumptions: 
# * Sales of HCs drive subscriptions to online services. 
#   Buyers of HC have high probability of subscribing.
# * Purchasers of HCs have some positive influence on their friends to encourage
#  them to buy, so this is another variable

# * Costs: Advertising, Physical products, IT (website fees)
#     Labor (maintain website), Labor (improve and maintain HC software)
# Revenue: Product and subscriptions to website.

 # * Labor costs are primarily administrative and IT related. Manufacturing is
# contracted out with manufacturing labor being considered part of the cost
# per unit of devices sold.

# Subscripting conventions
# w: website related item
# d: device related item
# n: new
# e: existing
# tx: where 'x' is one of the above this means "total value",
# i.e. unit_value * number of units.

# Variables are thus: 
# COSTS     ---------------------
# A: advertising (effectiveness a function of time (product maturity)?)
# L_w: IT staff for website
# L_d: IT staff to improve and maintain device code.
# C_d: Cost per unit of devices

# REVENUES  ---------------------
# P_d: Price per unit of devices
# P_w: Price of a website subscription
# S_n: New Subscribers
# S_e: Existing Subscribers
# 

# Independent variables: (

# B_d: buyers of devices
# B_s: buyers of subscriptions. B_s has some dependency on B_d
#   as we would offer a free initial subscription
#   lasting for a period P for new device purchasers.
# B_df: number of "friends" of a B_d.
# B_di: coefficient of influence (multiply by B_df to get an idea of new buyers)
#
# Dependent variables 
# 
# Equations
# C_tx(B_d) = B_d * C_d
# B_s = B_dfB_d + 

n_leagues = 5
n_teams_per_league = 20
n_players_per_team = 30
n_friends_per_player = 20
n_family_per_player = 3
r_nonplayers_per_player = 30

p_subscribe_baseline = 0.001
p_subscribe_per_friend = 0.01
p_subscribe_per_family = p_subscribe_per_friend * 10

p_team_join_baseline = 0.01
p_team_join_per_leaguemate = 0.01
subscription_freebie_period = 12

n_subscriptions_nonfree = 0
n_subscriptions_free = 0
n_units_sold = 0

income = 0
costs = 0

c_d = 100
pr_d = 200
pr_s = 10

n_time_periods = 12

def calculate_combined_probability(p_baseline,p,n):
    p = 1-(1-p)**n
    p = 1-((1-p)*(1-p_baseline))
    return p
    

class Friendable(object):
    def __init__(self):
        self.friends=[]
        
    def add_friend(self,other,linkback=True):
        if not hasattr(self,"friends"):
            self.friends=[]
        
        self.friends.append(other)
        if linkback:
            other.add_friend(self,linkback=False)
            
    def add_family(self,other,linkback=True):
        if not hasattr(self,"family"):
            self.family=[]
        
        self.family.append(other)
         
        if linkback:
            other.add_family(self,linkback=False)
            
        
class League(object):
    def __init__(self):
        self.teams = []
        self.n_teams_subscribed = 0
    
    def add(self,team):        
        self.teams.append(team)
    
class Person(Friendable):
    def __init__(self,team=None):
        self.team = team
        self.n_family_with_device = 0
        self.n_friends_with_device = 0
        
    def pick_friends(self,population):        
        for i in range(0,n_friends_per_player):
            r = randint(0,len(population)-1)
            self.add_friend(population[r])
            
    def pick_family(self,population):        
        for i in range(0,n_family_per_player):
            r = randint(0,len(population)-1)
            self.add_family(population[r])
            
    def buy_device(self):
        global income, costs, n_units_sold, n_subscriptions_free
        self.subscription_freebie_period = subscription_freebie_period
        income += pr_d
        costs += c_d
        n_units_sold += 1
        n_subscriptions_free += 1
            
    def purchases_device(self):
        global p_subscribe_baseline,p_subscribe_per_friend
        global p_subscribe_per_family
        
        
        r = random()
        p = calculate_combined_probability(p_subscribe_baseline,p_subscribe_per_friend,self.n_friends_with_device)
        p = calculate_combined_probability(p,p_subscribe_per_family,self.n_family_with_device)
        if r < p:
            self.buy_device()
            return True
        return False
        
         

        
    

        
class Team(object):
    def __init__(self,league):
        self.league = league
        self.players = []
        self.subscribed = False
        
    def add(self,player):
        self.players.append(player)
        
    def subscribes(self):
        # team MIGHT subscribe
        global p_team_join_baseline, p_team_join_per_leaguemate, calculate_combined_probability
        r = random()
        p = calculate_combined_probability(p_team_join_baseline, p_team_join_per_leaguemate, team.league.n_teams_subscribed)
        
        if r < p:
            team.subscribed = True
            print("Team subscribed!{}".format(p))
            team.league.n_teams_subscribed+=1
            for player in team.players:
                player.buy_device()
    
def grow_subscribers(population):
    global income, costs, n_subscriptions_free, n_subscriptions_nonfree, n_units_sold
    global p_team_join_baseline, p_team_join_per_leaguemate
    for person in population:
        if person.team == None:
            if not hasattr(person,"subscription_freebie_period"):
                person.purchases_device()
                    
            else:
                if person.subscription_freebie_period > 0:                    
                    person.subscription_freebie_period-=1
                elif person.subscription_freebie_period == 0:
                    person.subscription_freebie_period = -1
                    n_subscriptions_nonfree += 1
                    n_subscriptions_free -= 1
                    
    for league in leagues:
        #print("testing team")
        # count the teams in each league that subscribed
        for team in league.teams:
            if not team.subscribed:
               
                team.subscribes()
               
            
        
                    
    income += n_subscriptions_nonfree * pr_s 

if __name__ == '__main__':
    n_population = n_leagues * n_teams_per_league * n_players_per_team * r_nonplayers_per_player
    print("hello:" + str(n_population))
    print(income)
    leagues=[]
    population = []
    players_on_teams=[]
    for i in range(0,n_leagues):
        league = League()
        for j in range(0,n_teams_per_league):
            team = Team(league)
            for k in range(0,n_players_per_team):
                player = Person(team)
                n_population-=1
                team.add(player)
                players_on_teams.append(player)
                population.append(player)
            league.add(team)
        leagues.append(league)

    for i in range(0,n_population):
        np = Person()
        population.append(np)

    print("hello:" + str(n_population))
    n_players_on_teams = n_leagues * n_teams_per_league * n_players_per_team
    print(str(len(population) - n_players_on_teams))
    
    for person in population:
        person.pick_friends(population)
        person.pick_family(population)
     
     
    print("Done picking friends and family.")   
    for tp in range(0,n_time_periods):
        
        c = 0
        
        grow_subscribers(population)
        profit = income - costs
        print("t={},i={},c={},p={}:sf={},sp={},u={}".format(tp,income, costs, profit, n_subscriptions_free,n_subscriptions_nonfree,n_units_sold))
        

        
    print("All done!")
        

        
    
