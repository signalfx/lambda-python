import os
import warnings

from .version import name, version

fields = {}

def get_fields(context):
    function_arn = context.invoked_function_arn

    if fields.get('aws_request_id') != context.aws_request_id:
        # Expected format arn:aws:lambda:us-east-1:accountId:function:functionName:$LATEST
        splitted = function_arn.split(':')

        fields.update({
            'aws_request_id': context.aws_request_id,
            'aws_function_version': context.function_version,
            'aws_function_name': context.function_name,
            'aws_region': splitted[3],
            'aws_account_id': splitted[4],
            'function_wrapper_version': name + '_' + version
        })
        runtime_env = os.environ.get('AWS_EXECUTION_ENV')
        if runtime_env is not None:
            fields['aws_execution_env'] = runtime_env
        if splitted[5] == 'function':
            updatedArn = list(splitted)
            if len(splitted) == 8:
                fields['aws_function_qualifier'] = splitted[7]
                updatedArn[7] = context.function_version
            elif len(splitted) == 7:
                updatedArn.append(context.function_version)
            fields['lambda_arn'] = ':'.join(updatedArn)

        elif splitted[5] == 'event-source-mappings':
            fields['event_source_mappings'] = splitted[6]
            fields['lambda_arn'] = function_arn

    return fields.copy()


def get_metrics_url():
    url = os.environ.get('SIGNALFX_INGEST_ENDPOINT')
    if url:
        warnings.warn('SIGNALFX_INGEST_ENDPOINT is deprecated, use SIGNALFX_METRICS_URL instead.', DeprecationWarning)
    else:
        url = os.environ.get('SIGNALFX_METRICS_URL')

    if not url:
        url = os.environ.get('SIGNALFX_ENDPOINT_URL', 'https://pops.signalfx.com')

    return url


def get_tracing_url():
    url = os.environ.get('SIGNALFX_TRACING_URL')

    if not url:
        url = os.environ.get('SIGNALFX_ENDPOINT_URL')

        if url:
            # if the common endpoint url is used, we need to append the trace path
            url = url + '/v1/trace'
        else:
            url = 'https://ingest.signalfx.com/v1/trace'

    return url


def get_access_token():
    token = os.environ.get('SIGNALFX_ACCESS_TOKEN')
    if not token:
        warnings.warn('SIGNALFX_AUTH_TOKEN is deprecated, use SIGNALFX_ACCESS_TOKEN instead.', DeprecationWarning)
        token = os.environ.get('SIGNALFX_AUTH_TOKEN')

    return token
