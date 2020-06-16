import pandas as pd
from utils import *

def jdamparse(wpn):
    if wpn['Tail Year'] == '0':
        wpn['Tail Year'] = '00'
    wpn['Tail'] = wpn['Tail Year'][1] + '0' + "{:02d}".format(int(wpn['Tail Number']))
    # print(wpn['Tail Number'])

    if wpn['MSN Planned TGT'] == 'True':
        wpn['Dest'] = wpn['LP DT Num']
    else:
        if wpn['LP DT Num'].isnumeric():
            if wpn['LP DT Num'] == '127':
                if 'Continuous' in wpn['TGP Mode']:
                    wpn['Dest'] = "DS-Cont" + str(wpn['Stream operation']).replace('True',' ON').replace('False',' OFF')
                elif 'Static' in wpn['TGP Mode']:
                    wpn['Dest'] = "DS-Stat"
                elif 'Predict' in wpn['TGP Mode']:
                    wpn['Dest'] = "DS-Pred" + str(wpn['Stream operation']).replace('True',' ON').replace('False',' OFF')
            else:
                wpn['Dest'] = "D" + str(wpn['LP DT Num'])
                if 'TGP Mode' in wpn:
                    if 'Updated' in wpn['TGP Mode']:
                        if 'Continuous' in wpn['TGP Mode']:
                            wpn['Dest'] = wpn['Dest'] + "-Cont" + str(wpn['Stream operation']).replace('True',
                                                                                                            ' ON').replace(
                                'False', ' OFF')
                        elif 'Predict' in wpn['TGP Mode']:
                            wpn['Dest'] = wpn['Dest'] + "-Pred" + str(wpn['Stream operation']).replace('True',
                                                                                                            ' ON').replace(
                                'False', ' OFF')


    # print(wpn['Dest'])

    wpn['TOR'] = pd.to_datetime(wpn['Time (UTC)'] + ' ' + wpn['Date'])
    # print(wpn['TOR'])

    if wpn['IZ Status'] == 'Inside':
        wpn['LARstatus'] = 'ZONE'
        wpn['TOF'] = wpn['IZ TOF']
    elif wpn['IR Status'] == 'Inside':
        wpn['LARstatus'] = 'RANGE'
        wpn['TOF'] = wpn['IR TOF']
    else:
        wpn['LARstatus'] = 'UNACHIEV'
        wpn['TOF'] = 0

    if wpn['TOF'] != 0:
        try:
            wpn['TOF'] = round(float(wpn['TOF'].replace('  sec', '').replace('+ ', '')))
        except:
            print('TOF Parse Error- ' + wpn['TOF'])

    wpn['TOT'] = wpn['TOR'] + pd.to_timedelta(str(wpn['TOF']) + 's')
    # print(wpn['TOR'])
    # print(wpn['TOF'])
    # print(wpn['TOT'])

    # print(wpn['WPN Type'])
    if '0x00' in wpn['TGT Name']:
        wpn['TGT Name'] = ''

    if not 'TGT Name' in wpn:
        wpn['TGT Name'] = ''
    try:
        wpn['ALT'] = str(round(float(wpn['Altitude'].replace('  feet', '').replace('+ ', ''))))
    except:
        wpn['ALT'] = 'ERR'
    #print(wpn['ALT'])

    try:
        wpn['LAT'] = wpn['Latitude'].replace('  deg', '').replace(':', ' ').replace('N 0', "N ").replace('S 0', "S ")
    except:
        wpn['LAT'] = 'ERR'
    try:
        wpn['LONG'] = wpn['Longitude'].replace('  deg', '').replace(':', ' ')
    except:
        wpn['LONG'] = 'ERR'
    try:
        wpn['BULLrel'] = bullcalculate(wpn['LAT'],wpn['LONG'])
    except:
        wpn['BULLrel'] = ''

    # print(wpn['LAT'])
    # print(wpn['LONG'])

    try:
        wpn['TGT LAT'] = wpn['TGT LAT'].replace('  deg', '').replace(':', ' ').replace('N 0', "N ").replace('S 0', "S ")
    except:
        wpn['TGT LAT'] = 'ERR'
    try:
        wpn['TGT LONG'] = wpn['TGT LONG'].replace('  deg', '').replace(':', ' ')
    except:
        wpn['TGT LONG'] = 'ERR'

    # print(wpn['TGT LAT'])
    # print(wpn['TGT LONG'])
    try:
        wpn['TGT ELEV'] = float(wpn['TGT Altitude'].replace('  meters', '').replace('+ ', '').replace('- ', '')) * 3.28084
        if "- " in wpn['TGT Altitude']:
            wpn['TGT ELEV'] = "-" + str(round(wpn['TGT ELEV'])) + "' " + wpn['TGT Alt Ref']
        else:
            wpn['TGT ELEV'] = str(round(wpn['TGT ELEV'])) + "' " + wpn['TGT Alt Ref']
    except:
        wpn['TGT ELEV'] = 'ERR'

    # print(wpn['TGT ELEV'])
    try:
        wpn['BULL'] = bullcalculate(wpn['TGT LAT'],wpn['TGT LONG'])
    except:
        wpn['BULL'] = ''

    try:
        wpn['GTRK'] = round(float(wpn['GND Trk Angle'].replace('+ ', '').replace('- ', '').replace('  deg','')))
        if '-' in wpn['GND Trk Angle']:
            wpn['GTRK'] = 360 - wpn['GTRK']
    except:
        wpn['GTRK'] = 'ERR'

    wpn['LS'] = wpn['Dev ID'].replace('P', '')
    # print(wpn['LS'])

    wpn['WPN Code']= wpn['WPN Type']
    try:
        wpn['WPN Type'] = wpn['Store Description'].replace('GBU-','').replace('(V)','v')
        if wpn['WPN Type'] == '38' and wpn['Laser Kit Good'] == 'True':
            wpn['WPN Type'] = '54'
            Laser = wpn['Laser Code 1'] + wpn['Laser Code 2'] + wpn['Laser Code 3']+ wpn['Laser Code 4']
            if Laser == '0000':
                wpn['LS'] = wpn['LS']+ ' No LSR'
            else:
                wpn['LS'] = wpn['LS'] + ' L' + Laser
    except:
        if wpn['WPN Code'] in config.wpncodes:
            wpn['WPN Type'] = config.wpncodes[wpn['WPN Code']]
        else:
            wpn['WPN Type'] = wpn['WPN Code']

    wpn['GS'] = round(float(wpn['GND Speed'].replace('  ft/sec', '')) * 0.592484)
    # print(wpn['GS'])

    wpn['Delay'] = ''
    try:
        if wpn['Func at Impact'] == 'True':
            wpn['Delay'] = "IMP"
        else:
            if wpn['Func on Proximity'] == 'True':
                wpn['Delay'] = 'PROX'
            else:
                if wpn['Func on Time Aft Impact'] == 'True':
                    wpn['Delay'] = 'DEL'
                    if wpn['Integer'] == '+  313  microsec':
                        wpn['Delay'] = '5ms'
                    elif wpn['Integer'] == '+  938  microsec':
                        wpn['Delay'] = '15ms'
                else:
                    if wpn['Function on Void'] in wpn.keys():
                        wpn['Delay'] = 'VOID' + str(wpn['Void Number'])
                    else:
                        if wpn['Function on Void'] in wpn.keys():
                            if wpn['Function on Void'] == 'TRUE' and wpn['Delay'] == '':
                                wpn['Delay'] = 'VOID' + str(wpn['Void Number'])
    except:
        pass
    wpn['Delay'] = wpn['Delay'] + '  ' + wpn['Impact Angle'].replace('  deg','IA')

    return wpn
def wcmdparse(wpn):
    if wpn['Tail Year'] == '0':
        wpn['Tail Year'] = '00'
    wpn['Tail'] = wpn['Tail Year'][1] + '0' + "{:02d}".format(int(wpn['Tail Number']))

    if wpn['Direct Target'] == 'False':
        wpn['Dest'] = wpn['LP DT Number']
    else:
        if wpn['LP DT Number'].isnumeric():
            wpn['Dest'] = "D" + str(wpn['LP DT Number'])
        else:
            wpn['Dest'] = "DS" + wpn['Mode'].replace('Static', 'STAT').replace('Continuous', 'CONT')

    wpn['TOR'] = pd.to_datetime(wpn['Time (UTC)'] + ' ' + wpn['Date'])

    if wpn['IR Status'] == 'Inside':
        wpn['LARstatus'] = 'LAR'
    else:
        wpn['LARstatus'] = 'UNK'

    try:
        wpn['TOT'] = pd.to_datetime(wpn['TGT Impact Point TOT'].replace('+','').replace('hr,min,sec','').replace(' ','') + ' ' + wpn['Date'])
    except:
        wpn['TOT'] = ''
    try:
        wpn['TOF'] = wpn['TOT'] - wpn['TOR']
    except:
        wpn['TOF'] = ''

    wpn['WPN Type'] = wpn['Store Description'].replace('CBU-', '')

    try:
        wpn['ALT'] = str(round(float(wpn['Altitude'].replace('  feet', '').replace('+ ', ''))))
    except:
        wpn['ALT'] = 'ERR'

    try:
        wpn['LAT'] = wpn['Latitude'].replace('  deg', '').replace(':', ' ').replace('N 0', "N ").replace('S 0', "S ")
    except:
        wpn['LAT'] = 'ERR'
    try:
        wpn['LONG'] = wpn['Longitude'].replace('  deg', '').replace(':', ' ')
    except:
        wpn['LONG'] = 'ERR'
    try:
        wpn['BULLrel'] = bullcalculate(wpn['LAT'],wpn['LONG'])
    except:
        wpn['BULLrel'] = ''

    try:
        wpn['TGT LAT'] = wpn['Target Latitude'].replace('  deg', '').replace(':', ' ').replace('N 0', "N ").replace('S 0', "S ")
    except:
        wpn['TGT LAT'] = 'ERR'
    try:
        wpn['TGT LONG'] = wpn['Target Longitude'].replace('  deg', '').replace(':', ' ')
    except:
        wpn['TGT LONG'] = 'ERR'

    try:
        wpn['TGT ELEV'] = float(wpn['Target Altitude'].replace('  meters', '').replace('+ ', '')) * 3.28084
        wpn['TGT ELEV'] = str(round(wpn['TGT ELEV'])) + "' " + wpn['Target Alt Ref']
    except:
        wpn['TGT ELEV'] = 'ERR'

    if not 'TGT Name' in wpn:
        wpn['TGT Name'] = ''

    try:
        wpn['BULL'] = bullcalculate(wpn['TGT LAT'], wpn['TGT LONG'])
    except:
        wpn['BULL'] = ''
    wpn['LS'] = wpn['Device ID'].replace('P', '')
    wpn['GS'] = round(float(wpn['Ground Speed'].replace('  ft/sec', '')) * 0.592484)
    wpn['Delay'] = wpn['Fuze Option'].replace('Prox_Fuzing', 'PROX')

    return wpn

def jassmparse(wpn):
    if wpn['Tail Year'] == '0':
        wpn['Tail Year'] = '00'
    wpn['Tail'] = wpn['Tail Year'][1] + '0' + "{:02d}".format(int(wpn['Tail Number']))
    #print(wpn['Tail'])

    wpn['LS'] = wpn['Device ID'].replace('P', '').replace(' ','')
    #print(wpn['LS'])

    try:
        wpn['LAT'] = wpn['Latitude'].replace('  deg', '').replace(':', ' ').replace('N 0', "N ").replace('S 0', "S ")
    except:
        wpn['LAT'] = 'ERR'
    try:
        wpn['LONG'] = wpn['Longitude'].replace('  deg', '').replace(':', ' ')
    except:
        wpn['LONG'] = 'ERR'
    try:
        wpn['ALT'] = str(round(float(wpn['Altitude'].replace('  feet', '').replace('+ ', ''))))
    except:
        wpn['ALT'] = 'ERR'
    try:
        wpn['BULLrel'] = bullcalculate(wpn['LAT'],wpn['LONG'])
    except:
        wpn['BULLrel'] = ''

    #print(wpn['LAT'])
    #print(wpn['LONG'])
    #print(wpn['ALT'])

    try:
        wpn['GTRK'] = round(float(wpn['Ground Track Angle'].replace('+ ', '').replace('- ', '').replace('  deg', '')))
    except:
        wpn['GTRK'] = 'ERR'
    #print(wpn['GTRK'])

    wpn['GS'] = round(float(wpn['Ground Speed'].replace('  ft/sec', '')) * 0.592484)
    #print(wpn['GS'])

    wpn['PrimeNav'] = wpn['Prime Nav System']
    #print(wpn['PrimeNav'])

    if wpn['IZ Status'] == 'Inside':
        wpn['LARstatus'] = 'ZONE'
    elif wpn['IR Status'] == 'Inside':
        wpn['LARstatus'] = 'RANGE'
    else:
        wpn['LARstatus'] = 'UNK'
    #print(wpn['LARstatus'])

    try:
        if wpn['Mission Planned TGT'] == 'True':
            wpn['Dest'] = wpn['LP DT Number']
            if wpn['LP DT Number'].isnumeric():
                if int(wpn['LP DT Number']) > 109:
                    wpn['Dest'] = 'A' + str(int(wpn['LP DT Number']) -109)
        else:
            if wpn['LP DT Number'].isnumeric():
                wpn['Dest'] = "D" + str(wpn['LP DT Number'])
    except:
        wpn['Dest'] = ''
    #print(wpn['Dest'])

    wpn['TOR'] = pd.to_datetime(wpn['Time (UTC)'] + ' ' + wpn['Date'])
    wpn['TOF'] = ''
    wpn['TOT'] = ''

    #print(wpn['TOR'])
    #print(wpn['TOF'])
    #print(wpn['TOT'])

    try:
        if 'Store Description' in wpn:
            wpn['WPN Type'] = wpn['Store Description'].replace("AGM-","")
        else:
            if wpn['Variant Type A'] == 'True':
                wpn['WPN Type'] = '158A'
            if wpn['Variant Type B'] == 'True':
                wpn['WPN Type'] = '158B'
            if wpn['Variant Type C'] == 'True':
                wpn['WPN Type'] = '158C'
    except:
        print('Error Jassm type: ' + str(wpn['Record Number']))
        #print(wpn['WPN Type'])

    wpn['TGT LAT'] = ''
    wpn['TGT LONG'] = ''
    wpn['TGT ELEV'] = ''
    try:
        wpn['TGT Name'] = 'JASSMGRP_' + str(wpn['Weapon Group ID']).zfill(2) + " " + 'MSN'+ str(wpn['Primary Target ID'])
        if wpn['Weapon Group ID'] == '0x000000BC':
            wpn['TGT Name'] = ''
    except:
        wpn['TGT Name'] = ''

    wpn['BULL'] = ''
    #print(wpn['TGT LAT'])
    #print(wpn['TGT LONG'])
    #print(wpn['TGT ELEV'])

    wpn['Delay'] = ''
    #print(wpn['Delay'])
    return wpn
def maldparse(wpn):
    if wpn['Tail Year'] == '0':
        wpn['Tail Year'] = '00'
    wpn['Tail'] = wpn['Tail Year'][1] + '0' + "{:02d}".format(int(wpn['Tail Number']))
    #print(wpn['Tail'])

    wpn['LS'] = wpn['Device ID'].replace('P', '')
    #print(wpn['LS'])

    try:
        wpn['LAT'] = wpn['Latitude'].replace('  deg', '').replace(':', ' ').replace('N 0', "N ").replace('S 0', "S ")
    except:
        wpn['LAT'] = 'ERR'
    try:
        wpn['LONG'] = wpn['Longitude'].replace('  deg', '').replace(':', ' ')
    except:
        wpn['LONG'] = 'ERR'
    try:
        wpn['ALT'] = str(round(float(wpn['Altitude'].replace('  feet', '').replace('+ ', ''))))
    except:
        wpn['ALT'] = 'ERR'
    try:
        wpn['BULLrel'] = bullcalculate(wpn['LAT'],wpn['LONG'])
    except:
        wpn['BULLrel'] = ''

    #print(wpn['LAT'])
    #print(wpn['LONG'])
    #print(wpn['ALT'])

    try:
        wpn['GTRK'] = round(float(wpn['Ground Track Angle'].replace('+ ', '').replace('- ', '').replace('  deg', '')))
    except:
        wpn['GTRK'] = 'ERR'
    #print(wpn['GTRK'])

    wpn['GS'] = round(float(wpn['Ground Speed'].replace('+ ', '').replace('  ft/sec', '')) * 0.592484)
    #print(wpn['GS'])

    wpn['PrimeNav'] = wpn['Prime Nav System']
    #print(wpn['PrimeNav'])

    if wpn['IZ Status'] == 'Inside':
        wpn['LARstatus'] = 'ZONE'
    elif wpn['IR Status'] == 'Inside':
        wpn['LARstatus'] = 'RANGE'
    else:
        wpn['LARstatus'] = 'UNK'
    #print(wpn['LARstatus'])

    if wpn['Targeting Mode'] == 'Preplanned':
        wpn['Dest'] = wpn['LPT ADM Number']
    else:
        if wpn['LPT ADM Number'].isnumeric():
            wpn['Dest'] = "D" + str(wpn['LPT ADM Number'])

    #print(wpn['Dest'])

    wpn['TOR'] = pd.to_datetime(wpn['Time (UTC)'] + ' ' + wpn['Date'])
    wpn['TOF'] = ''
    wpn['TOT'] = ''

    #print(wpn['TOR'])
    #print(wpn['TOF'])
    #print(wpn['TOT'])
    try:
        if 'Z2' in wpn['Weapon Type'] or 'Z1' in wpn['Weapon Type']:
            wpn['WPN Type'] = wpn['Weapon Type'].replace('Z2', 'MALDJ').replace('Z1', 'MALD')
        else:
            if 'ADM-160B' in wpn['Store Description']:
                wpn['WPN Type'] = 'MALD'
            else:
                if 'ADM-160C' in wpn['Store Description']:
                    wpn['WPN Type'] = 'MALD'
                else:
                    wpn['WPN Type'] = wpn['Store Description']
    except:
        wpn['WPN Type'] = wpn['Weapon Type'].replace('Z2','MALDJ').replace('Z1','MALD')
    #print(wpn['WPN Type'])


    try:
        wpn['TGT LAT'] = wpn['EP Latitude'].replace('  deg', '').replace(':', ' ').replace('N 0', "N ").replace('S 0',
                                                                                                                "S ")
    except:
        wpn['TGT LAT'] = 'ERR'
    try:
        wpn['TGT LONG'] = wpn['EP Longitude'].replace('  deg', '').replace(':', ' ')
    except:
        wpn['TGT LONG'] = 'ERR'
    try:
        wpn['TGT ELEV'] = str(round(float(wpn['EP Elevation'].replace('  feet', '').replace('+ ', '')))) + "'"
    except:
        wpn['TGT ELEV'] = 'ERR'

    if '99 59' in wpn['TGT LAT']:
        wpn['TGT LAT'] = ''
    if '99 59' in wpn['TGT LONG']:
        wpn['TGT LONG'] = ''
    if '99999' in wpn['TGT ELEV']:
        wpn['TGT ELEV'] = ''


    try:
        wpn['BULL'] = bullcalculate(wpn['TGT LAT'], wpn['TGT LONG'])
    except:
        wpn['BULL'] = ''
    #print(wpn['TGT LAT'])
    #print(wpn['TGT LONG'])
    #print(wpn['TGT ELEV'])
    try:
        wpn['TGT Name'] = 'MALDGRP_' + str(wpn['Mission Group']).zfill(2) + " " + 'MSN'+ str(wpn['Mission ID Number'])
        if wpn['Mission ID Number'] == '9999':
            wpn['TGT Name'] = ''
    except:
        wpn['TGT Name'] = ''

    if wpn['Ingress Payload Control'] == "Payload Off (Decoy/Jammer)":
        wpn['INGRESS'] = 'OFF'
    else:
        wpn['INGRESS'] = wpn['Ingress Payload Control']

    if wpn['Orbit Payload Control'] == "Payload Off (Decoy/Jammer)":
        wpn['ORBIT'] = 'OFF'
    else:
        wpn['ORBIT'] = wpn['Orbit Payload Control']

    wpn['Delay'] = 'I:' + str(wpn['INGRESS']) + "/O:" + str(wpn['ORBIT'])
    #print(wpn['Delay'])
    return wpn

def gwdparse(wpn):
    if wpn['Tail Year'] == '0':
        wpn['Tail Year'] = '00'
    wpn['Tail'] = wpn['Tail Year'][1] + '0' + "{:02d}".format(int(wpn['Tail Number']))

    if wpn['Type Of Target'] == 'Mission_Planned':
        wpn['Dest'] = wpn['Target Identifier']
    else:
        wpn['Dest'] = wpn['Target Identifier']  # Continuous or Static?

    wpn['TOR'] = pd.to_datetime(wpn['Time (UTC)'] + ' ' + wpn['Date'])

    wpn['LARstatus']  = ' '  #Set as FCI From mission Event

    if wpn['Weapon Time Of Fall'] != 0:
        try:
            wpn['TOF'] = round(float(wpn['Weapon Time Of Fall'].replace('  SEC', "")))
        except:
            print('TOF Parse Error- ' + wpn['TOF'])
            wpn['TOF'] = 0

    wpn['TOT'] = wpn['TOR'] + pd.to_timedelta(str(wpn['TOF']) + 's')

    wpn['WPN Type'] = "B" + "{:02d}".format(int(wpn['Bomb Type']))
    if wpn['WPN Type'] in config.wpncodes:
        wpn['WPN Type'] = config.wpncodes[wpn['WPN Type']]

    try:
        wpn['ALT'] = str(round(float(wpn['Aircraft Altitude'].replace('  feet', '').replace('+ ', ''))))
    except:
        wpn['ALT'] = 'ERR'

    try:
        wpn['LAT'] = wpn['Aircraft Latitude'].replace('  deg', '').replace(':', ' ').replace('N 0', "N ").replace('S 0', "S ")
    except:
        wpn['LAT'] = 'ERR'
    try:
        wpn['LONG'] = wpn['Aircraft Longitude'].replace('  deg', '').replace(':', ' ')
    except:
        wpn['LONG'] = 'ERR'
    try:
        wpn['BULLrel'] = bullcalculate(wpn['LAT'],wpn['LONG'])
    except:
        wpn['BULLrel'] = ''



    try:
        wpn['TGT LAT'] = wpn['Target Latitude'].replace('  deg', '').replace(':', ' ').replace('N 0', "N ").replace('S 0', "S ")
    except:
        wpn['TGT LAT'] = 'ERR'
    try:
        wpn['TGT LONG'] = wpn['Target Longitude'].replace('  deg', '').replace(':', ' ')
    except:
        wpn['TGT LONG'] = 'ERR'

    try:
        wpn['TGT ELEV'] = float(wpn['Target Elevation'].replace('  feet', '').replace('+ ', ''))
        wpn['TGT ELEV'] = str(round(wpn['TGT ELEV'])) + "' " + wpn['Elevation Ref']
    except:
        wpn['TGT ELEV'] = 'ERR'

    if not 'TGT Name' in wpn:
        wpn['TGT Name'] = ''

    try:
        wpn['BULL'] = bullcalculate(wpn['TGT LAT'], wpn['TGT LONG'])
    except:
        wpn['BULL'] = ''

    try:
        wpn['GTRK'] = round(float(wpn['Ground Track'].replace('+ ', '').replace('- ', '').replace('  deg','')))
        if '-' in wpn['Ground Track']:
            wpn['GTRK'] = 360 - wpn['GTRK']
    except:
        wpn['GTRK'] = 'ERR'

    if wpn['RIU Present'] == 'True':
        wpn['LS'] = wpn['Master Location'].replace('Internal', 'INT').replace('External', 'EXT')
    else:
        wpn['LS'] = wpn['Master Location']

    try:
        DR = float(wpn['Weapon Down Range'].replace(' feet','').replace('+ ','').replace('- ','').replace(' ',''))
        if '+' in wpn['Weapon Down Range']:
            wpn['Weapon Down Range'] = DR
        elif '-' in wpn['Weapon Down Range']:
            wpn['Weapon Down Range'] = DR * -1
    except:
        pass
    try:
        CR = float(wpn['Weapon Cross Range'].replace(' feet','').replace('+ ','').replace('- ','').replace(' ',''))
        if '+' in wpn['Weapon Cross Range']:
            wpn['Weapon Cross Range'] = CR
        elif '-' in wpn['Weapon Cross Range']:
            wpn['Weapon Cross Range'] = CR * -1
    except:
        pass

    try:
        CRMD = float(wpn['Cross Range Miss Distance'].replace(' feet','').replace('+ ','').replace('- ','').replace(' ',''))
        if '+' in wpn['Cross Range Miss Distance']:
            wpn['Cross Range Miss Distance'] = CRMD
        elif '-' in wpn['Cross Range Miss Distance']:
            wpn['Cross Range Miss Distance'] = CRMD * -1
    except:
        pass

    try:
        DRMD = float(wpn['Down Range Miss Distance'].replace(' feet','').replace('+ ','').replace('- ','').replace(' ',''))
        if '+' in wpn['Down Range Miss Distance']:
            wpn['Down Range Miss Distance'] = DRMD
        elif '-' in wpn['Down Range Miss Distance']:
            wpn['Down Range Miss Distance'] = DRMD * -1
    except:
        pass

    try:
        wpn['FCI'] = round(np.arctan(float(CRMD)/float(DR))*180/np.pi,3)
    except:
        pass

    wpn['GS'] = round(float(wpn['Ground Speed'].replace('  ft/sec', '').replace('+ ', '')) * 0.592484)

    wpn['Delay'] = ""
    if wpn['First Sample Valid'] == 'True':
        wpn['FOM'] = wpn['FOM First Sample']
    elif wpn['Second Sample Valid'] == 'True':
        wpn['FOM'] = wpn['FOM Second Sample']   
    else:
        wpn['FOM'] = 'ERR'
    try:
        BuffersN = float(wpn['Trackball Buffer North'].replace('  feet', '').replace('N ', '').replace('S ', ''))
        BuffersE = float(wpn['Trackball Buffer East'].replace('  feet', '').replace('E ', '').replace('W ', ''))
        if "S " in wpn['Trackball Buffer North']:
            BuffersN = BuffersN * -1
        if "W " in wpn['Trackball Buffer East']:
            BuffersE = BuffersE * -1
        wpn['Buffers'] = round(Vector2Polar(BuffersN,BuffersE)[1])
    except:
        wpn['Buffers'] = "ERR"
    wpn['LARstatus'] = 'RANGE'

    return wpn

