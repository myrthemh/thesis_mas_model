import pandas as pd
import config
import matplotlib.pyplot as plt
import numpy as np
import re
import datetime
import time
import statistics
import networkx as nx
import pickle


def prepare_data_SIR_model(df: pd.DataFrame, date_time="Datetime", hashtag="stopdeverbreding",
                   timeframe="monthly", start_date=None, skip=False, user=None, external=None, stop_date="2021-10", date_diff=False):
    d = {'Jan': "01", 'Feb': "02", 'Mar': "03", 'Apr': "04", 'May': "05", 'Jun': "06",
         'Jul': "07", 'Aug': "08", 'Sep': "09", 'Oct': 10, 'Nov': 11, 'Dec': 12}

    if type(hashtag) == list:
        string_match = ""
        for i in hashtag:
            string_match += f".*{i}"
        df1 = df[df.apply(lambda r: r.str.contains(f'{string_match}', case=False).any(), axis=1)]
        string_match = ""
        for i in reversed(hashtag):
            string_match += f".*{i}"
        df2 = df[df.apply(lambda r: r.str.contains(f'{string_match}', case=False).any(), axis=1)]
        frames = [df1, df2]

        df_selected = pd.concat(frames)
        # df[ df["Hashtags"].str.match('.*amelisweerd.*a27.*') ]
    elif hashtag is None:
        df_selected = df
    else:
        df_selected = df[df.apply(lambda r: r.str.contains(hashtag, case=False).any(), axis=1)]

    # sort on date
    df_new = df_selected.sort_values(by=date_time, ascending=False)

    if timeframe == "monthly":
        date = [t[:7] for t in df_new[date_time] if not re.search('[a-zA-Z]', t)]
    elif timeframe == "weekly":
        date = [f"y:{t[:4]} w:{datetime.date(int(t[:4]), int(t[5:7]), int(t[8:10])).isocalendar()[1]}" for t in
                df_new[date_time] if not re.search('[a-zA-Z]', t)]
        if len(date) == 0:
            print(d[df_new[date_time][0][4:7]], df_new[date_time][0][8:10])
            date = [f"y:{t[-4:]} w:{datetime.date(int(t[-4:]), d[t[4:7]], int(t[8:10])).isocalendar()[1]}" for t in
                    df_new[date_time]]
            print(date)
    elif timeframe == "dayly":
        date = [t[:10] for t in
                df_new[date_time]]  # if not re.search('[a-zA-Z]', t)]
        if date_diff:
            date = [f"{t[-4:]}-{d[t[4:7]]}-{t[8:10]}" for t in df_new[date_time]]

    df_new = df_new.assign(date=date)
    # print("length:", len(df_new))
    # df_new = df_new[pd.to_numeric(df[date_time], errors='coerce').notnull()]
    # print("length:", len(df_new))

    if type(hashtag) == list:
        df_new.to_csv(
            f'data/{hashtag[0]}AND{hashtag[1]}_{start_date}_date_frequency_{timeframe}2.csv')
        df_new.to_pickle(
            f'data/{hashtag[0]}AND{hashtag[1]}_{start_date}_date_frequency_{timeframe}2.pkl')
    else:
        if not external:
            df_new.to_csv(f'{config.output_dir_frequency}dayly/{hashtag}_{start_date}_date_frequency_{timeframe}.csv')

    plt.figure(figsize=(40, 10))

    keys, counts = np.unique(date, return_counts=True)

    if not skip:
        if timeframe == "monthly":
            x = pd.date_range(start=str(keys[0]), end=str(keys[-1]), freq="M").astype(
                "period[M]")  # .difference(df.index)
            for idx, i in enumerate(x):
                if str(i) not in keys:
                    keys = np.insert(keys, idx, str(i))
                    counts = np.insert(counts, idx, 0)
            plt.bar(keys[:-2], counts[:-2])

        elif timeframe == "weekly":
            if start_date is None:
                year = int(keys[0][2:6])
                t_start = int(keys[0][-2:])
            else:
                year = int(start_date[:4])
                t_start = int(start_date[5:7])

            x_keys = []
            x_values = []
            for idx, i in enumerate(range(t_start, 53)):
                new_date = time.asctime(time.strptime('{} {} 1'.format(year, i), '%Y %W %w'))  # f"y:{year} w:{i}"
                x_keys.append(new_date)
                check = f"y:{year} w:{i}"
                if check in keys:
                    idx = np.where(keys == check)[0][0]
                    x_values.append(counts[idx])
                else:
                    x_values.append(0)

                if i == 52:
                    year += 1
                    for j in range(1, t_start):
                        new_date = time.asctime(
                            time.strptime('{} {} 1'.format(year, j), '%Y %W %w'))  # f"y:{year} w:{j}"
                        check = f"y:{year} w:{j}"
                        x_keys.append(new_date)
                        if check in keys:
                            idx = np.where(keys == check)[0][0]
                            x_values.append(counts[idx])
                        else:
                            x_values.append(0)

            # if max == 52:
            #     break
            #
            # max += 1

            plt.bar(x_keys, x_values)

        elif timeframe == "dayly":
            if start_date is not None:
                year = int(start_date[:4])
                t_start = int(start_date[5:7])
            else:
                year = int(keys[0][2:6])
                t_start = int(keys[0][-2:])

            x_keys = []
            x_values = []
            for idx, i in enumerate(range(t_start, 52)):
                # f"y:{year} w:{i}"
                new_date = time.asctime(time.strptime('{} {} 1'.format(year, i), '%Y %W %w'))
                month = d[new_date[4:7]]
                day = new_date[8:10]
                gDate = datetime.datetime(int(year), int(month), int(day))

                for day in range(0, 7):

                    curr_day = gDate + datetime.timedelta(days=day)
                    check = f"{str(curr_day)[:4]}-{str(curr_day)[5:7]}-{str(curr_day)[8:10]}"

                    x_keys.append(check)
                    if check in keys:
                        idx = np.where(keys == check)[0][0]
                        x_values.append(counts[idx])
                    else:
                        x_values.append(0)

            year += 1
            for j in range(1, t_start - 30):

                new_date = time.asctime(time.strptime('{} {} 1'.format(year, j), '%Y %W %w'))
                month = d[new_date[4:7]]
                day = new_date[8:10]
                gDate = datetime.datetime(int(year), int(month), int(day))

                for day in range(0, 7):
                    curr_day = gDate + datetime.timedelta(days=day)
                    check = f"{str(curr_day)[:4]}-{str(curr_day)[5:7]}-{str(curr_day)[8:10]}"
                    x_keys.append(check)

                    if check in keys:
                        idx = np.where(keys == check)[0][0]
                        x_values.append(counts[idx])
                    else:
                        x_values.append(0)
            plt.bar(x_keys, x_values)
    else:
        plt.bar(keys, counts)

    plt.xticks(rotation=90)
    plt.subplots_adjust(bottom=0.34)
    plt.title(f"Number of tweets with #{hashtag} over time")
    if type(hashtag) == list and len(hashtag) == 2:
        plt.title(f"Number of tweets with #{hashtag[0]} and #{hashtag[1]} over time")
    plt.tight_layout()
    if external is not None:
        start_date = f"{start_date}_{external}"
        plt.title(f"Number of tweets of user {user} tweeting about {external}")
        plt.savefig(f'{config.path_figures}/{timeframe}/{user}_{start_date}_date_frequency_{timeframe}_{external}.png')
    elif user:
        plt.savefig(f'{config.path_figures}/{timeframe}/{user}_{start_date}_date_frequency_{timeframe}.png')
    else:
        if type(hashtag) == list:
            plt.savefig(
                f'data/{string_match}_{start_date}_date_frequency_{timeframe}-new.png')
        else:
            plt.savefig(f'data/{hashtag}_{start_date}_date_frequency_{timeframe}-new.png')

    plt.show()


def initialize_SIR_model(df, df_network, threshold_start=5, peak_date="2020-12-06", threshold_recovery=500, variable = "Datetime"):

    df = df.drop_duplicates(["Username", "Datetime"])


    user_info = df.assign(freq=df.groupby(variable)[variable].transform('count')) \
        .sort_values(by=['freq', variable], ascending=[False, True]).loc[:, [variable]]
    variable_info = user_info.sort_values([variable], ascending=[False])
        # x = (frequency.Username)
    frequency = {}
    for item in variable_info[variable]:
        item_date = item[:10]
        if item_date not in frequency.keys():
            frequency[item_date] = 1
        else:
            frequency[item_date] += 1

    year = peak_date[0:4]
    month = peak_date[5:7]
    day = peak_date[8:10]
    gDate = datetime.datetime(int(year), int(month), int(day))
    count_days_infect = 0
    day_tweets = frequency[peak_date]
    infected_count = 0#frequency[peak_date]
    day = 0

    while day_tweets > threshold_start:
        day += 1
        curr_day = gDate - datetime.timedelta(days=day)
        if str(curr_day)[:10] not in frequency.keys():
            break
        day_tweets = frequency[str(curr_day)[:10]]
        infected_count += frequency[str(curr_day)[:10]]
        count_days_infect += 1

    users = np.unique(list(df["Username"]))
    no_users = len(users)

    recovery_count = 0
    count_days_recovered = 0
    day_tweets = 0
    while day_tweets < threshold_recovery:
        day += 1
        curr_day = gDate + datetime.timedelta(days=day)
        if str(curr_day)[:10] not in frequency.keys():
            break
        day_tweets = frequency[str(curr_day)[:10]]
        recovery_count += frequency[str(curr_day)[:10]]
        count_days_recovered += 1




    # option-1
    # df_network = pd.read_csv(f"{config.path_network}networkOfFollowers_stopdeverbreding3.csv")
    #
    # G = nx.from_pandas_edgelist(df_network, 'source', 'target') #Turn df into graph
    # avg_node_degree = nx.average_degree_connectivity(G)
    # print(avg_node_degree)
    # x = (2*len(G.edges))/len(G.nodes)
    # pos = nx.spring_layout(G) #specify layout for visual
    # y = nx.draw_networkx_labels(G, pos, font_size=8)



    # option-2
    # total_followers = list(df_user['followers_count'])[:no_users]
    #
    # avg_followers = sum(total_followers) / no_users
    # median_followers = statistics.median(total_followers)
    # print("1", sum(total_followers))
    # num_nodes = int(sum(total_followers)/200)
    # print("pre", num_nodes)
    # avg_node_degree = int(median_followers/100)
    # print(avg_node_degree)

    # fb_np = nx.from_pandas_edgelist(df_network, source='source', target='target', edge_attr=None, create_using=None, edge_key=None)
    # G_tmp = nx.k_core(fb_np, 20)  # Exclude nodes with degree less than 10
    #
    # num_nodes = G_tmp.number_of_nodes()

    df_network_small = pd.read_csv(f'{config.path_final}networks_all_users_small.csv')
    G_tmp = nx.from_pandas_edgelist(df_network_small, source='source', target='target', edge_attr=None,
                                    create_using=None,
                                    edge_key=None)
    num_nodes = len(G_tmp.nodes)

    print(f"number refined:{num_nodes}")
    G_sorted = pd.DataFrame(sorted(G_tmp.degree, key=lambda x: x[1], reverse=True))
    G_sorted.columns = ['snames', 'degree']

    avg_node_degree = sum(G_sorted['degree'])
    avg_node_degree /= num_nodes
    num_nodes = int(num_nodes)

    infection_rate = (infected_count / (num_nodes)) / count_days_infect
    recovery_rate = (recovery_count/ num_nodes)/ count_days_recovered

    file = open('/Users/myrthehemker/Desktop/MasterThesis/Programming/thesis_mas_model/v1_mas_model/data/dict_variables.pkl', 'wb')

    dict_variables = {"infection_rate": infection_rate, "recovery_rate" : recovery_rate, "num_nodes":num_nodes, "avg_node_degree": avg_node_degree, "threshold_start":threshold_start}
    pickle.dump(dict_variables, file)

    return infection_rate*2, recovery_rate/num_nodes*4, num_nodes, avg_node_degree, threshold_start





#df = pd.read_csv(filepath_or_buffer=config.all_hashtags_except_utrecht, header=0)
hashtag = ['a27', 'amelisweerd']
timeframe = "dayly"
start_date = "2020-45"
#prepare_data_SIR_model(df=df, hashtag=['a27', 'amelisweerd'], timeframe="dayly", start_date="2020-45")
#
# df_select = pd.read_csv(f'data/{hashtag[0]}AND{hashtag[1]}_{start_date}_date_frequency_{timeframe}2.csv')
#
# initialize_SIR_model(df=df_select)
