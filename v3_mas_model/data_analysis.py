import pandas as pd
import config
import networkx as nx

small_network = True


if small_network:
    df_network = pd.read_csv(f'{config.path_final}networks_all_users_small.csv')
    df_network["target"] = df_network["target"].astype(int)
else:
    df_network = pd.read_csv(f'{config.path_final}networks_all_users.csv')
    df_network["target"] = df_network["target"].astype(int)

df_userinfo = pd.read_csv(f'{config.path_final}userinfo.csv')
user_info = ['author_id', 'name', 'followers_count', 'following',
             'favourites_count', 'friends_count', 'description',
             'created_at_user', 'verified', 'location',
             'twitter_actions', 'topic_actions', 'total_actions',
             'twitter_activity', 'topic_twitter_frequency', 'topic_sentiment']

df_userinfo = df_userinfo[user_info]
df_userinfo = df_userinfo.drop_duplicates(subset=['author_id'])
#                  'name', 'topic_actions', 'total_actions',
#                  'twitter_activity', 'topic_twitter_frequency', 'topic_sentiment'])
fb_np = nx.from_pandas_edgelist(df_network, source='source', target='target', edge_attr=None, create_using=None,
                                edge_key=None)
num_nodes = len(fb_np.nodes)







