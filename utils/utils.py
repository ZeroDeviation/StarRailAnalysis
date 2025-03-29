import numpy as np
import pandas as pd

url = "Your repo to MoCStats's raw csvs"

# mostly play alone, rarely see with other core dps
core_dps = ['Acheron', 'Jing Yuan', 'Firefly', 'Feixiao', 'Rappa', 'Boothill', 'Seele', 'Jingliu', 'Dan Heng • Imbibitor Lunae',    
'Argenti', 'Dr. Ratio', 'The Herta', 'Aglaea', 'Yanqing']

# dps that can be play with core dps or solo
flexible_dps = ['Blade', 'Clara', 'Welt', 'Himeko', 'Jade', 'Yunli', 'Kafka']

sustains = ['Bailu', 'Natasha', 'Ice March 7th', 'Fire Trailblazer', 'Gepard', 'Luocha', 'Lynx', 'Fu Xuan', 'Huohuo', 'Aventurine', 'Lingsha', 'Gallagher']

mandatory_dps = [('Jing Yuan', 'Sunday'), ('Rappa', 'Fugue'), ('Boothill', 'Fugue'), ('Dr. Ratio', 'Robin'), ('Feixiao', 'Robin'), 
                 ('Firefly', 'Ruan Mei'), ('Acheron', 'Jiaoqiu'), ('Kafka', 'Black Swan'), ('Firefly', 'Fugue'), ('Aglaea', 'Sunday')]


def get_specific_team(x):
    unique_count = sum(1 for dps in core_dps if dps in x)
    if ('The Herta' in x) & ('Argenti' in x):
        return 'The Herta'
    elif unique_count > 1:
        return np.nan    
    for dps in core_dps:
        if dps in x:
            return dps
    for flex in flexible_dps:
        if flex in x:
            return flex

def read_and_add_csv(a, replace_substring):
    temp = pd.read_csv(a)
    temp['version'] = a.split('\\')[-1].replace(replace_substring, '')
    return temp

def num_there(s):
    return any(i.isdigit() for i in s)


def drop_columns_and_rows(df, x):
    # Identify columns to drop
    cols_to_drop = [col for col in df.columns if df[col].sum() < x]
    
    # Identify rows where any of the dropped columns had a truthy value
    rows_to_drop = df[cols_to_drop].any(axis=1)
    
    # Drop columns and rows
    df = df.drop(columns=cols_to_drop)
    df = df[~rows_to_drop].reset_index(drop=True)
    
    return df

def weighted_average(dataframe, value, weight):
    val = dataframe[value]
    wt = dataframe[weight]
    return (val * wt).sum() / wt.sum()

def create_team_info(df, drop_ch=False):
    data = df.copy()
    data['team_comp'] = data.apply(lambda x: " | ".join(sorted([x['ch1'] , x['ch2'] , x['ch3'] , x['ch4']])), axis=1)
    data['team_leader'] = data['team_comp'].apply(get_specific_team)
    data['team_leader'] = data['team_leader'].replace({'Dan Heng â€¢ Imbibitor Lunae': 'Dan Heng • Imbibitor Lunae'}, regex=True)
    data['team_comp'] = np.where(data['version'] < '2.39', data['team_comp'].replace('March 7th', 'Ice March 7th', regex=True), data['team_comp'])    
    data['has_sustain']  = data['team_comp'].str.contains("|".join(sustains))

    if drop_ch:
        data = data.drop(columns=['ch1','ch2','ch3','ch4'])
    return data 

def adjust_team_leader(df):
    data = df.copy()
    data['team_leader_adj'] = data['team_leader'] + ' E' + data['cons'].apply(int).astype(str)
    data['team_leader_adj'] = np.where((data['weapon'] == 'Along the Passing Shore') & (data['team_leader'] == 'Acheron'), data['team_leader_adj'] + 'S1', data['team_leader_adj'])
    data['team_leader_display'] = data['team_leader_adj'].values
    
    for (dps, support) in mandatory_dps:
        data['team_leader_adj'] = np.where((data['team_leader'] == dps)  & data['team_comp'].str.contains(support), data['team_leader_adj'] + ' X ' + support, data['team_leader_adj'])
    return data 
    