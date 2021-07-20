
import pandas as pd
from openpyxl import load_workbook
import numpy as np
import config
import pynmea2
import subprocess
import os
import xlrd
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from utils import *

def jassm_report_match(debrief_filename='none', jassm_report='jrep.xlsm'):

    if debrief_filename == 'none':
        debrief_filename = QFileDialog.getOpenFileName(self, 'Open Debrief Card Excel File',
                                    os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop'),
                                    "Excel File (*.xlsx)")
    if jassm_report == 'none':
        jassm_report = QFileDialog.getOpenFileName(self, 'Open JMPS JASSM Report Excel File',
                                    os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop'),
                                    "Excel File (*.xlsx)")
    jreport = pd.ExcelFile(jassm_report)
    wpngroups = []

    for sheet in jreport.sheet_names:
        if 'JASSMGRP' in sheet:
            print(sheet)
            df = jreport.parse(sheet, skiprows=5, index_col=None)
            df['wpngroup'] = str(sheet) + " " + 'MSN'+ df['Msn'].astype(str)
            wpngroups.append(df)
    wpns = pd.read_excel(debrief_filename, sheet_name='Combined',index_col=None,na_filter= False)
    wpns.astype({'TGT LAT':str,'TGT LONG':str,'TGT ELEV':str,'BULL':str}).dtypes
    wpns['TGT LAT'] = wpns['TGT LAT'].astype(str)
    wpns['TGT LONG'] = wpns['TGT LAT'].astype(str)
    wpns['TGT ELEV'] = wpns['TGT LAT'].astype(str)
    wpns['BULL'] = wpns['TGT LAT'].astype(str)

    for i, row in wpns.iterrows():
        for group in wpngroups:
            for j, rows in group.iterrows():
                if wpns.at[i,'TGT Name'] == group.at[j,'wpngroup']:
                    wpns.at[i, 'TGT Name'] = group.at[j,'Mission Name']
                    wpns.at[i, 'TGT LAT'] = group.at[j, 'Tgt Latitude']
                    wpns.at[i, 'TGT LONG'] = group.at[j,'Tgt Longitude']
                    wpns.at[i, 'TGT ELEV'] = str(group.at[j,'Tgt Elev (HAE)']) + "' HAE"
                    try:
                        wpns.at[i, 'BULL'] = bullcalculate(wpns.at[i, 'TGT LAT'], wpns.at[i, 'TGT LONG'])
                    except:
                        wpns.at[i, 'BULL']  = ''
    wpns = wpns.fillna('')
    wpns = wpns.replace('nan', '', regex=True)
    return wpns


QMessageBox.question(self.iface.mainWindow(), 'JASSM Match',
                             "JASSM releases were found for your mission.\n Would you like to match releases to a JMPS JASSM Report Summary to fill-in TOF, TOT, and Target Data?\n\nYou can also complete this later by selecting Tools>JASSM Report Match.",
                             QMessageBox.Yes | QMessageBox.No)

updatecombined = jassm_report_match()
#append_df_to_excel('input.xlsx', updatecombined, sheet_name="Combined", startrow=0, index=False)