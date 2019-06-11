import functools
import os
import opentracing
from opentracing.ext import tags as ext_tags
from jaeger_client import Config

from . import utils

def wrapper(func):
    @functools.wraps(func)
    def call(*args, **kwargs):
        context = args[1]

        tracer = init_jaeger_tracer(context)

        span_tags = utils.get_fields(context)
        span_tags['component'] = 'python-lambda-wrapper'
        span_tags[ext_tags.SPAN_KIND] = ext_tags.SPAN_KIND_RPC_SERVER

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
    endpoint = utils.get_tracing_url()
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

    tracer = config.new_tracer()
    opentracing.tracer = tracer

    return tracer
