import numpy as np
import matplotlib.pyplot as plt
import random

#Helper functions to calculate distances
def calcdistsqr(v):
    """Get euclidean distance^2 of v"""
    return np.sum(v**2)

def calcdist(v):
    """Get euclidean distance of v"""
    return np.sqrt(np.sum(v**2))


class Agent:
    """
    Base class for all types of agent
    """
    def __init__(self,position,speed):
        """
        food = how much food the agent has 'inside' (0=empty, 1=full)
        position = x,y position of the agent
        speed = how fast it can move (tiles/iteration)
        """

        self.position = position
        self.speed = speed
       
    def move(self,env):
        pass #to implement by child class
    
    def trymove(self,newposition,env):
        if env.check_position(newposition):
            self.position = newposition
        #ensures it's in the environment and rounds to nearest cell
        #env.fix_position(self.position)
    
    def summary_vector(self):
        """
        Returns a list of the location (x,y) and a 0=pathogen, 1=fish, e.g.
        [3,4,1] means a pathogen at (3,4).
        """
        return [self.position[0],self.position[1],type(self)!=Fish]
    
    
class Fish(Agent):
    
    infection_status = 0 #0 - Susceptible 1 - infected 2 - temporarilly immune
    infection_timesteps = 0 #How many timesteps the infection has left to finish
    infection_timesteps_initial = 0 # How many timesteps the infection will last
    infection_death_timesteps = 0 #0 unless they will die on a set timestep of infection
    infection_radius = 5 #Constant
    immune_timesteps = 0 # Timestemps the fish will not be infected
    shredding_rate = 0.75 # Rate at which the fish will produce pathogen population
    mean_infection_timesteps = 20 # Mean fish infection timestemps 
    
    exposed = False # Booleans to meassure attack rate at the end
    infected = False



    def __init__(self,position,speed=2.5,infection_status=0):
        super().__init__(position,speed)
        self.infection_status = infection_status #Infection status passed into the constructor
        if infection_status == 1:
            # If it's infected, calculate for how many days, and if it should die
            # Define a new pathogen (as we need information from the pathogen to calculate infecion + death chance)
            # This pathogen is not saved or used anywhere else besides this function
            self.set_infection_length(Pathogen(position))
        
    def move(self,env):
        """
        Fish just move randomly
        Fish leaves pathogen in it's old position if it is infected, and shredding rate probability succeeds
        """
        new_agent = None # Code for handling empty object in __init__.py
        if self.infection_status == 1:
            shed_prob = random.randint(0,100)
            if (self.shredding_rate * 100) < shed_prob:
                new_agent = Pathogen(self.position)

        d = np.random.rand()*2*np.pi #pick a random direction
        delta = np.round(np.array([np.cos(d),np.sin(d)])* self.speed)
        self.trymove(self.position + delta,env) #Default 
        return new_agent

    def progress_infection(self): 
        """
        Progresses the infection and immune timestemps of the fish 
        """
        if self.infection_timesteps > 0: #Progress infection by one timestep
            self.infection_timesteps -= 1
            
        elif self.infection_timesteps == 0 and self.infection_status == 1: #Enter immunity if infection has finished
            self.infection_status = 2 #Becomes immune
            self.immune_timesteps = 10 #Start immmune timestep timer
            
        if self.infection_status == 2: #Immune timestep counter
            if self.immune_timesteps > 0 :
                self.immune_timesteps -= 1
            else:
                self.infection_status = 0

            
    def check_infected(self, agents):
        """
        Detect if pathogen is nearby. Carry out calculations if the fish will be infected.
        """
        pathogen = self.get_nearby_pathogen(self.position, agents) #Returns the closest pathogen, if no pathogen inside infection radius it returns None
        if pathogen is not None:
            self.exposed = True # As it has been exposed, keep this set to true
            if self.infection_status == 0: #Only want to execute this code if not infected, if fish is immune or infected already we can skip this
                proximity = self.position - pathogen.position # Positive or negative has no relevance
                proximity = calcdist(proximity) #Inbuilt function to ecolab
                infection_chance = (1/(proximity+1)) * pathogen.get_infection_rate()
                if(random.uniform(0, 1) <= infection_chance):
                    self.set_infection_length(pathogen) # General infection calculation function

    def set_infection_length(self, pathogen):
        """
        Uniform Distribution for infection death. 
        Normal Distribution for infection period, s.d 5 (constant)
        """
        #For how many timestemps the fish will be infected
        self.infected = True
        self.infection_status = 1
        self.infection_timesteps = round(np.random.normal(self.mean_infection_timesteps, 5)) 
        # print(self.infection_timesteps)
        if(random.uniform(0, 1) <= pathogen.get_mortality_rate()):
            #Fish timestemps untill it will die
            # self.infection_death_timesteps = round(random.uniform(0, 1) * self.infection_timesteps)
            const = round(random.uniform(0,1)*self.infection_timesteps)
            if const > self.infection_timesteps:
                self.infection_death_timesteps = self.infection_timesteps
            elif const == 0:
                self.infection_death_timesteps = 1
            else:
                self.infection_death_timesteps = const
            # if self.infection_death_timesteps > self.infection_timesteps:  
            #print("Infected Timestamps:",self.infection_timesteps,"Depth Timestamps:",self.infection_death_timesteps)

    def get_nearby_pathogen(self,position,agents):
        """
        Find nearest pathogen to the fish. If it's within the infection radius return the pathogen, else return None
        """
        sqrdistances = np.sum((np.array([a.position if (type(a)==Pathogen) and (not a.die()) else np.array([-np.inf,-np.inf]) for a in agents])-position)**2,1)
        idx = np.argmin(sqrdistances)
        if sqrdistances[idx]<self.infection_radius**2:
            return agents[idx] # Only returns if pathogen inside infection radius
        else:
            return None
                     
    def die(self):
        """"
        Decision making wheather the fish will die when death timestemps will be the same as infection timestemps
        """
        if self.infection_death_timesteps > 0 and self.infection_death_timesteps == self.infection_timesteps:
            return True
        else:
            return False
        
    
class Pathogen(Agent):
    
    #Parameters of pathogen
    
    infection_rate = 0.4 # Rate at which fish is infected
    mortality_rate = 0.35 # Rate at which infected fish will die
    age = 0 # Never changes, used to note when the pathogen has died
    lifespan = 10

    def __init__(self,position,speed=0):
        super().__init__(position,speed)
    
    #Getters
    def get_infection_rate(self):
        return self.infection_rate

    def get_mortality_rate(self):
        return self.mortality_rate

    def die(self):
        if self.age>=self.lifespan: 
            return True
        else:
            return False
    
    def check_infected(self, agents):
        self.lifespan -= 1 # Countdown timer on lifespan of pathogen