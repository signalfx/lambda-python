import functools
import os
import opentracing
import pip
from jaeger_client import Config

from . import utils

def wrapper(func):
    @functools.wraps(func)
    def call(*args, **kwargs):
        context = args[1]

        tracer = init_jaeger_tracer(context)

        try:
            from signalfx_tracing import auto_instrument
            auto_instrument(tracer)
        except ImportError:
            pass

        span_tags = utils.get_fields(context)
        span_tags['component'] = 'python-lambda-wrapper'

        span_prefix = os.getenv('SIGNALFX_SPAN_PREFIX', 'lambda_python_')

        try:
            with tracer.start_active_span(span_prefix + context.function_name, tags=span_tags) as scope:
                # call the original handler
                return func(*args, **kwargs)
        except BaseException as e:
            scope.span.set_tag('error', True)
            scope.span.log_kv({'message': e})

            raise
        finally:
            tracer.close()

    return call


def init_jaeger_tracer(context):
    endpoint = os.environ.get('SIGNALFX_TRACING_URL')
    if not endpoint:
        endpoint = os.getenv('SIGNALFX_ENDPOINT_URL', 'https://ingest.signalfx.com/v1/trace')
    service_name = os.getenv('SIGNALFX_SERVICE_NAME', context.function_name)
    access_token = utils.get_access_token()

    tracer_config = {
            'sampler': {
                'type': 'const',
                'param': 1
                },
            'propagation': 'b3',
            'jaeger_endpoint': endpoint,
            'logging': True,
            }

    if access_token:
        tracer_config['jaeger_user'] = 'auth'
        tracer_config['jaeger_password'] = access_token

    config = Config(config=tracer_config, service_name=service_name)

    tracer = config.initialize_tracer()

    return tracer
