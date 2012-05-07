import logging

from django.utils.functional import lazy

class NullHandler(logging.Handler):
	def emit(self, record):
		pass

def init_logger():
	from django.conf import settings
	logger_name = getattr(settings, 'ASYM_LOGGER', 'asymm_logger')
	
	_logger = logging.getLogger(logger_name)
	_logger.addHandler(NullHandler())
	return _logger

logger = lazy(init_logger, logging.Logger)
