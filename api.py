import sys,os,re,uuid

from os import path
from flask import Flask, request, jsonify
from flask_restplus import Api, Resource, fields 
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from flask_restplus import reqparse

from services.ReportService import ReportService
from services.CSVParserService import CSVParserService


# Set up the application 
flask_app = Flask(__name__)
flask_app.config.from_object("config.Config")

api = Api(app = flask_app, 
		  version = "1.0", 
		  title = "Payroll Api", 
		  description = "Payroll api which has abaility to upload csv into db and generate reports ")

# Model define
# payPeriod = api.model('payrollReport', {
#     'startDate': fields.String,
#     'endDate': fields.String
# })

# employeeReport = api.model('employeeReport', {
#     'employeeId': fields.Integer,
#     'amountPaid': fields.Float,
#     'payPeriods': payPeriod

# })

# employeeReports = api.model('employeeReports', {
#     'employeeReport': fields.List(fields.Nested(employeeReport))
# })

# payrollReport = api.model('payrollReport',{
#     'employeeReports' : employeeReports
# })

# result = api.model('result',{
#     'payrollReport' : payrollReport
# })



upload_parser = reqparse.RequestParser()
upload_parser.add_argument('csv_file',  
                         type=FileStorage, 
                         location='files', 
                         required=True, 
                         help='csv file for payroll calculation')



# Configure the routeing for each endpoints
@api.route("/uploads/")
class Uploads(Resource):
    @api.doc(responses={ 200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error' }, parser=upload_parser)
    @api.expect(upload_parser)
    def post(self):
        try:
            args = upload_parser.parse_args()
            # Valid input and raise expection if needed
            if args['csv_file'].mimetype != 'text/csv':
                raise Exception('File type is incorrect.')
            filename = secure_filename(args['csv_file'].filename)
            if not re.match(r"time-report-[0-9]+.csv", filename):
                raise Exception('File name format is incorrect.')
            destination = os.path.join(flask_app.config.get('UPLOAD_FILE_FOLDER'), '')
            if not os.path.exists(destination):
                os.makedirs(destination)
            csv_file = '%s%s' % (destination, filename)
            if path.exists(csv_file):
                raise Exception('File already uploaded.')
            args['csv_file'].save(csv_file)

            ParserService = CSVParserService(flask_app.config.get('MSSQL_DATABASE_CONNECTION_STRING'),csv_file)
            ParserService.upload_file()
            ParserService.close_file()
            # Option to remove csv file after upload
            # os.remove(csv_file)

            return {"status": filename + " uploaded"}
        except KeyError as e:
            api.abort(500, e, statusCode = "500")
        except Exception as e:
            api.abort(400, e, statusCode = "400")

@api.route("/reports/")
class Report(Resource):
    @api.doc(responses={ 200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error' })
    def get(self):
        try:
            reportService = ReportService(flask_app.config.get('MSSQL_DATABASE_CONNECTION_STRING'))
            result = reportService.generate_report()
            return result
        except KeyError as e:
            api.abort(500, e, statusCode = "500")
        except Exception as e:
            api.abort(400, e, statusCode = "400")


if __name__ == '__main__':
    flask_app.run()