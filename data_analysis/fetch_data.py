import snscrape.modules.twitter as sntwitter
import pandas as pd
from collections import Counter


#link:
# Algorithm 1: obtain all important tweets
def scrape_tweets(start_query, start_date='2008-01-01', end_date='2022-03-01',
                  threshold=100):
    # Creating list to append tweet data to
    tweets_list2 = []
    hashtags = [start_query]
    old_hashtags = []



    # Using TwitterSearchScraper to scrape data and append tweets to list
    while len(hashtags) != 0:
        hashtag = hashtags.pop()
        old_hashtags.append(hashtag[1:])
        query = f'{hashtag} since:{start_date} until:{end_date}'
        print(f"loop over {hashtag}")
        if not hashtag == "#utrecht":

            for i, tweet in enumerate(
                    sntwitter.TwitterSearchScraper(query).get_items()):
                tweets_list2.append([tweet.date, tweet.id, tweet.content, tweet.user.username,
                                     tweet.hashtags, tweet.retweetCount, tweet.likeCount,
                                     tweet.replyCount, tweet.quoteCount, tweet.inReplyToUser,
                                     tweet.outlinks, tweet.tcooutlinks, tweet.media])

                if i > 10000:
                    break
            print("number of tweets", i, hashtag)

            # check for over hashtags
            x = [h[4] for h in tweets_list2]
            flat_list = list()
            for sub_list in x:
                if sub_list != None:
                    flat_list += sub_list

            hash_list = [i.lower() for i in flat_list]
            test = Counter(hash_list)

            # only look at max ten most used hashtags
            for item in list(test.items())[:10]:

                if item[1] > threshold and item[0] not in old_hashtags:
                    print(item[0], item[1])
                    if f'#{item[0]}' not in hashtags:
                        hashtags.append(f'#{item[0]}')

            print('hashtags', hashtags)

    tweets_df2 = pd.DataFrame(tweets_list2, columns=['Datetime', 'Tweet Id', 'Text', 'Username',
                                                     'Hashtags', 'RetweetCount', 'LikeCount',
                                                     'ReplyCount', 'QuoteCount', 'InReplyToUser',
                                                     'OutLinks', 'TCooutLinks', 'Media'])

    tweets_df2.to_csv(f"data/test_{start_query}_{start_date}-{end_date}_all_hashtags-tweets-{len(tweets_df2)}.csv")


scrape_tweets(start_query="#stopdeverbreding")
