# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 18:27:22 2021

@author: lenovo
"""

import io
import os.path
import xlsxwriter

from PyPDF2 import PdfFileReader
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager,PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams, LTTextBoxHorizontal
from pdfminer.converter import PDFPageAggregator


class extractPDF:
    
    def createFilePath(self,tempPath,pdffileName,excelFileName):
        success = True
        try:         
            pdfFilePath = os.path.join(tempPath,pdffileName)    
            excelFilePath = os.path.join(tempPath ,excelFileName)
            msg ="File path Creation successfull"
        except:
            msg = "File Path Creation! Throwing error"
            success = False  
        return [pdfFilePath,excelFilePath,success,msg]
    
    def textExtract(self,pdfFile,excelFile,lstPageNum):      
        success = True

        lstSortedPageNum=sorted(lstPageNum)
        lastPage = lstSortedPageNum[-1]
        
        lstSortedPageNum = [x - 1 for x in lstSortedPageNum]
        
        
        try:
            workbook = xlsxwriter.Workbook(excelFile)
            with open(pdfFile, "rb") as pdf_file:
                pdf_reader = PdfFileReader(pdf_file)
                totalPDFPages = pdf_reader.numPages
    
                if lastPage > int(totalPDFPages):
                    success = False
                    msg = "Entered page number doesnot exist"
                    return [success,msg]
                
                # Create a PDF resource manager object that stores shared resources.
                rsrcmgr = PDFResourceManager()
                # Create a PDF device object.
                device = PDFDevice(rsrcmgr)
                # BEGIN LAYOUT ANALYSIS
                # Set parameters for analysis.
                laparams = LAParams()
                # Create a PDF page aggregator object.
                device = PDFPageAggregator(rsrcmgr, laparams=laparams)
                # Create a PDF interpreter object.
                interpreter = PDFPageInterpreter(rsrcmgr, device)
                
                
                pageNum = 0
                for pagecontent in PDFPage.get_pages(pdf_file,lstSortedPageNum):
                    pageNum += 1
                    interpreter.process_page(pagecontent)
                    worksheet = workbook.add_worksheet("Page "+str(pageNum))
                    layout = device.get_result()
                    excelrowNum=0
                    for obj in layout:
                        excelrowNum += 1
                        # if it's a textbox, print text and location
                        if isinstance(obj, LTTextBoxHorizontal):
                            df_extracted_Text = [int(obj.bbox[0]), int(obj.bbox[1]), int(obj.bbox[2]),int(obj.bbox[3]),obj.get_text().replace('\n', '')]  
                            for col_num, data in enumerate(df_extracted_Text):
                                worksheet.write(excelrowNum,col_num,data)               
            msg="Text Extraction successfull and saved to excel"
        except:
            msg = "Text Extraction! Throwing error"
            success = False
        finally:
            workbook.close()
        return [success,msg]
    


    def removeFiles(self,lstFilePath,success,filetype):
        msg="File Deletion is successful"
        try:
            if filetype == "pdf":
                if not success:
                    if os.path.isfile(lstFilePath[1]):
                        os.remove(lstFilePath[1])
                   
                if  os.path.isfile(lstFilePath[0]):
                    os.remove(lstFilePath[0])
            else:
                 return_data = io.BytesIO()
                 with open(lstFilePath, 'rb') as fo:
                    return_data.write(fo.read())
                    return_data.seek(0) 
                 if os.path.isfile(lstFilePath):
                    os.remove(lstFilePath)
                 return return_data                    
        except:
            msg="File Deletion is not successful"
        return  msg 
    
    def validateFields(self,upload_file_extention,lstUploadExtention,startRange,endRange,lstPageNumber,maxNofPages):
        success = True
        msg = "Validation Successful"
        if ("." + str(upload_file_extention[1]).lower()) != lstUploadExtention[0]:
            msg = "Not valid file format! Only PDF is allowed"
            success = False
            return [success,msg]
        
        if startRange > endRange:
            msg = "Start page number is greater than end page number"
            success = False
            return [success,msg]     
 
        if len(lstPageNumber) > maxNofPages:
            msg = "Max of 25 pages can be processed"
            success = False
            return [success,msg]
    
        return [success,msg]

             