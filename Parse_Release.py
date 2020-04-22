from pyparsing import *
import pandas as pd
import csv

debug = False

def JdamParse(wpn):
    wpn['Tail'] = wpn['Tail Year'][1] + '0' + wpn['Tail Number']
    # print(wpn['Tail Number'])

    if wpn['MSN Planned TGT'] == 'True':
        wpn['Dest'] = 'MPdest'
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
        wpn['GTRK'] = round(float(wpn['GND Trk Angle'].replace('+ ', '').replace('- ', '').replace('  deg', '')))
    except:
        wpn['GTRK'] = 'ERR'
    # print(wpn['GTRK'])

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
    elif wpn['Func on Void'] == 'TRUE':
        wpn['Delay'] = 'VOID' + str(wpn['Void Number'])

    return wpn


sample = open('Test 1012.txt', 'r', errors='ignore').read()

record = Group(Literal("Record Number") + Word(nums)) + Suppress(Literal("Weapon Scoring") + lineEnd())
msnEventExpanded = Suppress(Group(Literal("Launch") + LineEnd())) | Suppress(Group(Literal("Gravity Weapon Scoring") + LineEnd()))
eventKey = SkipTo(": ")
    #Improve?
eventValue = SkipTo(lineEnd)
eventData = NotAny("Launch") + NotAny("Gravity Weapon Scoring") + Group(eventKey + Suppress(":") + eventValue) + Suppress(lineEnd())
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

if debug:
    for obj, start, end in name_parser.scanString(sample):
        if obj['Application ID'] == '13':
            JdamParse(obj)
        print(obj.asDict())
        count += 1
else:
    with open('test_gravity.csv', 'w+', newline='') as gravity:
        with open('test_jdam.csv', 'w+', newline='') as jdam:
            writergrav = csv.writer(gravity)
            writerjdam = csv.writer(jdam)

            for obj, start, end in name_parser.scanString(sample):
                if obj['Application ID'] == '13':
                    JdamParse(obj)
                    if jcount == 0:
                        writerjdam.writerow(obj.asDict().keys())
                    input = list(obj.asDict().values())
                    writerjdam.writerow(input)
                    jcount += 1
                if obj['Application ID'] == '1':
                    if gcount == 0:
                        writergrav.writerow(obj.asDict().keys())
                    input = list(obj.asDict().values())
                    writergrav.writerow(input)
                    gcount += 1
                count += 1

print(count)


