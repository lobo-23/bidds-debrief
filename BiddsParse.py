from pyparsing import *
import pandas as pd
import glob, sys, datetime, os, openpyxl
import threading
import numpy as np
import timeit
import time
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QThread, pyqtSignal

class External(QThread):
    """
    Runs a counter thread.
    """
    countChanged = pyqtSignal(int)

    def run(self):
        global ProgressMsnEvent
        ProgressMsnEvent = 0
        while ProgressMsnEvent < 100:
            time.sleep(1)
            self.countChanged.emit(ProgressMsnEvent)

class Ui(QtWidgets.QDialog):
    def __init__(self):
        super(Ui, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('GUI.ui', self) # Load the .ui file


        self.TXTload = self.findChild(QtWidgets.QPushButton, 'pushButton_TXTLoad') # Find the button
        self.TXTload.clicked.connect(self.TXTLoadPressed) # Remember to pass the definition/method, not the return value!

        self.BIDDSOpen = self.findChild(QtWidgets.QPushButton, 'pushButton_BIDDSOpen') # Find the button
        self.BIDDSOpen.clicked.connect(self.BIDDSLoadPressed) # Remember to pass the definition/method, not the return value!

        self.progressbar = self.findChild(QtWidgets.QProgressBar, 'progressBar')
        self.progressbar.setValue(0)
        self.show() # Show the GUI

    def onCountChanged(self, value):
        self.progressbar.setValue(value)

    def TXTLoadPressed(self):
        global filename
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open TXT file',
                                            os.getcwd(), "Text File (*.txt)")
        if len(filename[0]) > 0:

            global parse_pending
            parse_pending = threading.Event()
            filename = filename[0]

            global ProgressMsnEvent
            ProgressMsnEvent = 5

            threadParse = threading.Thread(target=Parse)
            threadParse.start()

            self.calc = External()
            self.calc.countChanged.connect(self.onCountChanged)
            self.calc.start()


    def BIDDSLoadPressed(self):
        # This is executed when the button is pressed
        print('BIDDSLoadPressed')
        copyDirectory(r'.\Files\BIDDS', "C:\BIDDS")
        os.startfile('C:\BIDDS\BIDDS.exe')

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
            wpn['TOF'] = round(float(wpn['TOF'].replace('  sec', '').replace('+ ', '')))
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

    wpn['WPN Code']= wpn['WPN Type']
    try:
        wpn['WPN Type'] = wpn['Store Description'].replace('GBU-','').replace('(V)','v')
    except:
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
                else:
                    if wpn['Function on Void'] in wpn.keys():
                        wpn['Delay'] = 'VOID' + str(wpn['Void Number'])
                    else:
                        if wpn['Function on Void'] in wpn.keys():
                            if wpn['Function on Void'] == 'TRUE' and wpn['Delay'] == '':
                                wpn['Delay'] = 'VOID' + str(wpn['Void Number'])
    except:
        pass


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
            wpn['TOF'] = round(float(wpn['Weapon Time Of Fall'].replace('  SEC', "")))
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
        wpn['LAT'] = wpn['Aircraft Latitude'].replace('  deg', '').replace(':', ' ').replace('N 0', "N ").replace('S 0', "S ")
    except:
        wpn['LAT'] = 'ERR'
    try:
        wpn['LONG'] = wpn['Aircraft Longitude'].replace('  deg', '').replace(':', ' ')
    except:
        wpn['LONG'] = 'ERR'



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
        wpn['LAT'] = wpn['Latitude'].replace('  deg', '').replace(':', ' ').replace('N 0', "N ").replace('S 0', "S ")
    except:
        wpn['LAT'] = 'ERR'
    try:
        wpn['LONG'] = wpn['Longitude'].replace('  deg', '').replace(':', ' ')
    except:
        wpn['LONG'] = 'ERR'

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
        wpn['TGT LAT'] = 'ERR'

    wpn['LS'] = wpn['Device ID'].replace('P', '')
    wpn['GS'] = round(float(wpn['Ground Speed'].replace('  ft/sec', '')) * 0.592484)
    wpn['Delay'] = wpn['Fuze Option'].replace('Prox_Fuzing', 'PROX')

    return wpn
def JassmParse(wpn):
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
    elif wpn['IR Status'] == 'RANGE':
        wpn['LARstatus'] = 'IR'
    else:
        wpn['LARstatus'] = 'UNK'
    #print(wpn['LARstatus'])

    if wpn['Mission Planned TGT'] == 'True':
        wpn['Dest'] = wpn['LP DT Number']
    else:
        if wpn['LP DT Number'].isnumeric():
            wpn['Dest'] = "D" + str(wpn['LP DT Number'])

    #print(wpn['Dest'])

    wpn['TOR'] = pd.to_datetime(wpn['Time (UTC)'] + ' ' + wpn['Date'])
    wpn['TOF'] = ''
    wpn['TOT'] = ''

    #print(wpn['TOR'])
    #print(wpn['TOF'])
    #print(wpn['TOT'])

    if wpn['Variant Type A'] == 'True':
        wpn['WPN Type'] = 'M1'
    if wpn['Variant Type B'] == 'True':
        wpn['WPN Type'] = 'M2'
    #print(wpn['WPN Type'])

    wpn['TGT LAT'] = ''
    wpn['TGT LONG'] = ''
    wpn['TGT ELEV'] = ''

    #print(wpn['TGT LAT'])
    #print(wpn['TGT LONG'])
    #print(wpn['TGT ELEV'])

    wpn['Delay'] = ''
    #print(wpn['Delay'])
    return wpn
def MaldParse(wpn):
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
    elif wpn['IR Status'] == 'RANGE':
        wpn['LARstatus'] = 'IR'
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

    wpn['WPN Type'] = wpn['Weapon Type']
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

    #print(wpn['TGT LAT'])
    #print(wpn['TGT LONG'])
    #print(wpn['TGT ELEV'])

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

def msnEventparse(input, msnevents):
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

    return input
def ParseRelease(filename):
    print('Parsing Releases...')
    debug = False
    sample = open(filename, 'r', errors='ignore').read()

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
    space = Word(SPACE_CHARS, exact=1) ^ Word(SPACE_CHARS, exact=2) ^ Word(SPACE_CHARS, exact=3) ^ Word(SPACE_CHARS,exact=4) ^ Word(SPACE_CHARS, exact=5)^ Word(SPACE_CHARS, exact=8)
    dataKey = delimitedList(dataField, delim=space, combine=True)
    dataValue = Combine(dataField + ZeroOrMore(space + dataField))
    dataBlock = Group(dataKey + dataValue) + Optional(Suppress("(" + Word(alphanums) + ")")) + Suppress(
        LineEnd()) | Group(dataKey + Suppress("(") + Word(alphanums) + Suppress(")")) + Suppress(LineEnd()) | Group(
        dataKey + dataValue) + Suppress(LineEnd())

    name_parser = Dict(recordBlock + pData + OneOrMore(dataBlock))

    global count
    global jdam
    global gwd
    global wcmd
    global jassm
    global mald

    count = 0

    jdam = []
    gwd = []
    wcmd = []
    jassm = []
    mald = []

    if debug:
        for obj, start, end in name_parser.scanString(sample):
            # print(obj.asDict())
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
                JassmParse(obj)
                jassm.append(obj)
                print(obj.asDict())
            if obj['Application ID'] == '12':
                MaldParse(obj)
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
                obj.append(['wpn', 'gwd'])
                currentWPN = obj.asDict()
                currentWPN['wpn'] = 'GWD'
                gwd.append(currentWPN)
            if obj['Application ID'] == '7':
                WcmdParse(obj)
                obj.append(['wpn', 'wcmd'])
                currentWPN = obj.asDict()
                currentWPN['wpn'] = 'WCMD'
                wcmd.append(currentWPN)
            if obj['Application ID'] == '9':
                JassmParse(obj)
                obj.append(['wpn', 'jassm'])
                currentWPN = obj.asDict()
                currentWPN['wpn'] = 'JASSM'
                jassm.append(currentWPN)
            if obj['Application ID'] == '12':
                MaldParse(obj)
                obj.append(['wpn', 'mald'])
                currentWPN = obj.asDict()
                currentWPN['wpn'] = 'MALD'
                mald.append(currentWPN)
            count += 1
        print('\rReleases Found: ' + str(count))
        releases_available.set()

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
    evn['XHair'] = str(evn['GPI Mnemonic'].replace('DEST','D').replace('FXPT','F')) + str(evn['GPI Display Number'])
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
def ParseMsnEvent(filename):
    print('Parsing Msn Events...')
    debug = False

    sample = open(filename, 'r', errors='ignore').read()

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
    global dfMsnEvents

    if debug:
        for obj, start, end in name_parser.scanString(sample):
            print(obj.dump())
            count += 1
    else:
        for obj, start, end in name_parser.scanString(sample):
            EventParse(obj)
            MsnEvents.append(obj.asDict())
            global ProgressMsnEvent
            ProgressMsnEvent = round(end/len(sample)*80,1)
        if len(MsnEvents) > 0:
            global dfMsnEvents
            dfMsnEvents = pd.DataFrame(MsnEvents)


    print('\rMission Events Found: ' + str(len(MsnEvents)))
    events_available.set()

def main():
    app = QtWidgets.QApplication(sys.argv)  # Create an instance of QtWidgets.QApplication
    window = Ui()  # Create an instance of our class
    app.exec_()  # Start the application

def Parse():

    global events_available
    global releases_available
    global ProgressMsnEvent
    global dfMsnEvents


    #filename = 'DTC5.txt'

    start_time = timeit.default_timer()

    events_available = threading.Event()
    releases_available = threading.Event()

    ProgressMsnEvent = 0

    threadEvents = threading.Thread(target=ParseMsnEvent,args=(filename,))
    threadEvents.start()
    threadReleases = threading.Thread(target=ParseRelease,args=(filename,))
    threadReleases.start()

    allWPNs = []
    dfAllWPNS = []

    while not events_available.wait(timeout=1):
        print('\r{}% done...'.format(ProgressMsnEvent), end='', flush=True)
    ProgressMsnEvent = 80
    print('\r{}% done...'.format(ProgressMsnEvent), end='', flush=True)

    releases_available.wait()

    dfMsnEvents['Time (UTC)'] = pd.to_datetime(dfMsnEvents['Date'] + ' ' + dfMsnEvents['Time (UTC)'])
    dfMsnEvents.to_csv('msnevents.csv')
    dfMsnEvents.sort_values(by=['Time (UTC)'], inplace=True)
    filter_mask = dfMsnEvents['Time (UTC)'] > pd.Timestamp(2000, 1, 2)
    dfMsnEvents = dfMsnEvents[filter_mask]
    dfMsnEvents.drop_duplicates(subset="Time (UTC)", keep=False, inplace=True)

    if len(jdam) > 0:
        dfJDAM = pd.DataFrame(jdam)
        dfJDAM.to_csv('jdam.csv')
        msnEventparse(dfJDAM, dfMsnEvents)
        allWPNs.append(dfJDAM)
        dfJDAMfiltered = dfJDAM.filter(
            ['Record Number', 'Tail', 'wpn', 'Dest', 'TOT', 'TOR', 'TOF', 'WPN Type', 'TGT LAT',
             'TGT LONG', 'TGT ELEV', 'PrimeNav', 'XHair', 'PrimeNavAiding', 'ALT', 'GTRK', 'IAS',
             'MHDG', 'TAS', 'LS', 'GS', 'LARstatus','Delay','FCI'], axis=1)
        dfAllWPNS.append(dfJDAMfiltered)
    if len(gwd) > 0:
        dfGWD = pd.DataFrame(gwd)
        dfGWD.to_csv('gwd.csv')
        msnEventparse(dfGWD, dfMsnEvents)
        allWPNs.append(dfGWD)
        dfGWDfiltered = dfGWD.filter(
            ['Record Number', 'Tail', 'wpn', 'Dest', 'TOT', 'TOR', 'TOF', 'WPN Type', 'TGT LAT',
             'TGT LONG', 'TGT ELEV', 'PrimeNav', 'XHair', 'PrimeNavAiding', 'ALT', 'GTRK', 'IAS',
             'MHDG', 'TAS', 'LS', 'GS', 'LARstatus','Delay','FCI'], axis=1)
        dfAllWPNS.append(dfGWDfiltered)
    if len(wcmd) > 0:
        dfWCMD = pd.DataFrame(wcmd)
        dfWCMD.to_csv('wcmd.csv')
        msnEventparse(dfWCMD, dfMsnEvents)
        allWPNs.append(dfWCMD)
        dfWCMDfiltered = dfWCMD.filter(
            ['Record Number', 'Tail', 'wpn', 'Dest', 'TOT', 'TOR', 'TOF', 'WPN Type', 'TGT LAT',
             'TGT LONG', 'TGT ELEV', 'PrimeNav', 'XHair', 'PrimeNavAiding', 'ALT', 'GTRK', 'IAS',
             'MHDG', 'TAS', 'LS', 'GS', 'LARstatus','Delay','FCI'], axis=1)
        dfAllWPNS.append(dfWCMDfiltered)
    if len(jassm) > 0:
        dfJASSM = pd.DataFrame(jassm)
        dfJASSM.to_csv('jassm.csv')
        msnEventparse(dfJASSM, dfMsnEvents)
        allWPNs.append(dfJASSM)
        dfJASSMfiltered = dfJASSM.filter(
            ['Record Number', 'Tail', 'wpn', 'Dest', 'TOT', 'TOR', 'TOF', 'WPN Type', 'TGT LAT',
             'TGT LONG', 'TGT ELEV', 'PrimeNav', 'XHair', 'PrimeNavAiding', 'ALT', 'GTRK', 'IAS',
             'MHDG', 'TAS', 'LS', 'GS', 'LARstatus','Delay', 'FCI'], axis=1)
        dfAllWPNS.append(dfJASSMfiltered)
    if len(mald) > 0:
        dfMALD = pd.DataFrame(mald)
        dfMALD.to_csv('mald.csv')
        msnEventparse(dfMALD, dfMsnEvents)
        allWPNs.append(dfMALD)
        dfMALDfiltered = dfMALD.filter(
            ['Record Number', 'Tail', 'wpn', 'Dest', 'TOT', 'TOR', 'TOF', 'WPN Type', 'TGT LAT',
             'TGT LONG', 'TGT ELEV', 'PrimeNav', 'XHair', 'PrimeNavAiding', 'ALT', 'GTRK', 'IAS',
             'MHDG', 'TAS', 'LS','GS', 'LARstatus','Delay', 'FCI'], axis=1)
        dfAllWPNS.append(dfMALDfiltered)

    ProgressMsnEvent = 90
    print('\r{}% done...'.format(ProgressMsnEvent), end='', flush=True)

    fname = 'raw_data ' + datetime.datetime.now().strftime('%H%M%S') + '.xlsx'
    writer = pd.ExcelWriter(fname)

    if count > 0:
        dfCombined = pd.concat(dfAllWPNS)
        dfCombined.sort_values(by=['TOR'], inplace=True)
        dfCombined.to_excel(writer, sheet_name='Combined', index=False)
        for df in allWPNs:
            sheetname = df.loc[0, 'wpn']
            df.to_excel(writer, sheet_name=str(sheetname), index=False)
    dfMsnEvents.to_excel(writer, sheet_name='Timestamps', index=False)
    writer.save()
    ProgressMsnEvent = 100
    print('\r{}% done...'.format(ProgressMsnEvent), end='', flush=True)
    elapsed = timeit.default_timer() - start_time
    print('\r' + str(round(elapsed/60)) + ' minutes')
    os.startfile(fname)
    parse_pending.set()


if __name__ == '__main__':
    main()
