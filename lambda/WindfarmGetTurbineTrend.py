import boto3
from time import sleep
import numbers
import decimal

#Function for starting athena query
def run_query(query, database, s3_output):

    client = boto3.client('athena', region_name='us-west-2')
    response = client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={
            'Database': database
            },
        ResultConfiguration={
            'OutputLocation': s3_output,
            }
        )
    print('Athena Execution ID: ' + response['QueryExecutionId'])

    qryState = "TBD"
    while qryState != "SUCCEEDED":
        if qryState == "FAILED":
            break
        qryStatusResponse = client.get_query_execution(QueryExecutionId=response['QueryExecutionId'])
        qryState = qryStatusResponse['QueryExecution']['Status']['State']
        print (qryState)
        sleep (1)

    if qryState == "SUCCEEDED":
        dataResponse = client.get_query_results(
            QueryExecutionId=response['QueryExecutionId'])
            #NextToken='',
            #MaxResults=1
            #)
        myVal = dataResponse['ResultSet']['Rows'][1]['Data'][0]['VarCharValue']

    else:
        myVal = 'Query error'

    return myVal


def lambda_handler(event, context):

    mySQL = "select avg(col5) from windfarms.windfarms where col1 > '2017-12-11 21:23:00'"
    s3Output = "s3://windfarms-results/turbine/test"
    aQryResult = run_query(mySQL, "windfarms", s3Output)
    #print ("aQryResult = " + json.dumps(aQryResult))
    #if isinstance(myVal, (int, long, float, complex)):

    if aQryResult == 'Query error':
        msg = {
            "turbine_speed_trend": "unknown"
            }
    else:
        #msg = str(int(round(float(aQryResult),0)))
        msg = {
            "turbine_speed_trend": str("%.1f" % round(float(aQryResult),1))
            }

    return msg
