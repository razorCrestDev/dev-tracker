# A file containing importable variables for the different
# sql execution logic

createSprintMaster = '''
    CREATE TABLE IF NOT EXISTS sprintmaster (
    Id             INTEGER  PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, 
    SprintValue    TEXT NOT NULL,
    StartDate      TEXT, 
    EndDate        TEXT 
)
'''
createDevTracker = '''
    CREATE TABLE IF NOT EXISTS devtracker (
    Id             INTEGER  PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, 
    SprintValue    TEXT NOT NULL, 
    TicketNumber   TEXT NOT NULL,
    TimeWorked     TEXT,
    TicketDetails  TEXT 
)
'''
saveDevTicket = '''
    INSERT INTO devtracker (
        SprintValue, 
        TicketNumber, 
        TimeWorked, 
        TicketDetails
        ) VALUES (?, ?, ?, ?)
'''

getCurrentSprint = '''
    SELECT SprintValue 
    FROM sprintmaster
    WHERE EndDate >= ? AND 
        StartDate <= ?
'''