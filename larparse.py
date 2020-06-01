import pandas as pd
from utils import *

def LARjassmparse(LAR):
    if LAR['Tail Year'] == '0':
        LAR['Tail Year'] = '00'
    LAR['Tail'] = LAR['Tail Year'][1] + '0' + "{:02d}".format(int(LAR['Tail Number']))
    #print(LAR['Tail'])

    LAR['LS'] = LAR['Device ID'].replace('P', '').replace(' ','')
    #print(LAR['LS'])

    try:
        LAR['LAT'] = LAR['Latitude'].replace('  deg', '').replace(':', ' ').replace('N 0', "N ").replace('S 0', "S ")
    except:
        LAR['LAT'] = 'ERR'
    try:
        LAR['LONG'] = LAR['Longitude'].replace('  deg', '').replace(':', ' ')
    except:
        LAR['LONG'] = 'ERR'
    try:
        LAR['ALT'] = str(round(float(LAR['Altitude'].replace('  feet', '').replace('+ ', ''))))
    except:
        LAR['ALT'] = 'ERR'


    try:
        LAR['GTRK'] = round(float(LAR['Ground Track Angle'].replace('+ ', '').replace('- ', '').replace('  deg', '')))
    except:
        LAR['GTRK'] = 'ERR'
    #print(LAR['GTRK'])

    LAR['GS'] = round(float(LAR['Ground Speed'].replace('+ ', '').replace('  ft/sec', '')) * 0.592484)
    #print(LAR['GS'])

    try:
        if 'LAR Time of Flight' in LAR: #JASSM
            LAR['TOF'] = LAR['LAR Time of Flight'].replace('hr,min,sec', '').replace('+', '').replace(' ', '')
            LAR['TOF'] = pd.to_timedelta(LAR['TOF'])
    except:
        LAR['TOF'] = 'ERR'

    #print(LAR['TOF'])
    LAR['LAR'] = 'JASSM LAR'
    return LAR
def LARmaldparse(LAR):
    if LAR['Tail Year'] == '0':
        LAR['Tail Year'] = '00'
    LAR['Tail'] = LAR['Tail Year'][1] + '0' + "{:02d}".format(int(LAR['Tail Number']))
    #print(LAR['Tail'])

    LAR['LS'] = LAR['Device ID'].replace('P', '').replace(' ','')
    #print(LAR['LS'])

    try:
        LAR['LAT'] = LAR['Latitude'].replace('  deg', '').replace(':', ' ').replace('N 0', "N ").replace('S 0', "S ")
    except:
        LAR['LAT'] = 'ERR'
    try:
        LAR['LONG'] = LAR['Longitude'].replace('  deg', '').replace(':', ' ')
    except:
        LAR['LONG'] = 'ERR'
    try:
        LAR['ALT'] = str(round(float(LAR['Altitude'].replace('  feet', '').replace('+ ', ''))))
    except:
        LAR['ALT'] = 'ERR'


    try:
        LAR['GTRK'] = round(float(LAR['Ground Track Angle'].replace('+ ', '').replace('- ', '').replace('  deg', '')))
    except:
        LAR['GTRK'] = 'ERR'
    #print(LAR['GTRK'])

    LAR['GS'] = round(float(LAR['Ground Speed'].replace('+ ', '').replace('  ft/sec', '')) * 0.592484)
    #print(LAR['GS'])

    try:
        if 'LAR Time Of Flight' in LAR: #MALD
            LAR['TOF'] = LAR['LAR Time Of Flight'].replace('hr,min,sec', '').replace("+ 000:","00:").replace("+ 001:","01:").replace("+ 002:","02:").replace('+', '').replace(' ', '')
            LAR['TOF'] = pd.to_timedelta(LAR['TOF'])
    except:
        LAR['TOF'] = 'ERR'

    #print(LAR['TOF'])

    try:
        if 'LAR Time To Loiter Point' in LAR:
            LAR['TTLP'] = LAR['LAR Time To Loiter Point'].replace('hr,min,sec', '').replace("+ 000:","00:").replace("+ 001:","01:").replace("+ 002:","02:").replace('+', '').replace(' ', '')
            LAR['TTLP'] = pd.to_timedelta(LAR['TTLP'])
            #print(LAR['TTLP'])
    except:
        pass
    LAR['LAR'] = 'MALD LAR'

    return LAR