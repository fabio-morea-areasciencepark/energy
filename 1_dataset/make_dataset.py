# create a tidy dataset of district heating operating conditions
# ambient tempreature, solar irradiation, power, operating mode
# at 15 minutes intervals
# arranged by "heating season" from 15 October to 15 April

import pandas as pd 
import matplotlib.pyplot as plt

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

data['date_time'] = pd.to_datetime(data['day'] + data['time'], format='%d-%m-%Y%H:%M:%S')
dt_extract = data['date_time'].astype(str).str[-15:].values
data['date_time_string'] = 'YYYY' + dt_extract

data['power'] = (data.energy/1000/4).round(3) #power in kW
data['Te'] = ((data.Te1 + data.Te2)/2).round(2) #Te2 readings are not reliable
data['Ir'] = ((data.Ir1 + data.Ir1 + data.Ir3)/3).round(0)


data = data [ ['date_time', 'date_time_string','Te', 'Ir', 'power'] ]

def add_date_time_columns(df):
    df['year'] =  df.date_time.dt.year
    df['month'] = df.date_time.dt.month 
    df['dd'] =    df.date_time.dt.day 
    df['dw'] =    df.date_time.dt.day_of_week +1
    df['dy'] =    df.date_time.dt.day_of_year
    df['hh'] =    df.date_time.dt.hour
    df['min'] =   df.date_time.dt.minute

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
    df.loc[ df.Ir < 0, "Ir"] = 0
    return df

data = add_date_time_columns(data)
data = set_holiday(data)
data = set_operating_mode(data)
data = clean(data)

plt.figure(figsize = (20,2))
data_to_plot = data[10000:11000]

data['winter'] = "-"
anni = [2018,2019,2020,2021,2022,2023]
winters = ["do_not_use","winter1" ,"winter2" ,"winter3" ,"winter4", "do_not_use"]

tempinv = pd.DataFrame( columns = winters ) 
nn = 183*24*4 #183 days, at time intervals of 15 minutes
nulls = list(["NaN"]*nn) 

for i in range(0,5):
    data.loc[ (data.year == anni[i])   & (data.dy >= 287) , "winter"] = winters[i]  
    data.loc[ (data.year == anni[i]+1) & (data.dy <= 106) , "winter"] = winters[i]


data = data[ data.winter.isin(["winter1" ,"winter2" ,"winter3" ,"winter4" ])]

col_order = ['date_time_string','winter','dy','month','dd','hh','min','dw','holiday','op_mode','Te','Ir','power']
data[col_order].to_csv(r'dataset.csv', index = False)

print('Done :-D')

