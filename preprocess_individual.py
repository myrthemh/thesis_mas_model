import pandas as pd

import re
import config
import twitter

import datetime
import time
import os


#link: https://techtldr.com/how-to-get-user-feed-with-twitter-api-and-python/
#analyze user data
def obtain_agent_data(users, user_id="author_id", file_name="userinfo_test",
                      keywords="([A|a]melisweerd)|(verbreding )?(a|A)27|(([Ss]top([Dd]e))??[Vv]erbreding)|(geluidswering)|((Kerngroep)? [Rr]ing[ |][Uu]trecht)|(stikstof(probleem)?)|Rijkswaterstaat|Tracebesluit|SUUNTA"
                               ,
                      hashtag="stopdeverbreding", start_date=None, stop_date=None, total_actions=180, days=True):
    d = {'Jan': "01", 'Feb': "02", 'Mar': "03", 'Apr': "04", 'May': "05", 'Jun': "06",
         'Jul': "07", 'Aug': "08", 'Sep': "09", 'Oct': 10, 'Nov': 11, 'Dec': 12}

    api = twitter.Api(consumer_key=config.consumer_key,
                  consumer_secret=config.consumer_secret,
                  access_token_key=config.access_key,
                  access_token_secret=config.access_secret)

    # Create headers for the data you want to save, in this example, we only want save these columns in our dataset
    user_info = ['author_id', 'name', 'followers_count', 'following', 'favourites_count', 'friends_count', 'description',
                 'created_at_user', 'verified', 'location',
                 'twitter_actions', 'topic_actions', 'total_actions',
                 'twitter_activity', 'topic_twitter_frequency', 'topic_sentiment']

    df_not_analyze = pd.DataFrame(["users_not_found"])

    if start_date and stop_date:
        start_date = datetime.date(day=int(start_date[-2:]), month=int(start_date[5:-3]), year=int(start_date[:4]) )
        stop_date = datetime.date(day=int(stop_date[-2:]), month=int(stop_date[5:-3]), year=int(stop_date[:4]))
        countdown = stop_date - start_date
        total_actions = countdown.days
        print(total_actions)

    file_name = f'{config.path_final}userinfo.csv'

    if os.path.isfile(file_name):
        df_old = pd.read_csv(file_name)  # , index_col=False)
        df_old = df_old[user_info]

        df_old.to_csv(file_name)

    else:
        df_old = pd.DataFrame(columns=[user_info])
    df_users = df_old

    users_not_analyzed = []
    i = 0
    for user in users:
        print("user", user)
        i += 1
        print(i)
        if not str(user) == "nan" and int(user) not in list(df_old["author_id"]):
            # x = api.GetUser(25755728)
            try:
                print(f"found user:{user}")
                get_user = api.GetUser(user_id=user)
                print(get_user.name)
                get_user_tweets = get_tweets_user(user=user, api=api)
                if get_user_tweets != 0:
                    print("get_user_tweets", len(get_user_tweets))
                    start_date_user = get_user_tweets[-1].created_at
                    last_date_user = get_user_tweets[0].created_at

                    start_date_user = datetime.date(day=int(start_date_user[8:10]), month=int(d[start_date_user[4:7]]),
                                                    year=int(start_date_user[-4:]))
                    last_date_user = datetime.date(day=int(last_date_user[8:10]), month=int(d[last_date_user[4:7]]),
                                                   year=int(last_date_user[-4:]))
                    countdown = last_date_user - start_date_user
                    timesteps = countdown.days
                else:
                    # start_date_user = get_user.created_at
                    # last_date_user = start_date_user
                    # timesteps = total_actions
                    #users_not_analyzed.append(user)
                    print(f'user {user} not found')
                    df_not_analyze.loc[len(df_not_analyze)] = [user]
                    df_not_analyze.to_csv(f"{config.path_final}notanalyzed.csv")
                    continue


                # save most important variables of user
                author_id = user
                name = get_user.name
                followers_count = get_user.followers_count
                following = get_user.following
                favourites_count = get_user.favourites_count
                friends_count = get_user.friends_count
                description = get_user.description
                created_at_user = get_user.created_at
                verified = get_user.verified
                location = get_user.location

                # start_date_user = get_user_tweets[-1].created_at
                # last_date_user = get_user_tweets[0].created_at

                # if days:
                #
                #
                #
                # else:
                #     d1 = int(start_date_user[-4:]), int(list(calendar.month_abbr).index(start_date_user[4:7]))
                #     d2 = int(last_date_user[-4:]), int(list(calendar.month_abbr).index(last_date_user[4:7]))
                #     timesteps = diff_month(d2, d1)
                total_tweets = get_user.statuses_count

                twitter_actions = total_tweets
                total_actions = timesteps

                try:
                    if get_user_tweets == 0:
                        topic_actions = get_user_tweets
                        print("total tweets:", total_tweets)
                        total_tweets = 0
                    else:
                        topic_actions = sum([1 for tweet in get_user_tweets
                                      if re.search(f"r'{keywords}'", tweet.text)])

                    print("topic_actions", topic_actions)
                except ZeroDivisionError:
                    topic_actions = 0
                    print("You cannot divide by 0.")

                try:
                    twitter_frequency = total_tweets / timesteps
                except ZeroDivisionError:
                    twitter_frequency = 0
                if twitter_frequency > 1:
                    twitter_frequency = 1

                try:
                    topic_twitter_frequency = topic_actions / twitter_actions
                except ZeroDivisionError:
                    topic_twitter_frequency = 0
                try:
                    topic_sentiment = topic_actions / total_actions
                except ZeroDivisionError:
                    topic_sentiment = 0
                # print("twitter_activity", twitter_activity, "topic_twitter_frequency",
                #       topic_twitter_frequency, "topic_sentiment",topic_sentiment)
                # print("ratio obtained tweets", len(get_user_tweets)/total_tweets)
                # print("twitter_actions", twitter_actions, "topic_actions", topic_actions, 'total_actions', total_actions )
                row = [author_id, name, followers_count, following, favourites_count, friends_count, description,
                       created_at_user, verified, location,
                       twitter_actions, topic_actions, total_actions,
                       twitter_frequency, topic_twitter_frequency, topic_sentiment
                       ]
                #df_users.loc[len(df_users)] = row
                df_users.loc[len(df_users.index)] = row
                df_users.to_csv(file_name)
                print(f"total users: {len(df_users)}")

            except twitter.TwitterError:
                #users_not_analyzed.append(user)
                print(f'user {user} not found')
                df_not_analyze.loc[len(df_not_analyze)] = [user]
                df_not_analyze.to_csv(f"{config.path_final}notanalyzed.csv")

            # except twitter.TwitterError as e:
            #     print(f"Not working for {user}")
            #     users_not_analyzed.append(users)



    #df_users.to_csv(file_name)
    # df_users.close()
    print(len(df_users))
    print(f"User not analyzed {len(users_not_analyzed)}")

    return df_users


def get_tweets_user(user, api):
    tweets = api.GetUserTimeline(user_id=user, count=200)
    if len(tweets) == 0:
        return 0
    all_tweets = []
    all_tweets.extend(tweets)
    oldest_id = tweets[-1].id
    while True:
        tweets = api.GetUserTimeline(user_id=user,
                                   # 200 is the maximum allowed count
                                   count=200,
                                   include_rts=False,
                                   max_id=oldest_id - 1,
                                   )
        if len(tweets) == 0:
            break
        oldest_id = tweets[-1].id
        all_tweets.extend(tweets)
        #print(all_tweets)

    df = pd.DataFrame(columns=["tweet", "date_time"])

    for i in all_tweets:
        #print(i.text, i.created_at)
        df = df.append({"tweet": i.text, "date_time": i.created_at}, ignore_index=True)

    # print(f"size:{len(df)}")
    # visualize_freq(df=df, date_time="date_time", hashtag=None, user=user,
    #                    timeframe="weekly", start_date="2021-01", skip=False)
    return all_tweets


def diff_month(d1, d2):
    return (d1[0] - d2[0]) * 12 + d1[1] - d2[1]


def add_not_analyzed(df_users, file_name, users_not_analyzed, source, target, keywords="([A|a]melisweerd)|(verbreding )?(a|A)27|(([Ss]top([Dd]e))??[Vv]erbreding)|(geluidswering)|((Kerngroep)? [Rr]ing[ |][Uu]trecht)|(stikstof(probleem)?)|Rijkswaterstaat|Tracebesluit|SUUNTA"
                      ):
        d = {'Jan': "01", 'Feb': "02", 'Mar': "03", 'Apr': "04", 'May': "05", 'Jun': "06",
         'Jul': "07", 'Aug': "08", 'Sep': "09", 'Oct': 10, 'Nov': 11, 'Dec': 12}

        df_not_analyze = pd.DataFrame(["users_not_found_2"])

        api = twitter.Api(consumer_key=config.consumer_key,
                          consumer_secret=config.consumer_secret,
                          access_token_key=config.access_key,
                          access_token_secret=config.access_secret)

        # Create headers for the data you want to save, in this example, we only want save these columns in our dataset
        user_info = ['author_id', 'name', 'followers_count', 'following', 'favourites_count', 'friends_count',
                     'description',
                     'created_at_user', 'verified', 'location',
                     'twitter_actions', 'topic_actions', 'total_actions',
                     'twitter_activity', 'topic_twitter_frequency', 'topic_sentiment']
        df_users = df_users[user_info]
        print(len(users_not_analyzed))
        for idx, user in enumerate(users_not_analyzed):
            print("id:", idx, user)
            if idx == 8000:
                print(len(users_not_analyzed))
            if user not in list(df_users["author_id"]) and user != "users_not_found":

                try:
                    print(f"found user: {user}")
                    get_user = api.GetUser(user_id=int(user))
                    print(get_user.name)

                    # save most important variables of user
                    author_id = user
                    name = get_user.name
                    followers_count = get_user.followers_count
                    following = get_user.following
                    favourites_count = get_user.favourites_count
                    friends_count = get_user.friends_count
                    description = get_user.description
                    created_at_user = get_user.created_at
                    verified = get_user.verified
                    location = get_user.location
                    total_tweets = get_user.statuses_count

                    twitter_actions = total_tweets
                    start_date = datetime.date(day=int(created_at_user[8:10]), month=int(d[created_at_user[4:7]]),
                                                        year=int(created_at_user[-4:]))
                    timesteps = datetime.date(2022, 4, 5) - start_date
                    total_actions = timesteps.days
                    try:
                        twitter_frequency = total_tweets / total_actions
                    except ZeroDivisionError:
                        twitter_frequency = 0

                    if twitter_frequency > 1:
                        twitter_frequency = 1

                    try:
                        get_user_tweets = get_tweets_user(user=user, api=api)
                        if not get_user_tweets == 0:
                            topic_actions = sum([1 for tweet in get_user_tweets
                                             if re.search(f"r'{keywords}'", tweet.text)])
                        else:
                            if int(user) in source:
                                print(f"source:{user}")
                                try:
                                    topic_actions = 0.2 * total_actions
                                except ZeroDivisionError:
                                    topic_actions = 0

                            elif int(user) in target:
                                topic_actions = 0
                    except twitter.TwitterError:
                        if int(user) in source:
                            print(f"source:{user}")
                            try:
                                topic_actions = 0.2 * total_actions
                            except ZeroDivisionError:
                                topic_actions = 0

                        elif int(user) in target:
                            topic_actions = 0
                    try:
                        topic_twitter_frequency = topic_actions / twitter_actions
                    except ZeroDivisionError:
                        topic_twitter_frequency = 0
                    try:
                        topic_sentiment = topic_actions / total_actions
                    except ZeroDivisionError:
                        topic_sentiment = 0

                    row = [author_id, name, followers_count, following, favourites_count, friends_count, description,
                           created_at_user, verified, location,
                           twitter_actions, topic_actions, total_actions,
                           twitter_frequency, topic_twitter_frequency, topic_sentiment
                           ]

                    df_users.loc[len(df_users.index)] = row
                    df_users.to_csv(file_name)
                    print(f"total users: {len(df_users)}")

                except twitter.TwitterError:

                    print(f'user {user} not found')
                    df_not_analyze.loc[len(df_not_analyze)] = [user]
                    df_not_analyze.to_csv(f"{config.path_final}notanalyzed_twice.csv")


def add_begin_topic_action(df_users, stop_date, fname_users_check=f"{config.path_final}metadata/df_analyzed_FINAL.csv",
                           keywords ="([A|a]melisweerd.*|verbreding.*)?(a|A)27|(([Ss]top.*([Dd]e))??.*[Vv]erbreding)|(geluidswering)|((Kerngroep)? [Rr]ing[ |][Uu]trecht)|Tracebesluit|SUUNTA"):
    user_info = ['author_id', 'name', 'followers_count', 'following', 'favourites_count', 'friends_count',
                 'description',
                 'created_at_user', 'verified', 'location',
                 'twitter_actions', 'topic_actions', 'total_actions',
                 'twitter_activity', 'topic_twitter_frequency', 'topic_sentiment']

    df = pd.DataFrame(columns=["tweet", "date_time"])
    df_spec = pd.DataFrame(columns=["tweet", "date_time"])

    api = twitter.Api(consumer_key=config.consumer_key,
                      consumer_secret=config.consumer_secret,
                      access_token_key=config.access_key,
                      access_token_secret=config.access_secret)
    df_users = df_users[user_info]
    df_users.drop_duplicates()

    d = {'Jan': "01", 'Feb': "02", 'Mar': "03", 'Apr': "04", 'May': "05", 'Jun': "06",
         'Jul': "07", 'Aug': "08", 'Sep': "09", 'Oct': 10, 'Nov': 11, 'Dec': 12}

    if not os.path.isfile(f"{config.path_final}userinfo_extra2.csv"):
        df_user_extra = df_users
        df_user_extra["first_topic_actions"] = 0
        df_user_extra["first_total_actions"] = 180
        df_user_extra["first_twitter_actions"] = df_users["twitter_actions"]
    else:
        df_user_extra = pd.read_csv(f"{config.path_final}userinfo_extra2.csv")

    if not os.path.isfile(fname_users_check):
        df_analyzed_first = pd.DataFrame(columns=['user_id'])
    else:
        df_analyzed_first = pd.read_csv(fname_users_check)
        df_analyzed_first = df_analyzed_first[['user_id']]

    for idx, user in df_users.iterrows():
        print(idx)
        if user["topic_actions"] > 0 and user["author_id"] not in list(df_analyzed_first["user_id"]):
            x = int(user["author_id"])
            print("user", int(user["author_id"]))
            if idx != 60:
                test = False
                tweets = api.GetUserTimeline(user_id=x, count=200)
            else:
                test = True
                print("wait")
                time.sleep(15000)
            if test:
                tweets = api.GetUserTimeline(user_id=x, count=200)

            all_tweets = []
            all_tweets.extend(tweets)
            oldest_id = tweets[-1].id
            while True:
                tweets = api.GetUserTimeline(user_id=x,
                                             # 200 is the maximum allowed count
                                             count=200,
                                             include_rts=False,
                                             max_id=oldest_id - 1,
                                             )
                if len(tweets) == 0:
                    break
                oldest_id = tweets[-1].id
                all_tweets.extend(tweets)
                # print(all_tweets)


            all_tweets_select = [i for i in all_tweets if datetime.date(day=int(i.created_at[8:10]), month=int(d[i.created_at[4:7]]),
                                     year=int(i.created_at[-4:])) < stop_date ]

            topic_actions = sum([1 for tweet in all_tweets_select
                                 if re.search(f"r'{keywords}'", tweet.text)])
            twitter_actions = sum([1 for tweet in all_tweets_select])
            if len(all_tweets_select):
                first_tweet = all_tweets_select[-1]
                total_actions = (stop_date - datetime.date(day=int(first_tweet.created_at[8:10]), month=int(d[first_tweet.created_at[4:7]]),
                                          year=int(first_tweet.created_at[-4:])) ).days
                df_user_extra[idx, "first_total_actions"] = total_actions

            df_user_extra[idx, "first_twitter_actions"] = twitter_actions
            df_analyzed_first.loc[len(df_analyzed_first.index)] = [x]
            df_analyzed_first.to_csv(fname_users_check)

            if topic_actions > 0:
                print("user", user["name"], topic_actions)
                df_user_extra[len(df_user_extra.index)] = topic_actions
                df_user_extra.to_csv(f"{config.path_final}userinfo_extra2.csv")

    #df_user_extra.to_csv(f"{config.path_final}userinfo_extra2.csv")

df_users = pd.read_csv(f"{config.path_final}userinfo.csv")
add_begin_topic_action(df_users=df_users, stop_date=datetime.date(year=2020, month=9, day=10))


# get the user ids of the list of usernames is provided
def obtain_user_ids(list_usernames):
    api = twitter.Api(consumer_key=config.consumer_key,
                      consumer_secret=config.consumer_secret,
                      access_token_key=config.access_key,
                      access_token_secret=config.access_secret)
    ids = []
    for username in list_usernames:
        user_info = api.GetUser(screen_name=username)

        ids.append(user_info.id)
        print(user_info.name, user_info.id)
    return ids


