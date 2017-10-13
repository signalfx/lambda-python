# SignalFx Python Lambda Wrapper

SignalFx Python Lambda Wrapper.

## Usage

The SignalFx Java Lambda Wrapper is a wrapper around an AWS Lambda Python function handler, used to instrument execution of the function and send metrics to SignalFx.

### Installation

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

### Sending metric from the Lambda function

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