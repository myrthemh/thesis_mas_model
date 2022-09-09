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


def avg_sentiment(model):
    return [agent.b for agent in model.schedule.agents if agent.type == "Citizen"]


def number_tweets(model):
    return model.tweets_topic


# define the social network
class SocialNetwork(Model):
    """A information diffusion model with some number of agents"""

    def __init__(
            self,
            num_nodes=10,
            avg_node_degree=3,
            influenceable=0.5,
            tweets_topic=0,
            network=True,
            verified=True,
            location=True,
            most_frequent_users=True,



    ):
        self.df_results_sir = pd.DataFrame(columns=[
                                                    'results_tweets'])

        self.verified = verified
        self.location = location
        self.most_frequent_users = most_frequent_users

        if network:
            self.G = fb_np
            self.num_nodes = len(self.G.nodes)

        else:
            self.num_nodes = num_nodes
            prob = avg_node_degree / self.num_nodes
            self.G = nx.erdos_renyi_graph(n=self.num_nodes, p=prob)

        self.grid = NetworkGrid(self.G)
        self.schedule = RandomActivation(self)

        self.influenceable = influenceable
        self.tweets_topic = tweets_topic

        self.datacollector = DataCollector(
            {

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
                if self.location:
                    location = True
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

                a = CitizenAgent(
                    i,
                    self,
                    influenceable=self.influenceable,
                    number_on_topic=number_on_topic,
                    number_off_topic=number_off_topic,
                    number_not_tweet=max(0, total_actions-number_off_topic-number_on_topic),
                    location=location,
                    verified=verified,
                    number_following=number_followers,
                    most_frequent_tweeter=most_frequent_tweeter,

                )
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


        self.running = True
        self.datacollector.collect(self)



    def step(self):
        self.tweets_topic = 0
        self.schedule.step()

        # collect data
        self.datacollector.collect(self)

        if int(self.schedule.steps) < 160:

            self.df_results_sir.loc[len(self.df_results_sir.index)] = [self.tweets_topic]

            self.df_results_sir.to_csv(
                f"{config.path_version2}/sir_results_INFL{str(self.influenceable)[2:]}_LOC{self.location}_MFT{self.most_frequent_users}_VER{self.verified}.csv")


    def run_model(self, n):
        for i in range(n):
            self.step()


class CitizenAgent(Agent):
    def __init__(
            self,
            unique_id,
            model,
            influenceable,
            number_on_topic,
            number_off_topic,
            number_not_tweet,
            location,
            verified,
            number_following,
            most_frequent_tweeter,
            type="Citizen",

    ):
        super().__init__(unique_id, model)

        self.type = type
        self.model = model

        self.number_on_topic = number_on_topic
        self.number_off_topic = number_off_topic
        self.number_not_tweet = number_not_tweet
        self.number_following = number_following

        self.location = location
        self.verified = verified
        self.most_frequent_tweeter = most_frequent_tweeter

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



    def do_nothing(self):
        return "DoNothing"

    def tweet_other(self):
        return "TweetOther"

    def sign_petition(self):
        self.model.signed_petitions += 1
        return "SignPetition"

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

            b = b_a / number_neigbors#self.number_following
            d = d_a / number_neigbors#self.number_following
            u = u_a / number_neigbors#self.number_following

            # d = d_a / number_neigbors
            # u = u_a / number_neigbors
            return b, d, u
        except ZeroDivisionError:
            return 0, 0, 0

    def update_variables(self, action):

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


        b = max(0, b)
        d = max(0, d)
        u = max(0, u)

        random = self.random.random()

        if random < b:
            if self.location or self.verified or self.most_frequent_tweeter:
                action = self.tweet_other()
            else:
                action = self.tweet_topic()
        else:
            action = self.do_nothing()

        self.update_variables(action)


