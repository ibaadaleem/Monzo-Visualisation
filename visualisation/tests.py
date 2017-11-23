from django.test import TestCase
from django.urls import reverse

from .models import MonzoCsvExport

class MonzoHomeView(TestCase):
	def test_model_is_empty(self):
		'''
		If no records exist in the model then make sure screen doesn't error
		'''
		response = self.client.get(reverse('visualisation:home'))
		self.assertEqual(response.status_code,200)
		
class MonzoVisualsView(TestCase):
	def test_model_is_empty(self):
		'''
		If no records exist in the model then make sure screen doesn't error
		'''
		response = self.client.get(reverse('visualisation:visuals'))
		self.assertEqual(response.status_code,200)

class MonzoAnalyticsView(TestCase):
	def test_model_is_empty(self):
		'''
		If no records exist in the model then make sure screen doesn't error
		'''
		response = self.client.get(reverse('visualisation:analytics'))
		self.assertEqual(response.status_code,200)
		
class MonzoUploadView(TestCase):
	def test_model_is_empty(self):
		'''
		If no records exist in the model then make sure screen doesn't error
		'''
		response = self.client.get(reverse('visualisation:upload'))
		self.assertEqual(response.status_code,200)
		
class MonzoCsvView(TestCase):
	def test_model_is_empty(self):
		'''
		If no records exist in the model then make sure screen doesn't error
		'''
		response = self.client.get(reverse('visualisation:csv_data'))
		self.assertEqual(response.status_code,200)