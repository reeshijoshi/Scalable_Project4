import boto3
import json
import time
import os
from random import randint

tempFile = "/Users/zhangruiqi/Downloads/TCD/Modules/CS7NS1SC/Project4/Scalable_Project4-master/tempFile.json"
sensorID = "TemperatureSensor_4"
sensorType = "Temperature"
functionNameAggregator = 'arn:aws:lambda:eu-west-1:331087843783:function:sensorToAggregator'
functionNamePedometer = 'arn:aws:lambda:eu-west-1:331087843783:function:pedometerBackupAggregator'
invocationType = 'RequestResponse'
sensor = {"SensorType" : sensorType}
sensorid = {"SensorID": sensorID}
ack = {"ACK" : str(0)}
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

        ack = {"ACK" : str(0)}
        data.update(ack)
        print("Request Payload = " + str(data))
        response = client.invoke(
        FunctionName=functionName,
        InvocationType=invocationType,
        LogType='Tail',
        Payload=json.dumps(data)
        )
        responsePayload = json.loads(response['Payload'].read().decode("utf-8"))
        statusCode = int(responsePayload["statusCode"])

        if (statusCode == 201) :
            # Successful
            print("Response Payload = " + str(responsePayload["body"]))
            print("StatusCode received = " + str(statusCode))
            print("Sent to Aggregator at " + functionName + " successfully")
            return True
        else: 
            if (statusCode != 200) :
                raise SomethingWentWrong("Status Code is not 200. Received response payload body as " + str(responsePayload["body"]))
            else:
                if verifyResponsePayload(responsePayload, data):
                    tempJson = {}
                    ack["ACK"] = str(1)
                    tempJson.update(ack)
                    tempJson.update(sensorid)
                    response = client.invoke(
                    FunctionName=functionName,
                    InvocationType=invocationType,
                    LogType='Tail',
                    Payload=json.dumps(tempJson)
                    )   
                else:
                    ack["ACK"] = str(-1)
                    data.update(ack)
                    tryConnection(data, functionNameAggregator)
 
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
 
def verifyResponsePayload(response, data):
    # This is dummy verification
    # rand = randint(0,5)
    # flag = True
    # if rand > 3:
    #     flag = True
    return True

while True:
    getCurrentReading()
    checkLoadDataFromTempFile()
    sendDataToAggregator(data)
    data = {}
    time.sleep(10)
