# Windfarm Demo Software

### Purpose:
This project is intended to demonstrate several features of AWS IoT and related services for an operational safety use case with a wind turbine. It leverages a 3D printed wind turbine and weather station that's documented seperately. The demo hardware for these models are in a seperate repo [here](https://github.com/KevinOleniczak/Windfarm-hardware).

### What's included:
This demo windfarm contains several model elements that help you experience the interactions between a wind turbine and a monitoring station on the edge. Connectivity with the AWS Cloud is not required to observe a safety assessment that is performed with real data that is published continually from the turbine.

<img src="windfarm_demo.jpg" width="400" />

### What does it do:
See how industrial edge connectivity is accomplished with AWS services. An IoT device read sensor values from a wind turbine continually and publish it to a local IoT Gateway using AWS Greengrass. The gateway receives the data and performs a local inference to evaluate turbine safety based on rotation speed and vibrations. Data is selectively shared with the AWS Cloud where it can be used to build and train machine learning models, stored for analytical purposes and visualized over time on a dashboard.

Noteworthy architectural features:
* Secure IoT edge connectivity between local devices and the AWS Cloud
* ML inference using Greengrass and Lambda with no cloud dependency to perform safety checks in near real-time
* Route IoT data to different storage services based on need – IoT Analytics supports snapshots of data for ML training with ease
* Perform feature engineering of data using IoT Analytics pipelines that can be applied in retrospect easily
* Elasticity of the AWS Cloud to build and train ML models
* State is managed using IoT shadows to request changes from the cloud and the edge
* Data is selectively subscribed to by the cloud for visualization and ML model training
* Re-use of Lambda functions to support multiple use case (UI, Alexa, Sumerian, etc.)
* Use of Step Functions to orchestrate the fan-out of multiple Lambda calls concurrently to speed response time in Alexa interaction
* Selectively data can be sent to the cloud one of three ways; normal IoT Core, Kinesis or using our newer IoT Basic Ingest method
* Kibana requires an ElasticSearch cluster but provides the shortest delay for data refresh vs. QuickSight via Athena or IoT Analytics with a longer delay but is serverless
* Sumerian VR provides remote visualization (CAD files imported) of current state (IoT shadow – the start of digital twin)

[Demo video on YouTube](http://bit.ly/2GyUvHj)

### What you need:
* Windturbine model with electronics as described [here](https://github.com/KevinOleniczak/Windfarm-hardware/blob/master/turbine/turbine.md).
* Weather station with electronics as described [here](https://github.com/KevinOleniczak/Windfarm-hardware/blob/master/wx-station/wx-station.md).
* Windturbine Raspberry PI Shield
* Windturbine Device >> Raspberry PI Zero W with at least 16 GB micro SD Card (with 40 pin male header for GPIO)
* Greengrass Gateway >> Raspberry PI 3b with at least 16 GB micro SD Card (with 40 pin male header for GPIO)
* WiFi Router to connect OR wired ethernet switch and router (if wired, then also get a usb to wired ethernet adapter for the Raspberry PI Zero W)
* Internet connection
* An electric desk fan with variable speeds
* An Alexa device (Echo or phone app would work)
* If using a wired ethernet network include a switch, cables and ethenet adapter for the RPI Zero W
* AWS Account with permissions to configure services as noted below

### How does it work:
The Turbine connects using MQTT to a Greengrass gateway that relays data to the AWS IoT Core. The IoT Core forwards that data to several services for caching of latest metrics and historical trends.

High Level architecture

<img src="high_level_arch.png" width="800" />

Detailed architecture

<img src="detailed_arch.png" width="800" />

### Raspberry PI Setup
sudo raspi-config
Then Advanced >> I2C >> Enable

### AWS Services Setup
In a region with all of the referenced services create:
* IAM Policy: WindfarmDataIngestPolicy
* IAM Role: WindfarmDataIngestRole (trusted entities iot.amazonaws.com)
* IAM Policy: WindfarmLambdaPolicy
* IAM Role: WindfarmLambdaRole (trusted entities lambda.amazonaws.com, iotanalytics.amazonaws.com and states.us-west-2.amazonaws.com)
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
* Lambda Function: WindfarmGetShadowState
* Step Function: WindfarmGetStatus (update lambda ARN)
* Step Function: WindfarmGetTurbineStatus (update lambda ARN)
* DynamoDB Table: windturbine-data-latest (used as a latest cache)
* DynamoDB Table: windfarm-weather-latest (used as a latest cache)
* S3 Bucket: windfarm-turbine-data-yourname
* S3 Bucket: windfarm-turbine-data-failed-yourname (Kinesis Stream to ElasticSearch)
* Kinesis Firehose: WindfarmTurbineDataStreamIoT (IoT to S3)
* Kinesis Firehose: WindfarmTurbineDataStream2ES (Kinesis Stream to ElastiSearch)
* Kinesis Firehose: WindfarmTurbineDataStream2S3 (Kinesis Stream to S3)

### IoT Core
* IoT Rule: WindfarmTurbineDataIoTRule (select * from 'windturbine-data')
* IoT Action for WindfarmTurbineDataIoTRule: Multi Column DynamoDB table >> windturbine-data-latest
* IoT Action for WindfarmTurbineDataIoTRule: Kinesis Firehose stream >> WindfarmTurbineDataStream
* IoT Action for WindfarmTurbineDataIoTRule: ElasticSearch cluster >> windfarm-es
* IoT Action for WindfarmTurbineDataIoTRule: IoT Analytics channel >> windturbine_data_channel
* IoT Rule: WindfarmWeatherData (select * from 'windfarm-weather')
* IoT Action for WindfarmWeatherData: Multi Column DynamoDB table >> windfarm-weather-latest
* IoT Action for WindfarmWeatherData: IoT Analytics channel >> windfarm_weather_channel
* GO Setup a device and load some data before continuing

### IoT Analytics
* IoT Analytics Channel: windturbine_data_channel
* IoT Analytics Channel: windfarm_weather_channel
* IoT Analytics Pipeline: windturbine_data_pipeline (enrich with calculated column called "turbine_vibe": "sqrt(power(turbine_vibe_x,2) + power(turbine_vibe_y,2)  + power(turbine_vibe_z,2) )"  )
* IoT Analytics Data Store: windturbine_data_datastore
* IoT Analytics Data Set: raw_windturbine_data (for quicksight reporting) >> SELECT * FROM windturbine_data_datastore_raw where turbine_vibe is not null
* IoT Analytics Data Set: ml_training_windturbine_data (for model building) >> SELECT * FROM windturbine_data_datastore_raw where turbine_vibe_peak is not null
* IoT Analytics Pipeline: windfarm_weather_pipeline
* IoT Analytics Data Store: windfarm_weather_datastore
* IoT Analytics Data Set: all_windturbine_data (select *, update every 15 minutes)
* IoT Analytics Notebook: WindfarmTurbineNotebook
* IoT Analytics Data Set: windfarm_weather_recent_dataset (used by lambda for status)

SELECT windfarmid,
max(timestamp) as timestamp,
avg(cast(wind_speed as double)) as avg_wind_speed,
max(cast(wind_speed as double)) as max_wind_speed
FROM windfarm_weather_datastore
where from_iso8601_timestamp(timestamp) > date_add('minute', -5, now())
and wind_speed is not null
group by windfarmid

* IoT Analytics Data Set: windfarm_turbine_recent_dataset (used by lambda for status)


SELECT deviceid, thing_name,
max(timestamp) as timestamp,
avg(cast(turbine_speed as double)) as avg_turbine_speed,
max(cast(turbine_speed as double)) as max_turbine_speed,
avg(cast(turbine_voltage as double)) as avg_turbine_voltage,
max(cast(turbine_voltage as double)) as max_turbine_voltage,
avg(cast(turbine_vibe_peak as double)) as avg_turbine_vibe_peak,
max(cast(turbine_vibe_peak as double)) as max_turbine_vibe_peak,
avg(cast(turbine_temp as double)) as avg_turbine_temp,
max(cast(turbine_temp as double)) as max_turbine_temp
FROM windturbine_data_datastore
where from_iso8601_timestamp(timestamp) > date_add('minute', -5, now())
and timestamp is not null
group by deviceid, thing_name


### Glue and Athena
* Glue: Build crawler for S3 bucket data and run an ad hoc crawl
* QuickSight: connector to IOTA
* Build a dashboard

### ElasticSearch
* ElasticSearch Cluster: windfarm-es (do not create in VPC as IoT Core can't access it there)
* (load some data before continuing)
* ElasticSearch: Add default index (turbines*)
* Kibana: Add visualizations and dashboard

### IoT Things
* IoT Thing Type: WindfarmCore (add this for gg cores)
* IoT Thing Type: WindfarmTurbine (add this for turbines)
* IoT Thing: WindTurbine1 (set the thing type)

### Greengrass Group Setup
* Greengrass Group Name: WindfarmGroup
* Settings: Associate the role >> WindfarmGreengrassRole, Set log levels for Error types.
* IoT Device: WindTurbine1 (or which ever number is appropriate)
* IoT Device: WindfarmGroup_Core1 (or which ever number is appropriate)
* Lambda Function: WindfarmWeatherReporter (zip archive with Greengrass SDK)
* Lambda Function: WindTurbineSafetyCheck (zip archive with Greengrass SDK)
* Local Resource: Weather (volume at /weather and make it read only) Associate it with the lambda function: WindfarmWeatherReporter
* Subscription: Local Shadow Service >> WindTurbine1 (on topic $aws/things/WindTurbine1/shadow/#)
* Subscription: WindTurbine1 >> Local Shadow Service (on topic $aws/things/WindTurbine1/shadow/#)
* Subscription: WindTurbine1 >> IoT Cloud (on topic windturbine-data)
* Subscription: WindfarmWeatherReporter >> IoT Cloud (on topic any topic)
* Subscription: WindTurbine1 >> WindTurbineSafetyCheck (on topic windturbine-data)

Run this to get the GG Group CA cert for use with devices that connect:

> aws greengrass list-groups  (get the group-id for the next command)


> aws greengrass list-group-certificate-authorities --group-id 823492f1-xxxxxxxxxxxxxxx-723efe873caa   (get the certificate-authority-id for the next step)


> aws greengrass get-group-certificate-authority --certificate-authority-id dad15d1xxxxxxxxxxxxxxxxxxxfd5aaba1f --group-id 1a161bbxxxxxxxxxxxxxxxx97f130 | jq -r ".PemEncodedCertificate" > myGgcRootCA.pem

### Amazon SageMaker
* IAM Policy: WindfarmNotebookPolicy
* IAM Role: WindfarmNotebookRole (trusted entities sagemaker.amazonaws.com)
* SageMaker Notebook Server: WindfarmNotebookInstance (if interested in training ml models for yourself or running analytics in a notebook)
* S3 Bucket: windfarm-turbine-data-ml-train
* SageMaker ML Model Artifact for GG-ML in S3 bucket: build for your platform

### SCIKIT Learn
* Model training script: scikit-iso-forest-turbine-vibe.py (requires iam keys if running on rpi)

### Scikit-Learn Training Server
* sudo pip install boto3
* sudo pip install pandas
* sudo pip install -U scikit-learn

### Greengrass ML Inference Setup
* On the RPI, go do the install of MXNet as described here: https://docs.aws.amazon.com/greengrass/latest/developerguide/ml-console.html#ml-console-create-lambda
* Lambda Function: WindTurbineSafetyCheckIF (for greengrass - uses Isolation Forest algo)

### Kinesis Streams
* Kinesis Stream: WindfarmTurbineStream (2 shards)
* Lambda Function: WindfarmTurbineStreamProcessor (event is Kinesis stream)


### Alexa for Business (A4B) in us-east-1
* IAM Policy: WindfarmAlexaSkillPolicy
* IAM Role: WindfarmAlexaSkillRole (trusted entities lambda.amazonaws.com)
* Lambda Function: WindFarmAlexaSkillDemo (must be in us-east-1 region. Also add the Alexa Skills Kit event source)
* Private Alexa Skill: Windfarm Demo (published in PRIVATE mode) https://developer.amazon.com/docs/alexa-for-business/create-and-publish-private-skills.html
* A4B Room: A4B_Room1
* A4B Room Profile: A4B_Room_Profile
* A4B Private skill: Windfarm (linked to the devices)
* Link the new private skill to the A4B account to make available for users: ask api add-private-distribution-account --skill-id amzn1.ask.skill.86aaxxxxxxxxx1e41 --stage live --account-id arn:aws:iam::1xxxxxxxxxx4:root
* Inviate users and/or add designated Alexa devices like an Echo

### Sumerian
* Gather turbine mast and fin OBJ files from hardware models repository (if not using the bundle)
* Import into an asset library and then add to your scene in Sumerian (if not using the bundle)
* Cognito Identity Pool: WindfarmSumerianIdentityPool (for Sumerian Lambda/IOT access)
* Sumerian Scene: Import scene bundle (start a new scene and drag-n-drop the zip file bundle onto it)

### Adding additional turbines to an existing Greengrass group
* Setup new IoT thing in AWS IoT Core and install certificates along with the Greengrass group CA
* Keep thing name in a numbered series (i.e. WindTurbine1, WindTurbine2, etc)
* Ensure the new IoT thing is added to the thing type for wind turbines
* Update the RPI device program (python) to reference the correct thing name

### Adding additional Windfarms to an AWS account (for the same region)
* Add a new Greengrass Group and core device. Ensure it is named in series with others.
* Ensure turbine devices continue with the numeric numbering sequence (Alexa skill asks for turbine number)

### TODO:
* Fix WindfarmSetTurbineBrake lambda to accept thingname
* GPIO Connector integration for Greengrass with weather station
