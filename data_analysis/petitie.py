import pandas as pd
from matplotlib import pyplot as plt
import collections
import datetime as dt
import config
import numpy as np
import datetime
import time
from matplotlib.ticker import FuncFormatter

df = pd.read_csv("/Users/myrthehemker/Desktop/MasterThesis/Programming/thesis_twitter_analysis/data/final/datapetities_raw.csv")

# obtain all number of signatures over time
sign_dates = df["signed_at"][20:]
sign_date = [date[:10] for date in sign_dates]

x = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in sign_date]

x = collections.Counter(sign_date).keys()
y = collections.Counter(sign_date).values()

fig, ax = plt.subplots()
plt.figure(figsize=(20,10))


formatter = FuncFormatter(lambda y, pos: "%d%%" % (y))
ax.yaxis.set_major_formatter(formatter)
# plt.bar(df, 'signed_at', ax=ax, kind='bar', xlabel='Date', ylabel='Number of sign petitions')
plt.bar(x, y)

plt.xticks(rotation=90)
plt.xlabel("Date (days)")
plt.ylabel("Number of signed petitions ")


d = {'Jan': "01", 'Feb': "02", 'Mar': "03", 'Apr': "04", 'May': "05", 'Jun': "06",
     'Jul': "07", 'Aug': "08", 'Sep': "09", 'Oct': 10, 'Nov': 11, 'Dec': 12}
df = pd.read_csv(filepath_or_buffer=f"{config.path_final}df_selected.csv", header=0)


# sort on date
df: pd.DataFrame
date_time = "Datetime"
hashtag = ["amelisweerd", 'amelisweerdnietgeasfalteerd', 'kappenmetkappen', 'a27']
start_date = "2021-09"
skip = False
user = None
external = None

df_selected = df[df.apply(lambda r: r.str.contains(hashtag, case=False).any(), axis=1)]
df_new = df_selected

date = [t[:10] for t in df_new[date_time]]  # if not re.search('[a-zA-Z]', t)]

keys, counts = np.unique(date, return_counts=True)

if not skip:

    if start_date:
        year = int(start_date[:4])
        t_start = int(start_date[5:7])
    else:
        year = int(keys[0][2:6])
        t_start = int(keys[0][-2:])

    x_keys = []
    x_values = []
    for idx, i in enumerate(range(t_start, 20)):
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
    for j in range(1, t_start - 45):

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


# x_labels= ["December", "January", "February", "March"]
# x_ticks = ["2020-12-01",  "2021-01-05", "2021-02-01", "2021-03-01"]

x_labels = [x_keys[index] for index in range(1, len(x_keys), 7)]
plt.xticks(rotation=90, ticks=x_labels, labels=x_labels)


plt.show()
plt.savefig(f'petition_over_time.png')
