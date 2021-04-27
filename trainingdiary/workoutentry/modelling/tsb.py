import pandas as pd
import numpy as np


class TSBProcessor:

    def __init__(self, atl_impact_days, atl_decay_days, ctl_impact_days, ctl_decay_days):
        self.ctl_decay = np.exp(-1 / ctl_decay_days)
        self.ctl_impact = 1 - np.exp(-1 / ctl_impact_days)
        self.atl_decay = np.exp(-1 / atl_decay_days)
        self.atl_impact = 1 - np.exp(-1 / atl_impact_days)

    def process(self, df):
        df['date'] = df.index
        df['date_shift'] = pd.to_datetime(df['date'].shift(1))
        df['days'] = (df['date'] - df['date_shift']) / np.timedelta64(1, 'D')
        df['atl_impact'] = df[df.columns[0]] * self.atl_impact
        df['ctl_impact'] = df[df.columns[0]] * self.ctl_impact
        df['atl'] = df['atl_impact']
        df['ctl'] = df['ctl_impact']

        for i in range(1, len(df)):
            df.iloc[i, df.columns.get_loc('atl')] = df.iloc[i]['atl_impact'] + df.iloc[i - 1]['atl'] * pow(self.atl_decay, df.iloc[i]['days'])
            df.iloc[i, df.columns.get_loc('ctl')] = df.iloc[i]['ctl_impact'] + df.iloc[i - 1]['ctl'] * pow(self.ctl_decay, df.iloc[i]['days'])

        df['tsb'] = df['ctl'] - df['atl']

        df = df.drop(columns=['date', 'date_shift', 'atl_impact', 'ctl_impact', 'days'])
        return df