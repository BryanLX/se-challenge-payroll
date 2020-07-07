import pyodbc
from datetime import datetime
from calendar import monthrange


class ReportService:

    def __init__(self,DBconfig):
        self.DBconfig = DBconfig

    def generate_report(self):
        sqlConnection = pyodbc.connect(self.DBconfig)
        cursor = sqlConnection.cursor()
        workRecords_get_Sql = "select * from WorkRecords left join JobGroups On  JobGroups.GroupId = WorkRecords.JobGroupId order by EmployeeId, DateWorked"

        cursor.execute(workRecords_get_Sql)

        dict = {}
        for row in cursor.fetchall():
            process_record(row, dict)
        sqlConnection.close()
        return format_result(dict)



def format_result(dict):
    employeeReports = []
    for key, val in dict.items():
        for key2, val2 in val.items():
            payPeriod = {'startDate':key2,'endDate':val2[0]}
            employeeReports.append({'employeeId':key,'payPeriod':payPeriod,'amountPaid':val2[1]})
    return  {
        'payrollReport': {
            'employeeReports':employeeReports
        }
    }



def process_record(record, dict):
    key = record.EmployeeId
    DateWorked = record.DateWorked
    HourRate = record.HourRate
    Hours = record.HoursWorked
    
    year = DateWorked.year
    month = DateWorked.month
    day = DateWorked.day

    startDate = str(year) +"-"+ str(month) + "-"
    endDate = str(year) +"-"+ str(month) + "-"

    startDate = startDate+"01" if day <= 15 else startDate+"16" 
    endDate = endDate+"15" if day <= 15 else endDate+str(monthrange(year, month)[1])

    amount = Hours * HourRate
    
    if key not in dict:
        dict[key] = {}
    if startDate not in dict[key]:
        dict[key][startDate] = [endDate,amount]
    else:
        dict[key][startDate][1] += amount