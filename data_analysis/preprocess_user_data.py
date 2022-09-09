import pandas as pd
import csv
import re
import config
import twitter


#link: https://techtldr.com/how-to-get-user-feed-with-twitter-api-and-python/
#analyze user data
def obtain_agent_data(api, df, user_id="author_id", file_name="userinfo", keywords=""):

    # Create headers for the data you want to save, in this example, we only want save these columns in our dataset
    user_info = ['author_id', 'name', 'followers_count', 'following', 'favourites_count', 'friends_count', 'description', 'created_at_user', 'verified', 'location', 'tweets_topic']
    df_users = pd.DataFrame(columns=user_info)
    users = list(dict.fromkeys(df[user_id]))

    csvFile = open(f"{file_name}.csv", "a", newline="", encoding='utf-8')
    csvWriter = csv.writer(csvFile)

    # Create headers for the data you want to save, in this example, we only want save these columns in our dataset
    csvWriter.writerow(user_info)  # , 'username', 'name', 'followers count', 'following count', 'tweet count', 'description', 'listed count'])

    for user in users:
        get_user = api.GetUser(user_id=user)
        get_user_tweets = api.GetUserTimeline(user_id=user, count=1000)
        amelisweerd_count = sum([1 for tweet in get_user_tweets if re.search(r'([A|a]melisweerd)|([Ss]top[Dd]e[Vv]erbreding)|(bomen)', tweet.text)])/200
        if len(get_user_tweets)!=200:
            print("different length:", get_user.name)
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
        tweets_topic = amelisweerd_count

        row = [author_id, name, followers_count, following, favourites_count, friends_count, description, created_at_user, verified, location, tweets_topic]
        print(row)
        df_users.loc[len(df_users)] = row
        csvWriter.writerow(row)

    df_users.to_csv(f'{config.output_dir}{file_name}.csv')
    csvFile.close()

    return df_users


api = twitter.Api(consumer_key=config.consumer_key,
                  consumer_secret=config.consumer_secret,
                  access_token_key=config.access_key,
                  access_token_secret=config.access_secret)


print(api.VerifyCredentials())
df = pd.read_csv(sep="\t", filepath_or_buffer=f"{config.path_hashtag_tweets_processed}twitterdata_StopDeVerbreding_preprocessed.csv" )

obtain_agent_data(api, df, file_name=f"user_info_all_hashtags", user_id="author id")
