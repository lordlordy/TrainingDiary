import pandas as pd
import random
import numpy as np

# series assumed to be sorted - don't want to be sorting an already sorted series.
def eddingtonHistoryDF(time_series):
    ltd_history = []
    annual_history = []
    ltd_contributors = np.array([])
    this_years_annual_contributors = np.array([])
    annual_contributors = []
    ed_num_history = []
    annual_ed_num_history = []
    plus_one_history = []
    annual_plus_one_history = []
    ed_num = 0
    annual_ed_num = 0
    plus_one = 0
    annual_plus_one = 0
    print(time_series.index[0])
    print(time_series.index[0][0])
    current_year = time_series.index[0][0].year

    for i,row in time_series.iteritems():
        if i[0].year != current_year:
            # reset all the annual stuff
            current_year = i[0].year
            annual_ed_num = 0
            annual_plus_one = 0
            annual_contributors = annual_contributors + this_years_annual_contributors.tolist()
            this_years_annual_contributors = np.array([])
        if row >= ed_num + 1:
            # this contributes to LTD
            ltd_history.append(row)
            ltd_contributors= np.append(ltd_contributors,row)
            plus_one = (ed_num + 1) - np.size(np.where(ltd_contributors > (ed_num + 1)))
        else:
            ltd_history.append(0)
            ltd_contributors = np.append(ltd_contributors, 0)
        if row >= annual_ed_num + 1:
            # this contributes to annual
            annual_history.append(row)
            this_years_annual_contributors= np.append(this_years_annual_contributors,row)
            annual_plus_one = (annual_ed_num + 1) - np.size(np.where(this_years_annual_contributors > (annual_ed_num + 1)))
        else:
            annual_history.append(0)
            this_years_annual_contributors = np.append(this_years_annual_contributors, 0)
        contributors_to_next = np.size(np.where(ltd_contributors > (ed_num + 1)))
        if contributors_to_next > ed_num:
            # new ed num
            ed_num += 1
            # remove non contributors - done in place
            np.place(ltd_contributors, ltd_contributors<ed_num, 0)
            plus_one = (ed_num + 1) - np.size(np.where(ltd_contributors > (ed_num + 1)))
        annual_contributors_to_next = np.size(np.where(this_years_annual_contributors > (annual_ed_num + 1)))
        if annual_contributors_to_next > annual_ed_num:
            # new annual ed num
            annual_ed_num += 1
            # remove non contributors - done in place
            np.place(this_years_annual_contributors, this_years_annual_contributors<annual_ed_num, 0)
            annual_plus_one = (annual_ed_num + 1) - np.size(np.where(this_years_annual_contributors > (annual_ed_num + 1)))

        plus_one_history.append(plus_one)
        ed_num_history.append(ed_num)
        annual_plus_one_history.append(annual_plus_one)
        annual_ed_num_history.append(annual_ed_num)

    annual_contributors = annual_contributors + this_years_annual_contributors.tolist()

    data = []
    for r in range(len(ltd_history)):
        data.append([ed_num_history[r], plus_one_history[r], ltd_contributors[r], ltd_history[r],
                     annual_ed_num_history[r], annual_plus_one_history[r], annual_contributors[r], annual_history[r]])

    df = pd.DataFrame(data, time_series.index, ['ed#', '+1', 'ltd contrb', 'ltd Hist', 'A ed#', 'A +1', 'A contrb', 'A Hist'])

    return df

if __name__=='__main__':
    import trainingdiarydataframes as tddf
    df = tddf.TDDataFramesSQLITE('td.db')
    # print(df.get_days_df())
    # print(df.get_workouts_df())
    # print(df.get_workouts_aggregators())
    bikeMiles = df.get_series('miles', 'Day', 'Bike')
    print(bikeMiles)
    e = eddingtonHistoryDF(bikeMiles)
    print(e)