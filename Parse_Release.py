from pyparsing import *
import pandas as pd
import csv, glob, datetime, os, openpyxl

debug = False

def JdamParse(wpn):
    if wpn['Tail Year'] == '0':
        wpn['Tail Year'] = '00'
    wpn['Tail'] = wpn['Tail Year'][1] + '0' + "{:02d}".format(int(wpn['Tail Number']))
    # print(wpn['Tail Number'])

    if wpn['MSN Planned TGT'] == 'True':
        wpn['Dest'] = wpn['LP DT Num']
    else:
        if wpn['LP DT Num'].isnumeric():
            wpn['Dest'] = "D" + str(wpn['LP DT Num'])
        else:
            wpn['Dest'] = "DS" + wpn['Mode'].replace('Static', 'STAT').replace('Continuous', 'CONT')

    # print(wpn['Dest'])

    wpn['TOR'] = pd.to_datetime(wpn['Time (UTC)'] + ' ' + wpn['Date'])
    # print(wpn['TOR'])

    if wpn['IZ Status'] == 'Inside':
        wpn['LARstatus'] = 'ZONE'
        wpn['TOF'] = wpn['IZ TOF']
    elif wpn['IR Status'] == 'RANGE':
        wpn['LARstatus'] = 'IR'
        wpn['TOF'] = wpn['IR TOF']
    else:
        wpn['LARstatus'] = 'UNK'
        wpn['TOF'] = 0

    if wpn['TOF'] != 0:
        try:
            wpn['TOF'] = float(wpn['TOF'].replace('  sec', '').replace('+ ', ''))
        except:
            print('TOF Parse Error- ' + wpn['TOF'])

    wpn['TOT'] = wpn['TOR'] + pd.to_timedelta(str(wpn['TOF']) + 's')
    # print(wpn['TOR'])
    # print(wpn['TOF'])
    # print(wpn['TOT'])

    # print(wpn['WPN Type'])

    try:
        wpn['ALT'] = str(round(float(wpn['Altitude'].replace('  feet', '').replace('+ ', '')))) + "'"
    except:
        wpn['ALT'] = 'ERR'
    #print(wpn['ALT'])

    try:
        wpn['LAT'] = wpn['Latitude'].replace('  deg', '').replace(':', ' ')
    except:
        wpn['LAT'] = 'ERR'
    try:
        wpn['LONG'] = wpn['Longitude'].replace('  deg', '').replace(':', ' ')
    except:
        wpn['LONG'] = 'ERR'

    # print(wpn['LAT'])
    # print(wpn['LONG'])

    try:
        wpn['TGT LAT'] = wpn['TGT LAT'].replace('  deg', '').replace(':', ' ')
    except:
        wpn['TGT LAT'] = 'ERR'
    try:
        wpn['TGT LONG'] = wpn['TGT LONG'].replace('  deg', '').replace(':', ' ')
    except:
        wpn['TGT LONG'] = 'ERR'

    # print(wpn['TGT LAT'])
    # print(wpn['TGT LONG'])
    try:
        wpn['TGT ELEV'] = float(wpn['TGT Altitude'].replace('  meters', '').replace('+ ', '')) * 3.28084
        wpn['TGT ELEV'] = str(round(wpn['TGT ELEV'])) + "' " + wpn['TGT Alt Ref']
    except:
        wpn['TGT LAT'] = 'ERR'

    # print(wpn['TGT ELEV'])

    try:
        wpn['GTRK'] = round(float(wpn['Ground Track'].replace('+ ', '').replace('- ', '').replace('  deg','')))
        if '-' in wpn['Ground Track']:
            wpn['GTRK'] = 360 - wpn['GTRK']
    except:
        wpn['GTRK'] = 'ERR'

    wpn['LS'] = wpn['Dev ID'].replace('P', '')
    # print(wpn['LS'])

    wpn['GS'] = round(float(wpn['GND Speed'].replace('  ft/sec', '')) * 0.592484)
    # print(wpn['GS'])

    wpn['PrimeNav'] = wpn['Prime Nav System']
    # print(wpn['PrimeNav'])

    if wpn['Func at Impact'] == 'TRUE':
        wpn['Delay'] = "IMP"
    elif wpn['Func on Proximity'] == 'TRUE':
        wpn['Delay'] = 'PROX'
    elif wpn['Func on Time Aft Impact'] == 'TRUE':
        wpn['Delay'] = 'DEL'
    elif wpn['Function on Void'] == 'TRUE':
        wpn['Delay'] = 'VOID' + str(wpn['Void Number'])

    return wpn
def GravParse(wpn):
    if wpn['Tail Year'] == '0':
        wpn['Tail Year'] = '00'
    wpn['Tail'] = wpn['Tail Year'][1] + '0' + "{:02d}".format(int(wpn['Tail Number']))

    if wpn['Type Of Target'] == 'Mission_Planned':
        wpn['Dest'] = wpn['Target Identifier']
    else:
        wpn['Dest'] = wpn['Target Identifier']  # Continuous or Static?

    wpn['TOR'] = pd.to_datetime(wpn['Time (UTC)'] + ' ' + wpn['Date'])

    # wpn['LARstatus']  = 'ZONE'  #Set as FCI From mission Event

    if wpn['Weapon Time Of Fall'] != 0:
        try:
            wpn['TOF'] = float(wpn['Weapon Time Of Fall'].replace('  SEC', ""))
        except:
            print('TOF Parse Error- ' + wpn['TOF'])
            wpn['TOF'] = 0

    wpn['TOT'] = wpn['TOR'] + pd.to_timedelta(str(wpn['TOF']) + 's')

    wpn['WPN Type'] = "B" + "{:02d}".format(int(wpn['Bomb Type']))

    try:
        wpn['ALT'] = str(round(float(wpn['Aircraft Altitude'].replace('  feet', '').replace('+ ', '')))) + "'"
    except:
        wpn['ALT'] = 'ERR'

    try:
        wpn['LAT'] = wpn['Aircraft Latitude'].replace('  deg', '').replace(':', ' ')
    except:
        wpn['LAT'] = 'ERR'
    try:
        wpn['LONG'] = wpn['Aircraft Longitude'].replace('  deg', '').replace(':', ' ')
    except:
        wpn['LONG'] = 'ERR'



    try:
        wpn['TGT LAT'] = wpn['Target Latitude'].replace('  deg', '').replace(':', ' ')
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
        wpn['TGT LAT'] = 'ERR'

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


    wpn['GS'] = round(float(wpn['Ground Speed'].replace('  ft/sec', '').replace('+ ', '')) * 0.592484)

    wpn['PrimeNav'] = ""
    wpn['Delay'] = ""
    if wpn['First Sample Valid'] == 'True':
        wpn['FOM'] = wpn['FOM First Sample']
    elif wpn['Second Sample Valid'] == 'True':
        wpn['FOM'] = wpn['FOM Second Sample']
    else:
        wpn['FOM'] = 'ERR'

    return wpn
def WcmdParse(wpn):
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

    wpn['TOF'] = ''  # Does not exist
    wpn['TOT'] = ''  # Unable to calculate with no TOF

    wpn['WPN Type'] = wpn['Store Description'].replace('CBU-', '')

    try:
        wpn['ALT'] = str(round(float(wpn['Altitude'].replace('  feet', '').replace('+ ', '')))) + "'"
    except:
        wpn['ALT'] = 'ERR'

    try:
        wpn['LAT'] = wpn['Latitude'].replace('  deg', '').replace(':', ' ')
    except:
        wpn['LAT'] = 'ERR'
    try:
        wpn['LONG'] = wpn['Longitude'].replace('  deg', '').replace(':', ' ')
    except:
        wpn['LONG'] = 'ERR'

    try:
        wpn['TGT LAT'] = wpn['Target Latitude'].replace('  deg', '').replace(':', ' ')
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
        wpn['TGT LAT'] = 'ERR'

    wpn['GTRK'] = ''
    wpn['LS'] = wpn['Device ID'].replace('P', '')
    wpn['GS'] = round(float(wpn['Ground Speed'].replace('  ft/sec', '')) * 0.592484)
    wpn['PrimeNav'] = wpn['Prime Nav System']
    wpn['Delay'] = wpn['Fuze Option'].replace('Prox_Fuzing', 'PROX')

sample = open('MALD.txt', 'r', errors='ignore').read()

record = Group(Literal("Record Number") + Word(nums)) + Suppress(Literal("Weapon Scoring") + lineEnd())
msnEventExpanded = Suppress(Group(Literal("Launch") + LineEnd())) | Suppress(Group(Literal("Gravity Weapon Scoring") + LineEnd()))| Suppress(Group(Literal("Weapon Launch") + LineEnd()))
eventKey = SkipTo(": ")
    #Improve?
eventValue = SkipTo(lineEnd)
eventData = NotAny("Launch") + NotAny("Gravity Weapon Scoring") + NotAny("Weapon Launch") + Group(eventKey + Suppress(":") + eventValue) + Suppress(lineEnd())
recordBlock = record + OneOrMore(eventData) + msnEventExpanded


pData = Suppress(Literal("PERTINENT DATA"))
SPACE_CHARS = ' \t'
dataField = CharsNotIn(SPACE_CHARS)
space = Word(SPACE_CHARS, exact=1)^Word(SPACE_CHARS, exact=2)^Word(SPACE_CHARS, exact=3)^Word(SPACE_CHARS, exact=4)^Word(SPACE_CHARS, exact=5)
dataKey = delimitedList(dataField, delim=space, combine=True)
dataValue = Combine(dataField + ZeroOrMore(space + dataField))

dataBlock = Group(dataKey + dataValue) + Optional(Suppress("(" + Word(alphanums) + ")")) + Suppress(LineEnd()) |  Group(dataKey + Suppress("(") + Word(alphanums) + Suppress(")")) + Suppress(LineEnd()) | Group(dataKey + dataValue) + Suppress(LineEnd())

name_parser = Dict(recordBlock + pData + OneOrMore(dataBlock))

count = 0
jcount = 0
gcount = 0
wcount = 0
jmcount = 0
mcount = 0

if debug:
    for obj, start, end in name_parser.scanString(sample):
        print(obj.asDict())
        if obj['Application ID'] == '13':
            obj.pop("TGTING Data", None)
            #JdamParse(obj)
            print(obj.asDict())
        if obj['Application ID'] == '1':
            #GravParse(obj)
            print(obj.asDict())
        if obj['Application ID'] == '7':
            #WcmdParse(obj)
            print(obj.asDict())
        if obj['Application ID'] == '9':
            #JassmParse(obj)
            print(obj.asDict())
        if obj['Application ID'] == '12':
            #MaldParse(obj)
            print(obj.asDict())
        count += 1
else:
    with open('raw_gravity.csv', 'w+', newline='') as gravity:
        with open('raw_jdam.csv', 'w+', newline='') as jdam:
            with open('raw_wcmd.csv', 'w+', newline='') as wcmd:
                with open('raw_jassm.csv', 'w+', newline='') as jassm:
                    with open('raw_mald.csv', 'w+', newline='') as mald:
                        writergrav = csv.writer(gravity)
                        writerjdam = csv.writer(jdam)
                        writerwcmd = csv.writer(wcmd)
                        writerjassm = csv.writer(jassm)
                        writermald = csv.writer(mald)

                        for obj, start, end in name_parser.scanString(sample):
                            if obj['Application ID'] == '13':
                                obj.pop("TGTING Data", None)
                                JdamParse(obj)
                                if jcount == 0:
                                    writerjdam.writerow(obj.asDict().keys())
                                input = list(obj.asDict().values())
                                writerjdam.writerow(input)
                                jcount += 1
                            if obj['Application ID'] == '1':
                                GravParse(obj)
                                if gcount == 0:
                                    writergrav.writerow(obj.asDict().keys())
                                input = list(obj.asDict().values())
                                writergrav.writerow(input)
                                gcount += 1
                            if obj['Application ID'] == '7':
                                WcmdParse(obj)
                                if wcount == 0:
                                    writerwcmd.writerow(obj.asDict().keys())
                                input = list(obj.asDict().values())
                                writerwcmd.writerow(input)
                                wcount += 1
                            if obj['Application ID'] == '9':
                                #JassmParse(obj)
                                if jmcount == 0:
                                    writerjassm.writerow(obj.asDict().keys())
                                input = list(obj.asDict().values())
                                writerjassm.writerow(input)
                                jmcount += 1
                            if obj['Application ID'] == '12':
                                #MaldParse(obj)
                                if mcount == 0:
                                    writermald.writerow(obj.asDict().keys())
                                input = list(obj.asDict().values())
                                writermald.writerow(input)
                                mcount += 1
                            count += 1
    path = './'
    all_files = glob.glob(os.path.join(path, "*.csv"))
    fname = 'raw_data' + datetime.datetime.now().strftime('%H%M%S') + '.xlsx'
    writer = pd.ExcelWriter(fname)
    for f in all_files:
        df = pd.read_csv(f)
        if not df.empty:
            df.to_excel(writer, sheet_name=os.path.splitext(os.path.basename(f))[0], index=False)

    writer.save()



print(count)





