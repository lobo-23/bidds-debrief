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

class External(QThread):
    countChanged = pyqtSignal(int)

    def run(self):
        config.ProgressMsnEvent = 0
        while config.ProgressMsnEvent < 100:
            time.sleep(1)
            self.countChanged.emit(config.ProgressMsnEvent)
class MainWindow(QDialog):
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

        self.show() # Show the GUI

    def onCountChanged(self, value):
        self.progressbar.setValue(value)

    def TXTLoadPressed(self):
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


        config.filename = QFileDialog.getOpenFileName(self, 'Open TXT file',
                                            os.path.join(os.getcwd(),'textfiles'), "Text File (*.txt)")


        if len(config.filename[0]) > 0:
            self.msnpicker = UiMsnPicker(self)
            self.msnpicker.show()

            self.calc = External()
            self.calc.countChanged.connect(self.onCountChanged)
            self.calc.start()


    def BIDDSLoadPressed(self):
        # This is executed when the button is pressed
        print('BIDDSLoadPressed')
        copyDirectory(r'.\Files\BIDDS', "C:\BIDDS")
        os.startfile('C:\BIDDS\BIDDS.exe')

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
        print('Select Flight Pressed')
        self.FlightCount.setText(print(self.cbFlights.currentIndex()))
        idx = self.cbFlights.currentIndex()


        i = int(config.ranges[idx][0])
        j = int(config.ranges[idx][1])
        config.msnData = config.msnData[i:j]
        print(i)
        print(j)


        config.parse_pending = threading.Event()


        config.ProgressMsnEvent = 5

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

    config.ProgressMsnEvent = 0

    threadEvents = threading.Thread(target=parsemsnevn)
    threadEvents.start()
    threadReleases = threading.Thread(target=parserelease)
    threadReleases.start()

    allWPNs = []
    dfAllWPNS = []

    while not config.events_available.wait(timeout=1):
        print('\r{}% done...'.format(config.ProgressMsnEvent), end='', flush=True)
    config.ProgressMsnEvent = 80
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
             'MHDG', 'TAS', 'LS', 'GS', 'LARstatus','Delay','FCI'], axis=1)
        dfAllWPNS.append(dfJDAMfiltered)
    if len(config.gwd) > 0:
        dfGWD = pd.DataFrame(config.gwd)
        #dfGWD.to_csv('gwd.csv')
        msnevnpair(dfGWD, config.dfMsnEvents)
        allWPNs.append(dfGWD)
        dfGWDfiltered = dfGWD.filter(
            ['Record Number', 'Tail', 'wpn', 'Dest', 'TOT', 'TOR', 'BULL', 'TOF', 'WPN Type', 'TGT Name', 'TGT LAT',
             'TGT LONG', 'TGT ELEV', 'PrimeNav', 'XHair', 'PrimeNavAiding', 'Buffers','FOM', 'ALT', 'GTRK', 'IAS',
             'MHDG', 'TAS', 'LS', 'GS', 'LARstatus','Delay','FCI'], axis=1)
        dfAllWPNS.append(dfGWDfiltered)
    if len(config.wcmd) > 0:
        dfWCMD = pd.DataFrame(config.wcmd)
        #dfWCMD.to_csv('wcmd.csv')
        msnevnpair(dfWCMD, config.dfMsnEvents)
        allWPNs.append(dfWCMD)
        dfWCMDfiltered = dfWCMD.filter(
            ['Record Number', 'Tail', 'wpn', 'Dest', 'TOT', 'TOR', 'BULL', 'TOF', 'WPN Type', 'TGT Name', 'TGT LAT',
             'TGT LONG', 'TGT ELEV', 'PrimeNav', 'XHair', 'PrimeNavAiding', 'Buffers','FOM', 'ALT', 'GTRK', 'IAS',
             'MHDG', 'TAS', 'LS', 'GS', 'LARstatus','Delay','FCI'], axis=1)
        dfAllWPNS.append(dfWCMDfiltered)
    if len(config.jassm) > 0:
        dfJASSM = pd.DataFrame(config.jassm)
        #dfJASSM.to_csv('jassm.csv')
        msnevnpair(dfJASSM, config.dfMsnEvents)
        allWPNs.append(dfJASSM)
        dfJASSMfiltered = dfJASSM.filter(
            ['Record Number', 'Tail', 'wpn', 'Dest', 'TOT', 'TOR', 'BULL', 'TOF', 'WPN Type', 'TGT Name', 'TGT LAT',
             'TGT LONG', 'TGT ELEV', 'PrimeNav', 'XHair', 'PrimeNavAiding', 'Buffers','FOM', 'ALT', 'GTRK', 'IAS',
             'MHDG', 'TAS', 'LS', 'GS', 'LARstatus','Delay','FCI'], axis=1)
        dfAllWPNS.append(dfJASSMfiltered)
    if len(config.mald) > 0:
        dfMALD = pd.DataFrame(config.mald)
        #dfMALD.to_csv('mald.csv')
        msnevnpair(dfMALD, config.dfMsnEvents)
        allWPNs.append(dfMALD)
        dfMALDfiltered = dfMALD.filter(
            ['Record Number', 'Tail', 'wpn', 'Dest', 'TOT', 'TOR', 'BULL', 'TOF', 'WPN Type', 'TGT Name', 'TGT LAT',
             'TGT LONG', 'TGT ELEV', 'PrimeNav', 'XHair', 'PrimeNavAiding', 'Buffers','FOM', 'ALT', 'GTRK', 'IAS',
             'MHDG', 'TAS', 'LS', 'GS', 'LARstatus','Delay','FCI'], axis=1)
        dfAllWPNS.append(dfMALDfiltered)

    config.ProgressMsnEvent = 90
    print('\r{}% done...'.format(config.ProgressMsnEvent), end='', flush=True)

    newfilename = 'Debrief Sheet ' + datetime.datetime.now().strftime('%H%M%S') + '.xlsx'
    newfilepath = os.path.join('output', newfilename)
    shutil.copy('Debrief Sheet Template v3.xlsx', newfilepath)
    updatefillins(newfilepath)

    if config.count > 0:
        dfCombined = pd.concat(dfAllWPNS)
        dfCombined.sort_values(by=['TOR'], inplace=True)
        append_df_to_excel(newfilepath, dfCombined, sheet_name='Combined', startrow=1, header=False, index=False)
        for df in allWPNs:
            sheetname = df.loc[0, 'wpn']
            append_df_to_excel(newfilepath,df,sheet_name=sheetname,startrow=0, index=False)
    append_df_to_excel(newfilepath, config.dfMsnEvents, sheet_name="Timestamps", startrow=0, index=False)
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
