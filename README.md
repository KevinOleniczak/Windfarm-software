# Windfarm Demo Software

### Purpose:
This project is intended to demonstrate several features of AWS IoT and related services for practical use cases. It leverages a 3D printed wind turbine and weather station that's documented seperately.

The demo hardware for these models are in a seperate repo [here](https://github.com/KevinOleniczak/Windfarm-hardware).

### What's included:
This demo windfarm contains several model elements that help you experience the interactions between a turbine and a monitoring station on the edge. Connectivity with the AWS Cloud is not required to observe a safety assessment that is performed with real data that published continually from the turbine.

![](windfarm_demo.jpg)

### What does it do:
See how industrial edge connectivity is accomplished with AWS services. An IoT device read sensor values from a wind turbine continually and publish it to a local IoT Gateway using AWS Greengrass. The gateway receives the data and performs a local inference to evaluate turbine safety based on rotation speed and vibrations. Data is selectively shared with the AWS Cloud where it can be used to build and train machine learning models, stored for analytical purposes and visualized over time on a dashboard.

### What you need:
* Windturbine model with electronics as described [here](https://github.com/KevinOleniczak/Windfarm-hardware/blob/master/turbine/turbine.md).
* Weather station with electronics as described [here](https://github.com/KevinOleniczak/Windfarm-hardware/blob/master/wx-station/wx-station.md).
* Windturbine Raspberry PI Shield
* Windturbine Device >> Raspberry PI Zero W with at least 16 GB micro SD Card (with 40 pin male header for GPIO)
* Greengrass Gateway >> Raspberry PI 3b with at least 16 GB micro SD Card (with 40 pin male header for GPIO)
* WiFi Router to connect OR wired ethernet switch and router (if wired, then also get a usb to wired ethernet adapter for the Raspberry PI Zero W)
* Internet connection
* An electric desk fan with variable speeds
* AWS Account with permissions to configure services as noted below

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
* IAM Role: WindfarmLambdaRole (trusted entities lambda.amazonaws.com AND iotanalytics.amazonaws.com)
* IAM Policy: WindfarmFirehosePolicy
* IAM Role: WindfarmFirehoseRole (trusted entities kinesis.amazonaws.com)
* IAM Policy: WindfarmGreengrassPolicy
* IAM Role: WindfarmGreengrassRole (trusted entities greengrass.amazonaws.com)
* Lambda Function: WindfarmTurbineJSON2CSV
* Lambda Function: WindfarmGetTurbineLiveStats
* Lambda Function: WindfarmGetTurbineCount
* Lambda Function: WindfarmGetWeather
* Lambda Function: WindfarmGetTurbineShadowState
* Lambda Function: WindfarmGetLatestWeather
* Lambda Function: WindfarmResetTurbine
* Lambda Function: WindfarmSetTurbineBrake
* Lambda Function: WindfarmGetTurbineTrend
* Step Function: WindfarmGetStatus (update lambda ARN)
* Step Function: WindfarmGetTurbineStatus (update lambda ARN)
* DynamoDB Table: windturbine-data-latest
* DynamoDB Table: windfarm-weather-latest
* S3 Bucket: windfarm-turbine-data-yourname
* Kinesis Firehose: WindfarmTurbineDataStream
* ElasticSearch Cluster: windfarm-es (do not create in VPC as IoT Core can't access it there)
* IoT Analytics Channel: windturbine_data_channel
* IoT Analytics Channel: windfarm_weather_channel
* IoT Rule: WindfarmTurbineDataIoTRule (select * from 'windturbine-data' >> 4 actions)
* GO Setup a device and load some data before continuing


* IoT Analytics Pipeline: windturbine_data_pipeline (enrich with calculated column called "turbine_vibe": "sqrt(power(turbine_vibe_x,2) + power(turbine_vibe_y,2)  + power(turbine_vibe_z,2) )"  )
* IoT Analytics Data Store: windturbine_data_datastore
* IoT Analytics Data Set: raw_windturbine_data (for quicksight reporting) >> SELECT * FROM windturbine_data_datastore_raw where turbine_vibe is not null
* IoT Analytics Data Set: ml_training_windturbine_data (for model building) >> SELECT * FROM windturbine_data_datastore_raw where turbine_vibe_peak is not null
* IoT Analytics Pipeline: windfarm_weather_pipeline
* IoT Analytics Data Store: windfarm_weather_datastore
* IoT Analytics Data Set: all_windturbine_data (select *, update every 15 minutes)
* Glue: Build crawler for S3 bucket data and run an ad hoc crawl
* QuickSight: connector to IOTA, dashboard
* ElasticSearch: Add default index (turbines*)
* Kibana: Add visualizations and dashboard
* Cognito Identity Pool: (for Sumerian Lambda/IOT access)
* Sumerian: Import scene bundle

* IAM Policy: WindfarmNotebookPolicy
* IAM Role: WindfarmNotebookRole (trusted entities sagemaker.amazonaws.com)

### IoT Things
IoT Thing: WindTurbine1

### Greengrass Setup
Lambda Function: WindfarmWeatherReporter (zip archive with Greengrass SDK)
Lambda Function: WindTurbineSafetyCheck (zip archive with Greengrass SDK)


Run this to get the GG Group CA cert for use with devices that connect:
> aws greengrass get-group-certificate-authority --certificate-authority-id dad15d1xxxxxxxxxxxxxxxxxxxfd5aaba1f --group-id 1a161bbxxxxxxxxxxxxxxxx97f130 | jq -r ".PemEncodedCertificate" > myGgcRootCA.pem

### Machine Learning Model using Amazon SageMaker
* SageMaker Notebook Server: WindfarmNotebookInstance (if interested in training ml models for yourself or running analytics in a notebook)
* IoT Analytics Notebook: WindfarmTurbineNotebook
* SageMaker ML Model Artifact for GG-ML in S3 bucket: tbd


### Alexa for Business (A4B) in us-east-1
* IAM Policy: WindfarmAlexaSkillPolicy
* IAM Role: WindfarmAlexaSkillRole (trusted entities lambda.amazonaws.com)
* Lambda Function: WindFarmAlexaSkillDemo (must be in us-east-1 region. Also add the Alexa Skills Kit event source)
* Private Alexa Skill: Windfarm Demo (published in PRIVATE mode) https://developer.amazon.com/docs/alexa-for-business/create-and-publish-private-skills.html
* A4B Room: A4B_Room1
* A4B Room Profile: A4B_Room_Profile
* A4B Private skill: Windfarm (linked to the devices)
* Link the new private skill to the A4B account to make available for users
* Inviate users and/or add designated Alexa devices like an Echo

### Sumerian
* Gather turbine mast and fin OBJ files from hardware models repository
* Import into an asset library and then add to your scene in Sumerian
* 

### TODO:
Fix WindfarmSetTurbineBrake lambda to accept thingname
