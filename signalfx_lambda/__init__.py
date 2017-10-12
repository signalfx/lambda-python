import signalfx
import os
import datetime

ingest_end_point = os.environ.get('SIGNALFX_INGEST_ENDPOINT')

sfx = signalfx.SignalFx(ingest_endpoint=ingest_end_point) if ingest_end_point else signalfx.SignalFx()

is_cold_start = True

default_dimensions = {}

ingest = {}


def map_datapoint(data_point):
    return {
        'metric': data_point['metric'],
        'value': data_point['value'],
        'dimensions':
            dict(data_point['dimensions'], **default_dimensions) if 'dimensions' in data_point else
            default_dimensions
    }


def map_datapoints(data_points):
    return map(map_datapoint, data_points)


# less convenient method
def send_metric(counters=[], gauges=[]):
    ingest.send(counters=map_datapoints(counters), gauges=map_datapoints(gauges))


# convenience method
def send_counter(metric_name, metric_value=1, dimensions={}):
    send_metric(counters=[{'metric': metric_name, 'value': metric_value, 'dimensions': dimensions}])


# convenience method
def send_gauge(metric_name, metric_value, dimensions={}):
    send_metric(gauges=[{'metric': metric_name, 'value': metric_value, 'dimensions': dimensions}])


def wrapper(func):
    def call(*args, **kwargs):
        global ingest
        ingest = sfx.ingest(os.environ.get('SIGNALFX_AUTH_TOKEN'))

        context = args[1]  # expect context to be second argument
        function_arn = context.invoked_function_arn

        # Expected format arn:aws:lambda:us-east-1:accountId:function:functionName:$LATEST
        splitted = function_arn.split(':')
        global default_dimensions

        default_dimensions = {
            'lambda_arn': function_arn,
            'aws_region': splitted[3],
            'aws_account_id': splitted[4],
        }
        if splitted[5] == 'function':
            default_dimensions['aws_function_name'] = splitted[6]
            if len(splitted) == 8:
                default_dimensions['aws_function_version'] = splitted[7]
            else:
                default_dimensions['aws_function_version'] = context.function_version
        elif splitted[5] == 'event-source-mappings':
            default_dimensions['event_source_mappings'] = splitted[6]

        global is_cold_start
        start_counters = [
            {
                'metric': 'aws.lambda.invocations',
                'value': 1
            },
        ]
        if is_cold_start:
            start_counters.append({
                'metric': 'aws.lambda.coldStarts',
                'value': 1
            })
            is_cold_start = False
        send_metric(
            counters=start_counters
        )
        end_counters = [
            {
                'metric': 'aws.lambda.completed',
                'value': 1
            }
        ]
        time_start = datetime.datetime.now()
        try:
            result = func(*args, **kwargs)
            return result
        except:
            end_counters.append({
                'metric': 'aws.lambda.errors',
                'value': 1
            })
            raise
        finally:
            time_taken = datetime.datetime.now() - time_start
            send_metric(
                counters=end_counters,
                gauges=[
                    {
                        'metric': 'aws.lambda.duration',
                        'value': time_taken.total_seconds() * 1000
                    }
                ]
            )

            # flush everything
            ingest.stop()

    return call
