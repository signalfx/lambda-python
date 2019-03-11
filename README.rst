SignalFx Python Lambda Wrapper
==============================

SignalFx Python Lambda Wrapper.

Usage
-----

The SignalFx Python Lambda Wrapper is a wrapper around an AWS Lambda
Python function handler, used to instrument execution of the function
and send metrics and traces to SignalFx.

Installation
~~~~~~~~~~~~

To install from PyPi

::

    $ pip install signalfx_lambda

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

**Note: the environment variables SIGNALFX_INGEST_ENDPOINT and SIGNALFX_AUTH_TOKEN are being deprecated and will not be supported in future releases.**

::

    SIGNALFX_ACCESS_TOKEN=access token

    # endpoint for both metrics and tracer. Overridden by SIGNALFX_METRICS_URL
    # and SIGNALFX_TRACING_URL if set
    SIGNALFX_ENDPOINT_URL=endpoint url

    # optional metrics and tracing configuration

    SIGNALFX_METRICS_URL=ingest endpoint [ default: https://pops.signalfx.com ]
    SIGNALFX_SEND_TIMEOUT=timeout in seconds for sending datapoint [ default: 0.3 ]

    SIGNALFX_TRACING_URL=tracing endpoint [ default: https://ingest.signalfx.com/v1/trace ]

SIGNALFX_TRACING_URL can be used to configure a common endpoint for metrics and
traces, as is the case when forwarding with the Smart Gateway.

If either SIGNALFX_TRACING_URL or SIGNALFX_METRICS_URL are set, they will take
precendence over SIGNALFX_ENDPOINT_URL for their respective components.

For example, if only SIGNALFX_ENDPOINT_URL is set:

::

    SIGNALFX_ENDPOINT_URL=<gateway_address>

both metrics and traces will be sent to the gateway address.

If SIGNALFX_ENDPOINT_URL and SIGNALFX_METRICS_URL are set:

::
    SIGNALFX_METRICS_URL=https://pops.signalfx.com

    SIGNALFX_ENDPOINT_URL=<gateway_address>

Traces will be sent to the gateway and metrics will go through POPS.

Wrapping a function
~~~~~~~~~~~~~~~~~~~

There are two wrappers provided.

For metrics, decorate your handler with @signalfx_lambda.emit_metrics

::

    import signalfx_lambda

    @signalfx_lambda.emit_metrics
    def handler(event, context):
        # your code

For tracing, use the @signalfx_lambda.is_traced decorator

::

    import signalfx_lambda

    @signalfx_lambda.is_traced
    def handler(event, context):
        # your code

The decorators can be used individually or together.

Metrics and dimensions sent by the metrics wrapper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Lambda wrapper sends the following metrics to SignalFx:

+-----------------------+-----------------------+-----------------------+
| Metric Name           | Type                  | Description           |
+=======================+=======================+=======================+
| function.invocations  | Counter               | Count number of       |
|                       |                       | Lambda invocations    |
+-----------------------+-----------------------+-----------------------+
| function.cold_starts  | Counter               | Count number of cold  |
|                       |                       | starts                |
+-----------------------+-----------------------+-----------------------+
| function.errors       | Counter               | Count number of       |
|                       |                       | errors from           |
|                       |                       | underlying Lambda     |
|                       |                       | handler               |
+-----------------------+-----------------------+-----------------------+
| function.duration     | Gauge                 | Milliseconds in       |
|                       |                       | execution time of     |
|                       |                       | underlying Lambda     |
|                       |                       | handler               |
+-----------------------+-----------------------+-----------------------+

The Lambda wrapper adds the following dimensions to all data points sent
to SignalFx:

+----------------------------------+----------------------------------+
| Dimension                        | Description                      |
+==================================+==================================+
| aws_request_id                   | AWS Request ID                   |
+----------------------------------+----------------------------------+
| lambda_arn                       | ARN of the Lambda function       |
|                                  | instance                         |
+----------------------------------+----------------------------------+
| aws_region                       | AWS Region                       |
+----------------------------------+----------------------------------+
| aws_account_id                   | AWS Account ID                   |
+----------------------------------+----------------------------------+
| aws_function_name                | AWS Function Name                |
+----------------------------------+----------------------------------+
| aws_function_version             | AWS Function Version             |
+----------------------------------+----------------------------------+
| aws_function_qualifier           | AWS Function Version Qualifier   |
|                                  | (version or version alias if it  |
|                                  | is not an event source mapping   |
|                                  | Lambda invocation)               |
+----------------------------------+----------------------------------+
| event_source_mappings            | AWS Function Name (if it is an   |
|                                  | event source mapping Lambda      |
|                                  | invocation)                      |
+----------------------------------+----------------------------------+
| aws_execution_env                | AWS execution environment        |
|                                  | (e.g. AWS_Lambda_python3.6)      |
+----------------------------------+----------------------------------+
| function_wrapper_version         | SignalFx function wrapper        |
|                                  | qualifier                        |
|                                  | (e.g. signalfx_lambda_0.0.2)     |
+----------------------------------+----------------------------------+
| metric_source                    | The literal value of             |
|                                  | ‘lambda_wrapper’                 |
+----------------------------------+----------------------------------+

Traces and tags sent by the Tracing wrapper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The tracing wrapper creates a span for the wrapper handler. This span has the following tags:

+----------------------------------+----------------------------------+
| Tag                              | Description                      |
+==================================+==================================+
| aws_request_id                   | AWS Request ID                   |
+----------------------------------+----------------------------------+
| lambda_arn                       | ARN of the Lambda function       |
|                                  | instance                         |
+----------------------------------+----------------------------------+
| aws_region                       | AWS Region                       |
+----------------------------------+----------------------------------+
| aws_account_id                   | AWS Account ID                   |
+----------------------------------+----------------------------------+
| aws_function_name                | AWS Function Name                |
+----------------------------------+----------------------------------+
| aws_function_version             | AWS Function Version             |
+----------------------------------+----------------------------------+
| aws_function_qualifier           | AWS Function Version Qualifier   |
|                                  | (version or version alias if it  |
|                                  | is not an event source mapping   |
|                                  | Lambda invocation)               |
+----------------------------------+----------------------------------+
| event_source_mappings            | AWS Function Name (if it is an   |
|                                  | event source mapping Lambda      |
|                                  | invocation)                      |
+----------------------------------+----------------------------------+
| aws_execution_env                | AWS execution environment        |
|                                  | (e.g. AWS_Lambda_python3.6)      |
+----------------------------------+----------------------------------+
| function_wrapper_version         | SignalFx function wrapper        |
|                                  | qualifier                        |
|                                  | (e.g. signalfx_lambda_0.0.2)     |
+----------------------------------+----------------------------------+
| component                        | The literal value of             |
|                                  | ‘python-lambda-wrapper’          |
+----------------------------------+----------------------------------+

Sending custom metric from the Lambda function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    import signalfx_lambda

    # sending application_performance metric with value 100 and dimension abc:def
    signalfx_lambda.send_gauge('application_performance', 100, {'abc':'def'})

    # sending counter metric with no dimension
    signalfx_lambda.send_counter('database_calls', 1)

Adding manual tracing to the Lambda function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Manual instrumentation can be added to trace critical parts of your handler
function.

::

    import opentracing

    tracer = opentracing.tracer

    def some_function():
        with tracer.start_active_span("span_name", tags=tags) as scope:

            # do some work

            span = scope.span
            span.set_tag("example_tag", "example_value")

More examples and usage information can be found in the Jaeger Python Tracer
`documentation <https://github.com/signalfx/jaeger-client-python>`_.

Testing it out locally
~~~~~~~~~~~~~~~~~~~~~~

Use python-lambda-local

::

    pip install python-lambda-local

::

    python-lambda-local tests/test.py tests/event.json -a 'arn:aws:lambda:us-east-1:accountId:function:functionNamePython:$LATEST'

Packaging
~~~~~~~~~

::

    python setup.py bdist_wheel --universal

License
~~~~~~~

Apache Software License v2. Copyright © 2014-2019 SignalFx
