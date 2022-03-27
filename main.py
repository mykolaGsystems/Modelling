import matplotlib.pyplot as plt
from lib.environment import Environment
from lib.agents import Fish
from lib import run_ecolab, get_agent_counts

env = Environment(shape=[100,100])

agents = []
Nfish = 130
Nfish_infected = 20

for i in range(Nfish):
    f = Fish(position=env.get_random_location(),speed=2.5,infection_status=0)
    agents.append(f)

for i in range(Nfish_infected):
    f = Fish(position=env.get_random_location(),speed=2.5,infection_status=1)
    agents.append(f)
    
record = run_ecolab(env,agents,Niterations=400)

counts = get_agent_counts(record)
plt.figure(figsize=[8,4])
plt.plot(counts[:,0],label='fish')
plt.plot(counts[:,1],label='pathogen')
plt.legend()
plt.grid()
plt.xlabel('Iteration')
plt.ylabel('Count')
plt.show()