from django.db import models


class MonzoCsvExport(models.Model):
	monzo_id = models.CharField(max_length=200)
	created = models.DateTimeField()
	amount = models.FloatField()
	currency = models.CharField(max_length=3)
	local_amount = models.FloatField()
	local_currency = models.CharField(max_length=3)
	category = models.CharField(max_length=20)
	emoji = models.CharField(max_length=20)
	description = models.CharField(max_length=200)
	address = models.CharField(max_length=200)
	notes = models.CharField(max_length=200)
	receipt = models.CharField(max_length=200)
