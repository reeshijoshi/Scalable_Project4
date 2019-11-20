import boto3
import json
import time
import os
from random import randint
import botocore.config
import BatteryHandling
import sys

tempFile = "D:/Documents/AWSIOT/tempFile.json"
sensorID = "TemperatureSensor_2"
sensorType = "Temperature"
functionNameAggregator = 'arn:aws:lambda:eu-west-1:094482812955:function:sensorToAggregator'
functionNamePedometer = 'arn:aws:lambda:eu-west-1:094482812955:function:pedometerAggregator'
invocationType = 'RequestResponse'
sensor = {"SensorType" : sensorType}
value = 0
message = ""
alert = False
data = {}
cfg = botocore.config.Config(connect_timeout = 5, read_timeout = 5)
energy = 0
powerType = 1
threshold1 = 20
threshold2 = 10

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
    global energy
    client = boto3.client("lambda", config = cfg)
    try:
        data.update(sensor)
        payload=json.dumps(data)
        print("Request Payload = " + str(data))
        request_size = sys.getsizeof(payload)
        startTime = int(round(time.time() * 1000))
        response = client.invoke(
        FunctionName=functionName,
        InvocationType=invocationType,
        LogType='Tail',
        Payload=payload,
        )
        endTime = int(round(time.time() * 1000))
        connectionDuration = endTime-startTime
        energy = BatteryHandling.decrease_transfer_energy(connectionDuration, energy)
        energy = BatteryHandling.increase_energy(energy, connectionDuration)
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

def writeToTempFile(data):
    try:
        with open(tempFile, "w+") as jsonFile:
            json.dump(data, jsonFile)
    except Exception as e:
        print(str(e))

def sendDataToAggregator(data):
    try:
        data = updatePayload(data)
        if not tryConnection(data, functionNameAggregator):
            if not tryConnection(data, functionNamePedometer):
                writeToTempFile(data)
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

def sleepTimer(duration):
    global energy
    for i in range(duration):
        time.sleep(1)
        energy = BatteryHandling.decrease_idle_time_energy(energy)
        print("\n*************************************Battery left (Idle time energy loss) - "+str(energy))
        energy = BatteryHandling.increase_energy(energy)
        print("\n*************************************Battery left (Recharging) - "+str(energy))

energy = int(sys.argv[1])
while True:
    data = {}
    getCurrentReading()
    checkLoadDataFromTempFile()
    if energy <=threshold1:
        print("\n*************************************Battery Left after txn - "+str(energy))
        if energy <= threshold2:
            writeToTempFile(data)
            print("----------------------------Readings written to temp file")
            sleepTimer(20)
        else:
            sendDataToAggregator(data)
            sleepTimer(20)
    else:
        getCurrentReading()
        checkLoadDataFromTempFile()
        sendDataToAggregator(data)
        print("\n*************************************Battery Left after txn - "+str(energy))
        sleepTimer(10)