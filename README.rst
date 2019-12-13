SignalFx Python Lambda Wrapper
==============================

Overview
---------

You can use this document to add a SignalFx wrapper to your AWS Lambda, specifically for Python. 

The SignalFx Python Lambda Wrapper wraps around an AWS Lambda Python function handler, which will allow metrics and traces to be sent to SignalFx.

At a high-level, to add a SignalFx python lambda wrapper, you can either package it yourself or you can use a Lambda layer containing the wrapper, and then attach the layer to a Lambda function.

~~~~~

Step 1: Add the Lambda wrapper in AWS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To add the SignalFx wrapper, you have the following options:
   * Use the wrapper as a regular dependency, and then create a Lambda function based on your artifact containing both code and dependencies.
   * In AWS, create a Lambda function, then attach a SignalFx-hosted layer with a wrapper.
   * In AWS, create a Lambda function, then create and attach a layer based on a SignalFx SAM (Serverless Application Model) template.

Review the appropriate option below.

**Option 1: Install the wrapper**

To begin, run the following installation script in your command line:

.. code::

    pip install signalfx_lambda

~~~~~

**Option 2: Create a Lambda function, then attach the SignalFx-hosted layer**

In this option, you will use a layer created and hosted by SignalFx.

1. To verify compatibility, review the list of supported regions. See [Lambda Layer Versions](https://github.com/signalfx/lambda-layer-versions/blob/master/python/PYTHON.md).
2. Access your AWS console. 
3. In the landing page, under **Compute**, click **Lambda**.
4. Click **Create function** to create a layer with SignalFx's capabilities.
5. Click **Author from scratch**.
6. In **Function name**, enter a descriptive name for the wrapper. 
7. In **Runtime**, select the desired language.
8. Click **Create function**. 
9. Click on **Layers**, then add a layer.
10. Mark **Provide a layer version**.
11. Enter an ARN number. 
    * To locate the ARN number, see [Lambda Layer Versions](https://github.com/signalfx/lambda-layer-versions/blob/master/python/PYTHON.md).

~~~~~

**Option 3: Create a Lambda function, then create and attach a layer based on a SignalFx template**

In this option, you will create and deploy a copy of a layer based on a SignalFx template.

Here, the user will chose a template and then deploy the copy into their own account:

1. Access your AWS console. 
2. In the landing page, under **Compute**, click **Lambda**.
3. Click **Create function** to create a layer with SignalFx's capabilities.
4. Click **Browse serverless app repository**.
5. Click **Public applications**.
6. In the search field, enter and select **signalfx-lambda-python-wrapper**.
7. Review the template, permissions, licenses, and then click **Deploy**.
    * A copy of the layer will now be deployed in your account.
8. Return to the previous screen to add a layer to the function, select from list of runtime compatible layers, and then select the name of the copy.  


~~~~~

Step 2: Configure the SignalFx realm
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, this function wrapper will send data to the ``us0`` realm.
If you are not in this realm, and you are not using the gateway, you will need to use the realm specific SignalFx subdomain: {REALM}.signalfx.com (for example, us1.signalfx.com).

Make sure to adjust the variables you set (any of ``SIGNALFX_ENDPOINT_URL``, ``SIGNALFX_TRACING_URL``, ``SIGNALFX_METRICS_URL``, ``SIGNALFX_INGEST_ENDPOINT``) to the correct realm ingest endpoint (``https://ingest.{REALM}.signalfx.com``).

To locate your realm:

1. In SignalFx, in the top, right corner, click your profile icon.
2. Click **My Profile**.
3. Next to **Organizations**, review the listed realm.

~~~~~

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

~~~~~

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


~~~~~

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

~~~~~

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

~~~~~

Step 7: Send custom metrics from the Lambda function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    import signalfx_lambda

    # sending application_performance metric with value 100 and dimension abc:def
    signalfx_lambda.send_gauge('application_performance', 100, {'abc':'def'})

    # sending counter metric with no dimension
    signalfx_lambda.send_counter('database_calls', 1)

~~~~~

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

~~~~~

Step 9: Test configurations locally 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use python-lambda-local

.. code::

    pip install python-lambda-local

.. code::

    python-lambda-local tests/test.py tests/event.json -a 'arn:aws:lambda:us-east-1:accountId:function:functionNamePython:$LATEST'

~~~~~

Packaging
~~~~~~~~~

.. code::

    python setup.py bdist_wheel --universal

~~~~~

License
~~~~~~~

Apache Software License v2. Copyright © 2014-2019 SignalFx
