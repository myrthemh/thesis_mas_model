import math
from enum import Enum
import networkx as nx
import pandas as pd

from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import NetworkGrid
from .data_analysis import fb_np, df_userinfo
import config
import re

# define state; whether susceptible, infected or resistant
class State(Enum):
    SUSCEPTIBLE = 0
    INFECTED = 1
    RESISTANT = 2


# count state
def number_state(model, state):
    return sum(1 for a in model.grid.get_all_cell_contents() if a.state is state)


def number_infected(model):
    return number_state(model, State.INFECTED)


def number_susceptible(model):
    return number_state(model, State.SUSCEPTIBLE)


def number_resistant(model):
    return number_state(model, State.RESISTANT)


def avg_sentiment(model):
    return [agent.b for agent in model.schedule.agents if agent.type == "Citizen"]


def number_tweets(model):
    return model.tweets_topic


def number_petitions(model):
    return model.signed_petitions


# define the social network
class SocialNetwork(Model):
    """A information diffusion model with some number of agents"""

    def __init__(
            self,
            num_nodes=10,
            avg_node_degree=3,
            initial_outbreak_size=1,
            recovery_change=0.0006,
            influenceable=0.5,
            tweets_topic=0,
            network=True,
            citizen_initiative_ids=[1139837243944787968, 738721272704737280, 586421809, 18761110],
            participation=1,
            budget=200,
            recovery=0,
            citizen_initiatives=True,
            prob_event=1/20,
            offline_event=False,
            days_infection=3,
            max_low_connected=10,
            verified=True,
            location=True,
            most_frequent_users=True,
            national_elections=100,
            scheduled=True,
            signed_petitions=0,
            weak_link=False,
            popularity=False,


    ):
        self.days_infection = days_infection
        self.max_low_connected = max_low_connected

        self.df_results_sir = pd.DataFrame(columns=['number_susceptible', 'number_infected', 'number_resistant',
                                                    'results_tweets', 'sustainability_score', 'infected_low'])
        self.citizen_initiatives = citizen_initiatives
        self.offline_event = offline_event
        self.national_elections = national_elections
        self.recovery = recovery
        self.participation = participation
        self.budget = budget
        self.verified = verified
        self.signed_petitions = signed_petitions
        self.location = location
        self.most_frequent_users = most_frequent_users
        self.scheduled = scheduled
        self.weak_link = weak_link
        self.popularity = popularity

        # infected rate
        self.infected_low = 0

        if network:
            self.G = fb_np
            self.num_nodes = len(self.G.nodes)

            if not self.citizen_initiatives:
                for node_ci in citizen_initiative_ids:
                    if any([node for node in self.G.nodes(data=True) if node == node_ci]):
                        self.G.remove_node(node_ci)
        else:
            self.num_nodes = num_nodes
            prob = avg_node_degree / self.num_nodes
            self.G = nx.erdos_renyi_graph(n=self.num_nodes, p=prob)

        self.grid = NetworkGrid(self.G)
        self.schedule = RandomActivation(self)
        self.prob_event = prob_event

        self.initial_outbreak_size = (
            initial_outbreak_size if initial_outbreak_size <= num_nodes else num_nodes
        )

        self.recovery_change = recovery_change
        self.influenceable = influenceable
        self.tweets_topic = tweets_topic
        self.participation = participation
        self.citizen_initiatives = citizen_initiatives
        self.video = False

        self.datacollector = DataCollector(
            {
                "Infected": number_infected,
                "Susceptible": number_susceptible,
                "Recovered": number_resistant,
                "Sentiment": avg_sentiment,
                "Tweets Topic": number_tweets,
                #"Number Signed Petitions": signed_petitions,

            }
        )

        verified_names = 0
        location_names = 0
        frequent_tweeters_names = 0
        year_i = 0

        # Create agents
        # sorting data frame by name

        for i, node in enumerate(self.G.nodes()):
            agent_info = df_userinfo[df_userinfo['author_id'] == node]
            location = False
            verified = False
            most_frequent_tweeter = False
            if agent_info.size == 0:
                number_on_topic = 0
                number_off_topic = int(1000)
                total_actions = int(2000)
                # if self.location:
                #     location = True
                number_followers = 100
            elif agent_info.shape[0] >= 2:
                agent_info
            else:
                number_on_topic = int(agent_info["topic_actions"])

                if self.verified:
                    if list(agent_info["verified"])[0]:
                        verified = True
                        verified_names = verified_names + 1

                if self.location:
                    location = list(agent_info["location"])[0]
                    if type(location) == str:
                        if re.search(r'(utrecht|utrecht, nederland|utrecht, the netherlands|nieuwegein|zeist|amersfoort)', location.lower()):
                            location = True
                            location_names = location_names + 1
                if self.most_frequent_users:
                    if number_on_topic > 200:
                        most_frequent_tweeter = True
                        frequent_tweeters_names = frequent_tweeters_names + 1

                if number_on_topic < 0:
                    number_on_topic = 0
                number_off_topic = int(agent_info["twitter_actions"])
                total_actions = int(agent_info["total_actions"])
                number_followers = int(agent_info["friends_count"])

                if number_followers == 0:
                    number_followers = 100

                if self.popularity:

                    if number_followers > 1000:
                        popular = True

                    else:
                        popular = False
                else:
                    popular = False

            if node not in citizen_initiative_ids:

                a = CitizenAgent(
                    i,
                    self,
                    initial_state=State.SUSCEPTIBLE,
                    recovery_change=self.recovery_change,
                    influenceable=self.influenceable,
                    number_on_topic=number_on_topic,
                    number_off_topic=number_off_topic,
                    number_not_tweet=max(0, total_actions-number_off_topic-number_on_topic),

                    location=location,
                    verified=verified,
                    number_following=number_followers,
                    most_frequent_tweeter=most_frequent_tweeter,
                    popular = popular

                )
                self.schedule.add(a)

            else:

                if self.citizen_initiatives:
                   # y_test = self.year[year_i]
                    a = CitizenInitiativeAgent(
                            unique_id=i,
                            model=self,
                            initial_state=State.INFECTED,
                            total_actions=total_actions,
                            number_tweets=(number_on_topic+number_off_topic),
                            prob_event=self.prob_event,
                            # year=self.year[year_i],
                            budget=100,
                        )
                    #year_i += 1
                    self.schedule.add(a)

            # Add the agent to the node
            self.grid.place_agent(a, node)

        # if not self.verified:
        #     for name in verified_names:
        #         if any([node for node in self.G.nodes(data=True) if node == int(name)]):
        #             self.G.remove_node(name)


            # for name in location_names:
            #     self.G.remove_node(name)
        #
        # if self.most_frequent_users:
        #     for name in frequent_tweeters_names:
        #         self.G.remove_node(name)

        print(location_names, verified_names, frequent_tweeters_names)
        # Infect some nodes
        infected_nodes = self.random.sample(self.G.nodes(), self.initial_outbreak_size)
        for a in self.grid.get_cell_list_contents(infected_nodes):
            a.state = State.INFECTED
            neighbors = a.model.grid.get_neighbors(a.pos, include_center=False)

            if len(neighbors) < 20:
                a.model.infected_low += 1

        self.running = True
        self.datacollector.collect(self)

    def resistant_susceptible_ratio(self):
        try:
            return number_state(self, State.RESISTANT) / number_state(
                self, State.SUSCEPTIBLE
            )
        except ZeroDivisionError:
            return math.inf

    def external_factor(self):
        if self.citizen_initiatives:
            if self.schedule.steps == 19:
                self.offline_event = True
            if self.schedule.steps == 106:
                self.offline_event = True
                self.video = True

    def step(self):
        self.tweets_topic = 0
        self.external_factor()
        self.schedule.step()
        if self.offline_event:
            self.recovery = 1
        elif self.recovery > 0.1:
            self.recovery *= 0.25
        else:
            self.recovery = 0


        # collect data
        self.datacollector.collect(self)

        if int(self.schedule.steps) < 160:

            sustainability_score = 0.75 * (number_susceptible(self) / (number_resistant(self) + number_susceptible(self) + number_infected(self))) + 0.25 * (number_resistant(self) / (number_resistant(self) + number_susceptible(self) + number_infected(self)))
            self.df_results_sir.loc[len(self.df_results_sir.index)] = [str(number_susceptible(self)), str(number_infected(self)), str(number_resistant(self)),
                                                                       self.tweets_topic, sustainability_score, self.infected_low]

            self.df_results_sir.to_csv(
                f"{config.path_version4}/sir_results_CI{self.citizen_initiatives}_INFL{str(self.influenceable)[2:]}_BUDGET{self.budget}_PART{self.participation}_LOC{self.location}_MFT{self.most_frequent_users}_VER{self.verified}SCH{self.scheduled}POP{self.popularity}.csv")

            if self.offline_event:
                self.offline_event = False

    def run_model(self, n):
        for i in range(n):
            self.step()


class CitizenAgent(Agent):
    def __init__(
            self,
            unique_id,
            model,
            initial_state,
            recovery_change,
            influenceable,
            number_on_topic,
            number_off_topic,
            number_not_tweet,
            location,
            verified,
            number_following,
            most_frequent_tweeter,
            popular,
            type="Citizen",


    ):
        super().__init__(unique_id, model)

        self.state = initial_state
        self.type = type
        self.model = model

        self.number_on_topic = number_on_topic
        self.number_off_topic = number_off_topic
        self.number_not_tweet = number_not_tweet
        self.number_following = number_following

        self.location = location
        self.verified = verified
        self.most_frequent_tweeter = most_frequent_tweeter
        self.popular = popular

        self.total_actions = self.number_on_topic + self.number_off_topic + self.number_not_tweet
        if self.total_actions == 0:
            self.total_actions = 180
        self.tweet_frequency = (self.number_on_topic + self.number_off_topic) / self.total_actions
        if self.number_on_topic == 0 or self.number_off_topic+self.number_on_topic == 0:
            self.tweet_topic_frequency = 0
        else:
            self.tweet_topic_frequency = self.number_on_topic / (self.number_on_topic + self.number_off_topic)

        self.b = self.tweet_frequency * self.tweet_topic_frequency
        self.d = self.tweet_frequency * (1 - self.tweet_topic_frequency)
        self.u = 1 - self.d - self.b
        self.influenceable = influenceable
        self.recovery_change = recovery_change
        self.recovery_count = 0
        self.weak_link = False


    def check_weak_link(self):
        neighbors_nodes = len(list(self.model.grid.get_neighbors(self.pos, include_center=False)))

        if self.number_following > 500 and neighbors_nodes <= 25:
            self.weak_link = True


    def try_to_infect_neighbors(self):
        neighbors_nodes = self.model.grid.get_neighbors(self.pos, include_center=False)
        susceptible_neighbors = [
            agent
            for agent in self.model.grid.get_cell_list_contents(neighbors_nodes)
            if agent.state is State.SUSCEPTIBLE
        ]
        for a in susceptible_neighbors:
            x = self.random.random()
            #
            if x < self.influenceable:
                a.state = State.INFECTED
                neighbors = a.model.grid.get_neighbors(a.pos, include_center=False)

                if len(neighbors) < 20:
                    a.model.infected_low += 1

    def try_gain_resistance(self):
        if self.random.random() < self.recovery_change:
            self.state = State.RESISTANT

    def try_remove_infection(self):
        # Try to remove
        if self.random.random() < self.recovery_change:
            # Success
            self.state = State.SUSCEPTIBLE
            self.try_gain_resistance()
        else:
            # Failed
            self.state = State.INFECTED

    def try_check_situation(self):
        if self.random.random() > self.recovery_change:
            # Checking...
            if self.state is State.INFECTED:
                self.try_remove_infection()

    def do_nothing(self):
        return "DoNothing"

    def tweet_other(self):
        return "TweetOther"

    def sign_petition(self):
        self.model.signed_petitions += 1
        return "SignPetition"

    def tweet_topic(self):

        self.model.tweets_topic += 1

        if self.random.random() < self.b:
            self.try_to_infect_neighbors()
        self.try_check_situation()

        return "TweetTopic"

    def observe_environment(self):
        b_a = 0
        d_a = 0
        u_a = 0
        neighbors_nodes = self.model.grid.get_neighbors(self.pos, include_center=False)
        neighbors_nodes = [agent for agent in self.model.grid.get_cell_list_contents(neighbors_nodes)]

        number_neigbors = len(neighbors_nodes)
        try:
            for a in neighbors_nodes:
                if a.type == "Citizen":
                    b_a += a.b
                    d_a += a.d
                    u_a += a.u

            b = b_a / self.number_following
            d = d_a / self.number_following
            u = u_a / self.number_following

            # d = d_a / number_neigbors
            # u = u_a / number_neigbors
            return b, d, u
        except ZeroDivisionError:
            return 0, 0, 0

    def update_variables(self, action):
        if self.state == State.SUSCEPTIBLE and action == "TweetTopic":
            self.state = State.INFECTED
            neighbors = self.model.grid.get_neighbors(self.pos, include_center=False)

            if len(neighbors) < 20:
                self.model.infected_low += 1

        if self.state == State.INFECTED and self.b < self.recovery_change:
            if self.random.random() < self.recovery_change:
                self.state = State.RESISTANT

        if action == 'TweetTopic':
            self.number_on_topic += 1
        elif action == 'TweetOther':
            self.number_off_topic += 1
        elif action == 'doNothing':
            self.number_not_tweet += 1

        self.total_actions += 1

        self.tweet_frequency = (self.number_on_topic + self.number_off_topic) / self.total_actions #(self.number_on_topic + self.number_off_topic + self.number_not_tweet)
        if self.number_on_topic == 0 or self.number_off_topic + self.number_on_topic == 0:
            self.tweet_topic_frequency = 0
        else:
            self.tweet_topic_frequency = self.number_on_topic / (self.number_on_topic + self.number_off_topic)

        self.prob_tweet = self.tweet_frequency * self.tweet_topic_frequency

        self.u = 1 - self.b

    # step function
    def step(self):
        b_neighbors, d_neighbors, u_neighbors = self.observe_environment()
        b = self.influenceable * self.b + (1 - self.influenceable) * b_neighbors
        d = self.influenceable * self.d + (1 - self.influenceable) * d_neighbors
        u = 1 - d - b
        if self.model.schedule.steps == 1:
            self.check_weak_link()

        if self.model.video:
            b += 0.005 * self.model.budget * self.model.recovery
            d -= 0.005 * self.model.budget * self.model.recovery

        else:
            b += 0.005 * self.model.budget * 0.25 * self.model.recovery
            d -= 0.005 * self.model.budget * 0.25 * self.model.recovery

        b = max(0, b)
        d = max(0, d)
        u = max(0, u)

        random = self.random.random()

        if random < b:
            if self.state == State.RESISTANT or self.location or self.verified or self.most_frequent_tweeter\
                    or (self.model.weak_link and self.weak_link) or self.popular:

                action = self.tweet_other()
            else:
                action = self.tweet_topic()
        elif self.model.video:
            action = self.sign_petition()
        else:
            action = self.do_nothing()

        self.update_variables(action)

        if self.state is State.INFECTED:
            self.try_check_situation()


class CitizenInitiativeAgent(Agent):
    def __init__(
            self,
            unique_id,
            model,
            initial_state,
            total_actions,
            number_tweets,
            prob_event,
            # year,
            budget=100,
            type="Citizen Initiative",

    ):
        super().__init__(unique_id, model)

        self.state = initial_state
        self.model = model
        self.type = type
        self.total_actions = total_actions
        self.number_tweets = number_tweets
        # self.year = year

        participation_score = 1 / (2022-self.model.participation)
        self.prob_event = prob_event * participation_score
        self.budget = budget

        self.tweet_frequency = self.number_tweets / self.total_actions
        if self.tweet_frequency >= 1:
            self.tweet_frequency = 1 - self.prob_event

        self.prob_nothing = 1 - self.tweet_frequency - self.prob_event

    def try_to_infect_neighbors(self):
        neighbors_nodes = self.model.grid.get_neighbors(self.pos, include_center=False)
        susceptible_neighbors = [
            agent
            for agent in self.model.grid.get_cell_list_contents(neighbors_nodes)
            if agent.state is State.SUSCEPTIBLE
        ]
        for a in susceptible_neighbors:
            x = self.random.random()

            if x < self.influenceable:
                a.state = State.INFECTED

    def do_nothing(self):
        return "DoNothing"

    def start_offline_event(self):
        if not self.model.scheduled:
            self.model.event = True
        return "StartOfflineEvent"

    def tweet_topic(self):
        self.model.tweets_topic += 1

        return "TweetTopic"

    def observe_environment(self):
        b_a = 0
        d_a = 0
        u_a = 0
        neighbors_nodes = self.model.grid.get_neighbors(self.pos, include_center=False)
        neighbors_nodes = [agent for agent in self.model.grid.get_cell_list_contents(neighbors_nodes)]

        number_neigbors = len(neighbors_nodes)
        try:
            for a in neighbors_nodes:
                if a.type == "Citizen":
                    b_a += a.b
                    d_a += a.d
                    u_a += a.u

            b = b_a / number_neigbors
            d = d_a / number_neigbors
            u = u_a / number_neigbors

            return b, d, u
        except ZeroDivisionError:
            return 0, 0, 0

    def update_variables(self, action):
        if action == 'TweetTopic':
            self.number_tweets += 1
        self.total_actions += 1

        if action == 'StartOfflineEvent':
            self.model.offline_event = True

        self.tweet_frequency = self.number_tweets / (
                    self.total_actions)

    # step function
    def step(self):

        random = self.random.random()
        if random < self.tweet_frequency:
            action = self.tweet_topic()
        elif random > (self.tweet_frequency + self.prob_nothing):
            action = self.start_offline_event()
        else:
            action = self.do_nothing()

        self.update_variables(action)

