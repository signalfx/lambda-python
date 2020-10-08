import functools
import os
import logging
import opentracing
from opentracing.ext import tags as ext_tags
from signalfx_tracing import auto_instrument
from jaeger_client import Config

from . import utils

_tracer = None

logger = logging.getLogger('signalfx-tracing')
if os.environ.get('SIGNALFX_TRACING_DEBUG', '').lower() in ['true', '1']:
    logger.setLevel(logging.DEBUG)


span_kind_mapping = {
    'aws:sqs': ext_tags.SPAN_KIND_CONSUMER, 
}

def wrapper(with_span=True):
    def inner(func):
        @functools.wraps(func)
        def call(event, context):
            tracer = init_jaeger_tracer(context)
            try:
                if with_span:
                    with create_span(event, context):
                        # call the original handler
                        return func(event, context)
                else:
                    return func(event, context)
            except BaseException as e:
                raise
            finally:
                tracer.flush()

        return call
    return inner


def init_jaeger_tracer(context):
    global _tracer
    if _tracer:
        return _tracer

    endpoint = utils.get_tracing_url()
    service_name = os.getenv('SIGNALFX_SERVICE_NAME', context.function_name)
    access_token = utils.get_access_token()

    logger = logging.getLogger('signalfx-tracing')
    tracer_config = {
            'sampler': {
                'type': 'const',
                'param': 1
                },
            'propagation': 'b3',
            'jaeger_endpoint': endpoint,
            'logging': True,
            'logger': logger,
            }

    if access_token:
        tracer_config['jaeger_user'] = 'auth'
        tracer_config['jaeger_password'] = access_token

    config = Config(config=tracer_config, service_name=service_name)

    tracer = config.new_tracer()
    _tracer = opentracing.tracer = tracer
    auto_instrument(_tracer)

    return tracer


def inject(carrier, ctx=None):
    if not _tracer:
        raise RuntimeError((
            'tracing has not been initialized. Use signalfx_lambda.is_traced'
            ' decorator to initialize tracing'))
    if not ctx:
        scope = _tracer.scope_manager.active
        if scope and scope.span:
            ctx = scope.span.context

    if ctx:
        _tracer.inject(ctx, opentracing.Format.HTTP_HEADERS, carrier)


class create_span(object):
    def __init__(self, event, context, auto_add_tags=True, operation_name=None):
        if not _tracer:
            raise RuntimeError((
                'tracing has not been initialized. Use signalfx_lambda.is_traced'
                ' decorator to initialize tracing'))
        self.event = event
        self.context = context
        self.auto_add_tags = auto_add_tags
        self.operation_name = operation_name
        self.tracer = _tracer
        self.scope = None
    
    def __enter__(self):
        if isinstance(self.event, dict):
            event = self.event
        else:
            event = {}

        headers = event.get('headers', event.get('attributes', {}))
        parent_span = self.tracer.extract(opentracing.Format.HTTP_HEADERS, headers)

        span_tags = {}
        if self.auto_add_tags:
            span_tags = utils.get_tracing_fields(self.context)
            span_tags['component'] = 'python-lambda-wrapper'
            span_tags[ext_tags.SPAN_KIND] = span_kind_mapping.get(
                event.get('eventSource'),
                ext_tags.SPAN_KIND_RPC_SERVER
            )

        op_name = self.operation_name
        if not op_name:
            span_prefix = os.getenv('SIGNALFX_SPAN_PREFIX', 'lambda_python_')
            op_name = span_prefix + self.context.function_name

        self.scope = self.tracer.start_active_span(
            op_name,
            tags=span_tags,
            child_of=parent_span
        )
        return self.scope

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.scope:
            return

        if exc_val:
            span = self.scope.span
            span.set_tag(ext_tags.ERROR, True)
            span.set_tag("sfx.error.message", str(exc_val))
            span.set_tag("sfx.error.object", str(exc_val.__class__))
            span.set_tag("sfx.error.kind", exc_val.__class__.__name__)
        self.scope.close()
