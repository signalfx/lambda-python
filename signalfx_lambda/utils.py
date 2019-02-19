import os

from .version import name, version

def get_fields(context):
    function_arn = context.invoked_function_arn

    fields = {}

    # Expected format arn:aws:lambda:us-east-1:accountId:function:functionName:$LATEST
    splitted = function_arn.split(':')

    fields.update({
        'aws_request_id': context.aws_request_id,
        'aws_function_version': context.function_version,
        'aws_function_name': context.function_name,
        'aws_region': splitted[3],
        'aws_account_id': splitted[4],
        'metric_source': 'lambda_wrapper',
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

    return fields

