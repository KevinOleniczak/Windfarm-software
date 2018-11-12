CREATE EXTERNAL TABLE `windfarm_turbine_data_demo`(
  `deviceid` bigint COMMENT 'null',
  `timestamp` timestamp,
  `location` string,
  `lat` double,
  `lng` double, 
  `temperature` bigint,
  `turbine_speed` double,
  `turbine_rev_cnt` bigint,
  `turbine_voltage` double,
  `turbine_vibe_x` bigint,
  `turbine_vibe_y` bigint,
  `turbine_vibe_z` bigint,
  `turbine_vibe_peak` double)
ROW FORMAT DELIMITED
  FIELDS TERMINATED BY ','
STORED AS INPUTFORMAT
  'org.apache.hadoop.mapred.TextInputFormat'
OUTPUTFORMAT
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://windfarm-turbine-data-demo/'
TBLPROPERTIES (
  'CrawlerSchemaDeserializerVersion'='1.0',
  'CrawlerSchemaSerializerVersion'='1.0',
  'UPDATED_BY_CRAWLER'='WindfarmTurbineDataS3',
  'averageRecordSize'='117',
  'classification'='csv',
  'columnsOrdered'='true',
  'compressionType'='none',
  'delimiter'=',',
  'objectCount'='1',
  'recordCount'='58',
  'sizeKey'='6837',
  'typeOfData'='file')
