import json
import boto3
import os
sourceBucketName = "cf-templates-gqptnqyrfxr9-eu-west-1"
destBucketName = "scalable-computing-project4"
destFolderName = "FogMemory/"
sourceFolderName = "AggregatorMemory/"
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
            print(filePath)
            
            fileName = filePath.split("/")[1]
            print(fileName)
            copySource = {"Bucket" : sourceBucketName, "Key" : filePath}
            s3.Object(destBucketName, destFolderName+fileName).copy_from(CopySource = copySource)
    except Exception as e:
        return {
        'statusCode': 500,
        'body': str(e)
        }
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
