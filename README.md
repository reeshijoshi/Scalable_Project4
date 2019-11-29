# Scalable_Project4
IOT Device Simulation using Lambda and S3

Sensor.py => Holds the code for generating sensor output and offloading into Aggregator.

Lambda.py => AWS Lambda which acts as an Aggregator

# Fog to Cloud Setup:
Create S3 bucket:
1. Go to S3 buckets module in AWS console.
2. Click on "Create Bucket"
3. Enter bucket name.
4. Create the bucket with default settings.

Create Lambda:
1. Navigate to the AWS Lambda console. Click "Create New Function"
2. Create a blank template
3. Copy code from `fogToCloud.py` and paste in the lambda handler
4. Create Function.

Add Trigger to Lambda:
1. Click on "Add Trigger"
2. Select S3 from the "Select Trigger" dopdown.
3. Select the Bucket you created.
4. Click on add 
