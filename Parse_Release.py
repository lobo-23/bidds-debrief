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
        wpn['GTRK'] = round(float(wpn['GND Trk Angle'].replace('+ ', '').replace('- ', '').replace('  deg','')))
        if '-' in wpn['GND Trk Angle']:
            wpn['GTRK'] = 360 - wpn['GTRK']
    except:
        wpn['GTRK'] = 'ERR'

    wpn['LS'] = wpn['Dev ID'].replace('P', '')
    # print(wpn['LS'])

    wpn['GS'] = round(float(wpn['GND Speed'].replace('  ft/sec', '')) * 0.592484)
    # print(wpn['GS'])


    if wpn['Func at Impact'] == 'TRUE':
        wpn['Delay'] = "IMP"
    elif wpn['Func on Proximity'] == 'TRUE':
        wpn['Delay'] = 'PROX'
    elif wpn['Func on Time Aft Impact'] == 'TRUE':
        wpn['Delay'] = 'DEL'

    try:
        if wpn['Function on Void'] == 'TRUE':
            wpn['Delay'] = 'VOID' + str(wpn['Void Number'])
    except:
        try:
            if wpn['Func on Void'] == 'TRUE':
                wpn['Delay'] = 'VOID' + str(wpn['Void Number'])
        except:
            print('Can\'t find Func on Void')



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
        wpn['ALT'] = str(round(float(wpn['Aircraft Altitude'].replace('  feet', '').replace('+ ', ''))))
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
        wpn['ALT'] = str(round(float(wpn['Altitude'].replace('  feet', '').replace('+ ', ''))))
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

    wpn['LS'] = wpn['Device ID'].replace('P', '')
    wpn['GS'] = round(float(wpn['Ground Speed'].replace('  ft/sec', '')) * 0.592484)
    wpn['Delay'] = wpn['Fuze Option'].replace('Prox_Fuzing', 'PROX')

def msnEventparse(input, msnevents):

    records = msnevents

    input['Time (UTC)'] = pd.to_datetime(input['Date'] + ' ' + input['Time (UTC)'])
    records['Time (UTC)'] = pd.to_datetime(records['Date'] + ' ' + records['Time (UTC)'])

    msnEventsIndex = [pd.Index(records['Time (UTC)']).get_loc(x, method='nearest') for x in input['Time (UTC)']]
    msnEvent = [records['Time (UTC)'].loc[x] for x in msnEventsIndex]
    recordNumber = [records['Record Number'].loc[x] for x in msnEventsIndex]
    XHair = [records['XHair'].loc[x] for x in msnEventsIndex]
    PrimeNav = [records['PrimeNav'].loc[x] for x in msnEventsIndex]
    PrimeNavAiding = [records['PrimeNavAiding'].loc[x] for x in msnEventsIndex]
    IAS = [records['IAS'].loc[x] for x in msnEventsIndex]
    TAS = [records['TAS'].loc[x] for x in msnEventsIndex]
    MHDG = [records['MHDG'].loc[x] for x in msnEventsIndex]
    GTRK= [records['GTRK'].loc[x] for x in msnEventsIndex]
    FCI= [records['FCI'].loc[x] for x in msnEventsIndex]
    Mach= [records['Mach'].loc[x] for x in msnEventsIndex]
    Temp= [records['Temp'].loc[x] for x in msnEventsIndex]
    WindDir= [records['WindDir'].loc[x] for x in msnEventsIndex]
    WindSpeed = [records['WindSpeed'].loc[x] for x in msnEventsIndex]


    input.insert(len(input.columns),"msnEventTime", msnEvent, False)
    input.insert(len(input.columns),"RecordNumber", recordNumber, False)
    input.insert(len(input.columns), "XHair", XHair, False)
    try:
        input.insert(len(input.columns), "PrimeNav", PrimeNav, False)
    except:
        print('Prime Nav already exists')
    input.insert(len(input.columns), "PrimeNavAiding", PrimeNavAiding, False)
    input.insert(len(input.columns), "IAS", IAS, False)
    input.insert(len(input.columns), "TAS", TAS, False)
    input.insert(len(input.columns), "MHDG", MHDG, False)
    try:
        input.insert(len(input.columns), "GTRK", GTRK, False)
    except:
        print("GTRK already exists")
    input.insert(len(input.columns), "FCI", FCI, False)
    input.insert(len(input.columns), "Mach", Mach, False)
    input.insert(len(input.columns), "Temp", Temp, False)
    input.insert(len(input.columns), "WindDir", WindDir, False)
    input.insert(len(input.columns), "WindSpeed", WindSpeed, False)

    return input
sample = open('Test 1012.txt', 'r', errors='ignore').read()

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

jdam = []
gwd = []
wcmd = []
jassm = []
mald = []

if debug:
    for wpn, start, end in name_parser.scanString(sample):
        #print(obj.asDict())
        if obj['Application ID'] == '13':
            obj.pop("TGTING Data", None)
            JdamParse(obj)
            jdam.append(obj)
            print(obj.asDict())
        if obj['Application ID'] == '1':
            GravParse(obj)
            gwd.append(obj)
            print(obj.asDict())
        if obj['Application ID'] == '7':
            WcmdParse(obj)
            wcmd.append(obj)
            print(obj.asDict())
        if obj['Application ID'] == '9':
            #JassmParse(obj)
            jassm.append(obj)
            print(obj.asDict())
        if obj['Application ID'] == '12':
            #MaldParse(obj)
            mald.append(obj)
            print(obj.asDict())
        count += 1
else:
    for obj, start, end in name_parser.scanString(sample):
        currentWPN = obj.asDict()
        if obj['Application ID'] == '13':
            obj.pop("TGTING Data", None)
            JdamParse(obj)
            currentWPN = obj.asDict()
            currentWPN['wpn'] = 'JDAM'
            jdam.append(currentWPN)
        if obj['Application ID'] == '1':
            GravParse(obj)
            obj.append(['wpn','gwd'])
            currentWPN = obj.asDict()
            currentWPN['wpn'] = 'GWD'
            gwd.append(currentWPN)
        if obj['Application ID'] == '7':
            WcmdParse(obj)
            obj.append(['wpn','wcmd'])
            currentWPN = obj.asDict()
            currentWPN['wpn'] = 'WCMD'
            wcmd.append(currentWPN)
        if obj['Application ID'] == '9':
            #JassmParse(obj)
            obj.append(['wpn','jassm'])
            currentWPN = obj.asDict()
            currentWPN['wpn'] = 'JASSM'
            jassm.append(currentWPN)
        if obj['Application ID'] == '12':
            #MaldParse(obj)
            obj.append(['wpn','mald'])
            currentWPN = obj.asDict()
            currentWPN['wpn'] = 'MALD'
            mald.append(currentWPN)
        count += 1

    allWPNs = []
    dfAllWPNS = []
    if len(jdam) > 0:
        dfJDAM = pd.DataFrame(jdam)
        msnEventparse(dfJDAM,pd.read_csv('msn_events.csv'))
        allWPNs.append(dfJDAM)
        dfJDAMfiltered = dfJDAM.filter(['Record Number', 'Tail', 'wpn', 'Dest', 'TOT', 'TOR', 'TOF', 'WPN Type','TGT LAT',
                                      'TGT LON', 'TGT ELEV', 'PrimeNav', 'XHair', 'PrimeNavAiding','ALT', 'GTRK', 'IAS',
                                      'MHDG', 'TAS', 'LS','FCI'], axis=1)
        dfAllWPNS.append(dfJDAMfiltered)
    if len(gwd) > 0:
        dfGWD = pd.DataFrame(gwd)
        msnEventparse(dfGWD, pd.read_csv('msn_events.csv'))
        allWPNs.append(dfGWD)
        dfGWDfiltered = dfGWD.filter(['Record Number', 'Tail', 'wpn', 'Dest', 'TOT', 'TOR', 'TOF', 'WPN Type','TGT LAT',
                                      'TGT LON', 'TGT ELEV', 'PrimeNav', 'XHair', 'PrimeNavAiding','ALT', 'GTRK', 'IAS',
                                      'MHDG', 'TAS', 'LS','FCI'], axis=1)
        dfAllWPNS.append(dfGWDfiltered)
    if len(wcmd) > 0:
        dfWCMD = pd.DataFrame(wcmd)
        msnEventparse(dfWCMD, pd.read_csv('msn_events.csv'))
        allWPNs.append(dfWCMD)
        dfWCMDfiltered = dfWCMD.filter(['Record Number', 'Tail', 'wpn', 'Dest', 'TOT', 'TOR', 'TOF', 'WPN Type','TGT LAT',
                                      'TGT LON', 'TGT ELEV', 'PrimeNav', 'XHair', 'PrimeNavAiding','ALT', 'GTRK', 'IAS',
                                      'MHDG', 'TAS', 'LS','FCI'], axis=1)
        dfAllWPNS.append(dfWCMDfiltered)
    if len(jassm) > 0:
        dfJASSM = pd.DataFrame(jassm)
        msnEventparse(dfJASSM, pd.read_csv('msn_events.csv'))
        allWPNs.append(dfJASSM)
        dfJASSMfiltered = dfJASSM.filter(['Record Number', 'Tail', 'wpn', 'Dest', 'TOT', 'TOR', 'TOF', 'WPN Type','TGT LAT',
                                      'TGT LON', 'TGT ELEV', 'PrimeNav', 'XHair', 'PrimeNavAiding','ALT', 'GTRK', 'IAS',
                                      'MHDG', 'TAS', 'LS','FCI'], axis=1)
        dfAllWPNS.append(dfJASSMfiltered)
    if len(mald) > 0:
        dfMALD = pd.DataFrame(dfMALD)
        msnEventparse(dfMALD, pd.read_csv('msn_events.csv'))
        allWPNs.append(dfJDAM)
        dfMALDfiltered = dfMALD.filter(['Record Number', 'Tail', 'wpn', 'Dest', 'TOT', 'TOR', 'TOF', 'WPN Type','TGT LAT',
                                      'TGT LON', 'TGT ELEV', 'PrimeNav', 'XHair', 'PrimeNavAiding','ALT', 'GTRK', 'IAS',
                                      'MHDG', 'TAS', 'LS','FCI'], axis=1)
        dfAllWPNS.append(dfMALDfiltered)

    dfCombined = pd.concat(dfAllWPNS)
    fname = 'raw_data ' + datetime.datetime.now().strftime('%H%M%S') + '.xlsx'

    writer = pd.ExcelWriter(fname)

    for df in allWPNs:
        sheetname = df.loc[0,'wpn']
        df.to_excel(writer, sheet_name=str(sheetname), index=False)
    dfCombined.to_excel(writer, sheet_name='Combined', index=False)
    writer.save()

print(count)





