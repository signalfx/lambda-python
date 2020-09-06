import functools
import signalfx
import os
import datetime
import six

from . import utils
from .version import name, version

ingest_endpoint = utils.get_metrics_url()
ingest_timeout = float(os.environ.get('SIGNALFX_SEND_TIMEOUT', 0.3))

sfx = signalfx.SignalFx(ingest_endpoint=ingest_endpoint)

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
    return [ map_datapoint(data_point) for data_point in data_points ]


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


def generate_wrapper_decorator(access_token):
    def wrapper_decorator(func):
        @functools.wraps(func)
        def call(*args, **kwargs):
            global ingest
            # timeout for connecting = 1 and responding 0.3
            ingest = sfx.ingest(access_token, timeout=(1, ingest_timeout))
            context = args[1]  # expect context to be second argument

            global default_dimensions
            default_dimensions.update(utils.get_fields(context))
            default_dimensions['metric_source'] = 'lambda_wrapper'

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
    return wrapper_decorator


def wrapper():
    def inner(*args, **kwargs):
        access_token = utils.get_access_token()
        if len(args) == 1 and callable(args[0]):
            # plain wrapper with no parameter
            # call the wrapper decorator like normally would
            decorator = generate_wrapper_decorator(access_token)
            return decorator(args[0])
        else:
            dimensions = kwargs.get('dimensions')
            if isinstance(dimensions, dict):
                # wrapper with dimension parameter
                # assign default dimensions
                # then return the wrapper decorator
                default_dimensions.update(dimensions)

            token = kwargs.get('access_token')
            if isinstance(token, six.string_types):
                access_token = token

            return generate_wrapper_decorator(access_token)
    return inner
