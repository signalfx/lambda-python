SignalFx Python Lambda Wrapper
===============================

Overview
---------

You can use this document to add a SignalFx wrapper to your AWS Lambda for Python. 

The SignalFx Python Lambda Wrapper wraps around an AWS Lambda Python function handler, which allows metrics and traces to be sent to SignalFx.

At a high-level, to add a SignalFx Python Lambda wrapper, you can package the code yourself, or you can use a Lambda layer containing the wrapper and then attach the layer to a Lambda function.

To learn more about Lambda Layers, please visit the AWS documentation site and see [AWS Lambda Layers](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html).

Step 1: Add the Lambda wrapper in AWS
-----------------------------------------

To add the SignalFx wrapper, you have the following options:
   
   * Option 1: In AWS, create a Lambda function, then attach a SignalFx-hosted layer with a wrapper.
      * If you are already using Lambda layers, then SignalFx recommends that you follow this option. 
      * In this option, you will use a Lambda layer created and hosted by SignalFx.
   * Option 2: In AWS, create a Lambda function, then create and attach a layer based on a SignalFx SAM (Serverless Application Model) template.
      * If you are already using Lambda layers, then SignalFx also recommends that you follow this option. 
      * In this option, you will choose a SignalFx template, and then deploy a copy of the layer.
   * Option 3: Use the wrapper as a regular dependency, and then create a Lambda function based on your artifact containing both code and dependencies.   
      
Option 1: Create a Lambda function, then attach the SignalFx-hosted Lambda layer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In this option, you will use a Lambda layer created and hosted by SignalFx.

1. To verify compatibility, review the list of supported regions. See [Lambda Layer Versions](https://github.com/signalfx/lambda-layer-versions/blob/master/python/PYTHON.md).
2. Open your AWS console. 
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

Option 2: Create a Lambda function, then create and attach a layer based on a SignalFx template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In this option, you will choose a SignalFx template, and then deploy a copy of the layer.

1. Open your AWS console. 
2. In the landing page, under **Compute**, click **Lambda**.
3. Click **Create function** to create a layer with SignalFx's capabilities.
4. Click **Browse serverless app repository**.
5. Click **Public applications**.
6. In the search field, enter and select **signalfx-lambda-python-wrapper**.
7. Review the template, permissions, licenses, and then click **Deploy**.
    * A copy of the layer will now be deployed into your account.
8. Return to the previous screen to add a layer to the function, select from list of runtime compatible layers, and then select the name of the copy. 

Option 3: Install the wrapper package with pip
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run the following installation script in your command line:

.. code::

    pip install signalfx_lambda


Step 2: Locate and set the ingest endpoint
-------------------------------------------
By default, this function wrapper will send data to the us0 realm. As a result, if you are not in us0 realm and you want to use the ingest endpoint directly, then you must explicitly set your realm. To set your realm, use a subdomain, such as ingest.us1.signalfx.com or ingest.eu0.signalfx.com.

To locate your realm:

1. Open SignalFx and in the top, right corner, click your profile icon.
2. Click **My Profile**.
3. Next to **Organizations**, review the listed realm.


Step 3: Set environment variables
----------------------------------

1. Set SIGNALFX_ACCESS_TOKEN with your correct access token. Review the following example. 

.. code:: bash

    SIGNALFX_ACCESS_TOKEN=access token

2. If you use Smart Gateway, or want to ingest directly from a realm other than us0, then you must set at least one endpoint variable. (For environment variables, SignalFx defaults to the us0 realm. As a result, if you are not in the us0 realm, you may need to set your environment variables.) There are two options: 


**Option 1**

Set ``SIGNALFX_TRACING_URL`` and ``SIGNALFX_METRICS_URL`` to configure where traces and metrics will be sent to. The following example will send traces to the gateway and metrics directly to the ingest endpoint. 

.. code:: bash

    SIGNALFX_METRICS_URL=https://ingest.us0.signalfx.com
    SIGNALFX_TRACING_URL=http://<my_gateway>:8080/v1/trace
    
To learn more, see: 
  * [Deploying the SignalFx Smart Gateway](https://docs.signalfx.com/en/latest/apm/apm-deployment/smart-gateway.html)
        
    
2. (Optional) Set additional environment variables. Review the following examples.  

.. code:: bash

    SIGNALFX_SEND_TIMEOUT=timeout in seconds for sending datapoint [ default: 0.3 ]
    SIGNALFX_TRACING_URL=tracing endpoint [ default: https://ingest.signalfx.com/v1/trace ]
    

Step 4: Wrap a function
--------------------------

There are two wrappers provided.

The decorators can be used individually or together.

1. For metrics, decorate your handler with **@signalfx_lambda.emits_metrics**. Review the following example. 

.. code:: python

    import signalfx_lambda

    @signalfx_lambda.emits_metrics()
    def handler(event, context):
        # your code

2. For tracing, decorate your handler with **@signalfx_lambda.is_traced**. Review the following example. 

.. code:: python

    import signalfx_lambda

    @signalfx_lambda.is_traced()
    def handler(event, context):
        # your code

3. Optionally, you can tell the wrapper to not auto-create a span but still initialize tracing for manual usage.

This is useful when processing SQS messages and you want each message to tie to the trace from producer that emitted the message.

.. code:: python

    import signalfx_lambda

    @signalfx_lambda.is_traced(with_span=False)
    def handler(event, context):
        for record in event.get('Records', []):
            with signalfx_lambda.tracing.create_span(record, context):
                # your code to process record


Step 5: Send custom metrics from a Lambda function
-------------------------------------------------------

1. To send custom metrics from a Lambda function, include the following code in your function:

.. code:: python

    import signalfx_lambda

    # sending application_performance metric with value 100 and dimension abc:def
    signalfx_lambda.send_gauge('application_performance', 100, {'abc':'def'})

    # sending counter metric with no dimension
    signalfx_lambda.send_counter('database_calls', 1)


Step 6: Add tracing to the Lambda function
-------------------------------------------

1. To trace critical parts of your handler function, include the following code in your function:

.. code:: python

    import opentracing
    
    @signalfx_lambda.is_traced()
    def some_function():
        # opentracing.tracer must be referenced from within
        # a function decorated with the is_traced() decorator
        # or it'll not reference the correct tracer initialized
        # for the lambda function.
        tracer = opentracing.tracer
        with tracer.start_active_span("span_name", tags=tags) as scope:

            # do some work

            span = scope.span
            span.set_tag("example_tag", "example_value")

To review more examples and usage details, see [Jaeger Python Tracer](https://github.com/signalfx/jaeger-client-python>).

Propagating trace context to outgoing requests or lambda response
------------------------------------------------------------------

The library ships a helper function to inject tracing context headers into a dictionary like object.
The function accepts two arguments. First argument must be a dictionary like object that the trace context is injected into.
The second argument is optional and must be a OpenTracing span context. If one is not provided, the function uses the currently
active span. Example:

.. code:: python

    import signalfx_lambda

    @signalfx_lambda.is_traced()
    def handler(event, context):
        headers = {}

        # inject trace context into the headers dictionary
        signalfx_lambda.tracing.inject(headers)
        
        # Or inject traces from a specific span context instead of the 
        # one from the active scope.
        # signalfx_lambda.tracing.inject(headers, span.context)

        request = urllib.request.Request('http://some-service', headers=headers)
        response = urllib.request.urlopen(request)

        # your code


Additional information 
------------------------

Metrics and dimensions sent by the metrics wrapper
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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


Tags sent by the tracing wrapper 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The tracing wrapper creates a span for the wrapper handler. This span contains the following tags:

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



Auto-instrumentation packages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The SignalFx Python Lambda Wrapper can automatically instrument supported packages. All you need to do is to install instrumentations you need in addition to `signalfx_lambda`. Below is a list of all instrumentation packages supported:

+--------------------------+------------------------------------------------------------------------------------------------------+
| Library/Framework        | Instrumentation Package                                                                              |
+==========================+======================================================================================================+
| celery                   | ``https://github.com/signalfx/python-celery/tarball/0.0.1post0#egg=celery-opentracing``              |
+--------------------------+------------------------------------------------------------------------------------------------------+
| django                   | ``https://github.com/signalfx/python-django/tarball/0.1.18post1#egg=django-opentracing``             |
+--------------------------+------------------------------------------------------------------------------------------------------+
| elasticsearch            | ``https://github.com/signalfx/python-elasticsearch/tarball/0.1.4post#egg=elasticsearch-opentracing`` |
+--------------------------+------------------------------------------------------------------------------------------------------+
| flask                    | ``https://github.com/signalfx/python-flask/tarball/1.1.0post1#egg=flask_opentracing``                |
+--------------------------+------------------------------------------------------------------------------------------------------+
| psycopg                  | ``https://github.com/signalfx/python-dbapi/tarball/v0.0.5post1#egg=dbapi-opentracing``               |
+--------------------------+------------------------------------------------------------------------------------------------------+
| pymongo                  | ``https://github.com/signalfx/python-pymongo/tarball/v0.0.3post1#egg=pymongo-opentracing``           |
+--------------------------+------------------------------------------------------------------------------------------------------+
| pymysql                  | ``https://github.com/signalfx/python-dbapi/tarball/v0.0.5post1#egg=dbapi-opentracing``               |
+--------------------------+------------------------------------------------------------------------------------------------------+
| redis                    | ``https://github.com/signalfx/python-redis/tarball/v1.0.0post1#egg=redis-opentracing``               |
+--------------------------+------------------------------------------------------------------------------------------------------+
| requests                 | ``https://github.com/signalfx/python-requests/archive/v0.2.0post1.zip#egg=requests-opentracing``     |
+--------------------------+------------------------------------------------------------------------------------------------------+
| tornado                  | ``https://github.com/signalfx/python-tornado/archive/1.0.1post1.zip#egg=tornado_opentracing``        |
+--------------------------+------------------------------------------------------------------------------------------------------+

For example, if your Lambda function uses ``requests``, then you should add ``https://github.com/signalfx/python-requests/archive/v0.2.0post1.zip#egg=requests-opentracing`` to your ``requirements.txt`` file or make sure it gets installed into the Lambda environment.

Test locally 
^^^^^^^^^^^^^^^^^
If you would like to test changes to a wrapper, run the following commands in your command line: 


.. code::

    pip install python-lambda-local

.. code::

    python-lambda-local tests/test.py tests/event.json -a 'arn:aws:lambda:us-east-1:accountId:function:functionNamePython:$LATEST'


Publish a new version
^^^^^^^^^^^^^^^^^^^^^^^
If you would like to publish a new version, run the following command in your command line to install a new Python package (build a wheel): 

.. code::

    python setup.py bdist_wheel --universal
    
License
^^^^^^^^
Apache Software License v2. Copyright © 2014-2020 Splunk, Inc.

