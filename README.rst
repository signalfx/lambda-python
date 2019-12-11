SignalFx Python Lambda Wrapper
==============================

Overview
---------

You can use this document to add a SignalFx wrapper to AWS Lamba Layers, specifically for Python. 

You can use the SignalFx Python Lambda Wrapper to wrap around an AWS Lambda Python function handler, which will allow metrics and traces to be sent to SignalFx.


Before you begin
~~~~~~~~~~~~~~~~~

- To review a list of supported regions and versions, see [Lamba Layer Versions](https://github.com/signalfx/lambda-layer-versions/blob/master/python/PYTHON.md).

- 


Later 

Similarly, to skip the installation step, you can attach the resulting layer to your Lambda function. To learn more, see 

The installation step can be replaced by attaching the resulting layer to your Lambda function.

For more information on attaching a layer to a Lambda see AWS documentation.



To report metrics and traces to SignalFx, see the extract below or follow the wrapper's README. The installation step can be replaced by attaching the resulting layer to your Lambda function.




Step 1: Add the Lamba wrapper in AWS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::  These instructions require that you access your AWS account. If you prefer, you can simply run the installation script in your command line. Afterwards, you can skip to Step 2. 

.. code:: pip install signalfx_lambda 


To add a wrapper, you can create your own wrapper or use a wrapper generated from SignalFx. Review the correct option below. 


*Option 1: Create and add your own wrapper 

1. Access your AWS console. 
2. In the landing page, under **Compute**, click **Lamba**.
3. Click **Create function** to create a layer with SignalFx's capabilities.
4. Click **Author from scratch**.
5. In **Function name**, enter a descriptive name for the wrapper. 
6. In **Runtime**, select the desired language.
7. Click **Create function**. 
8. Click on **Layers**, then add a layer.
9. Mark **Provide a layer version**.
10. Enter an ARN number. 
    * To locate the ARN number, see [Lamba Layer Versions](https://github.com/signalfx/lambda-layer-versions/blob/master/python/PYTHON.md).


**Option 2: Add a wrapper from a SignalFx template 

Here, the user will chose a template and then deploy the copy into their own account:

1. Access your AWS console. 
2. In the landing page, under **Compute**, click **Lamba**.
3. Click **Create function** to create a layer with SignalFx's capabilities.
4. Click **Browse serverless app repository**.
5. Click **Public applications**.
6. In the search field, enter **the official name**. 
7. Review the template, permissions, licenses, and then click **Deploy**. 
    * A copy of the layer will now be deployed in your account.
8. Return to the previous screen to add a layer to the function, select from list of runtime compatible layers, and then select the name of the copy.  


Step 2: Configure the ingest endpoint
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, this function wrapper will send data to the ``us0`` realm. 

If you are not in this realm, you will need to set the ``SIGNALFX_INGEST_ENDPOINT`` environment variable to the correct realm ingest endpoint (``https://ingest.{REALM}.signalfx.com``).

To locate your realm:

1. In SignalFx, in the top, right corner, click your profile icon.
2. Click **My Profile**.
3. Next to **Organizations**, review the listed realm.


Step 3: Environment Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Note: the environment variables ``SIGNALFX_INGEST_ENDPOINT`` and ``SIGNALFX_AUTH_TOKEN`` are being deprecated and will not be supported in future releases.**

.. code:: bash

    SIGNALFX_ACCESS_TOKEN=access token

    # endpoint for both metrics and tracer. Overridden by SIGNALFX_METRICS_URL
    # and SIGNALFX_TRACING_URL if set
    SIGNALFX_ENDPOINT_URL=http://<my_gateway>:8080

    # optional metrics and tracing configuration

    SIGNALFX_METRICS_URL=ingest endpoint [ default: https://pops.signalfx.com ]
    SIGNALFX_SEND_TIMEOUT=timeout in seconds for sending datapoint [ default: 0.3 ]

    SIGNALFX_TRACING_URL=tracing endpoint [ default: https://ingest.signalfx.com/v1/trace ]

``SIGNALFX_ENDPOINT_URL`` can be used to configure a common endpoint for metrics and
traces, as is the case when forwarding with the Smart Gateway. The path ``/v1/trace``
will automatically be added to the endpoint for traces.

If either ``SIGNALFX_TRACING_URL`` or ``SIGNALFX_METRICS_URL`` are set, they will take
precendence over ``SIGNALFX_ENDPOINT_URL`` for their respective components.

For example, if only ``SIGNALFX_ENDPOINT_URL`` is set:

.. code:: bash

    SIGNALFX_ENDPOINT_URL=http://<my_gateway>:8080

Both metrics and traces will be sent to the gateway address.

If ``SIGNALFX_ENDPOINT_URL`` and ``SIGNALFX_METRICS_URL`` are set:

.. code:: bash

    SIGNALFX_METRICS_URL=https://pops.signalfx.com
    SIGNALFX_ENDPOINT_URL=http://<my_gateway>:8080

Traces will be sent to the gateway and metrics will go through POPS.

Step 4: Wrap a function
~~~~~~~~~~~~~~~~~~~~~~~~~`

There are two wrappers provided.

The decorators can be used individually or together.

1. For metrics, decorate your handler with @signalfx_lambda.emits_metrics

.. code:: python

    import signalfx_lambda

    @signalfx_lambda.emits_metrics
    def handler(event, context):
        # your code

2. For tracing, use the @signalfx_lambda.is_traced decorator

.. code:: python

    import signalfx_lambda

    @signalfx_lambda.is_traced
    def handler(event, context):
        # your code


Step 5: Review the metrics and dimensions sent by the metrics wrapper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

Step 6: Review the traces and tags sent by the Tracing wrapper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

Step 7: Send custom metrics from the Lambda function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    import signalfx_lambda

    # sending application_performance metric with value 100 and dimension abc:def
    signalfx_lambda.send_gauge('application_performance', 100, {'abc':'def'})

    # sending counter metric with no dimension
    signalfx_lambda.send_counter('database_calls', 1)

Step 8: Add manual tracing to the Lambda function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Manual instrumentation can be added to trace critical parts of your handler
function.

.. code:: python

    import opentracing

    tracer = opentracing.tracer

    def some_function():
        with tracer.start_active_span("span_name", tags=tags) as scope:

            # do some work

            span = scope.span
            span.set_tag("example_tag", "example_value")

More examples and usage information can be found in the Jaeger Python Tracer
`documentation <https://github.com/signalfx/jaeger-client-python>`_.

Step 9: Test configurations locally 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use python-lambda-local

.. code::

    pip install python-lambda-local

.. code::

    python-lambda-local tests/test.py tests/event.json -a 'arn:aws:lambda:us-east-1:accountId:function:functionNamePython:$LATEST'

Packaging
~~~~~~~~~

.. code::

    python setup.py bdist_wheel --universal

License
~~~~~~~

Apache Software License v2. Copyright © 2014-2019 SignalFx
