import pynmea2
import pandas as pd

df=pd.read_csv('NMEAtest.csv')
df['LAT'] = df['LAT'].str.replace(" ",'')
df['LONG'] = df['LONG'].str.replace(" ",'')
df['TIME'] = pd.to_datetime(df['TIME'])
for index, row in df.iterrows():
    #print(row.LAT)
    GGA = pynmea2.GGA('GP', 'GGA', (row.TIME.strftime('%H%M%S'), row.LAT[1:], row.LAT[0], row.LONG[1:], row.LONG[0], '1', '', '', str(round(row.ALT*0.3048)), 'M', '', '', '', '0'))
    RMC = pynmea2.ZDA('GP', 'RMC', (row.TIME.strftime('%H%M%S'), 'A', row.LAT[1:], row.LAT[0], row.LONG[1:], row.LONG[0],str(row.GS),str(row.GTRK),row.TIME.strftime('%d%m%y'),'0','E'))
    #msgdt = pynmea2.ZDA('GP','ZDA',(row.TIME.strftime('%H%M%S'),row.TIME.strftime('%d'),row.TIME.strftime('%m'),row.TIME.strftime('%Y'),'0','0'))
    print(str(RMC))
    print(str(GGA))


#msgdt = pynmea2.ZDA('GP','ZDA',(row.TIME.strftime('%H%M%S.%f'),row.TIME.strftime('%d'),row.TIME.strftime('%m'),row.TIME.strftime('%Y'),'0','0'))
#print(str(msg))