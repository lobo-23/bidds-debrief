import pandas as pd
import numpy as np

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
import glob, sys, datetime, os, openpyxl, threading, timeit, time, shutil
from pyqtspinner.spinner import WaitingSpinner
from utils import *
from msnparse import *
from LatLon23 import string2latlon
from pyproj import _datadir, datadir
import config
import json
import csv
import resource
from pathlib import Path

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True) #enable highdpi scaling
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True) #use highdpi icons

class External(QThread):
    countChanged = pyqtSignal(int)

    def run(self):
        config.ProgressMsnEvent = 0
        while config.ProgressMsnEvent < 100:
            time.sleep(1)
            self.countChanged.emit(config.ProgressMsnEvent)

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent) # Call the inherited classes __init__ method
        uic.loadUi('maingui.ui', self) # Load the .ui file

        self.TXTload = self.findChild(QPushButton, 'pushButton_TXTLoad') # Find the button
        self.TXTload.clicked.connect(self.TXTLoadPressed) # Remember to pass the definition/method, not the return value!

        self.progressbar = self.findChild(QProgressBar, 'progressBar')
        self.progressbar.setValue(0)

        self.benametext = self.findChild(QLineEdit, 'line_BEName')
        self.belattext = self.findChild(QLineEdit, 'line_BELat')
        self.belongtext = self.findChild(QLineEdit, 'line_BELong')

        self.gpsfile = self.findChild(QCheckBox,'cbGPS')
        self.turbo = self.findChild(QCheckBox, 'cbTurbo')
        self.csname = self.findChild(QLineEdit, 'line_CS')

        self.manualjassmmatch = self.findChild(QAction,'actionJASSM_Report_Match')
        self.manualjassmmatch.triggered.connect(self.jassmmatch)

        self.bullupdatebutton = self.findChild(QAction,'actionUpdate_Bullseyes')
        self.bullupdatebutton.triggered.connect(self.bullupdate)

        self.howtoguide = self.findChild(QAction,'actionHow_To_Guide')
        self.howtoguide.triggered.connect(self.guideopen)

        self.changelog = self.findChild(QAction,'actionChangelog')
        self.changelog.triggered.connect(self.changelogopen)

        self.BIDDS = self.findChild(QPushButton, 'pushButton_BIDDS')
        self.BIDDS.clicked.connect(self.BIDDSopen)

        self.Folder = self.findChild(QPushButton, 'pushButton_Folder')
        self.Folder.clicked.connect(self.FolderCreate)

        self.BIDDSDRD = self.findChild(QAction,'actionCopy_DRD_to_BIDDS')
        self.BIDDSDRD.triggered.connect(self.BIDDSfolderopen)

        try:
            with open('defaults.json') as f:
                config.defaults = json.load(f)
                self.benametext.setText(config.defaults['BEname'])
                self.belattext.setText(config.defaults['BElat'])
                self.belongtext.setText(config.defaults['BElon'])
                self.csname.setText(config.defaults['CS'])
                if os.path.isdir(config.defaults['defaultpath']):
                    config.outputpath = config.defaults['defaultpath']
                else:
                    config.outputpath = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')

        except:
            pass
        self.show() # Show the GUI

    def guideopen(self):
        prefixed = [filename for filename in os.listdir('.') if filename.startswith("BIDDS Debrief Card Guide") and filename.endswith("pdf")]
        try:
            os.startfile(prefixed[-1])
        except:
            QMessageBox.question(self, 'Error',
                                                  "Guide not found.",
                                                  QMessageBox.Ok)
            return
    def changelogopen(self):
        prefixed = [filename for filename in os.listdir('.') if filename.startswith("Changelog") and filename.endswith("pdf")]
        try:
            os.startfile(prefixed[-1])
        except:
            QMessageBox.question(self, 'Error',
                                                  "Changelog not found.",
                                                  QMessageBox.Ok)
            return
    def jassmmatch(self):
        config.bename = self.benametext.text()
        config.belat = self.belattext.text()
        config.belong = self.belongtext.text()
        config.csname = '' #Doesnt overwrite callsign
        if len(config.bename)>0 or len(config.belat)>0 or len(config.belong)>0:
            try:
                config.becoord = string2latlon(config.belat, config.belong, 'H% %d% %M')
            except:
                config.becoord = QMessageBox.question(self, 'Bullseye Error',
                                                    "Coordinate format not recognized.\n N/S DD MM.MMMM, E/W DDD MM.MMMM",
                                                    QMessageBox.Ok)
                print('Bullseye Lat/Long Error: Input DD MM.MMMM format.')
                return
        else:
            config.becoord = None
        self.matchpick = UiJassmMatch(self)
        self.matchpick.show()

    def bullupdate(self):
        config.bename = self.benametext.text()
        config.belat = self.belattext.text()
        config.belong = self.belongtext.text()
        if len(config.bename)>0 or len(config.belat)>0 or len(config.belong)>0:
            try:
                config.becoord = string2latlon(config.belat, config.belong, 'H% %d% %M')
            except:
                config.becoord = QMessageBox.question(self, 'Bullseye Error',
                                                    "Coordinate format not recognized.\n N/S DD MM.MMMM, E/W DDD MM.MMMM",
                                                    QMessageBox.Ok)
                print('Bullseye Lat/Long Error: Input DD MM.MMMM format.')
                return
        else:
            config.becoord = None
        selectedfile = QFileDialog.getOpenFileName(self, 'Select Debrief Card Excel File',
                                                   config.outputpath,
                                                   "Excel File (*.xlsx)")
        if len(selectedfile[0])> 0:
            debriefcard = pd.ExcelFile(selectedfile[0])
            for sheet in debriefcard.sheet_names:
                if 'Combined' in sheet:
                    wpns = pd.read_excel(debriefcard, sheet_name='Combined', index_col=None, na_filter=False)
                    wpns.astype({'TGT LAT': str, 'TGT LONG': str, 'TGT ELEV': str, 'BULL': str,'Release LAT': str, 'Release LONG': str,'Release Bull': str}).dtypes

                    wpns['TGT LAT'] = wpns['TGT LAT'].astype(str)
                    wpns['TGT LONG'] = wpns['TGT LONG'].astype(str)
                    wpns['BULL'] = wpns['TGT LAT'].astype(str)

                    wpns['Release LAT'] = wpns['Release LAT'].astype(str)
                    wpns['Release LONG'] = wpns['Release LONG'].astype(str)
                    wpns['Release Bull'] = wpns['Release Bull'].astype(str)

                    for i, row in wpns.iterrows():
                        try:
                            wpns.at[i, 'BULL'] = bullcalculate(wpns.at[i, 'TGT LAT'], wpns.at[i, 'TGT LONG'])
                        except:
                            wpns.at[i, 'BULL'] = ''
                        #try:
                        wpns.at[i, 'Release Bull'] = bullcalculate(wpns.at[i, 'Release LAT'], wpns.at[i, 'Release LONG'])
                        #except:
                        #    wpns.at[i, 'Release Bull'] = ''

                    wpns = wpns.fillna('')
                    wpns = wpns.replace('nan', '', regex=True)

                    append_df_to_excel(debriefcard, wpns, sheet_name="Combined", startrow=0,
                                       index=False)
                    os.startfile(debriefcard)


    def onCountChanged(self, value):
        self.progressbar.setValue(value)
        if value == 95:
            config.ProgressMsnEvent = 96
            config.jassmmatch = QMessageBox.question(self, 'JASSM Match',
                                     "JASSM releases were found for your mission:\n\nWould you like to match these releases to a JMPS DTC JASSM TARGET SUMMARY for JDPI Data to show properly?\n\nYou can also complete this later by selecting Tools>JASSM Report Match.",
                                     QMessageBox.Yes | QMessageBox.No)
            if config.jassmmatch == QMessageBox.Yes:
                selectedfile = QFileDialog.getOpenFileName(self, 'Open JMPS JASSM Report Excel File',
                                            config.outputpath,
                                            "Excel File (*.xlsm)")
                if len(selectedfile[0]) > 0:
                    config.jassmreport_filename = selectedfile[0]
                else:
                    config.jassmreport_filename = False
            else:
                config.jassmreport_filename = False

    def TXTLoadPressed(self):
        config.bename = self.benametext.text()
        config.belat = self.belattext.text()
        config.belong = self.belongtext.text()
        config.csname = self.csname.text()

        config.defaults['gpsfile'] = self.gpsfile.isChecked()
        config.turbocharge = not self.turbo.isChecked()



        if len(config.bename)>0 or len(config.belat)>0 or len(config.belong)>0:
            try:
                config.becoord = string2latlon(config.belat, config.belong, 'H% %d% %M')
            except:
                config.becoord = QMessageBox.question(self, 'Bullseye Error',
                                                    "Coordinate format not recognized.\n N/S DD MM.MMMM, E/W DDD MM.MMMM",
                                                    QMessageBox.Ok)
                print('Bullseye Lat/Long Error: Input DD MM.MMMM format.')
                return
        else:
            config.becoord = None

        if len(config.csname)<1:
            config.csname = QMessageBox.question(self, 'Callsign Error',
                                                  "Please enter a Callsign",
                                                  QMessageBox.Ok)
            return


        config.filename = QFileDialog.getOpenFileName(self, 'Open TXT file',
                                            config.outputpath, "Text File (*.txt)")
        #config.filename = QFileDialog.getOpenFileName(self, 'Open TXT file',
         #                                   os.path.join(os.getcwd(),'textfiles'), "Text File (*.txt)")


        if len(config.filename[0]) > 0:
            config.outputpath = os.path.dirname(config.filename[0])
            try:
                with open('defaults.json', 'w') as f:
                    config.defaults['BEname'] = config.bename
                    config.defaults['BElat'] = config.belat
                    config.defaults['BElon'] = config.belong
                    config.defaults['CS'] = ''.join([i for i in config.csname if not i.isdigit()])
                    config.defaults['defaultpath'] = config.outputpath
                    json.dump(config.defaults, f)
            except:
                pass
            self.msnpicker = UiMsnPicker(self)
            self.msnpicker.show()

            self.calc = External()
            self.calc.countChanged.connect(self.onCountChanged)
            self.calc.start()


    def BIDDSopen(self):
        try:
            os.startfile(config.defaults['bidds'])
        except:
            QMessageBox.question(self, 'File Error',
                                 "Unable to find BIDDS Program located at " + str(config.defaults['bidds']) ,
                                 QMessageBox.Ok)

    def FolderCreate(self):
        config.csname = self.csname.text()
        basefolder = config.defaults['savepath']
        foldername = datetime.datetime.now().strftime("%Y%m%d") + ' ' + config.csname
        try:
            if not os.path.isdir(basefolder):
                basefolder = 'Desktop'
            if basefolder == 'Desktop':
                basefolder = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')

            basefolder = os.path.join(basefolder, config.defaults['savefolder'])
            sortiefolder = os.path.join(basefolder, foldername)
            Path(sortiefolder).mkdir(parents=True, exist_ok=True)

            if os.path.isdir(sortiefolder):
                os.startfile(sortiefolder)
            config.outputpath = sortiefolder
        except:
            QMessageBox.question(self, 'Folder Error',
                                 "Unable to create folder \nBase Folder: " + str(basefolder)+"\nSortie Folder: "+ str(sortiefolder),
                                 QMessageBox.Ok)

    def BIDDSfolderopen(self):
        try:
            biddspath, tail = os.path.split(config.defaults['bidds'])
            if os.path.isdir(biddspath):
                os.startfile(biddspath)
        except:
            QMessageBox.question(self, 'File Error',
                                 "Unable to find BIDDS Program located at " + str(config.defaults['bidds']) ,
                                 QMessageBox.Ok)

"""
            CopyConfirm = QMessageBox.question(self, 'Copy DRD Files',
                                     "Would you like to update the BIDDS folder DRD files with new ones?" ,
                                     QMessageBox.Yes|QMessageBox.No)
            if CopyConfirm ==QMessageBox.Yes:
                selectedFolder = QFileDialog.getExistingDirectory(self, 'Select Folder with new DRD files',
                                                           config.outputpath)
                count =0
                if len(selectedFolder[0]) > 0:
                    for basename in os.listdir(selectedFolder):
                        if basename.endswith('.drd'):
                            pathname = os.path.join(selectedFolder, basename)
                            destfile = os.path.join(biddspath, basename)
                            if os.path.isfile(pathname):
                                if os.path.exists(destfile):
                                    try:
                                        os.remove(destfile)
                                    except PermissionError as exc:
                                        os.chmod(destfile, 0o777)
                                        os.remove(destfile)
                                shutil.copy2(pathname, biddspath)
                                count += 1
                QMessageBox.question(self, 'DRD Copy',
                                     f"DRD Files copied: {count}.",
                                     QMessageBox.Ok)
        else:
            QMessageBox.question(self, 'File Error',
                                 "Unable to find BIDDS Program located at " + str(config.defaults['bidds']) ,
                                 QMessageBox.Ok)
"""
class Worker(QObject):
    """
    Must derive from QObject in order to emit signals, connect slots to other signals, and operate in a QThread.
    """
    sig_done = pyqtSignal(int)  # worker id: emitted at end of work()

    def __init__(self, id: int):
        super().__init__()
        self.__id = id
        self.__abort = False

    @pyqtSlot()
    def work(self):

        thread_name = QThread.currentThread().objectName()
        thread_id = int(QThread.currentThreadId())  # cast to int() is necessary

        msnsplit()

        self.sig_done.emit(self.__id)

    def abort(self):
        self.__abort = True
class UiJassmMatch(QDialog):
    def __init__(self,parent=None):
        super(UiJassmMatch, self).__init__(parent) # Call the inherited classes __init__ method
        uic.loadUi('jassmmatch.ui', self) # Load the .ui file

        self.debriefload = self.findChild(QPushButton, 'loaddebrief') # Find the button
        self.debriefload.clicked.connect(self.debriefpicker)
        self.sumload = self.findChild(QPushButton, 'loadjassmreport')
        self.sumload.clicked.connect(self.jassmreportpicker)
        self.match = self.findChild(QPushButton, 'match') # Find the button
        self.match.clicked.connect(self.match_releases) # Remember to pass the definition/method, not the return value!
        config.debriefcard_filename = ''
        config.jassmreport_filename = ''
        self.show()  # Show the GUI

    def match_releases(self):
        self.match.setText('Matching...')
        self.repaint()
        newfilename = config.debriefcard_filename.replace('.xlsx', ' (matched).xlsx')
        try:
            shutil.copy(config.debriefcard_filename, newfilename)
        except:
            QMessageBox.question(self, 'File Error',
                                 "File copy error, please close " + str(newfilename) + ' and try again.',
                                 QMessageBox.Ok)
            self.match.setText('Match')
            self.repaint()
            return
        config.debriefcard_filename = newfilename
        updatecombined = jassm_report_match(config.debriefcard_filename, config.jassmreport_filename)
        if not updatecombined.empty:
            updatecombined = updatecombined.fillna('')
            updatecombined = updatecombined.replace('nan', '', regex=True)
            append_df_to_excel(config.debriefcard_filename, updatecombined, sheet_name="Combined", startrow=0, index=False)
            updatefillins(config.debriefcard_filename)
            os.startfile(config.debriefcard_filename)
        self.match.setText('Match')
        self.repaint()
    def debriefpicker(self):
        selectedfile = QFileDialog.getOpenFileName(self, 'Open Debrief Card to Pair',
                                                   config.outputpath,
                                                   "Excel File (*.xlsx)")
        if len(selectedfile[0]) > 0:
            config.debriefcard_filename = selectedfile[0]
            if len(config.debriefcard_filename) > 0 and len(config.jassmreport_filename) > 0:
                self.match.setEnabled(True)
    def jassmreportpicker(self):
        selectedfile = QFileDialog.getOpenFileName(self, 'Open JMPS JASSM Report Excel File',
                                                   config.outputpath,
                                                   "Excel File (*.xlsm)")
        if len(selectedfile[0]) > 0:
            config.jassmreport_filename = selectedfile[0]
            if len(config.debriefcard_filename) > 0 and len(config.jassmreport_filename) > 0:
                self.match.setEnabled(True)
class UiMsnPicker(QDialog):
    def __init__(self,parent=None):
        super(UiMsnPicker, self).__init__(parent) # Call the inherited classes __init__ method
        uic.loadUi('fdrsplit.ui', self) # Load the .ui file

        self.cbFlights = self.findChild(QComboBox, 'cbFlights') # Find the button

        self.SelectFlight = self.findChild(QPushButton, 'pushButton') # Find the button
        self.SelectFlight.clicked.connect(self.SelectFlightPressed) # Remember to pass the definition/method, not the return value!

        self.FlightCount = self.findChild(QLabel, 'labelFlightCount')
        self.spinner = WaitingSpinner(self, True, True, Qt.ApplicationModal)
        self.spinner.start()

        self.__threads = None
        self.start_threads()
        self.show()  # Show the GUI


    def SelectFlightPressed(self):
        #self.FlightCount.setText(print(self.cbFlights.currentIndex()))
        idx = self.cbFlights.currentIndex()

        i = int(config.ranges[idx][0])
        j = int(config.ranges[idx][1])
        config.msnData = config.msnData[i:j]
        if config.turbocharge == True:
            larmald = [m.start() for m in re.finditer('Change of IR IZ LAR', config.msnData)]
            larjassm = [m.start() for m in re.finditer('Change of In-Range/In-Zone Status', config.msnData)]
            rel = [m.start() for m in re.finditer('Weapon Scoring', config.msnData)]

            config.larparse = len(larmald + larjassm) >0
            releases = rel + larmald + larjassm
            releases.sort()

            records = [m.start() for m in re.finditer('Mission Event', config.msnData)]

            print('Partial Sortie Search')
            try:
                if min(releases)> 30000:
                    K = min(releases)-30000
                else:
                    K = 1
                start = records[min(range(len(records)), key = lambda i: abs(records[i]-K))]
                K = max(releases)+30000
                stop = records[min(range(len(records)), key=lambda i: abs(records[i] - K))]
                config.msnData = config.msnData[start:stop]
            except:
                print('Partial Sortie Search Error, searching full sortie...')
        else:
            larmald = [m.start() for m in re.finditer('Change of IR IZ LAR', config.msnData)]
            larjassm = [m.start() for m in re.finditer('Change of In-Range/In-Zone Status', config.msnData)]

            config.larparse = len(larmald + larjassm) >0

        config.parse_pending = threading.Event()

        config.ProgressMsnEvent = 2.3

        threadParse = threading.Thread(target=Parse)
        threadParse.start()

        self.close()

    def spinner_start(self):
        self.spinner.start()

    def spinner_stop(self):
        self.spinner.stop()

    def start_threads(self):
        self.SelectFlight.setDisabled(True)

        self.__threads = []
        for idx in range(1):
            worker = Worker(idx)
            thread = QThread()
            thread.setObjectName('thread_' + str(idx))
            self.__threads.append((thread, worker))  # need to store worker too otherwise will be gc'd
            worker.moveToThread(thread)

        worker.sig_done.connect(self.on_worker_done)

        thread.started.connect(worker.work)
        thread.start()  # this will emit 'started' and start thread's event loop

    @pyqtSlot(int)
    def on_worker_done(self, worker_id):
        for thread, worker in self.__threads:  # note nice unpacking by Python, avoids indexing
            thread.quit()  # this will quit **as soon as thread event loop unblocks**
            thread.wait()  # <- so you need to wait for it to *actually* quit

        if config.msndates:
            self.spinner_stop()

            self.FlightCount.setText(str(len(config.msndates)))

            self.cbFlights.clear()
            for i in config.msndates:
                self.cbFlights.addItem(i)
            self.SelectFlight.setDisabled(False)
        else:
            self.close()


def Parse():

    start_time = timeit.default_timer()

    config.events_available = threading.Event()
    config.releases_available = threading.Event()
    config.lars_available = threading.Event()

    config.ProgressMsnEvent = 0

    threadEvents = threading.Thread(target=parsemsnevn)
    threadEvents.start()
    threadReleases = threading.Thread(target=parserelease)
    threadReleases.start()
    if config.larparse:
        threadLars = threading.Thread(target=parselar())
        threadLars.start()


    allWPNs = []
    dfAllWPNS = []
    allLARs = []

    reader = csv.reader(open('wpncodes.csv', 'r'))
    config.wpncodes = {}
    for row in reader:
        k, v = row
        config.wpncodes[k] = v

    while not config.events_available.wait(timeout=1) :
        print('\r{}% done...'.format(config.ProgressMsnEvent), end='', flush=True)

    config.ProgressMsnEvent = 80

    if config.larparse:
        config.lars_available.wait()

    config.ProgressMsnEvent = 81

    print('\r{}% done...'.format(config.ProgressMsnEvent), end='', flush=True)

    config.releases_available.wait()

    config.dfMsnEvents['Time (UTC)'] = pd.to_datetime(config.dfMsnEvents['Date'] + ' ' + config.dfMsnEvents['Time (UTC)'])
    #dfMsnEvents.to_csv('msnevents.csv')
    config.dfMsnEvents.sort_values(by=['Time (UTC)'], inplace=True)
    filter_mask = config.dfMsnEvents['Time (UTC)'] > pd.Timestamp(2000, 1, 2)
    config.dfMsnEvents = config.dfMsnEvents[filter_mask]
    config.dfMsnEvents.drop_duplicates(subset="Time (UTC)", keep=False, inplace=True)

    if len(config.jdam) > 0:
        dfJDAM = pd.DataFrame(config.jdam)
        #dfJDAM.to_csv('jdam.csv')
        msnevnpair(dfJDAM, config.dfMsnEvents)
        allWPNs.append(dfJDAM)
        dfJDAMfiltered = dfJDAM.filter(
            ['Record Number', 'Tail', 'wpn', 'Dest', 'TOT', 'TOR', 'BULL', 'TOF', 'WPN Type', 'TGT Name', 'TGT LAT',
             'TGT LONG', 'TGT ELEV', 'PrimeNav', 'XHair', 'PrimeNavAiding', 'Buffers','FOM', 'ALT', 'GTRK', 'IAS',
             'MHDG', 'TAS', 'LS', 'GS', 'LARstatus','Delay','FCI','Mach','LAT','LONG','BULLrel','Wind'], axis=1)
        dfAllWPNS.append(dfJDAMfiltered)
    if len(config.gwd) > 0:
        dfGWD = pd.DataFrame(config.gwd)
        #dfGWD.to_csv('gwd.csv')
        msnevnpair(dfGWD, config.dfMsnEvents)
        dfGWD.LARstatus = dfGWD.FCI
        allWPNs.append(dfGWD)
        dfGWDfiltered = dfGWD.filter(
            ['Record Number', 'Tail', 'wpn', 'Dest', 'TOT', 'TOR', 'BULL', 'TOF', 'WPN Type', 'TGT Name', 'TGT LAT',
             'TGT LONG', 'TGT ELEV', 'PrimeNav', 'XHair', 'PrimeNavAiding', 'Buffers','FOM', 'ALT', 'GTRK', 'IAS',
             'MHDG', 'TAS', 'LS', 'GS', 'LARstatus','Delay','FCI','Mach','LAT','LONG','BULLrel','Wind'], axis=1)
        dfAllWPNS.append(dfGWDfiltered)
    if len(config.wcmd) > 0:
        dfWCMD = pd.DataFrame(config.wcmd)
        #dfWCMD.to_csv('wcmd.csv')
        msnevnpair(dfWCMD, config.dfMsnEvents)
        allWPNs.append(dfWCMD)
        dfWCMDfiltered = dfWCMD.filter(
            ['Record Number', 'Tail', 'wpn', 'Dest', 'TOT', 'TOR', 'BULL', 'TOF', 'WPN Type', 'TGT Name', 'TGT LAT',
             'TGT LONG', 'TGT ELEV', 'PrimeNav', 'XHair', 'PrimeNavAiding', 'Buffers','FOM', 'ALT', 'GTRK', 'IAS',
             'MHDG', 'TAS', 'LS', 'GS', 'LARstatus','Delay','FCI','Mach','LAT','LONG','BULLrel','Wind'], axis=1)
        dfAllWPNS.append(dfWCMDfiltered)
    if len(config.jassm) > 0:
        dfJASSM = pd.DataFrame(config.jassm)
        #dfJASSM.to_csv('jassm.csv')
        msnevnpair(dfJASSM, config.dfMsnEvents)
        if len(config.LARjassm) > 0:
            dfLARjassm = pd.DataFrame(config.LARjassm)
            allLARs.append(dfLARjassm)
            try:
                larreleasepair(dfLARjassm,dfJASSM)
            except:
                pass
        allWPNs.append(dfJASSM)
        dfJASSMfiltered = dfJASSM.filter(
            ['Record Number', 'Tail', 'wpn', 'Dest', 'TOT', 'TOR', 'BULL', 'TOF', 'WPN Type', 'TGT Name', 'TGT LAT',
             'TGT LONG', 'TGT ELEV', 'PrimeNav', 'XHair', 'PrimeNavAiding', 'Buffers','FOM', 'ALT', 'GTRK', 'IAS',
             'MHDG', 'TAS', 'LS', 'GS', 'LARstatus','Delay','FCI','Mach','LAT','LONG','BULLrel','Wind'], axis=1)
        dfAllWPNS.append(dfJASSMfiltered)
    if len(config.mald) > 0:
        dfMALD = pd.DataFrame(config.mald)
        #dfMALD.to_csv('mald.csv')
        msnevnpair(dfMALD, config.dfMsnEvents)
        if hasattr(config, 'LARmald'):
            if len(config.LARmald) > 0:
                dfLARmald = pd.DataFrame(config.LARmald)
                allLARs.append(dfLARmald)
                try:
                    larreleasepair(dfLARmald,dfMALD)
                except:
                    pass
        allWPNs.append(dfMALD)
        dfMALDfiltered = dfMALD.filter(
            ['Record Number', 'Tail', 'wpn', 'Dest', 'TOT', 'TOR', 'BULL', 'TOF', 'WPN Type', 'TGT Name', 'TGT LAT',
             'TGT LONG', 'TGT ELEV', 'PrimeNav', 'XHair', 'PrimeNavAiding', 'Buffers','FOM', 'ALT', 'GTRK', 'IAS',
             'MHDG', 'TAS', 'LS', 'GS', 'LARstatus','Delay','FCI','Mach','LAT','LONG','BULLrel','Wind'], axis=1)
        dfAllWPNS.append(dfMALDfiltered)


    config.ProgressMsnEvent = 90
    print('\r{}% done...'.format(config.ProgressMsnEvent), end='', flush=True)

    newfilename = config.csname + ' Debrief Card ' + datetime.datetime.now().strftime('%H%M%S') + '.xlsx'
    newfilepath = os.path.join(config.outputpath, newfilename)
    shutil.copy('Debrief Sheet Template.xlsx', newfilepath)
    updatefillins(newfilepath)

    if config.count > 0:
        dfCombined = pd.concat(dfAllWPNS)
        dfCombined.sort_values(by=['TOR'], inplace=True)
        append_df_to_excel(newfilepath, dfCombined, sheet_name='Combined', startrow=1, header=False, index=False)
        for df in allWPNs:
            sheetname = df.loc[0, 'wpn']
            append_df_to_excel(newfilepath,df,sheet_name=sheetname,startrow=0, index=False)
    append_df_to_excel(newfilepath, config.dfMsnEvents, sheet_name="Timestamps", startrow=0, index=False)
    for df in allLARs:
        sheetname = df.loc[0,'LAR']
        append_df_to_excel(newfilepath, df, sheet_name=sheetname, startrow=0, index=False)

    if len(config.jassm) > 0:
        config.ProgressMsnEvent = 95
        config.jassmreport_filename = None
        while config.jassmreport_filename == None:
            time.sleep(1)
        config.debriefcard_filename = newfilepath
        if config.jassmmatch == QMessageBox.Yes and config.jassmreport_filename != False:
            updatecombined = jassm_report_match(config.debriefcard_filename,config.jassmreport_filename)
            if not updatecombined.empty:
                updatecombined = updatecombined.fillna('')
                updatecombined = updatecombined.replace('nan', '', regex=True)
                append_df_to_excel(newfilepath, updatecombined, sheet_name="Combined", startrow=0, index=False)

    config.ProgressMsnEvent = 99
    if config.defaults['gpsfile']:
        try:
            to_gpsnmea(config.dfMsnEvents,newfilepath)
        except:
            pass
    config.ProgressMsnEvent = 100
    print('\r{}% done...'.format(config.ProgressMsnEvent), end='', flush=True)
    elapsed = timeit.default_timer() - start_time
    print('\r' + str(round(elapsed/60)) + ' minutes')
    os.startfile(newfilepath)
    config.parse_pending.set()

def main():
    app = QApplication(sys.argv)  # Create an instance of QApplication
    window = MainWindow()  # Create an instance of our class
    app.exec_()  # Start the application

if __name__ == '__main__':
    main()
