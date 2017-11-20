from django.contrib import admin

from visualisation.models import MonzoCsvExport

class MonzoAdmin(admin.ModelAdmin):
	fieldsets = [
		('Monzo Id', {'fields': ['monzo_id']}),
		('Created', {'fields': ['created']}),
		('Amount',  {'fields': ['amount']}),
		('Currency', {'fields': ['currency']}),
		('Local Amount', {'fields': ['local_amount']}),
		('Local Currency', {'fields': ['local_currency']}),
		('Category', {'fields': ['category']}),
		('Emoji', {'fields': ['emoji']}),
		('Description', {'fields': ['description']}),
		('Address', {'fields': ['address']}),
		('Notes', {'fields': ['notes']}),
		('Receipt', {'fields': ['receipt']}),
	]
	list_display = ('created','amount','description')
	list_filter = ['created']
	ordering = ['-created']


admin.site.register(MonzoCsvExport, MonzoAdmin)