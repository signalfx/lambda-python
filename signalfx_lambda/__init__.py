import signalfx
import os
import datetime

from . import metrics
from . import tracing
from .version import name, version

def wrapper(*args, **kwargs):
    return metrics.wrapper(*args, **kwargs)

def tracing_wrapper(*args, **kwargs):
    return tracing.wrapper(*args, **kwargs)
