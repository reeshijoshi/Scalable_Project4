import json
import boto3
import os
import datetime
sourceBucketName = "scalable-computing-project4"
destBucketName = "group18-cloud-bucket"
todaysdate = str(datetime.datetime.now()).split(" ")[0]
sourceFolderName = "FogMemory/"
def lambda_handler(event, context):
    s3 = boto3.resource("s3")
    try:
        s3.meta.client.head_bucket(Bucket=sourceBucketName)
    except Exception as e:
        return {
        'statusCode': 501,
        'body': str(e)
        }
    try:
        for file in s3.Bucket(sourceBucketName).objects.filter(Prefix=sourceFolderName):
            filePath = file.key
            #print(file)
            fileName = filePath.split("FogMemory/")[1]
            print(fileName)
            copySource = {"Bucket" : sourceBucketName, "Key" : filePath}
            s3.Object(destBucketName, todaysdate+"/"+fileName).copy_from(CopySource = copySource)
            boto3.client('s3').put_object_acl(ACL='public-read-write', Bucket = destBucketName, Key = todaysdate+"/"+fileName )
    except Exception as e:
        return {
        'statusCode': 500,
        'body': str(e)
        }
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
