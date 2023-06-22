/* Database schema for the Dev Tracker app */
/*DROP TABLE devtracker*/

CREATE TABLE IF NOT EXISTS devtracker (
    Id             INTEGER  PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, 
    SprintValue    TEXT NOT NULL, 
    TicketNumber   TEXT NOT NULL,
    TimeWorked     TEXT,
    TicketDetails  TEXT 
)

CREATE TABLE IF NOT EXISTS sprintMaster (
    Id             INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
    SprintValue     TEXT NOT NULL,
    StartDate       TEXT,
    EndDate         TEXT
)