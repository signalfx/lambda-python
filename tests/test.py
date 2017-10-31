import signalfx_lambda


@signalfx_lambda.wrapper
def handler(event, context):
    print(context)
    print(context.function_name)
    print(context.function_version)
    print(event["abc"])
    signalfx_lambda.send_gauge('application_performance', 100)
    return "result"
