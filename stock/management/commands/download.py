from django.core.management.base import BaseCommand, CommandError
from datetime import datetime, timedelta
import os
import shutil
import urllib3
import zipfile

class Command(BaseCommand):
    help = 'Downloads the stock data for specific range'
    
    def add_arguments(self, parser):
        #Variable Declaration
        messageHelp = "The Start Date - format YYYY-MM-DD"
        parser.add_argument("-s",
                            "--startdate",
                            help= messageHelp,
                            required=True,
                            type=lambda d: datetime.strptime(d, '%Y-%m-%d'))
        parser.add_argument("-e",
                            "--enddate",
                            help=messageHelp,
                            required=True,
                            type=lambda d: datetime.strptime(d, '%Y-%m-%d'))

    def handle(self, *args, **options):
    #Declaring constants   
        dirStocks = "stock/static/data/stock_files/"
        dirZipExtract = "stock/static/data/temp/"
        dirZip = "stock/static/data/zip/"
        messageDownload = "Downloading file for %s"
        messageFileNotFound = "File not found for %s"
        messageSuccess = "Successfully finished executing the command"
        modeGet = "GET"
        modeRead = "r"
        modeWriteBinary = "wb"       
        url_nse = "https://www.nseindia.com/archives/equities/bhavcopy/pr/"
        user_agent = {'user-agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) ..'}
        extensionCsv = ".csv"
        extensionZip = ".zip"

    #Read Arguments
        start = options['startdate']
        end = options['enddate']

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        for single_date in self.daterange(start, end):
            fileZip = "PR" + str(single_date.day).zfill(2) + \
               str(single_date.month).zfill(2) + \
               str(single_date.year)[-2:] + extensionZip
            fileCsv = "Pd" + str(single_date.day).zfill(2) + \
                str(single_date.month).zfill(2) + \
                str(single_date.year)[-2:] + extensionCsv
            pathFile = dirZip + fileZip
            url = url_nse + fileZip     
            http = urllib3.PoolManager(10, headers=user_agent)
            r1 = http.urlopen(modeGet, url)
            if r1.status == 200:
                print(messageDownload %str(single_date))
                file = open(pathFile, modeWriteBinary)
                file.write(r1.data)
                file.close()
                zip_ref = zipfile.ZipFile(pathFile, modeRead)
                zip_ref.extractall(dirZipExtract)
                zip_ref.close()
                if(os.path.isfile(dirZipExtract+fileCsv)):
                    os.rename(dirZipExtract+fileCsv,
                              dirStocks+fileCsv)
                    shutil.rmtree(dirZipExtract)

            elif r1.status == 404:
                print( messageFileNotFound %str(single_date))

        self.stdout.write(self.style.SUCCESS(messageSuccess))

    def daterange(self, start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)



