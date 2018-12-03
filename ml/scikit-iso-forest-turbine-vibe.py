import boto3
import botocore
import sys
import pandas as pd
from urllib2 import urlopen
import numpy as np
from sklearn.ensemble import IsolationForest
import pickle
import os

bucket_name = 'windfarm-turbine-data-ml-train'   # <--- specify a bucket you have access to

# create IoT Analytics client
iota_client = boto3.client('iotanalytics', region_name='us-west-2', aws_access_key_id='xxxxxxxxxxxxxxx', aws_secret_access_key='xxxxxxxxxxxxxxxxxxxxxxxxx')

#IoT Analytics dataset name
dataset = "ml_training_windturbine_data2"
dataset_test = "ml_testing_windturbine_data2"

time_col = 'timestamp'
value_col = 'turbine_vibe_peak'

model_path = '/home/pi/windfarm'
model_name = 'turbine-vibe-model.pkl'

# import target Data Set from AWS IoT Analytics service
dataset_url = iota_client.get_dataset_content(datasetName = dataset)['entries'][0]['dataURI']
df = pd.read_csv(dataset_url, index_col=time_col, parse_dates=True, infer_datetime_format=True).sort_index()

if df.empty:
    raise Exception('No data found')
if (value_col not in df):
    value_col = df.columns[0]

#drop columns not needed
drop=["rownum","timestamp_unix"]
df.drop(drop, axis=1, inplace=True)

# import target Data Set from AWS IoT Analytics service
# TEST DATASET
dataset_url = iota_client.get_dataset_content(datasetName = dataset_test)['entries'][0]['dataURI']
df_test = pd.read_csv(dataset_url, index_col=time_col, parse_dates=True, infer_datetime_format=True).sort_index()

if df_test.empty:
    raise Exception('No data found')
if (value_col not in df_test):
    value_col = df_test.columns[0]

#drop columns not needed
drop=["rownum","timestamp_unix"]
df_test.drop(drop, axis=1, inplace=True)

# fit the model
rng = np.random.RandomState(42)
clf = IsolationForest(max_samples=1000, random_state=rng, contamination=0.01)
clf.fit(df)
y_pred_train = clf.predict(df)
y_pred_test = clf.predict(df_test)

#write the model artifact to disk
import zipfile
with open(os.path.join(model_path, model_name), 'w') as out:
    pickle.dump(clf, out)
aZipFile = os.path.splitext(model_path + '/' + model_name)[0] + '.zip'
zipfile.ZipFile(aZipFile, mode='w').write(model_path + '/' + model_name)

#transfer the artifact to S3
head, tail = os.path.split(aZipFile)
s3_client = boto3.resource('s3', region_name='us-west-2', aws_access_key_id='xxxxxxxxxxxxxxxxx', aws_secret_access_key='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
s3_client.meta.client.upload_file(aZipFile, bucket_name, tail)
