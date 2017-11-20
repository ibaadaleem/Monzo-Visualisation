from django import forms

class uploadFileForm(forms.Form):
	uploadCsvFile = forms.FileField()
   
class checkbox(forms.Form):
	check = forms.BooleanField()