import numpy as np
import matplotlib.pyplot as plt
from ecolab3.environment import Environment
from ecolab3.agents import Fish, Pathogen
from ecolab3 import run_ecolab, get_agent_counts, draw_animation

env = Environment(shape=[100,100],growrate=50,maxgrass=5,startgrass=1)

agents = []
#create agents (rabbits and foxes)
Nfish = 40

NPathogen = 20
for i in range(Nfish):
    f = Fish(position=env.get_random_location(),speed=5)
    agents.append(f)

for i in range(NPathogen):
    f = Pathogen(position=env.get_random_location(),speed=0)
    agents.append(f)

record = run_ecolab(env,agents,Niterations=1000)
# anim = draw_animation(fig,record[::5],5) #draw every 5th frame


counts = get_agent_counts(record)
plt.figure(figsize=[8,4])
plt.plot(counts[:,0],label='fish')
plt.legend()
plt.grid()
plt.xlabel('Iteration')
plt.ylabel('Count')
plt.show()