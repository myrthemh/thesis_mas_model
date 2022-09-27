import pandas as pd
from pingouin import ancova
import numpy as np
import config
from preprocess_population_data_new import plot_freq


def compute_score(file1, incl=False, total_inclusion=190, location=False, verified=False, most_frequent_tweeters=False):
    df1 = pd.read_csv(file1)

    if incl:
        s, i, r, i_low = df1['number_susceptible'], df1['number_infected'], df1['number_resistant'], df1['infected_low']
    else:
        s, i, r = df1['number_susceptible'], df1['number_infected'], df1['number_resistant']

    total = s[0] + i[0] + r[0]

    print(total)
    print(f'susceptible total: {s[150]}')
    print(f'infected total: {i[150]}')
    print(f'recovered total: {r[150]}')

    if location:
        total -= 1572
    if verified:
        total -= 205
    if most_frequent_tweeters:
        total -= 124
    empowerment_avg = sum([(i[idx]+r[idx]) / total for idx in range(0, 150)]) / 150
    empowerment = (i[150]+r[150]) / total

    if incl:
        inclusion_avg = sum([i_low[idx]/total_inclusion for idx in range(0, 150)]) / 150
        inclusion = i_low[150] / total_inclusion
        print(f'Empowerment:{empowerment_avg} and final: {empowerment}, Inclusion: {inclusion_avg} and final {inclusion}')

    else:
        print(f'Empowerment:{empowerment_avg} and final: {empowerment}')


def compute_time(df, y):
    df = pd.read_csv(df)
    dataframe = pd.DataFrame({"real":y, "model": df["nr_tweets"],"time": range(0,150)})
    print(ancova(df=dataframe, dv='real', covar='model', between='time'))


# plot the model version 2 (without retweets)
df = pd.read_csv(f"{config.path_final}df_selected.csv")
y = plot_freq(df)


# test ANCOVA between subject test
df1 = pd.read_csv(f"/Users/myrthehemker/Desktop/MasterThesis/Programming/thesis_mas_model/v2_mas_model/results/results_frequency1.5.csv")


df1 = df1.iloc[:150,:]
df1["time"] = range(0, len(df1))
df1["real"] = y[:150]

#
# print("hoi")
# ancova(data=df1, dv='results', covar='real', between='time')#, between='time'[:150])
#

# model 1:
model1 = False
if model1:
    compute_score(file1=f"/Users/myrthehemker/Desktop/MasterThesis/Programming/thesis_mas_model/v1_mas_model/results/SIR/final/version 1- Avg degree33 inf_ra0.0010604721626057316 rec_ra0.0006480663215923915 .csv")
    compute_score(file1=f"/Users/myrthehemker/Desktop/MasterThesis/Programming/thesis_mas_model/v1_mas_model/results/SIR/final/version 1- Avg degree66 inf_ra0.0010604721626057316 rec_ra0.0006480663215923915 .csv")
    compute_score(file1=f"/Users/myrthehemker/Desktop/MasterThesis/Programming/thesis_mas_model/v1_mas_model/results/SIR/final/version 1- Avg degree99 inf_ra0.0010604721626057316 rec_ra0.0006480663215923915 .csv")


# model 3:
print("Version 3")
model3=False
if model3:
    compute_score(file1=f"/Users/myrthehemker/Desktop/MasterThesis/Programming/thesis_mas_model/v3_mas_model/results/final/results_recchan_0.0004_infl25.csv", incl=True)
    compute_score(file1=f"/Users/myrthehemker/Desktop/MasterThesis/Programming/thesis_mas_model/v3_mas_model/results/final/results_recchan_0.0004_infl5.csv", incl=True)
    compute_score(file1=f"/Users/myrthehemker/Desktop/MasterThesis/Programming/thesis_mas_model/v3_mas_model/results/final/results_recchan_0.0004_infl75.csv", incl=True)


# model 4:
path = '/Users/myrthehemker/Desktop/MasterThesis/Programming/thesis_mas_model/v4_mas_model/results/final/'
print("Version 4")

model4=False
if model4:
    print("with citizen initiative")
    compute_score(file1=f"{path}sir_results_CITrue_INFL5_BUDGET15_PART0.2_LOCFalse_MFTFalse_VERFalseSCHTrue test with ci.csv", incl=True)
    print("without citizen initiative")
    compute_score(file1=f"{path}sir_results_CIFalse_INFL5_BUDGET15_PART0.2_LOCFalse_MFTFalse_VERFalseSCHFalse - test without ci.csv", incl=True)
    print()

    compute_time(
        df=f"{path}sir_results_CITrue_INFL5_BUDGET15_PART0.2_LOCFalse_MFTFalse_VERFalseSCHTrue test with ci.csv", y=y)

    # budget
    print("low budget =10")
    compute_score(file1=f"{path}sir_results_CI_INFL5_middleBUDGET100_PART1.csv", incl=True)
    print("middle budget =500")
    compute_score(file1=f"{path}sir_results_CI_INFL5_middleBUDGET500_PART1.csv", incl=True)
    print("high budget =1000")
    compute_score(file1=f"{path}sir_results_withCI_INFL5_highBUDGET1000_PART1.csv", incl=True)
    print()

    # participation score
    print("low participation new ci")
    compute_score(file1=f"{path}sir_results_CI_INFL5_middleBUDGET100_PART1.csv", incl=True)
    print("middle participation new ci")
    compute_score(file1=f"{path}sir_results_CI_INFL5_middleBUDGET500_PART1.csv", incl=True)
    print("high participation new ci")
    compute_score(file1=f"{path}sir_results_withCI_INFL5_highBUDGET1000_PART1.csv", incl=True)
    print()

# verified - authority
# print('!!!')
# print("verified - authority included")
# compute_score(file1=f"{path}sir_results_CITrue_INFL5_BUDGET15_PART0.2_LOCFalse_MFTFalse_VERFalse.csv", incl=True, verified=True)
# print("verified - excluded")
# compute_score(file1=f"{path}sir_results_CITrue_INFL5_BUDGET15_PART0.2_LOCFalse_MFTFalse_VERTrueSCHTrue-test verified.csv", incl=True, verified=True)
# print()

# # location
# print("location excluded")
# compute_score(file1=f"{path}sir_results_CI_INFL5_middleBUDGET100_PART1.csv", incl=True, location=True)
# print("location included")
# compute_score(file1=f"{path}sir_results_CI_INFL5_middleBUDGET500_PART1.csv", incl=True, location=True)
# print()

# # most frequent tweeters
# print("most frequent tweeters - excluded")
# compute_score(file1=f"{path}sir_results_CI_INFL5_middleBUDGET100_PART1.csv", incl=True)
# print("most frequent tweeters - included")
# compute_score(file1=f"{path}sir_results_CI_INFL5_middleBUDGET500_PART1.csv", incl=True)
# print()
