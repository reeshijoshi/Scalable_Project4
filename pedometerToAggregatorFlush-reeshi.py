import json
import boto3
import os

pedometerBucketName = "scalable-project4-pedometer-bucket"
aggregatorBucketname = "scalable-project4-aggregator-bucket"
sourceFolderName = "PedometerMemory/"
destFolderName = "AggregatorMemory/"
tempPedo = "/tmp/pedometer.json"
tempAggr = "/tmp/aggregator.json"
def lambda_handler(event, context):
    s3 = boto3.resource("s3")
    try:
        s3.meta.client.head_bucket(Bucket=pedometerBucketName)
    except Exception as e:
        print(str(e))
        return {
        'statusCode': 501,
        'body': str(e)
        }
    try:
        for file in s3.Bucket(pedometerBucketName).objects.filter(Prefix=sourceFolderName):
            filePath = file.key
            print(filePath)
            fileName = filePath.split("/")[1]
            print(fileName)
            try:
                boto3.client('s3').download_file(pedometerBucketName, filePath, tempPedo)
                try:
                    boto3.client('s3').download_file(aggregatorBucketname, destFolderName+fileName, tempAggr)
                    with open(tempPedo, "r") as p:
                        with open(tempAggr, "a") as a:
                            pedoData = json.load(p)
                            aggrData = json.load(a)
                            for i in pedoData["Readings"]:
                                aggrData["Readings"].append(i)
                        with open(tempAggr, "w") as a:
                            json.dump(aggrData, a)
                        with open(tempAggr, "rb") as a:
                            s3.Bucket(aggregatorBucketname).put_object(Body = a.read(), Key = destFolderName+fileName)
                except:
                    with open(tempPedo, "rb") as p:
                        s3.Bucket(aggregatorBucketname).put_object(Body = p.read(), Key = destFolderName+fileName)
            except Exception as e:
                print(str(e))
                return {
                'statusCode': 500,
                'body': str(e)
                }
    except Exception as e:
        print(str(e))
        return {
        'statusCode': 500,
        'body': str(e)
        }
    return {
        'statusCode': 200,
        'body': "Data Transferred Successfully"
    }

