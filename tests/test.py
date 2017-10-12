import signalfx_lambda


@signalfx_lambda.wrapper
def handler(event, context):
    signalfx_lambda.send_gauge('application_performance', 100)
    return "result"
