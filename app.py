# -*- coding: utf-8 -*-

from datetime import datetime
import os.path
from flask import Flask,render_template,request, send_file, Markup
import TextExtractModel
from werkzeug.exceptions import RequestEntityTooLarge


app=Flask(__name__)

app.config['UPLOAD_EXTENSIONS'] = ['.pdf']
app.config['DOWNLOAD_EXTENSIONS'] = ['.xlsx']
app.config["Mime_Type"] = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
app.config["TEMP_PATH"] = os.path.join(app.root_path,"TempFileStorage")
app.config['MAX_PAGES'] = 25
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

pdfExt = TextExtractModel.extractPDF()

@app.route("/",methods=["Get","POST"])
def home():
    return render_template("index.html")

@app.route("/extract",methods=["Get","POST"])
def extract():
    
    success = True
    excelFileName = ""
    
    try:
        pdfReq = request.files["pdfFile"]
    except RequestEntityTooLarge:
        success = False
        msg="File size exceeds the max upload limit"
    
    if success:
        
        upload_file_extention = request.files["pdfFile"].filename.split(".")
        
        
        if request.form["chkRange"] == "range":
            lstPageNumber = [*range(int(request.form["startRange"]),int(request.form["endRange"])+1)]
            startRange = int(request.form["startRange"])
            endRange = int(request.form["endRange"])
        else:
            lstPageNumber = [int(strChar) for strChar in request.form["commaSepValues"].split(",")]
            startRange=0
            endRange=0
    
        lstValidate = pdfExt.validateFields(upload_file_extention,app.config['UPLOAD_EXTENSIONS'],startRange,endRange,lstPageNumber,app.config['MAX_PAGES'])
            
        if not lstValidate[0]:
            msg=lstValidate[1]
              
        success = lstValidate[0]
    
 

    if success:
        
        FILE_CREATE_TIMESTAMP = str(datetime.now().strftime("-%d%m%Y-%H%M%S%f"))

        excelFileName = upload_file_extention[0] + FILE_CREATE_TIMESTAMP + app.config['DOWNLOAD_EXTENSIONS'][0]
        pdffileName = upload_file_extention[0] + FILE_CREATE_TIMESTAMP  + app.config['UPLOAD_EXTENSIONS'][0]
        lstFilePath = pdfExt.createFilePath(app.config["TEMP_PATH"],pdffileName,excelFileName)
        
        
        if lstFilePath[2]:      
            try:           
               if os.path.isfile(lstFilePath[0]):
                  msg="File exists! Please rename the file"
                  success = False
               else:
                  pdfReq.save(lstFilePath[0])
                  msg="File uploaded! Will be processed"
                  success = lstFilePath[2]
            except:
                  msg="Temporary file generation is throwing an exception"
                  success = False
            

            if success:
                lstTextExtract = pdfExt.textExtract(lstFilePath[0],lstFilePath[1],lstPageNumber)
                
                if lstTextExtract[0]:
                    contentMessage = "<br/> Note: Download the file before closing the browser."
                    msg = Markup(lstTextExtract[1] + contentMessage)
                    
                else:
                   msg = lstTextExtract[1]
                
                success = lstTextExtract[0]
                   
        else:
             msg = lstFilePath[3]
             success = lstFilePath[2]
        
        deleteMessage=pdfExt.removeFiles(lstFilePath,success,"pdf")

    return render_template("index.html",fileSucess=success,message=msg,downloadFle=excelFileName) 
   

@app.route("/savetosystem/<downloadFle>",methods=['GET', 'POST'])
def savetosystem(downloadFle):
    if downloadFle != "":
        exlFileName = downloadFle
        #exlFileName = downloadFle + app.config["FILE_CREATE_TIMESTAMP"] + app.config['DOWNLOAD_EXTENSIONS'][0]
        deleteExcelFile = os.path.join(app.config["TEMP_PATH"],exlFileName)
        #print(deleteExcelFile)              
        return_data = pdfExt.removeFiles(deleteExcelFile,True,"excel")           
        return send_file(return_data,as_attachment=True,
                         mimetype=str(app.config["Mime_Type"][0])
                         ,attachment_filename=exlFileName)
    else:
        return render_template("index.html",fileSucess=False)


       
if __name__ == "_main_":
    app.run(debug=True, port=5000, reload=True)
