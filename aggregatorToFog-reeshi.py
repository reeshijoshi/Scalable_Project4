import json
import boto3
import os
sourceBucketName = "scalable-project4-aggregator-bucket"
destBucketName = "scalable-computing-project4"
destFolderName = "FogMemory/Aggregator_1/"
dFN = "FogMemory"
sourceFolderName = "AggregatorMemory/"
def lambda_handler(event, context):
    s3 = boto3.resource("s3")
    try:
        s3.meta.client.head_bucket(Bucket=sourceBucketName)
    except Exception as e:
        print(str(e))
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
        #for obj in s3.Bucket(destBucketName).objects.filter(Prefix = dFN):
            boto3.client('s3').put_object_acl(ACL='public-read-write', Bucket = destBucketName, Key = destFolderName+fileName )
    except Exception as e:
        print(str(e))
        return {
        'statusCode': 500,
        'body': str(e)
        }
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
