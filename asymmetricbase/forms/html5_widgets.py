# -*- coding: utf-8 -*-
#    Asymmetric Base Framework - A collection of utilities for django frameworks
#    Copyright (C) 2013  Asymmetric Ventures Inc.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; version 2 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from django.forms import widgets
from django.conf import settings

HTML5_WIDGETS = getattr(settings, 'ASYM_HTML5_WIDGETS',  {})

if HTML5_WIDGETS.get('time', False):
	widgets.TimeInput.input_type = 'time'
	
if HTML5_WIDGETS.get('date', False):
	widgets.DateInput.input_type = 'date'
	
if HTML5_WIDGETS.get('datetime', False):
	widgets.DateTimeInput.input_type = 'datetime'
