import signalfx
import os
import datetime

from . import metrics
from . import tracing
from .version import name, version


def emits_metrics(*args, **kwargs):
    return metrics.wrapper(*args, **kwargs)


def is_traced(*args, **kwargs):
    return tracing.wrapper(*args, **kwargs)


# backwards compatibility
wrapper = emits_metrics


# less convenient method
def send_metric(counters=[], gauges=[]):
    metrics.send_metric(counters, gauges)


# convenience method
def send_counter(metric_name, metric_value=1, dimensions={}):
    metrics.send_counter(metric_name, metric_value, dimensions)


# convenience method
def send_gauge(metric_name, metric_value, dimensions={}):
    metrics.send_gauge(metric_name, metric_value, dimensions)

