import boto3
import json
import time
import os
from random import randint
import botocore.config

tempFile = "D:/Study/Project4/tempFile.json"
sensorID = "TemperatureSensor_1"
sensorType = "Temperature"
functionNameAggregator = 'arn:aws:lambda:eu-west-1:023947881979:function:sendReceiveDataHopefully'
functionNamePedometer = 'arn:aws:lambda:eu-west-1:023947881979:function:pedometerSecondaryAggregator'
invocationType = 'RequestResponse'
sensor = {"SensorType" : sensorType}
value = 0
message = ""
alert = False
data = {}
cfg = botocore.config.Config(connect_timeout = 5, read_timeout = 5)
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
    client = boto3.client("lambda", config = cfg)
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
                with open(tempFile, "w+") as jsonFile:
                    json.dump(data, jsonFile)
        return True
    except Exception as e:
        print(str(e))
        return False

def getCurrentReading():
    global value
    global message
    global alert
    value = randint(35, 44)
    if value > 40:
        if value >= 43:
            message = "Very High"
            alert = True
        else:
            message = "High"
    else:
        message = "OK"

def checkLoadDataFromTempFile():
    if os.path.exists(tempFile):
        with open(tempFile, "r") as jsonFile:
            data = json.load(jsonFile)
        os.remove(tempFile)
    

while True:
    getCurrentReading()
    checkLoadDataFromTempFile()
    sendDataToAggregator(data)
    data = {}
    time.sleep(10)