from wpnparse import *
from pyparsing import *
from larparse import *
import timeit
import config
import numpy as np




def msnsplit():
    start_time = timeit.default_timer()

    config.msnData = open(config.filename[0], 'r', errors='ignore').read()

    flts = [m.start() for m in re.finditer('Minor Frame: 0000000', config.msnData)]
    flts.append(len(config.msnData))

    diff = []
    config.ranges = []
    config.msndates = []


    for x,y in zip(flts[1:],flts):
        flight = config.msnData[y:x]
        records = [m.start() for m in re.finditer('Mission Event',flight)]
        #print(len(records))
        if len(records)>40:
            diff.append(x - y)
            config.ranges.append([y, x - 1])

            dates = re.findall("[0-9]+\/[0-9]+/[0-9]+", flight)
            dates[:] = [x for x in dates if x != '01/01/00']
            config.msndates.append(dates[0])


    config.ranges.reverse()
    config.msndates.reverse()


    #print(flts)
    #print(alldates)
    #print(len(alldates))
    #print(datestarts)
    #print(len(datestarts))
    #print(config.ranges)


    elapsed = timeit.default_timer() - start_time
    print('\r' + str(round(elapsed)) + ' secs')

def parserelease():


    print('Parsing Releases...')

    debug = False

    record = Group(Literal("Record Number") + Word(nums)) + Suppress(Literal("Weapon Scoring") + lineEnd())
    msnEventExpanded = Suppress(Group(Literal("Launch") + LineEnd())) | Suppress(
        Group(Literal("Gravity Weapon Scoring") + LineEnd())) | Suppress(Group(Literal("Weapon Launch") + LineEnd()))
    eventKey = SkipTo(": ")
    # Improve?
    eventValue = SkipTo(lineEnd)
    eventData = NotAny("Launch") + NotAny("Gravity Weapon Scoring") + NotAny("Weapon Launch") + NotAny('Weapon Jettison') + Group(
        eventKey + Suppress(":") + eventValue) + Suppress(lineEnd())
    recordBlock = record + OneOrMore(eventData) + msnEventExpanded

    pData = Suppress(Literal("PERTINENT DATA"))
    SPACE_CHARS = ' \t'
    dataField = CharsNotIn(SPACE_CHARS)
    space = Word(SPACE_CHARS, exact=1) ^ Word(SPACE_CHARS, exact=2) ^ Word(SPACE_CHARS, exact=3) ^ Word(SPACE_CHARS,exact=4) ^ Word(SPACE_CHARS, exact=5) #^ Word(SPACE_CHARS, exact=8)
    dataKey = delimitedList(dataField, delim=space, combine=True)
    dataValue = Combine(dataField + ZeroOrMore(space + dataField))
    dataBlock = Group(dataKey + dataValue) + Optional(Suppress("(" + Word(alphanums) + ")")) + Suppress(
        LineEnd()) | Group(dataKey + Suppress("(") + Word(alphanums) + Suppress(")")) + Suppress(LineEnd()) | Group(
        dataKey + dataValue) + Suppress(LineEnd())

    name_parser = Dict(recordBlock + pData + OneOrMore(dataBlock))

    config.count = 0

    config.jdam = []
    config.gwd = []
    config.wcmd = []
    config.jassm = []
    config.mald = []

    if debug:
        for obj, start, end in name_parser.scanString(config.msnData):
            # print(obj.asDict())
            if obj['Application ID'] == '13':
                obj.pop("TGTING Data", None)
                jdamparse(obj)
                config.jdam.append(obj)
                print(obj.asDict())
            if obj['Application ID'] == '1':
                gwdparse(obj)
                config.gwd.append(obj)
                print(obj.asDict())
            if obj['Application ID'] == '7':
                wcmdparse(obj)
                config.wcmd.append(obj)
                print(obj.asDict())
            if obj['Application ID'] == '9':
                jassmparse(obj)
                config.jassm.append(obj)
                print(obj.asDict())
            if obj['Application ID'] == '12':
                maldparse(obj)
                config.mald.append(obj)
                print(obj.asDict())
            config.count += 1
    else:
        for obj, start, end in name_parser.scanString(config.msnData):
            currentWPN = obj.asDict()
            if obj['Application ID'] == '13':
                obj.pop("TGTING Data", None)
                jdamparse(obj)
                currentWPN = obj.asDict()
                currentWPN['wpn'] = 'JDAM'
                config.jdam.append(currentWPN)
            if obj['Application ID'] == '1':
                gwdparse(obj)
                obj.append(['wpn', 'gwd'])
                currentWPN = obj.asDict()
                currentWPN['wpn'] = 'GWD'
                config.gwd.append(currentWPN)
            if obj['Application ID'] == '7':
                wcmdparse(obj)
                obj.append(['wpn', 'wcmd'])
                currentWPN = obj.asDict()
                currentWPN['wpn'] = 'WCMD'
                config.wcmd.append(currentWPN)
            if obj['Application ID'] == '9':
                jassmparse(obj)
                obj.append(['wpn', 'jassm'])
                currentWPN = obj.asDict()
                currentWPN['wpn'] = 'JASSM'
                config.jassm.append(currentWPN)
            if obj['Application ID'] == '12':
                maldparse(obj)
                obj.append(['wpn', 'mald'])
                currentWPN = obj.asDict()
                currentWPN['wpn'] = 'MALD'
                config.mald.append(currentWPN)
            config.count += 1
        print('\rReleases Found: ' + str(config.count))
        config.releases_available.set()
def parselar():
    print('\rParsing LARs...')

    debug = False

    record = Group(Literal("Record Number") + Word(nums)) + Suppress(Literal("Weapon Event") + lineEnd())
    msnEventExpanded = Suppress(Group(Literal("Change of IR IZ LAR") + LineEnd())) | Suppress(
        Group(Literal("Change of In-Range/In-Zone Status") + LineEnd()))
    eventKey = SkipTo(": ")
    # Improve?
    eventValue = SkipTo(lineEnd)
    eventData = NotAny("Change of In-Range/In-Zone Status") + NotAny("Change of IR IZ LAR") + NotAny("Launch") + NotAny(
        "Gravity Weapon Scoring") + NotAny("Weapon Launch") + NotAny('Weapon Jettison') + Group(
        eventKey + Suppress(":") + eventValue) + Suppress(lineEnd())
    recordBlock = record + OneOrMore(eventData) + msnEventExpanded

    pData = Suppress(Literal("PERTINENT DATA"))
    SPACE_CHARS = ' \t'
    dataField = CharsNotIn(SPACE_CHARS)
    space = Word(SPACE_CHARS, exact=1) ^ Word(SPACE_CHARS, exact=2)  # ^ Word(SPACE_CHARS, exact=8)
    dataKey = delimitedList(dataField, delim=space, combine=True)
    dataValue = Combine(dataField + ZeroOrMore(space + dataField))
    dataBlock = Group(dataKey + dataValue) + Optional(Suppress("(" + Word(alphanums) + ")")) + Suppress(
        LineEnd()) | Group(dataKey + Suppress("(") + Word(alphanums) + Suppress(")")) + Suppress(LineEnd()) | Group(
        dataKey + dataValue) + Suppress(LineEnd())

    name_parser = Dict(recordBlock + pData + OneOrMore(dataBlock))

    config.countlars = 0

    config.LARjassm = []
    config.LARmald = []

    if debug:
        for obj, start, end in name_parser.scanString(config.msnData):

            if obj['Application ID'] == '9':
                LARjassmparse(obj)
                config.LARjassm.append(obj.asDict())
            if obj['Application ID'] == '12':
                LARmaldparse(obj)
                config.LARmald.append(obj.asDict())
            print(obj.asDict())
            config.countlars += 1
        print('\rLARs Found: ' + str(config.countlars))
    else:
        for obj, start, end in name_parser.scanString(config.msnData):
            if obj['Application ID'] == '9':
                LARjassmparse(obj)
                config.LARjassm.append(obj.asDict())
            if obj['Application ID'] == '12':
                LARmaldparse(obj)
                config.LARmald.append(obj.asDict())

            config.countlars += 1
        print('\rLARs Found: ' + str(config.countlars))
    config.lars_available.set()

def parsemsnevn():


    print('Parsing Msn Events...')

    debug = False

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
        for obj, start, end in name_parser.scanString(config.msnData):
            print(obj.dump())
            count += 1
    else:
        for obj, start, end in name_parser.scanString(config.msnData):
            evnparse(obj)
            MsnEvents.append(obj.asDict())

            config.ProgressMsnEvent = round(end / len(config.msnData) * 80, 1)

        if len(MsnEvents) > 0:

            config.dfMsnEvents = pd.DataFrame(MsnEvents)


    print('\rMission Events Found: ' + str(len(MsnEvents)))
    config.events_available.set()

def evnparse(evn):
    try:
        evn['FCIraw'] = evn.pop('FCI')
    except:
        pass

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
            evn['FCI'] = round(float(evn['FCI']) * (-1),2)
        if '+ ' in evn['FCIraw']:
            evn['FCI'] = round(float(evn['FCI']),2)
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
    evn['XHair'] = str(evn['GPI Mnemonic'].replace('DEST','D').replace('FXPT','FX')) + str(evn['GPI Display Number'])
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

    try:
        BuffersN = float(evn['SPPA Distance North'].replace('  feet', '').replace('+ ', '').replace('- ', ''))
        BuffersE = float(evn['SPPA Distance East'].replace('  feet', '').replace('+ ', '').replace('- ', ''))
        if "- " in evn['SPPA Distance North']:
            BuffersN = BuffersN * -1
        if "- " in evn['SPPA Distance East']:
            BuffersE = BuffersE * -1
        evn['Buffers'] = round(Vector2Polar(BuffersN,BuffersE)[1])
    except:
        evn['Buffers'] = "ERR"

    return evn
def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return str(d["hours"]) + ':'+ str(d["minutes"]).zfill(2) + ':' + str(d["minutes"]).zfill(2)

#print(strfdelta(pd.to_timedelta("00:08:50"),"{hours}:{minutes}:{seconds}"))

def larreleasepair(lar, release):
    #Inefficient way to match the last LAR LS record with the release record
    #Subtracts time difference between LAR TOF Timestamp and Release Timestamp
    release['Time (UTC)']= pd.to_datetime(release['Time (UTC)'])
    release['TOR'] = pd.to_datetime(release['TOR'])
    lar['Time (UTC)'] = pd.to_datetime(lar['Date'] + ' ' + lar['Time (UTC)'])
    lar['TOF'] = pd.to_timedelta(lar['TOF'])

    for i, row in release.iterrows():
        try:
            pairedlars = lar[lar['LS'] == row.LS]
            TOF = pairedlars['TOF'][pairedlars.index[-1]]
            TOFtimestamp = pairedlars['Time (UTC)'][pairedlars.index[-1]]
            TimeVariation = release.at[i,'Time (UTC)'] - TOFtimestamp #Difference between LARevent and TOR
            if TOF > pd.Timedelta(12,unit='hours'):
                TOF = TOF - pd.Timedelta(12,unit='hours')
            release.at[i,'TOF'] = strfdelta(TOF,"{hours}:{minutes}:{seconds}")
            release.at[i, 'TOT'] = release.at[i,'Time (UTC)'] + (TOF - TimeVariation)
        except:
            pass
        """
        print(row.LS)
        print(TOFtimestamp)
        print(release.at[i, 'Time (UTC)'])
        print(TOF)
        print(TimeVariation)
        print(release.at[i,'Time (UTC)'] + (TOF))
        print(release.at[i, 'TOT'])
        """
    return release
def msnevnpair(input, msnevents):

    input['Time (UTC)'] = pd.to_datetime(input['Date'] + ' ' + input['Time (UTC)'])

    msnEventsIndex = [pd.Index(msnevents['Time (UTC)']).get_loc(x, method='nearest') for x in input['Time (UTC)']]
    msnEvent = [msnevents['Time (UTC)'].loc[x] for x in msnEventsIndex]
    recordNumber = [msnevents['Record Number'].loc[x] for x in msnEventsIndex]
    XHair = [msnevents['XHair'].loc[x] for x in msnEventsIndex]
    PrimeNav = [msnevents['PrimeNav'].loc[x] for x in msnEventsIndex]
    PrimeNavAiding = [msnevents['PrimeNavAiding'].loc[x] for x in msnEventsIndex]
    IAS = [msnevents['IAS'].loc[x] for x in msnEventsIndex]
    TAS = [msnevents['TAS'].loc[x] for x in msnEventsIndex]
    MHDG = [msnevents['MHDG'].loc[x] for x in msnEventsIndex]
    GTRK= [msnevents['GTRK'].loc[x] for x in msnEventsIndex]
    FCI= [msnevents['FCI'].loc[x] for x in msnEventsIndex]
    Mach= [msnevents['Mach'].loc[x] for x in msnEventsIndex]
    Temp= [msnevents['Temp'].loc[x] for x in msnEventsIndex]
    WindDir= [msnevents['WindDir'].loc[x] for x in msnEventsIndex]
    WindSpeed = [msnevents['WindSpeed'].loc[x] for x in msnEventsIndex]
    Buffers = [msnevents['Buffers'].loc[x] for x in msnEventsIndex]




    input.insert(len(input.columns),"msnEventTime", msnEvent, False)
    input.insert(len(input.columns),"RecordNumber", recordNumber, False)
    input.insert(len(input.columns), "XHair", XHair, False)
    try:
        input.insert(len(input.columns), "PrimeNav", PrimeNav, False)
    except:
        pass
    input.insert(len(input.columns), "PrimeNavAiding", PrimeNavAiding, False)
    input.insert(len(input.columns), "IAS", IAS, False)
    input.insert(len(input.columns), "TAS", TAS, False)
    input.insert(len(input.columns), "MHDG", MHDG, False)
    try:
        input.insert(len(input.columns), "GTRK", GTRK, False)
    except:
        pass
    input.insert(len(input.columns), "FCI", FCI, False)
    input.insert(len(input.columns), "Mach", Mach, False)
    input.insert(len(input.columns), "Temp", Temp, False)
    input.insert(len(input.columns), "WindDir", WindDir, False)
    input.insert(len(input.columns), "WindSpeed", WindSpeed, False)

    input.insert(len(input.columns), "TGT NAME", "", False)
    try:
        input.insert(len(input.columns), "Buffers", Buffers, False)
    except:
        pass

    try:
        input.insert(len(input.columns), "FOM", "1", False)
    except:
        pass

    return input