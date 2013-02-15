import logging
from logging import CRITICAL, DEBUG, ERROR, FATAL, INFO, WARN
import re
from pprint import pformat

from django.utils.encoding import force_unicode

class DBTraceHandler(logging.Handler):
	def __init__(self):
		self.rows = []
		self.django_request = None
		super(DBTraceHandler, self).__init__()
	
	def _get_safe_dict(self, d, *extra_rxs):
		new_dict = {}
		sensitive_rxs = ['pass', 'password', 'key'] + list(extra_rxs)
		rx = re.compile(r'|'.join(re.escape(r) for r in sensitive_rxs), re.I)
		
		for k, v in d.items():
			new_dict[k] = v
			m = rx.match(k)
			if m is not None:
				new_dict[k] = '**SENSITIVE**'
	
		return new_dict
	
	def _get_request_dict_string(self, key, dict_process = None):
		d = getattr(self.django_request, key, {})
		if dict_process is not None:
			d = dict_process(d)
		safe_d = self._get_safe_dict(d)
		return force_unicode(pformat(safe_d))
	
	def _trim_meta_dict(self, d):
		new_dict = {}
		
		rx = re.compile(r'^(HTTP|CONTENT|SERVER|REMOTE).*')
		
		for k, v in d.items():
			if rx.match(k) is not None:
				new_dict[k] = v
		
		return new_dict
	
	def emit(self, record):
		if self.django_request is None:
			return
		self.rows.append(DBTraceLogGenerator(self.django_request, record).generate())
	
	def flush(self):
		from django.db import connection
		from django.db.utils import DatabaseError
		from asymmetricbase.models import TraceEntry
		
		msg = u''
		url_path = getattr(self.django_request, 'path', '')
		request_method = getattr(self.django_request, 'method', 'REQUEST')
		
		if url_path.startswith('/static'):
			# Ignore static files in DEBUG
			return
		
		entry = TraceEntry(get = url_path, method = request_method)
		
		entry.request_meta = self._get_request_dict_string('META', dict_process = self._trim_meta_dict)
		entry.request_data = self._get_request_dict_string(request_method if request_method in ['POST', 'GET'] else 'REQUEST')
		
		user = getattr(self.django_request, 'user', None)
		
		if user:
			entry.user = u'{} {}'.format(getattr(user, 'id', '0'), getattr(user, 'username', 'anonymous'))
		else:
			entry.user = '0 None'
		
		for row in self.rows:
			msg_row = u'''[{level}] {file_name}:{lineno} {msg}\n'''
			
			if row['exc_info']:
				entry.exc_info = row['exc_info']
			
			msg += msg_row.format(**row)
		
		if len(msg) > 1:
			entry.msg = msg
			try:
				# "current transaction is aborted, commands ignored until end of transaction block"
				# If there is a database error before this point, then this
				# insert may fail because we may still be inside a transaction
				# block. So, we rollback and allow the code to continue. 
				entry.save()
			except DatabaseError:
				connection._rollback()
		self.rows = []
		
class DBTraceLogGenerator(object):
	def __init__(self, request, record):
		self.request = request
		self.record = record
	
	def generate(self):
		return {
			'file_name' : self.record.pathname,
			'lineno' : self.record.lineno,
			'level' : {CRITICAL : 'C', DEBUG : 'D', ERROR : 'E', FATAL : 'F', INFO : 'I', WARN : 'W'}.get(self.record.levelno, 'I'),
			'msg' : self.record.msg,
			'exc_info' : self.record.exc_info,
		}
