'''
Created on Aug 11, 2016

@author: gregory
'''

from random import random, randint
from matplotlib import pyplot as plt
import numpy as np
import math

# The model world consists of leagues, leagues consist of teams, teams consist of people.
# Spatial factors (i.e. physical proximity) are not modeled at this time.

# Premises of the model: 
# ======================================================================
# * People can be members of only one team.
# * Teams can be members of only one league.
# * There are many non-players for each player in the population.
# * When a team buys devices it buys one for each player.
# * Buyers of HC get a subscription which is free for a while.
# * Players have lists of friends and a smaller list of family. They have some influence
#     on both to encourage them to buy though more influence on their family.
# * A team becomes more likely to buy according to the number of its fellow teams
#     in its league that have done so.
# * Public awareness of product starts at 0 and increase with each ad campaign.
# * Likelihood of purchase for all possible buyers increases during ad campaigns.
# * Salaries and other expenses rise with size of website
# * There is little physical presence of the company (i.e. no large plants or offices).
# * Cost of factories, factory labor, etc is simply rolled into cost of devices.
# * Company does not own or desire to own device factories themselves at this time. 
# * Website grows in size with subscriber base.
# * Software maintenance cost (i.e development of new HC software and internal use software) 
#    is a function of the scale of the revenue (not profit). The idea here is that revenue
#    rather than profit reflects the sheer SCALE of the business. A good example would be
#    airlines. Most have enormous revenue and are giant companies but many are not even
#    profitable.


class World(object):
    def __init__(self,d=dict()):
        self.__dict__ = d
        self.c_website_bandwidth_per_Mb = self.c_website_bandwidth_per_Gb/1000
        self.n_population = self.n_leagues * self.n_teams_per_league * self.n_players_per_team * self.n_nonplayers_per_player
        self.c_website_hosting_per_subscription = self.c_website_bandwidth_per_Mb * self.n_website_bandwidth_Mb_per_subscription
             
        self.c_website_labor_per_subscription = 1/self.n_subscriptions_per_website_staffer * self.c_salary_per_website_staffer
        self.c_overhead = self.c_labor_overhead + self.c_physical_plant_overhead
        self.current_ad_blitz_time_left = self.n_ad_blitz_duration
        
        self.p_originals = [
            self.p_subscribe_baseline,
            self.p_subscribe_per_friend,
            self.p_subscribe_per_family,
            
            self.p_team_join_baseline,
            #"p_team_join_baseline" : 0.0,
            self.p_team_join_per_leaguemate
        ]
        
        
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
    
    
    def calculate_combined_probability(self, p_baseline, p, n, personally_aware=False):
        p = 1-(1-p)**n
        p = 1-((1-p)*(1-p_baseline))
        #return 0.005
        if personally_aware == False:
            return p * self.f_public_awareness_factor
        else:
            return p * max(self.f_public_awareness_factor,1)


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
        cost = self.f_device_software_maintenance_coefficient * self.income
        return cost
    
    def calculate_cost_advertising(self):
        ## FIXME ##
        
        self.f_public_awareness_factor = self.f_public_awareness_factor * self.f_public_awareness_decay_coefficient
        r = random()
        
        if r < self.p_ad_blitz:
            self.current_ad_blitz_time_left = self.n_ad_blitz_duration
            print("AD BLITZ")
            [   
            self.p_subscribe_baseline,
            self.p_subscribe_per_friend,
            self.p_subscribe_per_family,
            
            self.p_team_join_baseline,
            #"p_team_join_baseline" : 0.0,
            self.p_team_join_per_leaguemate
            ] = [x*self.p_ad_boost_factor for x in self.p_originals]
        
            
        if self.current_ad_blitz_time_left > 0:
            self.f_public_awareness_factor += self.f_public_awareness_factor_ad_boost
            self.current_ad_blitz_time_left-=1
            print("Ad blitz in effect")
            return self.c_initial_ad_campaign 
        
        else:
            [   
            self.p_subscribe_baseline,
            self.p_subscribe_per_friend,
            self.p_subscribe_per_family,
            
            self.p_team_join_baseline,
            #"p_team_join_baseline" : 0.0,
            self.p_team_join_per_leaguemate
            ] = self.p_originals  
        
             
        
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
        if self.n_family_with_device + self.n_friends_with_device > 0:           
            p = self.w.calculate_combined_probability(self.w.p_subscribe_baseline,self.w.p_subscribe_per_friend,self.n_friends_with_device, personally_aware=True)
            p = self.w.calculate_combined_probability(p,self.w.p_subscribe_per_family,self.n_family_with_device, personally_aware=True)
        else:
            p = self.w.calculate_combined_probability(self.w.p_subscribe_baseline,self.w.p_subscribe_per_friend,self.n_friends_with_device)
            p = self.w.calculate_combined_probability(p,self.w.p_subscribe_per_family,self.n_family_with_device)
        
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
        if self.league.n_teams_subscribed > 0:
            p = self.w.calculate_combined_probability(self.w.p_team_join_baseline, self.w.p_team_join_per_leaguemate, self.league.n_teams_subscribed, personally_aware=True)
        else:
            p = self.w.calculate_combined_probability(self.w.p_team_join_baseline, self.w.p_team_join_per_leaguemate, self.league.n_teams_subscribed)
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
        "f_public_awareness_factor" : 0,
        "f_public_awareness_factor_ad_boost" : 0.1,
        "f_device_software_maintenance_coefficient" : 20000/1000000,
        "f_public_awareness_decay_coefficient" : 0.99, # half-life of about 5 years.
        "c_labor_overhead" : 10000, 
        "c_physical_plant_overhead" : 2000,
        "c_website_bandwidth_per_Gb" : 20,
        "n_website_bandwidth_Mb_per_subscription" : 10,
        "n_ad_blitz_duration" : 5,
             
        "n_subscriptions_per_website_staffer" : 2000,
        "c_salary_per_website_staffer" : 50000,
        
                  
                  
        "n_leagues" : 5,
        "n_teams_per_league" : 20,
        "n_players_per_team" : 30,
        "n_friends_per_player" : 20,
        "n_family_per_player" : 3,
        "n_nonplayers_per_player" : 600,
        
        "p_ad_blitz" : 0.08,
        "p_ad_boost_factor" : 130,
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
    
