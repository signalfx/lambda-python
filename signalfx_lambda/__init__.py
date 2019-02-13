import signalfx
import os
import datetime

from . import metrics
from .version import name, version

def wrapper(*args, **kwargs):
    return metrics.wrapper(*args, **kwargs)
