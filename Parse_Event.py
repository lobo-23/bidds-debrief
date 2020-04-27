from pyparsing import *
import pandas as pd
import timeit
import numpy as np

def Vector2Polar(N,E):
    Mag = np.sqrt(N**2 + E**2)
    Az = 90 - np.arctan2(N, E) * 180/np.pi
    if Az <= 0:
        Az = Az + 360
    return(Az, Mag)
def EventParse(evn):
    evn['FCIraw'] = evn.pop('FCI')
    evn['TASraw'] = evn.pop('TAS')

    if evn['Tail Year'] == '0':
        evn['Tail Year'] = '00'
    evn['Tail'] = evn['Tail Year'][1] + '0' + "{:02d}".format(int(evn['Tail Number']))
    # print(wpn['Tail Number'])

    try:
        evn['LAT'] = evn['Present Latitude'].replace('  deg', '').replace(':', ' ').replace('N 0', "N ").replace('S 0', "S ")
    except:
        evn['LAT'] = 'ERR'
    try:
        evn['LONG'] = evn['Present Longitude'].replace('  deg', '').replace(':', ' ')
    except:
        evn['LONG'] = 'ERR'

    # print(wpn['LAT'])
    # print(wpn['LONG'])

    try:
        evn['ALT'] = str(round(float(evn['Present Altitude'].replace('  feet', '').replace('+ ', '').replace('- ', ''))))
    except:
        evn['ALT'] = 'ERR'
    #print(wpn['ALT'])

    try:
        evn['MHDG'] = round(float(evn['Magnetic Heading'].replace('+ ', '').replace('- ', '').replace('  deg', '')))
        if '-' in evn['Magnetic Heading']:
            evn['MHDG'] = 360 - evn['MHDG']
    except:
        evn['MHDG'] = 'ERR'
    #print(wpn['THDG'])
    try:
        evn['THDG'] = round(float(evn['Present Heading'].replace('+ ', '').replace('- ', '').replace('  deg', '')))
        if '-' in evn['Present Heading']:
            evn['THDG'] = 360 - evn['THDG']
    except:
        evn['THDG'] = 'ERR'
    #print(wpn['THDG'])



    try:
        evn['GTRK'] = round(float(evn['Present Ground Track'].replace('+ ', '').replace('- ', '').replace('  deg', '')))
        if '-' in evn['Present Ground Track']:
            evn['GTRK'] = 360 - evn['GTRK']
    except:
        evn['GTRK'] = 'ERR'
    try:
        evn['FCI'] = evn['FCIraw'].replace('+ ', '').replace('- ', '').replace('  deg', '')
        if '- ' in evn['FCIraw']:
            evn['FCI'] = float(evn['FCI']) * (-1)
    except:
        evn['FCI'] = 'ERR'
    try:
        evn['IAS'] = round(float(evn['Indicated air Speed'].replace('  ft/sec', '')) * 0.592484)
    except:
        evn['IAS'] = 'ERR'
    try:
        evn['TAS'] = round(float(evn['TASraw'].replace('  ft/sec', '').replace('+ ', '')) * 0.592484)
    except:
        evn['TAS'] = 'ERR'

    evn['GS'] = round(float(evn['Present Ground Speed'].replace('  knots', '')))
    evn['Mach'] = float(evn['Mach Value'])
    # print(wpn['GS'])
    evn['PrimeNav'] = evn['Prime Data Source'].replace(' ','')
    # print(wpn['PrimeNav'])
    evn['PrimeNavAiding'] = evn['Prime INU Aiding Mode'].replace(' Inertial','').replace('Doppler','DOPP')
    # print(wpn['PrimeNavAiding'])
    evn['XHair'] = str(evn['GPI Mnemonic'].replace('DEST','D')) + str(evn['GPI Display Number'])
    # print(wpn['PrimeNavAiding'])
    try:
        evn['Temp'] = round((float(evn['Free Air Temperature'].replace('  deg R','')) -491.67)*5/9)
    except:
        evn['Temp'] = 'ERR'
    try:
        WindN = float(evn['Wind Velocity N'].replace('  ft/sec', '').replace('+ ', '').replace('- ', '')) * 0.592484
        WindE = float(evn['Wind Velocity E'].replace('  ft/sec', '').replace('+ ', '').replace('- ', '')) * 0.592484
        evn['WindDir'] = round(Vector2Polar(WindN,WindE)[0])
        evn['WindSpeed'] = round(Vector2Polar(WindN,WindE)[1])
    except:
        evn['WindDir'] = "ERR"
        evn['WindSpeed'] = "ERR"

    return evn


start_time = timeit.default_timer()
debug = False

sample = open('Test MSN EVN.txt', 'r', errors='ignore').read()


record = Group(Literal("Record Number") + Word(nums)) + Suppress(Literal("Mission Event") + Literal("Application ID: 36") + Literal("Record Type: 1") + Literal("Record Subtype: 1")+ Suppress(lineEnd()))
msnEventExpanded = Suppress(Group(Literal("Mission Event") + LineEnd()))
eventKey = SkipTo(": ") # Improve?
eventValue = SkipTo(lineEnd)
eventData = NotAny("Mission Event") + Group(eventKey + Suppress(":") + eventValue) + Suppress(lineEnd())
recordBlock = record  + OneOrMore(eventData) + msnEventExpanded

pData = Suppress(Literal("PERTINENT DATA"))
SPACE_CHARS = ' \t'
dataField = CharsNotIn(SPACE_CHARS,max=25)
space = Word(SPACE_CHARS, exact=1)^Word(SPACE_CHARS, exact=2)^Word(SPACE_CHARS, exact=3)^Word(SPACE_CHARS, exact=4)^Word(SPACE_CHARS, exact=5)
dataKey = delimitedList(dataField, delim=space, combine=True)
dataValue = Combine(dataField + ZeroOrMore(space + dataField))

dataBlock = Group(dataKey + dataValue) + Optional(Suppress("(" + dataValue + ")")) + Optional(Suppress("(" + Word(alphanums) + ")")) + Suppress(LineEnd()) |   Group(dataKey + Suppress("(") + Word(alphanums) + Suppress(")")) + Suppress(LineEnd()) | Group(dataKey + dataValue) + Suppress(LineEnd()) | Group(dataKey + Literal('Undefined Value')) + Suppress("(Enum Value" + Word(nums) +")" +  "(" + Word(alphanums) + ")" + LineEnd())

name_parser = Dict(recordBlock + pData + OneOrMore(dataBlock))

count = 0
MsnEvents = []

if debug:
    for obj, start, end in name_parser.scanString(sample):
        print(obj.dump())
        count += 1
else:
    for obj, start, end in name_parser.scanString(sample):
        EventParse(obj)
        MsnEvents.append(obj.asDict())
    if len(MsnEvents) > 0:
        dfMsnEvents = pd.DataFrame(MsnEvents)

    dfMsnEvents.to_csv('msn_events.csv',index=False)
elapsed = timeit.default_timer() - start_time
print(elapsed)
print(len(MsnEvents))