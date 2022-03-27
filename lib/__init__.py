from pickle import TRUE
from ssl import ALERT_DESCRIPTION_PROTOCOL_VERSION
import numpy as np
from simplejson import OrderedDict
from sniffio import AsyncLibraryNotFoundError
from lib.agents import Pathogen, Fish
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

def run_ecolab(env,agents,Niterations=500,earlystop=True):
    """
    Run ecolab, this applies the rules to the agents and the environment. It records
    the grass array and the locations (and type) of agents in a list it returns.
    
    Arguments:
    - env = an Environment object
    - agents = a list of agents (all inherited from Agent)
    - Niterations = number of iterations to run (default = 1000)
    - earlystop = if true (default), will stop the simulation early if no agents left.
    """
    start = time.time() # For measuring efficieny
    record = []
    dead_fish = 0 #Used to store the number of fish that have died, as they are deleted
    
    #Variables used to calculate the attack rate
    exposed_fish = 0 
    infected_fish = 0
    for it in range(Niterations):
        if (it+1)%100==0: print("%5d" % (it+1), end="\r") #progress message
        
        # 1. Kill fish and pathogens
        # 2. Update death statistics
        # 3. Progress infections
        # 4. Move the fish
        # 5. Check if fish infected
        # 6. append any pathogen that has been shred from a fish

        alive_fish = []
        for a in agents:
            if type(a) == Fish:
                alive_fish.append(a)
                    
        agents = [a for a in agents if not a.die()]
        
        d_fish = []
        for b in agents:
            if type(b) == Fish:
                d_fish.append(b)
                
        dead_fish+=len(alive_fish) - len(d_fish) #Calculate the difference in the arrays before and after death


        #for each agent, apply rules (progress infection, move, check infected, shred pathogens)
        for agent in agents:
            a = None
            if type(agent) == Fish:
                agent.progress_infection()       
                a = agent.move(env)
            agent.check_infected(agents)
            if a is not None:
                agents.append(a)


        #record the agent locations (and types) for later plotting & analysis
        record.append({'agents':np.array([a.summary_vector() for a in agents])})

        #stop early if we run out of fish
        if earlystop:
            if len(agents)==0: break

    #calculating the attack rate of the virus based on agent and environment parameters
    for b in agents:
      if type(b) == Fish:
        if b.infected:
            infected_fish +=1
        if b.exposed:
            exposed_fish += 1
    exposed_fish += dead_fish
    infected_fish += dead_fish
    print("Exposed Fish: {}; Infected Fish: {}".format(exposed_fish, infected_fish))
    end = time.time()
    total = end - start
    print("\nRuntime took " + str(total) + " seconds") #Used for computational Effeciency metrics
    return record

def draw_animation(fig,record,fps=20,saveto=None):
    """
    Draw the animation for the content of record. This doesn't use the draw
    functions of the classes.
    - fig figure to draw to
    - record = the data to draw
    - fps = frames per second
    - saveto = where to save it to
    """
    #rc('animation', html='html5')
    if len(record)==0: return None

    im = plt.imshow(np.zeros(10000).reshape((100,100)))
    ax = plt.gca()

    foxesplot = ax.plot(np.zeros(1),np.zeros(1),'bo',markersize=10)
    rabbitsplot = ax.plot(np.zeros(1),np.zeros(1),'yx',markersize=10,mew=3)

    def animate_func(i):
            im.set_array(np.zeros(10000).reshape(100,100))
            ags = record[i]['agents']
            if len(ags)==0:
                rabbitsplot[0].set_data([],[])
                foxesplot[0].set_data([],[])
                return
            coords = ags[ags[:,-1].astype(bool),0:2]
            rabbitsplot[0].set_data(coords[:,1],coords[:,0])
            coords = ags[~ags[:,-1].astype(bool),0:2]
            foxesplot[0].set_data(coords[:,1],coords[:,0])

    anim = animation.FuncAnimation(
                                   fig, 
                                   animate_func, 
                                   frames = len(record),
                                   interval = 1000 / fps, repeat=False # in ms
                                   )
    if saveto is not None: anim.save(saveto, fps=fps, extra_args=['-vcodec', 'libx264']) 
    from IPython.display import HTML
    return HTML(anim.to_jshtml())

def get_agent_counts(record):
    """
    Returns the number of foxes, rabbits and amount of grass in a N x 3 numpy array
    the three columns are (Foxes, Rabbits, Grass).
    """
    counts = []
    for r in record:
        ags = r['agents']
        if len(ags)==0:
            nF = 0
            nR = 0
        else:
            nF = np.sum(ags[:,-1]==0)
            nR = np.sum(ags[:,-1]==1)
        counts.append([nF,nR])
    counts = np.array(counts)
    return counts
