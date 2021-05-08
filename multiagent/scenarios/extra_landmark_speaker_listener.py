import numpy as np
from multiagent.core import World, Agent, Landmark
from multiagent.scenario import BaseScenario

class Scenario(BaseScenario):
    def make_world(self):
        world = World()
        # set any world properties first
        world.dim_c = 3
        num_landmarks = 4
        world.collaborative = True
        
        # this will be the furthest any agent can move in any direction
        world.size = 5
        
        # add agents
        world.agents = [Agent() for i in range(2)]
        for i, agent in enumerate(world.agents):
            agent.name = 'agent %d' % i
            agent.collide = False
            agent.size = 0.075 # I think this is irrelevant?
        # speaker
        world.agents[0].movable = False
        # listener (discrete)
        world.agents[1].silent = True
        world.agents[1].hopper = True
        # add landmarks
        world.landmarks = [Landmark() for i in range(num_landmarks)]
        for i, landmark in enumerate(world.landmarks):
            landmark.name = 'landmark %d' % i
            landmark.collide = False
            landmark.movable = False
            landmark.size = 0.04 # I think this is irrelevant?
        # make initial conditions
        self.reset_world(world)
        return world

    def reset_world(self, world):
        # assign goals to agents
        for agent in world.agents:
            agent.goal_a = None
            agent.goal_b = None
        # want listener to go to the goal landmark
        world.agents[0].goal_a = world.agents[1]
        world.agents[0].goal_b = np.random.choice(world.landmarks)
        # random properties for agents
        for i, agent in enumerate(world.agents):
            agent.color = np.array([0.25,0.25,0.25])               
        # random properties for landmarks
        world.landmarks[0].color = np.array([0.65,0.15,0.15]) # red
        world.landmarks[1].color = np.array([0.15,0.65,0.15]) # green
        world.landmarks[2].color = np.array([0.15,0.15,0.65]) # blue
        world.landmarks[3].color = np.array([0.15, 0.65, 0.65]) # cyan
        # world.landmarks[4].color = np.array([0.65, 0.15, 0.65]) # magenta
        # world.landmarks[5].color = np.array([0.65, 0.65, 0.15]) # yellow
        # special colors for goals
        world.agents[0].goal_a.color = world.agents[0].goal_b.color + np.array([0.45, 0.45, 0.45])
        # set random initial states
        # setting to an int this time
        for agent in world.agents:
            agent.state.p_pos = np.random.randint(-world.size,+world.size, world.dim_p).astype(float)
            agent.state.p_vel = np.zeros(world.dim_p)
            agent.state.c = np.zeros(world.dim_c)
        for i, landmark in enumerate(world.landmarks):
            landmark.state.p_pos = np.random.randint(-world.size,+world.size, world.dim_p).astype(float)
            landmark.state.p_vel = np.zeros(world.dim_p)

    def benchmark_data(self, agent, world):
        # returns data for benchmarking purposes
        return self.reward(agent, reward)

    def reward(self, agent, world):
        # squared distance from listener to landmark
        a = world.agents[0]
        dist2 = np.sum(np.square(a.goal_a.state.p_pos - a.goal_b.state.p_pos))
        return -dist2

    def observation(self, agent, world):
        # goal color
        goal_color = np.zeros(world.dim_color)
        if agent.goal_b is not None:
            goal_color = agent.goal_b.color

        # get positions of all entities in this agent's reference frame
        # changing to get actual positions, not just distances away
        entity_pos = []
        for entity in world.landmarks:
            entity_pos.append(entity.state.p_pos) #  - agent.state.p_pos)

        # communication of all other agents
        comm = []
        for other in world.agents:
            if other is agent or (other.state.c is None): continue
            comm.append(other.state.c)
        
        # speaker
        if not agent.movable:
            return np.concatenate([goal_color])
        # listener
        if agent.silent:
            return np.concatenate([agent.state.p_pos] + entity_pos + comm)
