import json
import boto3
import os
bucketname = "cf-templates-gqptnqyrfxr9-eu-west-1"

data = {}
def lambda_handler(event, context):
    try:
        print(str(event))
        if event is None:
            return {
                "statusCode" : 500,
                "body" : "Payload Empty"
            }
        if not "Readings" in event:
            return {
                "statusCode" : 500,
                "body" : "No Readings in Payload"
            }
        if not "SensorType" in event:
            return {
                "statusCode" : 500,
                "body" : "No SensorType in Payload"
            }
        filename = str(event["SensorType"]) + ".json"
        buck = check_lambda_connection()
        if buck is None:
            return {
                "statusCode" : 500,
                "body" : "Data received. Error saving data because bucket not found. Try again later . . ."
            }
        
        try:
            boto3.client('s3').download_file(bucketname, filename, "/tmp/update.json")
        except:
            buck.put_object(Body=b"{\"Readings\" : []}", Key=filename)
            boto3.client("s3").download_file(bucketname, filename, "/tmp/update.json")
        
        with open("/tmp/update.json", "r") as f:
            data = json.load(f)
        
        for i in event["Readings"]:
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
def check_lambda_connection():
    try:
        s3 = boto3.resource("s3")
        s3.meta.client.head_bucket(Bucket=bucketname)
        print("Bucket Found")
        return s3.Bucket(bucketname)
    except:
        return None