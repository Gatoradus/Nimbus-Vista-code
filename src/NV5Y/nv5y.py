'''
Created on Aug 11, 2016

@author: gregory
'''

from random import random, randint
from matplotlib import pyplot as plt
import numpy as np
import math

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

class World(object):
    def __init__(self,d=dict()):
        self.__dict__ = d
        self.c_website_bandwidth_per_Mb = self.c_website_bandwidth_per_Gb/1000
        self.n_population = self.n_leagues * self.n_teams_per_league * self.n_players_per_team * self.n_nonplayers_per_player
        self.c_website_hosting_per_subscription = self.c_website_bandwidth_per_Mb * self.n_website_bandwidth_Mb_per_subscription
             
        self.c_website_labor_per_subscription = 1/self.n_subscriptions_per_website_staffer * self.c_salary_per_website_staffer
        self.c_overhead = self.c_labor_overhead + self.c_physical_plant_overhead
        
        print("hello:" + str(self.n_population))
        print(self.income)
        self.leagues=[]
        self.population = []
        self.players_on_teams=[]
        for i in range(0,self.n_leagues):
            league = League(self)
            for j in range(0,self.n_teams_per_league):
                team = Team(self,league)
                for k in range(0,self.n_players_per_team):
                    player = Person(self,team)
                    self.n_population-=1
                    team.add(player)
                    self.players_on_teams.append(player)
                    self.population.append(player)
                league.add(team)
            self.leagues.append(league)
    
        for i in range(0,self.n_population):
            np = Person(self)
            self.population.append(np)
    
        print("hello:" + str(self.n_population))
        self.n_players_on_teams = self.n_leagues * self.n_teams_per_league * self.n_players_per_team
        print(str(len(self.population) - self.n_players_on_teams))
        
        for person in self.population:
            person.pick_friends()
            person.pick_family()
    
    @staticmethod
    def calculate_combined_probability(p_baseline,p,n):
        p = 1-(1-p)**n
        p = 1-((1-p)*(1-p_baseline))
        #return 0.005
        return p


    def run(self):
        self.a_income = []
        self.a_costs = []
        self.a_profit = []
        self.a_n_subscriptions_free = []
        self.a_n_subscriptions_nonfree = []
        self.a_n_units_sold = []
        self.t = 0
        
        self.tps = range(0,self.n_time_periods)
        for self.t in self.tps:
            
            self.iterate()
            self.profit = self.income - self.costs
            print("t={},i={},c={},p={}:sf={},sp={},u={}".format(self.t,self.income, self.costs, self.profit, self.n_subscriptions_free,self.n_subscriptions_nonfree,self.n_units_sold))
            
          
            self.a_income.append(self.income)
            self.a_costs.append(self.costs)
            self.a_profit.append(self.profit)
            self.a_n_subscriptions_free.append(self.n_subscriptions_free)
            self.a_n_subscriptions_nonfree.append(self.n_subscriptions_nonfree)
            self.a_n_units_sold.append(self.n_units_sold)
            
    def iterate(self):
        #global income, costs, self.n_subscriptions_free, self.n_subscriptions_nonfree, self.n_units_sold
        #global p_team_join_baseline, p_team_join_per_leaguemate
        for person in self.population:
            
            if not hasattr(person,"subscription_freebie_period"):
                person.purchases_device()
                    
            else:
                if person.subscription_freebie_period > 0:                    
                    person.subscription_freebie_period-=1
                elif person.subscription_freebie_period == 0:
                    person.subscription_freebie_period = -1
                    self.n_subscriptions_nonfree += 1
                    self.n_subscriptions_free -= 1
                    
        for league in self.leagues:
            #print("testing team")
            # count the teams in each league that subscribed
            for team in league.teams:
                #print("testing team")
                if not team.subscribed:
                   
                    team.subscribes()
            
        self.c_website = self.calculate_cost_website()
        self.c_advertising = self.calculate_cost_advertising()
        self.c_device_software_maintenance = self.calculate_cost_device_software_maintenance()
        self.income += self.n_subscriptions_nonfree * self.pr_s 
        self.costs += self.c_website + self.c_device_software_maintenance + self.c_labor_overhead + self.c_physical_plant_overhead 
        self.costs += self.c_advertising

    def calculate_cost_website(self):
        total_subscribers = self.n_subscriptions_nonfree + self.n_subscriptions_free
        cost = self.c_website_hosting_per_subscription * total_subscribers + self.c_website_labor_per_subscription *  math.log(total_subscribers+1)
        return cost
    
    def calculate_cost_device_software_maintenance(self):
        # assumption is that software products and maintencance scale
        # with the absolute size of the business (using revenue as a proxy)
        cost = self.c_device_software_maintenance_coefficient * self.income
        return cost
    
    def calculate_cost_advertising(self):
        ## FIXME ##
        if self.t < 12:
             return self.c_initial_ad_campaign 
        else:
             return 0   
        
         

    

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
    def __init__(self,world):
        self.w = world
        self.teams = []
        self.n_teams_subscribed = 0
    
    def add(self,team):        
        self.teams.append(team)
    
class Person(Friendable):
    def __init__(self,world,team=None):
        self.w = world
        self.team = team
        self.n_family_with_device = 0
        self.n_friends_with_device = 0
        
    def pick_friends(self):        
        for i in range(0,self.w.n_friends_per_player):
            r = randint(0,len(self.w.population)-1)
            self.add_friend(self.w.population[r])
            
    def pick_family(self):        
        for i in range(0,self.w.n_family_per_player):
            r = randint(0,len(self.w.population)-1)
            self.add_family(self.w.population[r])
            
    def buy_device(self):
        #global income, costs, n_units_sold, n_subscriptions_free
        self.subscription_freebie_period = self.w.subscription_freebie_period
        self.w.income += self.w.pr_d
        self.w.costs += self.w.c_d
        self.w.n_units_sold += 1
        self.w.n_subscriptions_free += 1
            
    def purchases_device(self):
        #global p_subscribe_baseline,p_subscribe_per_friend
        #global p_subscribe_per_family
        
        
        r = random()
        p = World.calculate_combined_probability(self.w.p_subscribe_baseline,self.w.p_subscribe_per_friend,self.n_friends_with_device)
        p = World.calculate_combined_probability(p,self.w.p_subscribe_per_family,self.n_family_with_device)
        if r < p:
            self.buy_device()
            return True
        return False

        
class Team(object):
    def __init__(self,world,league):
        self.w = world
        self.league = league
        self.players = []
        self.subscribed = False
        
    def add(self,player):
        self.players.append(player)
        
    def subscribes(self):
        # team MIGHT subscribe
        #global p_team_join_baseline, p_team_join_per_leaguemate, calculate_combined_probability
        r = random()
        p = World.calculate_combined_probability(self.w.p_team_join_baseline, self.w.p_team_join_per_leaguemate, self.league.n_teams_subscribed)
        #print("{},{}".format(p,r))
        if r < p:
            self.subscribed = True
            print("Team subscribed!{},{}".format(p,r))
            self.league.n_teams_subscribed+=1
            print("n_teams_subscribed {}".format(self.league.n_teams_subscribed))
            for player in self.players:
                player.buy_device()
    


if __name__ == '__main__':

    world_dict = {
        "c_initial_ad_campaign" : 30000,
        "c_device_software_maintenance_coefficient" : 20000/1000000,
        "c_labor_overhead" : 10000, 
        "c_physical_plant_overhead" : 2000,
        "c_website_bandwidth_per_Gb" : 20,
        "n_website_bandwidth_Mb_per_subscription" : 10,
             
        "n_subscriptions_per_website_staffer" : 2000,
        "c_salary_per_website_staffer" : 50000,
        
                  
                  
        "n_leagues" : 5,
        "n_teams_per_league" : 20,
        "n_players_per_team" : 30,
        "n_friends_per_player" : 20,
        "n_family_per_player" : 3,
        "n_nonplayers_per_player" : 30,
        
        "p_subscribe_baseline" : 0.001,
        "p_subscribe_per_friend" : 0.01,
        "p_subscribe_per_family" : 0.1,
        
        "p_team_join_baseline" : 0.01,
        #"p_team_join_baseline" : 0.0,
        "p_team_join_per_leaguemate" : 0.1,
        #"p_team_join_per_leaguemate" : 0,
        "subscription_freebie_period" : 12,
        
        "n_subscriptions_nonfree" : 0,
        "n_subscriptions_free" : 0,
        "n_units_sold" : 0,
        
        "income" : 0,
        "costs" : 0,
        
        "c_d" : 100,
        "pr_d" : 200,
        "pr_s" : 10,
        
        "n_time_periods" : 60
    }
     
    w = World(world_dict)
    w.run()
       
    
        
    print("All done!")
        

    x = np.linspace(0, w.n_time_periods)
    
    with plt.style.context('fivethirtyeight'):
        plt.plot(w.tps, w.a_income)
        plt.plot(w.tps, w.a_costs)
        plt.plot(w.tps, w.a_profit)
        plt.plot(w.tps, w.a_n_units_sold)
    
    
    plt.show()        
    
