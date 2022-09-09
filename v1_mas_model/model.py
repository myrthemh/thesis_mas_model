import math
from enum import Enum
import networkx as nx
import config

from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import NetworkGrid
from .data_analysis import initialize_SIR_model
import pandas as pd
import os
import pickle

class State(Enum):
    SUSCEPTIBLE = 0
    INFECTED = 1
    RESISTANT = 2


def number_state(model, state):
    return sum(1 for a in model.grid.get_all_cell_contents() if a.state is state)


def number_infected(model):
    return number_state(model, State.INFECTED)


def number_susceptible(model):
    return number_state(model, State.SUSCEPTIBLE)


def number_resistant(model):
    return number_state(model, State.RESISTANT)


def obtain_variable_from_data(file=f'/Users/myrthehemker/Desktop/MasterThesis/Programming/thesis_mas_model/v1_mas_model/data/dict_variables.pkl'):

    if os.path.isfile(file):
        unpickleFile = open(file, 'rb')
        variables = pickle.load(unpickleFile, encoding='latin1')
        #return 0.001, 0.001, variables["num_nodes"], int(variables["avg_node_degree"]), variables["threshold_start"]
        return variables["infection_rate"], variables["recovery_rate"], variables["num_nodes"], int(variables["avg_node_degree"]), variables["threshold_start"]
        #return 0.0018937002903673778, 0.0005786306442789209, variables["num_nodes"], int(variables["avg_node_degree"]), variables["threshold_start"]+10
    else:
        df_select = pd.read_csv(f"{config.path_final}df_selected.csv")
        df_network = pd.read_csv(f"{config.path_final}networks_all_users.csv")

        return initialize_SIR_model(df=df_select, df_network=df_network)


infection_rate, recovery_rate, num_nodes, avg_node_degree, initial_outbreak_size = obtain_variable_from_data()

class SocialNetwork(Model):
    """A information diffusion model with some number of agents"""

    def __init__(
            self,
            num_nodes=num_nodes,
            avg_node_degree = avg_node_degree,
            initial_outbreak_size=initial_outbreak_size,
            recovery_rate=recovery_rate,
            infection_rate=infection_rate,

    ):

        infection_rate, recovery_rate, num_nodes, x, initial_outbreak_size = obtain_variable_from_data()
        infection_rate = infection_rate*1.4
        recovery_rate = recovery_rate*1.4
        self.df_results_sir = pd.DataFrame(columns=['number_susceptible', 'number_infected', 'number_resistant'])
        print("infection_rate", infection_rate, "recovery_rate", recovery_rate, "num_nodes:", num_nodes, "avg_node_degree:", avg_node_degree, initial_outbreak_size)
        self.recovery_rate = recovery_rate
        self.infection_rate = infection_rate
        self.num_nodes = num_nodes
        self.avg_node_degree = avg_node_degree

        prob = avg_node_degree / self.num_nodes
        self.G = nx.erdos_renyi_graph(n=self.num_nodes, p=prob)
        self.grid = NetworkGrid(self.G)
        self.schedule = RandomActivation(self)
        self.initial_outbreak_size = (
            initial_outbreak_size if initial_outbreak_size <= num_nodes else num_nodes
        )

        self.datacollector = DataCollector(
            {
                "Infected": number_infected,
                "Susceptible": number_susceptible,
                "Resistant": number_resistant,

            }
        )

        # Create agents
        for i, node in enumerate(self.G.nodes()):
            a = CitizenAgent(
                i,
                self,
                State.SUSCEPTIBLE,
                self.infection_rate,
                self.recovery_rate,

            )
            self.schedule.add(a)
            # Add the agent to the node
            self.grid.place_agent(a, node)

        # Infect some nodes
        infected_nodes = self.random.sample(self.G.nodes(), self.initial_outbreak_size)
        for a in self.grid.get_cell_list_contents(infected_nodes):
            a.state = State.INFECTED

        self.running = True
        self.datacollector.collect(self)

    def resistant_susceptible_ratio(self):
        try:
            return number_state(self, State.RESISTANT) / number_state(
                self, State.SUSCEPTIBLE
            )
        except ZeroDivisionError:
            return math.inf

    def step(self):
        self.schedule.step()


        # collect data
        self.datacollector.collect(self)
        self.df_results_sir.loc[len(self.df_results_sir.index)] = [str(number_susceptible(self)),
                                                                   str(number_infected(self)),
                                                                   str(number_resistant(self))]

        self.df_results_sir.to_csv(
            f"{os.getcwd()}/v1_mas_model/results/SIR/version 1- Avg degree{self.avg_node_degree} inf_ra{self.infection_rate} rec_ra{self.recovery_rate} .csv")

    def run_model(self, n):
        for i in range(n):
            self.step()

    def run_until_stable(self):
        print(f"Number of agents: {self.schedule.get_agent_count()}")
        while not self.check_stop_case():
            # if self.changes_per_step:
            #     last_step = max(self.changes_per_step.keys())
            #     last_step = 0 if last_step - 1 < 0 else last_step - 1
            # print(f"Current step: {self.schedule.steps} \n Number of changes in step {last_step}: {self.changes_per_step[last_step]}")
            self.step()
        self.store_result()


class CitizenAgent(Agent):
    def __init__(
            self,
            unique_id,
            model,
            initial_state,
            recovery_rate,
            infection_rate

    ):
        super().__init__(unique_id, model)

        self.state = initial_state

        self.model = model

        self.infection_rate = infection_rate
        self.recovery_rate = recovery_rate

    def try_to_infect_neighbors(self):
        neighbors_nodes = self.model.grid.get_neighbors(self.pos, include_center=False)
        susceptible_neighbors = [
            agent
            for agent in self.model.grid.get_cell_list_contents(neighbors_nodes)
            if agent.state is State.SUSCEPTIBLE
        ]
        for a in susceptible_neighbors:
            x = self.random.random()

            if x < self.infection_rate:
                a.state = State.INFECTED

    def try_gain_resistance(self):
        if self.random.random() > self.recovery_rate:
            self.state = State.RESISTANT

    def try_remove_infection(self):
        # Try to remove
        if self.random.random() < self.recovery_rate:
            # Success
            self.state = State.SUSCEPTIBLE
            self.try_gain_resistance()
        else:
            # Failed
            self.state = State.INFECTED

    def try_check_situation(self):
        if self.random.random() > self.recovery_rate:
            # Checking...
            if self.state is State.INFECTED:
                self.try_remove_infection()

    # step function
    def step(self):

        if self.state is State.INFECTED:
            self.try_to_infect_neighbors()
        self.try_check_situation()


