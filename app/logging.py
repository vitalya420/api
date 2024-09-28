import os
import sys
from datetime import datetime, UTC

log_dir = os.path.join(os.getcwd(), 'logs')
os.makedirs(log_dir, exist_ok=True)

timestamp = datetime.now(UTC).strftime('%Y%m%d_%H%M%S')
log_filename = os.path.join(log_dir, f'app_{timestamp}.log')

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        'sanic.root': {'level': 'INFO', 'handlers': ['console', 'file']},
        'sanic.error': {
            'level': 'INFO',
            'handlers': ['error_console', 'file'],
            'propagate': True,
            'qualname': 'sanic.error'
        },
        'sanic.access': {
            'level': 'INFO',
            'handlers': ['access_console', 'file'],
            'propagate': True,
            'qualname': 'sanic.access'
        },
        'sanic.server': {
            'level': 'INFO',
            'handlers': ['console', 'file'],
            'propagate': True,
            'qualname': 'sanic.server'
        },
        'sanic.websockets': {
            'level': 'INFO',
            'handlers': ['console', 'file'],
            'propagate': True,
            'qualname': 'sanic.websockets'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'generic',
            'stream': sys.stdout
        },
        'error_console': {
            'class': 'logging.StreamHandler',
            'formatter': 'generic',
            'stream': sys.stderr
        },
        'access_console': {
            'class': 'logging.StreamHandler',
            'formatter': 'access',
            'stream': sys.stdout
        },
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'generic',
            'filename': log_filename,
            'mode': 'a',
        }
    },
    'formatters': {
        'generic': {'class': 'sanic.logging.formatter.AutoFormatter'},
        'access': {'class': 'sanic.logging.formatter.AutoAccessFormatter'}
    }
}