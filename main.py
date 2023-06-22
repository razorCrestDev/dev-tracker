# Dev Tracker app 
import sys
from datetime import datetime
import random
from PyQt6.QtCore import Qt, QTimer, QTime
from PyQt6.QtGui import QIcon
from PyQt6.QtSql import (
    QSqlDatabase,
    QSqlQuery,
)
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow, # might need to switch this to a QDialog 
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget
)

__version__ = '0.0.0'

TICKET_WINDOW_SIZE = 480 
TICKET_DISPLAY_SIZE = int(TICKET_WINDOW_SIZE / 2)
TABLE_NAME = 'devtracker'
DB_NAME = 'devtracker.sqlite'

class DevTrackerDatabase:

    def __init__(self, _driver, _db_name, _port=0, _user="", _password=""):
        self.driver = _driver
        self.db_name = _db_name  
        self.port = _port
        self.user = _user
        self.password = _password
        # create the connection
        self.connection = QSqlDatabase.addDatabase(self.driver)
        self.connection.setDatabaseName(self.db_name)
        
        if not self.connection.open():
            self._showErrorMessage()
        else:
            self._checkForTrackerTable()

    def open(self):
        if not self.connection.open():
            self._showErrorMessage()
        return self.connection

    def close(self):
        if not self.connection.close(): 
            self._showErrorMessage()
        return self.connection
    
    # Basic connection error handling
    def _showErrorMessage(self):
        QMessageBox.critical(
            None, 
            "Error",
            f"Error: {self.connection.lastError().text()}",
            QMessageBox.StandardButton.Ok
            )
        
    # This will get fired every time the class is intantiated
    # Table script has IF NOT EXISTS clause to safe guard against
    # object already exists error. 
    def _createDevTrackerTable(self):
        createTableQuery = QSqlQuery()
        with open('db.sql', 'r') as createTableScript: 
            sql = createTableScript.read()
            
        return createTableQuery.exec(sql)

    def _checkForTrackerTable(self):
        if TABLE_NAME not in self.connection.tables():
            if not self._createDevTrackerTable():
                self._showErrorMessage()
        

class DevTrackerMainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dev Tracker")
        self.setWindowIcon(QIcon('Images/time-clock.svg')) 
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        self._createButtonWidgets()
        centralWidget.setLayout(self._createLayout()) 
        self.activeWindows = []

    def _getLayout(self): 
        return QVBoxLayout()
    
    def _createButtonWidgets(self):
        buttons = [ 
            "Start New Ticket",
            "Setup", 
            "History", 
        ]
        self.button_list = [QPushButton(text=button) for button in buttons]

    def _createLayout(self):
        Mainlayout = self._getLayout()
        subLayout1 = QHBoxLayout()
        subLayout2 = QHBoxLayout()
      
        for button in self.button_list:
            subLayout2.addWidget(button)
        
        self.currentSprintLabel = QLabel(text='<h2>Current Sprint</h2>')
        self.currentSprintDisplay = QLineEdit()
        self.currentSprintDisplay.setMinimumWidth(TICKET_DISPLAY_SIZE)

        subLayout1.addWidget(self.currentSprintLabel)
        subLayout1.addWidget(self.currentSprintDisplay)

        Mainlayout.addLayout(subLayout1)
        Mainlayout.addLayout(subLayout2)

        return Mainlayout
    
    def _getSprintValue(self):
        return self.currentSprintDisplay.text()
    
    def startNewTicket(self):
        newTicket = DevTrackerTicket(self._getSprintValue())
        self.activeWindows.append(newTicket)
        # TODO: revist styling later
        # self.activeWindows[-1].setStyleSheet(f'background-color:{random.choice(self.activeWindows[-1].colorScheme)}')
        self.activeWindows[-1].show()
        TicketController(view=self.activeWindows[-1])

        
class DevTrackerTicket(QWidget):

    def __init__(self, _sprint):
        super().__init__()
        self.currentSprint = _sprint
        self.setWindowTitle(f'Work In Progress: {self.currentSprint}')
        self.setWindowIcon(QIcon('Images/clipboard-list.svg')) 
        self.setMinimumSize(TICKET_WINDOW_SIZE, int(TICKET_WINDOW_SIZE / 2))
        # TODO: create themes for customization
        self.colorScheme = ['#ff006e', '#FFBE0B', '#FB5607', '#8338EC', '#3A86FF'] 
        self.mainLayout = QVBoxLayout()
        self.db_connection = self._createConnection()
        self.connectionOpen = self.db_connection.isOpen()

        self._createTime()
        self._createTimer()
        self._setWidgets()
       
        self.setLayout(self.mainLayout)
        self.buttonMap = {}

    def _setWidgets(self):
        # sub layouts
        ticketLayout = QHBoxLayout()
        subLayout = QHBoxLayout()
        labelLayout = QHBoxLayout()
        displayLayout = QVBoxLayout()
        buttonLayout = QHBoxLayout()

        # widgets
        self.ticketNumber = QLabel(text="<h2>Ticket</h2>")
        self.startTimeLabel = QLabel(text='<h2>Start Time</h2>')
        self.currentTimeLabel = QLabel(f'<h2>{self.time.toString("hh:mm:ss")}</h2>', self)
        
        self.ticketDisplay = QLineEdit()
        self.ticketDisplay.setMinimumWidth(TICKET_DISPLAY_SIZE)

        self.notesLabel = QLabel(text='Notes')
        self.notesField = QTextEdit()

        self.startWork = QPushButton(text='Start')
        self.resumeWork = QPushButton(text='Resume')
        self.endWork = QPushButton(text='Pause')
        self.saveTimer = QPushButton(text='Save')
        
        # Fahhhhk there's a better way...
        labelLayout.addWidget(self.startTimeLabel)   
        labelLayout.addWidget(self.currentTimeLabel)     
        
        buttonLayout.addWidget(self.startWork)
        buttonLayout.addWidget(self.endWork)
        buttonLayout.addWidget(self.resumeWork)
        buttonLayout.addWidget(self.saveTimer)

        subLayout.addLayout(labelLayout)
        subLayout.addLayout(displayLayout)

        ticketLayout.addWidget(self.ticketNumber)
        ticketLayout.addWidget(self.ticketDisplay)
    
        # add sub layouts to main layout
        self.mainLayout.addLayout(ticketLayout)
        self.mainLayout.addLayout(subLayout)
        self.mainLayout.addLayout(buttonLayout)
        self.mainLayout.addWidget(self.notesLabel)
        self.mainLayout.addWidget(self.notesField)
        
    def _createTimer(self):
        self.timer = QTimer()
        # we're going ot connect the timer to the timer event in our 
        # ticket scontroller

    def _createTime(self):
        self.time = QTime(0, 0, 0)

    def _createConnection(self):
        # create a connection with a unique id
        connectionName = f"con{random.randint(0, 9999)}"
        connection = QSqlDatabase.addDatabase('QSQLITE', connectionName=connectionName)
        connection.setDatabaseName(DB_NAME)
        if not connection.open(): 
            QMessageBox.critical(
                None, 
                "App Name - Error!",
                f"Database Error {connection.lastError().databaseText()}",
            )
            sys.exit(1)
        else:
            return connection
    
    def _prepareSaveQuery(self):
        saveQuery = QSqlQuery()
        saveQuery.prepare("""
            INSERT INTO devtracker (
                SprintValue, 
                TicketNumber, 
                TimeWorked, 
                TicketDetails
                ) VALUES (?, ?, ?, ?)
            """)
        return saveQuery

    def _closeConnection(self):
        self.db_connection.close()

    def _getTicketValues(self):
        insert_values = []
        insert_values.append(self.currentSprint) # passing this to ticket from main window
        insert_values.append(self.ticketDisplay.text())
        insert_values.append(self.time.toString("hh:mm:ss"))
        insert_values.append(self.notesField.toPlainText())

        return insert_values

    # TODO: naturalize the time here so that it's easier to read
    def startTimer(self):
        self.timer.start(1000)

    def stopTimer(self):
        self.timer.stop()

    def resumeTimer(self):
        self.timer.start()

    def updateTime(self):
        self.time = self.time.addSecs(1)
        self.currentTimeLabel.setText(f"<h2>{self.time.toString('hh:mm:ss')}</h2>")
    
    def saveTime(self):
        query = self._prepareSaveQuery()
        self.stopTimer()
        values = self._getTicketValues()

        for value in values: 
            query.addBindValue(value)

        if not query.exec():
            QMessageBox.critical(
                None, 
                "App Name - Error!",
                f"Database Error {self.db_connection.lastError().databaseText()}",
            )
        else: 
            QMessageBox.information(
                None,
               "Inserted Values",
                " ,".join([str(value) for value in values])
            )

        
class DevTrackerController:

    def __init__(self, view):
        self._view = view
        self._connectSignalsAndSlots()

    def _connectSignalsAndSlots(self):
        
        self._view.button_list[0].clicked.connect(self._view.startNewTicket)

class TicketController:
    def __init__(self, view):
        self._view = view
        self._connectSignalsAndSlots()

    def _connectSignalsAndSlots(self):
        self._view.startWork.clicked.connect(self._view.startTimer)
        self._view.endWork.clicked.connect(self._view.stopTimer)
        self._view.resumeWork.clicked.connect(self._view.resumeTimer)
        self._view.timer.timeout.connect(self._view.updateTime)
        self._view.saveTimer.clicked.connect(self._view.saveTime)
        
def main():
    # TODO: add a way to change the database - thank you refact.ai
    trackerApp = QApplication([])
    trackerDb = DevTrackerDatabase('QSQLITE', DB_NAME)
    trackerWindow = DevTrackerMainWindow()
    trackerWindow.show()
    
    DevTrackerController(view=trackerWindow)
    sys.exit(trackerApp.exec())

if __name__ == '__main__': 
    main()
