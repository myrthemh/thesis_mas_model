import pandas as pd
import config



#link: https://techtldr.com/how-to-get-user-feed-with-twitter-api-and-python/
#analyze user data
def obtain_population_data(df, date="Datetime", file_name="population_info"):

    # sort on date
    df_population = df.sort_values(by='Datetime')

    time_steps = []
    sentiment = []
    objectivity = []

    t = 0
    curr_month, curr_year = df_population.iloc[0]['Datetime']
    for row in df_population:
        if df_population.iloc[row][[date]][1:2] != curr_month or df_population.iloc[row][[date]][1:2] != curr_year:
            t += 1
        time_steps.append(t)

        sent, obj = sentiment(df_population.iloc[row][['text']])
        sentiment.append(sent)
        objectivity.append(obj)

    df_population['time_step'] = time_steps
    df_population['sentiment'] = sentiment
    df_population['objectivity'] = objectivity

    df_population.to_csv(f'{config.output_dir}{file_name}.csv')

    return df


df = pd.read_csv(sep="\t", filepath_or_buffer=f"{config.path_hashtag_tweets_processed}twitterdata_StopDeVerbreding_preprocessed.csv" )

obtain_population_data(df, file_name=f"user_info_all_hashtags")
