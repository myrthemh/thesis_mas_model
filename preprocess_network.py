import pandas as pd
import config
import os
import tweepy


# source: https://towardsdatascience.com/how-to-download-and-visualize-your-twitter-network-f009dbbf107b
def create_network_data(user_list,  user_ID=False, df_name='networks_all_users'):

    auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
    auth.set_access_token(config.access_key, config.access_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    if os.path.isfile(df_name):
        df_output = pd.read_csv(df_name)
        sources = list(df_output["source"])
        len_source = len(list(set(sources)))
        print("hoi", len_source)
    else:
        sources = []
        df_output = pd.DataFrame(columns=['source', 'target'])  # Empty DataFrame

        for userID in user_list:

            print("user", userID)
            followers = []
            follower_list = []

            # fetching the user
            try:
                if user_ID:
                    user = api.get_user(user_id=userID)
                else:
                    user = api.get_user(screen_name=userID)

                if str(user.id_str) not in sources: #str(userID) != "Kookgek" and
                    sources.append(userID)
                # fetching the followers_count
                    followers_count = user.followers_count

                    #
                    try:

                        for page in tweepy.Cursor(api.get_follower_ids, user_id=user.id_str).pages():
                            followers.extend(page)

                            if followers_count >= 5000:  # Only take first 5000 followers
                                print("above 5000")
                                break
                    except tweepy.TweepyException:
                        print("error")
                        continue
                    follower_list.append(followers)
                    temp = pd.DataFrame(columns=['source', 'target'])
                    sources.append(user.id_str)
                    temp['target'] = follower_list[0]
                    temp['source'] = user.id_str
                    df_output = df_output.append(temp)
                    print(f"add one, now {len(list(set(df_output['source'])))} users")
                    df_output.to_csv(df_name)
            except tweepy.TweepyException:
                print(f"Not working for {userID}")
    return df_output
