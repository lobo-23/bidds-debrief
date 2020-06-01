import pynmea2
import pandas as pd
import os

df=pd.read_csv('NMEAtest.csv')
df['LAT'] = df['LAT'].str.replace(" ",'')
df['LONG'] = df['LONG'].str.replace(" ",'')
df['TIME'] = pd.to_datetime(df['Time (UTC)'])
filename = 'test.gps'
gpsfile = open(filename, 'a')
for index, row in df.iterrows():
    mvar = float(row.THDG) - float(row.MHDG)
    if mvar < 0:
        mvarH = 'W'
    else:
        mvarH = 'E'
    GS = f'{row.GS:05.1f}'
    GTRK = f'{row.GTRK:05.1f}'
    MHDG = f'{row.MHDG:05.1f}'
    dtime = row.TIME.strftime('%H%M%S')
    ddate = row.TIME.strftime('%d%m%y')
    alt = str(round(row.ALT * 0.3048))

    RMC = pynmea2.ZDA('GP', 'RMC', (dtime, 'A', row.LAT[1:], row.LAT[0], row.LONG[1:], row.LONG[0], GS, GTRK, ddate, f'{mvar:05.1f}', mvarH))
    GGA = pynmea2.GGA('GP', 'GGA', (dtime, row.LAT[1:], row.LAT[0], row.LONG[1:], row.LONG[0], '1', '', '', alt, 'M', '', '', '', '0'))
    VTG = pynmea2.GGA('GP', 'VTG', (GTRK, 'T', MHDG, 'M', f'{row.GS:06.2f}', 'N', '', 'K'))

    gpsfile.write(str(RMC) + "\n")
    gpsfile.write(str(GGA) + "\n")
    gpsfile.write(str(VTG) + "\n")
gpsfile.close()
