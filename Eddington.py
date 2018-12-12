import pandas as pd
import random
import numpy as np

# series assumed to be sorted - don't want to be sorting an already sorted series.
def eddingtonHistoryDF(timeSeries):
    ltdHistory = []
    annualHistory = []
    ltdContributors = np.array([])
    thisYearsAnnualContributors = np.array([])
    annualContributors = []
    edNumHistory = []
    annualEdNumHistory = []
    plusOneHistory = []
    annualPlusOneHistory = []
    edNum = 0
    annualEdNum = 0
    plusOne = 0
    annualPlusOne = 0
    currentYear = timeSeries.index[0].year

    for i,row in timeSeries.iteritems():
        if i.year != currentYear:
            # reset all the annual stuff
            currentYear = i.year
            annualEdNum = 0
            annualPlusOne = 0
            annualContributors = annualContributors + thisYearsAnnualContributors.tolist()
            thisYearsAnnualContributors = np.array([])
        if row >= edNum + 1:
            # this contributes to LTD
            ltdHistory.append(row)
            ltdContributors= np.append(ltdContributors,row)
            plusOne = (edNum + 1) - np.size(np.where(ltdContributors > (edNum + 1)))
        else:
            ltdHistory.append(0)
            ltdContributors = np.append(ltdContributors, 0)
        if row >= annualEdNum + 1:
            # this contributes to annual
            annualHistory.append(row)
            thisYearsAnnualContributors= np.append(thisYearsAnnualContributors,row)
            annualPlusOne = (annualEdNum + 1) - np.size(np.where(thisYearsAnnualContributors > (annualEdNum + 1)))
        else:
            annualHistory.append(0)
            thisYearsAnnualContributors = np.append(thisYearsAnnualContributors, 0)
        contributorsToNext = np.size(np.where(ltdContributors > (edNum + 1)))
        if contributorsToNext > edNum:
            # new ed num
            edNum += 1
            # remove non contributors - done in place
            np.place(ltdContributors, ltdContributors<edNum, 0)
            plusOne = (edNum + 1) - np.size(np.where(ltdContributors > (edNum + 1)))
        annualContributorsToNext = np.size(np.where(thisYearsAnnualContributors > (annualEdNum + 1)))
        if annualContributorsToNext > annualEdNum:
            # new annual ed num
            annualEdNum += 1
            # remove non contributors - done in place
            np.place(thisYearsAnnualContributors, thisYearsAnnualContributors<annualEdNum, 0)
            annualPlusOne = (annualEdNum + 1) - np.size(np.where(thisYearsAnnualContributors > (annualEdNum + 1)))

        plusOneHistory.append(plusOne)
        edNumHistory.append(edNum)
        annualPlusOneHistory.append(annualPlusOne)
        annualEdNumHistory.append(annualEdNum)

    annualContributors = annualContributors + thisYearsAnnualContributors.tolist()

    data = []
    for r in range(len(ltdHistory)):
        data.append([edNumHistory[r], plusOneHistory[r], ltdContributors[r], ltdHistory[r],
                     annualEdNumHistory[r], annualPlusOneHistory[r], annualContributors[r], annualHistory[r]])

    df = pd.DataFrame(data,timeSeries.index,['ed#','+1','ltd contrb', 'ltd Hist', 'A ed#', 'A +1', 'A contrb', 'A Hist'])

    return df

if __name__=='__main__':
    import trainingdiarydataframes as tddf
    df = tddf.TDDataFramesSQLITE('td.db', 'StevenLordDiary')
    bikeMiles = df.get_series('miles', 'Bike', 'Day')
    e = eddingtonHistoryDF(bikeMiles)