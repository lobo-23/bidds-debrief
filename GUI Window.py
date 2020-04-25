from PyQt5 import QtWidgets, uic
import sys, os, shutil

class Ui(QtWidgets.QDialog):
    def __init__(self):
        super(Ui, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('GUI.ui', self) # Load the .ui file

        self.FDRload = self.findChild(QtWidgets.QPushButton, 'pushButton_FDRLoad') # Find the button
        self.FDRload.clicked.connect(self.FDRLoadPressed) # Remember to pass the definition/method, not the return value!

        self.TXTload = self.findChild(QtWidgets.QPushButton, 'pushButton_TXTLoad') # Find the button
        self.TXTload.clicked.connect(self.TXTLoadPressed) # Remember to pass the definition/method, not the return value!

        self.BIDDSOpen = self.findChild(QtWidgets.QPushButton, 'pushButton_BIDDSOpen') # Find the button
        self.BIDDSOpen.clicked.connect(self.BIDDSLoadPressed) # Remember to pass the definition/method, not the return value!
        self.show() # Show the GUI

    def FDRLoadPressed(self):
        # This is executed when the button is pressed
        print('FDRLoadPressed')

    def TXTLoadPressed(self):
        # This is executed when the button is pressed
        print('TXTLoadPressed')
    def BIDDSLoadPressed(self):
        # This is executed when the button is pressed
        print('BIDDSLoadPressed')
        copyDirectory(r'.\Files\BIDDS', "C:\BIDDS")
        os.startfile('C:\BIDDS\BIDDS.exe')

def copyDirectory(src, dest):
    try:
        shutil.copytree(src, dest)
    # Directories are the same
    except shutil.Error as e:
        print('Directory not copied. Error: %s' % e)
    # Any error saying that the directory doesn't exist
    except OSError as e:
        print('Directory not copied. Error: %s' % e)


app = QtWidgets.QApplication(sys.argv) # Create an instance of QtWidgets.QApplication
window = Ui() # Create an instance of our class
app.exec_() # Start the application