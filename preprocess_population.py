import pandas as pd
import config
import matplotlib.pyplot as plt
import numpy as np
from pattern.nl import sentiment
import re
import datetime
import time
import pickle


# link: https://techtldr.com/how-to-get-user-feed-with-twitter-api-and-python/
# analyze user data
def obtain_population_data(df, date="Datetime", file_name="population_info", timeframe="month"):
    # sort on date
    df_population = df.sort_values(by='Datetime', ascending=False)

    time_steps = []
    sentiment = []
    objectivity = []

    t = 0
    curr_year = df_population.iloc[0][date][:4]
    if timeframe == "monthly":
        curr_time_step = df_population.iloc[0][date][5:7]

    if timeframe == "weekly":
        x = df_population.iloc[0][date]
        curr_time_step = datetime.date(int(x[:4]), int(x[5:7]), int(x[8:10])).isocalendar()[1]

    for idx, row in enumerate(df_population.iterrows()):
        if timeframe == "monthly":
            tweet_time_step = df_population.iloc[0][date][5:7]

        if timeframe == "weekly":
            x = df_population.iloc[0][date]
            tweet_time_step = datetime.date(int(x[:4]), int(x[5:7]), int(x[8:10])).isocalendar()[1]

        tweet_year = df_population.iloc[idx][[date]].Datetime[:4]

        # print(str(df_population.iloc[idx][[date]])[5:7])
        if tweet_year != curr_year or tweet_time_step != curr_time_step:
            t += 1
        time_steps.append(t)

        # sent, obj = sentiment(df_population.iloc[row][['text']])
        # sentiment.append(sent)
        # objectivity.append(obj)

    df_population['time_step'] = time_steps
    # df_population['sentiment'] = sentiment
    # df_population['objectivity'] = objectivity

    df_population.to_csv(f'{config.output_dir}{file_name}_{timeframe}.csv')

    return df


# add sentiment to tweets

def add_sentiment(df, text="text", filename="sentiment_amelisweerd500"):
    sa = [sentiment(tweet)[0] for tweet in df[text]]
    objective = [sentiment(tweet)[1] for tweet in df[text]]
    print(sa)
    df['sa'] = sa
    df['objective'] = objective

    df.to_csv(f'{config.path_sentiment}{filename}.csv', decimal='.')
    df.to_pickle(f'{config.path_sentiment}{filename}.pkl')
    return df


def visualize_freq_year(df: pd.DataFrame, date_time="Datetime"):
    select_date = df[date_time]

    select_years = [date[:4] for date in select_date if not re.search('[a-zA-Z]', date)]
    keys, counts = np.unique(select_years, return_counts=True)
    plt.figure(figsize=(10, 6))
    plt.bar(keys, counts)
    plt.xticks(rotation=90)
    plt.xlabel("Date (years)")
    plt.ylabel("Number of tweets ")
    # plt.subplots_adjust(bottom=0.34)
    # plt.title(f"Number of tweets per year")
    plt.savefig(f'{config.path_figures}/tweets a year-selected hashtags.png')
    plt.show()

year_test = False
if year_test:
    df = pd.read_csv(filepath_or_buffer=f"{config.path_final}df_selected.csv", header=0)
    visualize_freq_year(df)


def visualize_freq(df: pd.DataFrame, date_time="Datetime", hashtag="stopdeverbreding",
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
                df_new[date_time]]# if not re.search('[a-zA-Z]', t)]
        if date_diff:

            date = [f"{t[-4:]}-{d[t[4:7]]}-{t[8:10]}" for t in df_new[date_time]]

    df_new = df_new[:len(date)].assign(date=date)


    if type(hashtag) == list:
        df_new.to_csv(f'{config.output_dir_frequency}dayly/{hashtag[0]}AND{hashtag[1]}_{start_date}_date_frequency_{timeframe}.csv')
        df_new.to_pickle(f'{config.output_dir_frequency}dayly/{hashtag[0]}AND{hashtag[1]}_{start_date}_date_frequency_{timeframe}.pkl')
    else:
        if not external:
            df_new.to_csv(f'{config.output_dir_frequency}dayly/{hashtag}_{start_date}_date_frequency_{timeframe}.csv')

    plt.figure(figsize=(10, 6))

    keys, counts = np.unique(date, return_counts=True)

    if not skip:
        if timeframe == "monthly":
            # keys = [i for i in keys if int(i[:4]) > int(start_date)  ]
            for idx, x in enumerate(keys):
                if x[:4] > start_date:
                    print(idx)
                    break
            keys = keys[idx:]
            counts = counts[idx:]

            x = pd.date_range(start=str(keys[0]), end=str(keys[-1]), freq="M").astype(
                "period[M]")  # .difference(df.index)
            for idx, i in enumerate(x):
                if str(i) not in keys:
                    keys = np.insert(keys, idx, str(i))
                    counts = np.insert(counts, idx, 0)
            plt.bar(keys[:-2], counts[:-2])

        elif timeframe == "weekly":
            if not start_date:
                year = int(keys[0][2:6])
                t_start = int(keys[0][-2:])
            else:
                year = int(start_date[:4])
                t_start = int(start_date[5:7])

            x_keys = []
            x_values = []
            for idx, i in enumerate(range(t_start, 53)):
                new_date = time.asctime(time.strptime('{} {} 1'.format(year, i-1), '%Y %W %w'))  # f"y:{year} w:{i}"
                new_date = f"{new_date[:11]} {new_date[-4:]}"
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

                        new_date = time.asctime(time.strptime('{} {} 1'.format(year, j-1), '%Y %W %w'))
                        new_date = f"{new_date[:11]} {new_date[-4:]}"
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
            if start_date:
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
                # curr_day = gDate + datetime.timedelta(days=6)
                # month_end, day_end = d[curr_day[4:7]], new_date[8:10]
                new_date = f"{day}-{month}-{year}"

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

    # x_labels= ["December", "January", "February", "March"]
    #x_ticks = ["2020-12-01",  "2021-01-05", "2021-02-01", "2021-03-01"]
    if timeframe == 'dayly':
        x_labels = [x_keys[index] for index in range(1, len(x_keys), 7)]
        plt.xticks(rotation=90, ticks=x_labels, labels=x_labels)
    else:
        plt.xticks(rotation=90)


    # x_labels = ["Jan 2010", "Jan 2011", "Jan 2012", "Jan 2013", "Jan 2014", "Jan 2015", "Jan 2016", "Jan 2017", "Jan 2018", "Jan 2019", "Jan 2020", "Jan 2021"]
    # x_ticks = ["2010-01", "2011-01", "2012-01", "2013-01", "2014-01", "2015-01", "2016-01", "2017-01", "2018-01", "2019-01", "2020-01", "2021-01"]

    # plt.xticks(rotation=90, ticks=x_labels, labels=x_labels)
    if timeframe == "monthly":
        plt.xlabel("Date (monthly)")
    if timeframe == "weekly":
        plt.xlabel("Date (weekly)")
    if timeframe == "dayly":
        plt.xlabel("Date (dayly)")

    plt.ylabel("Number of tweets")
    plt.subplots_adjust(bottom=0.34)
    if not hashtag:
        hashtag = "all obtained"
   # plt.title(f"Number of tweets with {hashtag} over time")
   #  if type(hashtag) == list and len(hashtag) == 2:
   #      plt.title(f"Number of tweets with #{hashtag[0]} and #{hashtag[1]} over time")
    plt.tight_layout()
    if external is not None:
        start_date = f"{start_date}_{external}"
        plt.title(f"Number of tweets of user {user} tweeting about {external}")
        plt.savefig(f'{config.path_figures}/{timeframe}/{user}_{start_date}_date_frequency_{timeframe}_{external}.png')
    elif user:
        plt.savefig(f'{config.path_figures}/{timeframe}/{user}_{start_date}_date_frequency_{timeframe}.png')
    else:
        if type(hashtag) == list:
            plt.savefig(f'{config.path_figures}/{timeframe}/{string_match}_{start_date}_date_frequency_{timeframe}-both.png')
        else:
            plt.savefig(f'{config.path_figures}/{hashtag}_{start_date}_date_frequency_{timeframe}-both.png')

    plt.show()


def plot_freq(df: pd.DataFrame, date_time = "Datetime", hashtag = None, print_name="test",
                   timeframe="dayly", start_date="2020-46", skip=False, user=None, external=None,  stop_date="2021-20", date_diff=False):
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
                df_new[date_time]]# if not re.search('[a-zA-Z]', t)]
        if date_diff:

            date = [f"{t[-4:]}-{d[t[4:7]]}-{t[8:10]}" for t in df_new[date_time]]

    df_new = df_new.assign(date=date)
    # print("length:", len(df_new))
    # df_new = df_new[pd.to_numeric(df[date_time], errors='coerce').notnull()]
    # print("length:", len(df_new))

    if type(hashtag) == list:
        df_new.to_csv(f'{config.output_dir_frequency}dayly/{hashtag[0]}AND{hashtag[1]}_{start_date}_date_frequency_{timeframe}.csv')
        df_new.to_pickle(f'{config.output_dir_frequency}dayly/{hashtag[0]}AND{hashtag[1]}_{start_date}_date_frequency_{timeframe}.pkl')
    else:
        if not external:
            df_new.to_csv(f'{config.output_dir_frequency}dayly/{hashtag}_{start_date}_date_frequency_{timeframe}.csv')

    # plt.figure(figsize=(40, 40))
    plt.rc('font', size=40)
    plt.rc('axes', labelsize=40)# controls default text size
    plt.rc('axes', titlesize=40)  # fontsize of the title
    plt.rc('xtick', labelsize=20)
    plt.rc('ytick', labelsize=20)

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
                new_date = time.asctime(time.strptime('{} {} 1'.format(year, i), '%y d %d'))  # f"y:{year} w:{i}"
                new_date = new_date[:9] + new_date[-4:]
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
                            time.strptime('{} {} 1'.format(year, j), '%Y %M %D'))  # f"y:{year} w:{j}"
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
                new_date = time.asctime(time.strptime('{} {} 1'.format(year, i), '%Y %W %w'))
                month = d[new_date[4:7]]
                day = new_date[8:10]
                gDate = datetime.datetime(int(year), int(month), int(day))
                curr_day = gDate + datetime.timedelta(days=6)

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
            if year == int(stop_date[:4]):
                for j in range(1, t_start - 52):

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
            #plt.plot(x_keys, x_values, label="Real world data")
    else:
        print("hoi")
       # plt.plot(keys, counts)
    return x_values

    file_name = "/Users/myrthehemker/Desktop/MasterThesis/Programming/thesis_mas_model/v3b_mas_model/results/results_5.csv"
    df_results = pd.read_csv(file_name)
    y2 = list(df_results["results"].values)
    plt.plot(x_keys, y2[:len(x_keys)], label="Simulation")
    plt.rc('legend', fontsize=30)  # fontsize of the leg
    plt.legend()


    plt.xticks(rotation=90)
    plt.subplots_adjust(bottom=0.34)
    plt.title(f"Number of tweets with #{hashtag} over time")


    # naming the x axis
    plt.yticks(range(0,250,10))
    plt.xlabel('Time')
    # naming the y axis
    plt.ylabel('Number of tweets')
    plt.ylim(bottom=0, top=250)

    # giving a title to my graph
    plt.title('Results simulation version 2')

    plt.savefig(f'{config.path_figures}/final/simulation/{print_name}')

    # function to show the plot
    plt.show()


# df = pd.read_csv(filepath_or_buffer=config.all_hashtags_except_utrecht, header=0)
df = pd.read_csv(filepath_or_buffer=f"{config.path_final}df_selected.csv", header=0)
# visualize_freq(df, hashtag=None, timeframe="monthly", start_date="2019")#, stop_date="2021-4")
# visualize_freq(df, hashtag=None, timeframe="weekly", start_date="2020-43", stop_date="2021-4")
#
# print("check")
# visualize_freq(df, hashtag=None, timeframe="dayly", start_date="2020-45", stop_date="2021-4")


#visualize_freq(df, hashtag="stopdeverbreding", timeframe="weekly", start_date="2020-30", stop_date="2021-4")
#
#
# visualize_freq(df, hashtag=['a27', 'amelisweerd'], timeframe="weekly", start_date="2020-48")  # , stop_date="2021-48")
#
#
# hashtags = ["amelisweerd", 'amelisweerdnietgeasfalteerd', 'kappenmetkappen', 'a27']
# for hashtag in hashtags:
#     visualize_freq(df, hashtag=hashtag, timeframe="weekly", start_date="2020-45")


# visualize_freq(df, hashtag=['amelisweerd', 'a27'], timeframe="weekly", start_date="2020-45")
# df = pd.read_csv(filepath_or_buffer=f"{config.path_final}df_selected.csv", header=0)
# visualize_freq(df, hashtag=None, timeframe="dayly",date_diff=True)


def analyze_data_peak(df, date_column="date", date_peak="2020-12-06", variables=["Username"]):
    print(len(df))
    selection = df[df[date_column] == date_peak]
    for variable in variables:

        user_info = selection.assign(freq=selection.groupby(variable)[variable].transform('count')) \
            .sort_values(by=['freq', variable], ascending=[False, True]).loc[:, ["Username", variable]]
        if variable in ["ReplyCount", "RetweetCount", "OutLinks", "InReplyToUser", "LikeCount", "QuoteCount"]:
            variable_info = user_info.sort_values([variable], ascending=[False])
            # x = (frequency.Username)
            frequency = {}
            for name, item in zip(variable_info["Username"], variable_info[variable]):
                if name not in frequency.keys():
                    frequency[name] = item
            # print(frequency)

        else:
            frequency = dict()
            list_freq = list(user_info[variable])
            # list_id = list(selection.Username.T)

            for item in list_freq:
                frequency[item] = list_freq.count(item)
            print(f"With total users: {len(frequency)} and total tweets: {len(selection)}")

        print(f"variable:{variable}")
        print(f"User who posted most about it on {date_peak}:")
        for i in list(frequency.items())[:3]:
            print(f"{i[0]}: {i[1]}")

#df = pd.read_csv(f'{config.output_dir_frequency}dayly/a27ANDamelisweerd_2020-48_date_frequency_dayly.csv')
#df = pd.read_csv(f'{config.output_dir_frequency}dayly/stopdeverbreding_2021-7_date_frequency_dayly.csv')
#analyze_data_peak(df, date_column="date", date_peak="2021-03-10", variables=["Username", "ReplyCount", "RetweetCount", "OutLinks", "InReplyToUser", "LikeCount", "QuoteCount"])
#analyze_data_peak(df, date_column="date", date_peak="2020-12-05")


def visualize_sentiment(df: pd.DataFrame, datetime="Datetime", measure="sa", hashtag="stopdeverbreding"):
    if not hashtag:
        df_new = df[df.apply(lambda r: r.str.contains(hashtag, case=False).any(), axis=1)].sort_values(by='Datetime',ascending=True)
    else:
        df_new = df

    df_new = df_new.sort_values(by=datetime, ascending=True)
    date = [t[:7] for t in df_new[datetime] if not re.search('[a-zA-Z]', t)]

    sentiment = [t for t in df_new[measure]]


    # date = date[310:-40]
    # sentiment = sentiment[310:-40]
    score = 0
    n_tweets = 0
    sentiment_dict = {}
    for idx, i in enumerate(date):
        if idx != len(date) - 1:
            if i == date[(idx + 1)]:
                score += sentiment[idx]
                n_tweets += 1
            else:
                try:
                    sentiment_dict[i] = score / n_tweets
                    if n_tweets < 20:
                        sentiment_dict[i] = 0
                except ZeroDivisionError:
                    sentiment_dict[i] = 0
        else:
            try:
                sentiment_dict[i] = score / n_tweets
            except ZeroDivisionError:
                sentiment_dict[i] = 0

    plt.figure(figsize=(15, 8))

    keys = list(sentiment_dict.keys())
    counts = list(sentiment_dict.values())

    x = pd.date_range(start=str(keys[0]), end=str(keys[-1]), freq="M").astype("period[M]")  # .difference(df.index)

    for idx, i in enumerate(x):
        if str(i) not in keys:
            keys = np.insert(keys, idx, str(i))
            counts = np.insert(counts, idx, 0)

    plt.bar(keys, counts)
    if measure == "sa":
        plt.ylabel("Sentiment")
    else:
        plt.ylabel("Objectivity")
    plt.xlabel("Date (months)")

    x_labels = [date[index] for index in range(1, len(date), 12)]

    #plt.xticks(rotation=90,  x_ticks=x_labels, x_labels=x_labels)
    plt.subplots_adjust(bottom=0.34)
    if measure == "sa":
        measure = "sentiment"
    #plt.title(f"{measure} with #{hashtag} over time")
    plt.tight_layout()
    plt.savefig(f'{config.path_figures}_{measure}_overtime.png')
    plt.show()

# df_all_hashtags = pd.read_csv(filepath_or_buffer=f"{config.all_hashtags_except_utrecht}" )
# add_sentiment(df_all_hashtags, text="Text", filename="sentiment-all_hashtags-tweets-717")
sentiment_test = False
if sentiment_test:
    df_all_hashtags = pd.read_csv(filepath_or_buffer=f"{config.path_final}df_selected.csv" )
    df_sentiment = add_sentiment(df_all_hashtags, text="Text", filename="sentiment-all_hashtags-tweets-all-final")
    visualize_sentiment(df_sentiment)
    visualize_sentiment(df_sentiment, measure="objective")

# hashtags = ["amelisweerd", 'amelisweerdnietgeasfalteerd', 'kappenmetkappen', 'a27']
# for hashtag in hashtags:
#     visualize_sentiment(df_sentiment, hashtag=hashtag)
#     visualize_sentiment(df_sentiment, measure="objective", hashtag=hashtag)

# df = pd.read_csv(filepath_or_buffer=f"/Users/myrthehemker/Desktop/MasterThesis/Programming/thesis_mas_model/data_analysis/data/test_#stopdeverbreding_2008-01-01-2022-03-01_all_hashtags-tweets-35533.csv" )
#
# for hashtag in hashtags:
#     visualize(df, hashtag=hashtag)
