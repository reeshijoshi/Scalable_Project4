import json
import boto3
import os
import time
from random import randint
bucketname = "scalable-project4-pedometer-bucket"
rand = randint(0,5)
flag = False
if rand > 3:
    flag = True
data = {}
def lambda_handler(event, context):
    if flag:
        time.sleep(10)
    try:
        valid = validateData(event)
        if not valid[0] :
            return {
                "statusCode" : 500,
                "body" : valid[1]
            }
        filename = "PedometerMemory/"+str(event["SensorType"]) + ".json"
        buck = checkBucketExists()
        if buck is None:
            return {
                "statusCode" : 500,
                "body" : "Data received. Error saving data because bucket not . Try again later . . ."
            }
        try:
            boto3.client('s3').download_file(bucketname, filename, "/tmp/update.json")
        except:
            buck.put_object(Body=b"{\"Readings\" : []}", Key=filename)
            boto3.client("s3").download_file(bucketname, filename, "/tmp/update.json")
        
        with open("/tmp/update.json", "r") as f:
            data = json.load(f)
        
        for i in event["Readings"]:
            if event["SensorType"] == "Pedometer":
                if len(data["Readings"]) == 0:
                    data["Readings"] = event["Readings"]
                else:
                    data["Readings"][0]["Value"] = int(data["Readings"][0]["Value"]) + int(event["Readings"][0]["Value"])
                    data["Readings"][0]["TimeStamp"] = event["Readings"][0]["TimeStamp"]
            else:
                data["Readings"].append(i)
            
        with open("/tmp/update.json", "w+") as f:
            json.dump(data, f)
            
        with open("/tmp/update.json", "rb") as fi:
            obj = fi.read()
            buck.put_object(Body=obj, Key=filename)
            print("Uploaded JSON = " + str(event))
        return {
            "statusCode" : 200,
            "body" : "Data received and saved successfully"
        }
    except Exception as e:
        return {
            "statusCode" : 500,
            "body" : "An exception has occured: StackTrace : \n" + str(e)
        }
        raise e
def checkBucketExists():
    try:
        s3 = boto3.resource("s3")
        s3.meta.client.head_bucket(Bucket=bucketname)
        print("Bucket Found")
        return s3.Bucket(bucketname)
    except:
        return None
def validateData(event):
    if event is None:
        return (False, "Payload Empty")
    if not "Readings" in event:
        return (False, "No Readings in Payload")
    if not "SensorType" in event:
        return (False, "No SensorType in Payload")
    return (True,)