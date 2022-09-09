import math

from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import ChartModule
from mesa.visualization.modules import NetworkModule
from mesa.visualization.modules import TextElement
from .model import SocialNetwork, State, number_infected


def network_portrayal(G):
    # The model ensures there is always 1 agent per node

    # link colors: https://www.webfx.com/web-design/color-picker/#
    def node_color(agent):
        return {"Citizen": "#8423e0", "Citizen Initiative": "#539c32",
                "National Government": "#ff8a00", "Local Government": "#00000"
                }.get(
            agent.type, "#808080"
        )

    def edge_color(agent1, agent2):
        if agent1.type=="National Government" or agent2.type=="National Government" or agent1.type=="Local Government" or agent2.type=="Local Government":
            return "#1F85DE"
        if agent1.type == "Citizen Initiative" or agent2.type == "Citizen Initiative":
            return "#23e096"
        if State.RESISTANT in (agent1.state, agent2.state):
            return "#000000"
        return "#e8e8e8"

    def edge_width(agent1, agent2):
        if agent1.type == "National Government" or agent2.type == "National Government" or agent1.type == "Local Government" or agent2.type == "Local Government":
            return 3
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
            # <br>state: {agents[0].state.name}
            "tooltip": f"id: {agents[0].unique_id}<br>type: {agents[0].type}",
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


network = NetworkModule(network_portrayal, 500, 500, library="d3")

chart = ChartModule(
    [
        {"Label": "Topic Sentiment", "Color": "#FF0000", },

    ]
)

chart3 = ChartModule(
    [

        {"Label": "Tweets Topic", "Color": "#008000"},
      ]
)


chart2 = ChartModule(
    [
        {"Label": "Infected", "Color": "#FF0000"},
        {"Label": "Susceptible", "Color": "#008000"},
        {"Label": "Recovered", "Color": "#808080"},
    ]
)


class MyTextElement(TextElement):
    def render(self, model):
        ratio = model.resistant_susceptible_ratio()
        ratio_text = "&infin;" if ratio is math.inf else f"{ratio:.2f}"
        infected_text = str(number_infected(model))

        return "Recovered/Susceptible Ratio: {}<br>Infected Remaining: {}".format(
            ratio_text, infected_text
        )


model_params = {



    "network": UserSettableParameter("checkbox", "Real-word network based", True),
    "num_nodes": UserSettableParameter(
        "slider",
        "Number of agents",
        10,
        10,
        1000,
        1,
        description="Choose how many agents to include in the model",
    ),

    "avg_node_degree": UserSettableParameter(
        "slider", "Avg Node Degree", 3, 3, 8, 1, description="Avg Node Degree"),

    # "recovery_change": UserSettableParameter(
    #     "slider", "Recovery change", 0.0006, 0.0001, 1, 0.0001,  description="Avg Node Degree",),

    "influenceable": UserSettableParameter(
        "slider",
        "Influenceability",
        0.5,
        0,
        1,
        0.05,
        description="Choose to what degree the agents are influenced by the actions of the other agents",
    ),

    "citizen_initiatives": UserSettableParameter("checkbox", "Citizen initiative included", True),

    # "most_frequent_users": UserSettableParameter(
    #     "slider", "Budget", 1, 10, 1000, 1, description="frequent", ),

    "budget": UserSettableParameter(
        "slider", "Budget", 15, 1, 50, 1, description="budget", ),

    "participation": UserSettableParameter(
        "slider", "Participation of citizen initiative", 1980, 1980, 2020, 1,
        description="Participation of citizen initiatives", ),

    "verified": UserSettableParameter("checkbox", "Verified accounts excluded", False),

    "location": UserSettableParameter("checkbox", "Location excluded", False),

    "most_frequent_users": UserSettableParameter("checkbox", "Most frequent users excluded", False),

    # "weak_link": UserSettableParameter("checkbox", "Weak link excluded", False),

   "popularity": UserSettableParameter("checkbox", "Excluded user with most followers", True),

    'scheduled': UserSettableParameter("checkbox", "Events scheduled", True),

    # "avg_node_degree": UserSettableParameter(
    #     "slider", "Avg Node Degree", 3, 3, 8, 1, description="Avg Node Degree"),
    #
    # "recovery_change": UserSettableParameter(
    #     "slider", "Recovery change", 0.001, 0.001, 1, 0.001, description="Avg Node Degree", ),
    #
    # "threshold_infected": UserSettableParameter(
    #     "slider", "Threshold infected", 0.001, 0.001, 1, 0.001, description="Avg Node Degree", ),



    # "initial_outbreak_size": UserSettableParameter(
    #     "slider",
    #     "Initial number of agent tweet about topic",
    #     1,
    #     1,
    #     100,
    #     1,
    #     description="Initial Outbreak Size",
    # ),

}

chart = ChartModule(
    [
        {"Label": "Sentiment", "Color": "#FF0000"},
      ]
)

#network
server = ModularServer(
    SocialNetwork, [chart3, chart2], "Tweet Topic Model - Version 4", model_params
)
server.port = 8521
