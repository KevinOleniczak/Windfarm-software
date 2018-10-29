# Windfarm Demo Software

### Purpose:
This project is intended to demonstrate several features of AWS IoT and related services for practical use cases. It leverages a 3D printed wind turbine and weather station that's documented seperately.

The demo hardware for these models are in a seperate repo [here](https://github.com/KevinOleniczak/Windfarm-hardware).

### What's included:
This demo windfarm contains several model elements that help you experience the interactions between a turbine and a monitoring station on the edge. Connectivity with the AWS Cloud is not required to observe a safety assessment that is performed with real data that published continually from the turbine.

![](windfarm_demo.jpg)

### What does it do:
See how industrial edge connectivity is accomplished with AWS services. An IoT device read sensor values from a wind turbine continually and publish it to a local IoT Gateway using AWS Greengrass. The gateway receives the data and performs a local inference to evaluate turbine safety based on rotation speed and vibrations. Data is selectively shared with the AWS Cloud where it can be used to build and train machine learning models, stored for analytical purposes and visualized over time on a dashboard.

### How does it work:
The Turbine connects using MQTT to a Greengrass gateway that relays data to the AWS IoT Core. The IoT Core forwards that data to several services for caching of latest metrics and historical trends.

High Level architecture
![](high_level_arch.png)

Detailed architecture
![](detailed_arch.png)

### AWS Services Setup
In a region with all of the referenced services create:
* IAM Policy: WindfarmDataIngestPolicy
* IAM Role: WindfarmDataIngestRole (trusted entities iot.amazonaws.com)
* IAM Policy: WindfarmLambdaPolicy
* IAM Role: WindfarmLambdaRole (trusted entities lambda.amazonaws.com)
* IAM Policy: WindfarmFirehosePolicy
* IAM Role: WindfarmFirehoseRole (trusted entities kinesis.amazonaws.com)
* Lambda Function: WindfarmTurbineJSON2CSV
* Lambda Function: WindfarmGetTurbineLiveStats
* Lambda Function: WindfarmGetTurbineCount
* Lambda Function: WindfarmGetWeather
* Lambda Function: WindfarmGetTurbineShadowState
* Lambda Function: WindfarmGetLatestWeather
* Lambda Function: WindfarmResetTurbine
* Lambda Function: WindfarmSetTurbineBrake
* Lambda Function: WindfarmGetTurbineTrend
* Lambda Function: WindFarmAlexaSkillDemo (must be in us-east-1 region)
* Step Function: WindfarmGetStatus (update lambda ARN)
* Step Function: WindfarmGetTurbineStatus (update lambda ARN)
* DynamoDB Table: windturbine-data-latest
* DynamoDB Table: windfarm-weather-latest
* S3 Bucket: windfarm-turbine-data-yourname
* Kinesis Firehose: WindfarmTurbineDataStream
* ElasticSearch Cluster: windfarm-es
* IoT Analytics Channel: windturbine_data_channel
* IoT Analytics Channel: windfarm_weather_channel
* IoT Rule: WindfarmTurbineDataIoTRule (select * from 'windturbine-data' >> 4 actions)
* GO Setup a device and load some data before continuing


* IoT Analytics Pipeline: windturbine_data_pipeline
* IoT Analytics Pipeline: windfarm_weather_pipeline
* IoT Analytics Data Store: ?
* QuickSight: connector to IOTA, dashboard
* Kibana:
* Alexa for Business: private skill
* Cognito Identity Pool:
* Sumerian:

### IoT Things
IoT Thing: WindTurbine1

### Greengrass Setup
Lambda Function: WindfarmWeatherReporter
Lambda Function: WindTurbineSafetyCheck

### TODO:
Fix WindfarmSetTurbineBrake lambda to accept thingname
