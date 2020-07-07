import csv
import pyodbc
from datetime import datetime
  

class CSVParserService:

    def __init__(self, DBconfig,dir):
        self.dir = dir
        self.file = open(dir, 'r')
        self.DBconfig = DBconfig

    def close_file(self):
        if self.file:
            self.file.close()
            self.file = None

    def upload_file(self):
        sqlConnection = pyodbc.connect(self.DBconfig)
        cursor = sqlConnection.cursor()
        csv_file = csv.DictReader(self.file)
        # The code below can be improved use bulk insert
        insertSql = "insert into WorkRecords (DateWorked,CreationDateTime, HoursWorked, EmployeeId, JobGroupId) values (?, ?, ?, ?, ?)"
        for row in csv_file:
            DateWorked = datetime.strptime(row["date"], '%d/%m/%Y').date()
            CreationDateTime = datetime.now().date()
            cursor.execute(insertSql, DateWorked, CreationDateTime,row["hours worked"],row["employee id"],row["job group"])
            cursor.commit()
        sqlConnection.close()
