import boto3
import json
import time
import os
from random import randint

glucoseFile = "D:/Study/Project4/glucoseFile.json"
sensorID = "GlucoseSensor_1"
sensorType = "Glucose"
functionNameAggregator = 'arn:aws:lambda:eu-west-1:023947881979:function:sendReceiveDataHopefully'
functionNamePedometer = 'arn:aws:lambda:eu-west-1:023947881979:function:pedometerSecondaryAggregator'
invocationType = 'RequestResponse'
sensor = {"SensorType" : sensorType}
value = 0
message = ""
alert = False
data = {}

class SomethingWentWrong(Exception):
    pass
def updatePayload(data):
    if not "Readings" in data:
        data["Readings"] = []
    data["Readings"].append({
        "SensorID" : sensorID,
        "Value" : str(value),
        "TimeStamp" : str(time.asctime(time.localtime(time.time()))),
        "Message" : message,
        "Alert" : str(alert)
    })
    return data

def tryConnection(data, functionName):
    client = boto3.client("lambda")
    try:
        data.update(sensor)
        print("Request Payload = " + str(data))
        response = client.invoke(
        FunctionName=functionName,
        InvocationType=invocationType,
        LogType='Tail',
        Payload=json.dumps(data),
        )
        responsePayload = json.loads(response['Payload'].read().decode("utf-8"))
        statusCode = int(responsePayload["statusCode"])
        if (statusCode != 200) :
            raise SomethingWentWrong("Status Code is not 200. Received response payload body as " + str(responsePayload["body"]))
        print("Response Payload = " + str(responsePayload["body"]))
        print("StatusCode received = " + str(statusCode))
        print("Sent to Aggregator at " + functionName + " successfully")
        return True
    except Exception as e:
        print(str(e))
        return False

def sendDataToAggregator(data):
    try:
        data = updatePayload(data)
        if not tryConnection(data, functionNameAggregator):
            if not tryConnection(data, functionNamePedometer):
                with open(glucoseFile, "w+") as jsonFile:
                    json.dump(data, jsonFile)
        return True
    except Exception as e:
        print(str(e))
        return False

def getCurrentReading():
    global value
    global message
    global alert
    value = randint(50, 180)
    if value >= 100:
        if value > 125:
            message = "Diabetic"
            alert = True
        else:
            message = "Prediabetic"
    else:
    	if value < 70:
    		message = "Hypoglycemic"
    	else:
        	message = "Normalglycemic"

def checkLoadDataFromGlucoseFile():
    if os.path.exists(glucoseFile):
        with open(glucoseFile, "r") as jsonFile:
            data = json.load(jsonFile)
        os.remove(glucoseFile)
    
while True:
    getCurrentReading()
    checkLoadDataFromGlucoseFile()
    sendDataToAggregator(data)
    data = {}
    time.sleep(10)
