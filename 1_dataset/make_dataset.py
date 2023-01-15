# create a tidy dataset of district heating operating conditions
# ambient tempreature, solar irradiation, power, operating mode
# at 15 minutes intervals
# arranged by "heating season" from 15 October to 15 April

import pandas as pd 
import seaborn as sns 
import matplotlib.pyplot as plt
import numpy as np

data = pd.read_csv(r"raw_data\raw_data_file.csv",
                 sep = ";",
                 skiprows = 2)

expected_cols = [   'day', 'time', '(D)Energia Termica Edificio D', 'Temp. Ambiente',
                    'Temperatura Ambiente', 'Temp. Ambiente.1',
                    'Irraggiamento Imp.15,9 kWp', 'Irraggiamento imp.17,9 kWp',
                    'Irraggiamento']
actual_cols = data.columns

assert set(expected_cols) == set(actual_cols)

data.columns = ['day', 'time', 'energy', 'Te1', 'Te2', 'Te3', 'Ir1', 'Ir2', 'Ir3']

data['day_time'] = pd.to_datetime(data['day'] + data['time'], format='%d-%m-%Y%H:%M:%S')

data['power'] = data.energy/1000/4 
data['Te'] = ((data.Te1 + data.Te2)/2).round(2) #Te2 readings are not reliable
data['Ir'] = ((data.Ir1 + data.Ir1 + data.Ir3)/3).round(0)


data = data [ ['day_time', 'Te', 'Ir', 'power'] ]

# crea nuove colonne anno, mese, giorno, giorno della settimana e dell'anno
def add_date_time_columns(df):
    df['year'] =  df.day_time.dt.year
    df['month'] = df.day_time.dt.month 
    df['dd'] =    df.day_time.dt.day 
    df['dw'] =    df.day_time.dt.day_of_week +1
    df['dy'] =    df.day_time.dt.day_of_year
    df['hh'] =    df.day_time.dt.hour
    df['min'] =   df.day_time.dt.minute
    df['date_id'] = (df.year.astype(str) + df.month.astype(str).str.zfill(2) + df.dd.astype(str).str.zfill(2)).astype(int)
    return df

def set_holiday(df):
    df['holiday'] = False
    df.loc[ (df.month == 1 ) &  df.dd.isin( (1,2,3,4,5,6)) , "holiday"   ] = True
    df.loc[ (df.month == 11) &  df.dd.isin( (2,3,4)) , "holiday"         ] = True
    df.loc[ (df.month == 12) &  df.dd.isin( (24,25,26)) , "holiday"   ] = True
    return df
 
def set_operating_mode(df):
    w_hours =    (df.hh >= 8 ) & (df.hh <= 18 )
    peak_start = (df.hh == 7 ) 
    peak_stop  = (df.hh >= 19) & (df.hh <= 20 )
    w_days  =    (df.dw <= 5 )          & (-df.holiday) 
    df['op_mode'] = 0   # spento
    df.loc[ (-w_days & -w_hours   ), "op_mode"] = 1 # notte feriale
    df.loc[ (-w_days &  w_hours   ), "op_mode"] = 2 # giorno feriale
    df.loc[ ( w_days & -w_hours   ), "op_mode"] = 3 # notte lavorativo
    df.loc[ ( w_days &  w_hours   ), "op_mode"] = 4 # giorno lavorativo
    df.loc[ ( w_days &  peak_stop ), "op_mode"] = 5 # picco spegnimento lavorativo
    df.loc[ ( w_days &  peak_start), "op_mode"] = 6 # picco accensione lavorativo
    return df

def clean(df):
    df.loc[ df.power < 0, "power"] = 0
    df.loc[ df.power < 0, "power"] = 0
    return df

data = add_date_time_columns(data)
data = set_holiday(data)
data = set_operating_mode(data)
data = clean(data)

plt.figure(figsize = (20,2))
data_to_plot = data[10000:11000]

plt.plot( data_to_plot.day_time,  data_to_plot.Te)
plt.show()
plt.plot( data_to_plot.day_time,  data_to_plot.Ir)
plt.show()





