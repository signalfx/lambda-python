import signalfx
import os
import time

ingestEndPoint = os.environ.get('SIGNALFX_INGEST_ENDPOINT')

sfx = signalfx.SignalFx(ingest_endpoint=ingestEndPoint)

isColdStart = True

defaultDimensions = {}

ingest = {}

def populateDefaultDimensions(dataPoints):
	for dataPoint in dataPoints:
		if 'dimensions' in dataPoint:
			dataPoint['dimensions'] = dict(dataPoint['dimensions'], **defaultDimensions)
		else:
			dataPoint['dimensions'] = defaultDimensions

# less convenience method
def send_metric(counters=[], gauges=[]):
	populateDefaultDimensions(counters)
	populateDefaultDimensions(gauges)
	ingest.send(counters=counters, gauges=gauges)

# convenience method
def send_counter(metric_name, metric_value=1, dimensions=[]):
	send_metric(counters=[{'metric': metric_name, 'value': metric_value, 'dimensions': dimensions}])

# convenience method
def send_gauge(metric_name, metric_value, dimensions=[]):
	send_metric(gauges=[{'metric': metric_name, 'value': metric_value, 'dimensions': dimensions}])

def wrapper(func):
	def call(*args, **kwargs):
		accessToken = os.environ.get('SIGNALFX_AUTH_TOKEN')
		context = args[1] # expect context to be second argument
		functionArn = context.invoked_function_arn

		# Expected format arn:aws:lambda:us-east-1:accountId:function:functionName:$LATEST
		splitted = functionArn.split(':')
		global defaultDimensions
		global ingest
		defaultDimensions = {
			'lambda_arn': functionArn,
			'aws_region': splitted[3],
			'aws_account_id': splitted[4],
		}
		if splitted[5] == 'function':
			defaultDimensions['aws_function_name'] = splitted[6]
			if len(splitted) == 8:
				defaultDimensions['aws_function_version'] = splitted[7]
			else:
				defaultDimensions['aws_function_version'] = context.function_version
		elif splitted[5] == 'event-source-mappings':
			defaultDimensions['event_source_mappings'] = splitted[6]

		ingest = sfx.ingest(accessToken)
		global isColdStart
		startCounters = [
				{
					'metric': 'aws.lambda.invocations',
					'value': 1
				},
			]
		if isColdStart:
			startCounters.append({
					'metric': 'aws.lambda.coldStarts',
					'value': 1,
					'dimensions': defaultDimensions
				})
			isColdStart = False
		send_metric(
			counters=startCounters
		)
		endCounters = [
			{
				'metric': 'aws.lambda.completed',
				'value': 1
			}
		];
		time.clock()
		try:
			result = func(*args, **kwargs)
			return result
		except:
			endCounters.append({
						'metric': 'aws.lambda.errors',
						'value': 1
					})
			raise
		finally:
			timeTaken = time.clock() * 1000 # make it millisecond from second
			send_metric(
				counters=endCounters,
				gauges=[
					{
						'metric': 'aws.lambda.duration',
						'value': timeTaken
					}
				]
			)

			# flush everything
			ingest.stop()
	return call

