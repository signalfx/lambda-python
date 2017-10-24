# SignalFx Python Lambda Wrapper

SignalFx Python Lambda Wrapper.

## Usage

The SignalFx Java Lambda Wrapper is a wrapper around an AWS Lambda Python function handler, used to instrument execution of the function and send metrics to SignalFx.

### Installation

To install from CDN
```
$ pip install https://cdn.signalfx.com/signalfx_lambda-0.0.1-py2.py3-none-any.whl
```


To install from source
```
$ pip install -e git+https://github.com/signalfx/lambda-python#egg=signalfx-lambda
```

### Environment Variables

```
SIGNALFX_AUTH_TOKEN=access token

SIGNALFX_INGEST_ENDPOINT=[optional]
```

### Wrapping a function

Decorate your handler with @signalfx_lambda.wrapper

```
import signalfx_lambda

@signalfx_lambda.wrapper
def handler(event, context):
    # your code
```

### Metrics and Dimensions sent by the wrapper

Lambda wrapper sends following metrics to SignalFx 

| Metric Name  | Type | Description |
| ------------- | ------------- | ---|
| aws.lambda.invocations  | Counter  | Count number of lambda invocations|
| aws.lambda.coldStarts  | Counter  | Count number of coldstarts|
| aws.lambda.errors  | Counter  | Count number of errors from underlying lambda handler|
| aws.lambda.duration  | Gauge  | Milliseconds in execution time of underlying lambda handler|

Lambda wrapper includes following dimensions to all data points sent to SignalFx

| Dimension | Description |
| ------------- | ---|
| lambda_arn  | ARN of the lambda function instance |
| aws_region  | AWS Region  |
| aws_account_id | AWS Account ID  |
| aws_function_name  | AWS Function Name (if it is not event source mapping lambda invocation)|
| aws_function_version  | AWS Function Version (if it is not event source mapping lambda invocation)|
| event-source-mappings  | AWS Function Name (if it is event source mapping lambda invocation) |


### Sending custom metric from the Lambda function

```
import signalfx_lambda

# sending application_performance metric with value 100 and dimension abc:def
signalfx_lambda.send_gauge('application_performance', 100, {'abc':'def'})

# sending counter metric with no dimension
signalfx_lambda.send_counter('database_calls', 1)
```

### Testing it out locally

Use python-lambda-local
```
pip install python-lambda-local
```

```
python-lambda-local tests/test.py tests/event.json -a 'arn:aws:lambda:us-east-1:accountId:function:functionNamePython:$LATEST'
```

### License

Apache Software License v2. Copyright © 2014-2017 SignalFx