import signalfx
import os
import datetime

from version import name, version

ingest_end_point = os.environ.get('SIGNALFX_INGEST_ENDPOINT', 'https://pops.signalfx.com')

sfx = signalfx.SignalFx(ingest_endpoint=ingest_end_point)

is_cold_start = True

default_dimensions = {}

ingest = None


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
    if ingest:
        ingest.send(counters=map_datapoints(counters), gauges=map_datapoints(gauges))


# convenience method
def send_counter(metric_name, metric_value=1, dimensions={}):
    send_metric(counters=[{'metric': metric_name, 'value': metric_value, 'dimensions': dimensions}])


# convenience method
def send_gauge(metric_name, metric_value, dimensions={}):
    send_metric(gauges=[{'metric': metric_name, 'value': metric_value, 'dimensions': dimensions}])


def wrapper_decorator(func):
    def call(*args, **kwargs):
        global ingest
        # timeout for connecting = 1 and responding 0.3
        ingest = sfx.ingest(os.environ.get('SIGNALFX_AUTH_TOKEN'), timeout=(1, 0.3))
        context = args[1]  # expect context to be second argument
        function_arn = context.invoked_function_arn

        # Expected format arn:aws:lambda:us-east-1:accountId:function:functionName:$LATEST
        splitted = function_arn.split(':')
        global default_dimensions

        default_dimensions.update({
            'aws_function_version': context.function_version,
            'aws_function_name': context.function_name,
            'aws_region': splitted[3],
            'aws_account_id': splitted[4],
            'metric_source': 'lambda_wrapper',
            'function_wrapper_version': name + '_' + version
        })
        runtime_env = os.environ.get('AWS_EXECUTION_ENV')
        if runtime_env is not None:
            default_dimensions['aws_execution_env'] = runtime_env
        if splitted[5] == 'function':
            updatedArn = list(splitted)
            if len(splitted) == 8:
                default_dimensions['aws_function_qualifier'] = splitted[7]
                updatedArn[7] = context.function_version
            elif len(splitted) == 7:
                updatedArn.append(context.function_version)
            default_dimensions['lambda_arn'] = ':'.join(updatedArn)

        elif splitted[5] == 'event-source-mappings':
            default_dimensions['event_source_mappings'] = splitted[6]
            default_dimensions['lambda_arn'] = function_arn

        global is_cold_start
        start_counters = [
            {
                'metric': 'function.invocations',
                'value': 1
            },
        ]
        if is_cold_start:
            start_counters.append({
                'metric': 'function.cold_starts',
                'value': 1
            })
            is_cold_start = False
        send_metric(
            counters=start_counters
        )
        end_counters = []
        time_start = datetime.datetime.now()
        try:
            result = func(*args, **kwargs)
            return result
        except:
            end_counters.append({
                'metric': 'function.errors',
                'value': 1
            })
            raise
        finally:
            time_taken = datetime.datetime.now() - time_start
            send_metric(
                counters=end_counters,
                gauges=[
                    {
                        'metric': 'function.duration',
                        'value': time_taken.total_seconds() * 1000
                    }
                ]
            )

            # flush everything
            ingest.stop()

    return call


def wrapper(param):
    if callable(param):
        # plain wrapper with no parameter
        # call the wrapper decorator like normally would
        return wrapper_decorator(param)
    else:
        if isinstance(param, dict):
            # wrapper with dimension parameter
            # assign default dimensions
            # then return the wrapper decorator
            default_dimensions.update(param)
        return wrapper_decorator

