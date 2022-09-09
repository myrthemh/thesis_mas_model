import math

from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import ChartModule
from mesa.visualization.modules import NetworkModule
from mesa.visualization.modules import TextElement
from .model import SocialNetwork, State, obtain_variable_from_data, number_infected, number_susceptible, number_resistant#, #num_nodes, avg_node_degree

infection_rate, recovery_rate, num_nodes, avg_node_degree, initial_outbreak_size = obtain_variable_from_data()


def network_portrayal(G):
    # The model ensures there is always 1 agent per node

    def node_color(agent):
        return {State.INFECTED: "#FF0000", State.SUSCEPTIBLE: "#008000"}.get(
            agent.state, "#808080"
        )

    def edge_color(agent1, agent2):
        if State.RESISTANT in (agent1.state, agent2.state):
            return "#000000"
        return "#e8e8e8"

    def edge_width(agent1, agent2):
        if State.RESISTANT in (agent1.state, agent2.state):
            return 3
        return 2

    def get_agents(source, target):
        return G.nodes[source]["agent"][0], G.nodes[target]["agent"][0]

    portrayal = dict()
    portrayal["nodes"] = [
        {
            "size": 6,
            "color": node_color(agents[0]),
            "tooltip": f"id: {agents[0].unique_id}<br>state: {agents[0].state.name}",
        }
        for (_, agents) in G.nodes.data("agent")
    ]

    portrayal["edges"] = [
        {
            "source": source,
            "target": target,
            "color": edge_color(*get_agents(source, target)),
            "width": edge_width(*get_agents(source, target)),
        }
        for (source, target) in G.edges
    ]

    return portrayal


#network = NetworkModule(network_portrayal, 500, 500, library="d3")

chart2 = ChartModule(
    [
        {"Label": "Infected", "Color": "#FF0000"},
        {"Label": "Susceptible", "Color": "#008000"},
        {"Label": "Resistant", "Color": "#808080"},
        # {"Label": "avg_sentiment", "Color": "#808080"},
    ]
)


class MyTextElement(TextElement):
    def render(self, model):
        no_infected = number_infected(model)
        no_susceptible = str(number_susceptible(model))
        no_resistant = str(number_resistant(model))
        ratio = model.resistant_susceptible_ratio()
        ratio_text = "&infin;" if ratio is math.inf else f"{ratio:.2f}"
        infected_text = str(number_infected(model))

        return "Susceptible: {}, Infected: {} Recovered: {}<br>Resistant/Susceptible Ratio: {}<br>".format(
            no_susceptible, no_infected, no_resistant, ratio_text, infected_text
        )


model_params = {
    "num_nodes": UserSettableParameter(
        "slider",
        "Number of agents",
        num_nodes,
        10,
        11000,
        1,
        description="Choose how many agents to include in the model",
    ),
    "avg_node_degree": UserSettableParameter("slider", "Avg Node Degree", avg_node_degree, 1, 100, 1, description="Avg Node Degree"
    ),

"recovery_rate": UserSettableParameter(
        "slider",
        "Recovery Rate",
    0.0001,
    0.0001,
    1,
    0.001,
        description="Initial Outbreak Size",
    ),

"infection_rate": UserSettableParameter(
        "slider",
        "Infection rate",
        0.0001,
    0.0001,
        1,
        0.001,
        description="Initial Outbreak Size",
    ),

    "initial_outbreak_size": UserSettableParameter(
        "slider",
        "Initial number of agent tweet about topic",
        1,
        1,
        100,
        1,
        description="Initial Outbreak Size",
    ),

}

server = ModularServer(
    SocialNetwork, [MyTextElement(), chart2], "Tweet Topic Model - Version 1", model_params
)
server.port = 8521
