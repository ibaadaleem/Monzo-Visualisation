from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils import timezone
from django.urls import reverse
from django.views import generic
from django.db.models import Max

from .models import MonzoCsvExport
from .forms import uploadFileForm

import os
import pandas as pd
from dateutil import relativedelta
from datetime import datetime, timedelta
from colour import Color

import plotly.offline as opy
import plotly.graph_objs as go

values_dict = {'sincemonday':{'dates':datetime.now().date() - timezone.timedelta(days=datetime.now().weekday()),
							  'average':'Average since Monday',
							  'start':'Since Monday',
							  'color':'#c94414'},
			   '7days':{'dates':timezone.now() - timezone.timedelta(days=7),
						'average':'Average over 7 days',
						'start':'Last 7 days',
						'color':'#fff263'},
			   'startofmonth':{'dates':datetime.now().replace(day=1,hour=0,minute=0,second=0),
							   'average':'Average since start of month',
							   'start':'Since start of month',
							   'color':'#44c10f'},
			   '30days':{'dates':timezone.now() - timezone.timedelta(days=30),
						 'average':'Average over 30 days',
						 'start':'Last 30 days',
						 'color':'#1292e2'}
			  }
			  
def set_transactions_df():
	global transactions
	transactions = pd.DataFrame()
	if MonzoCsvExport.objects.exists():
		df = pd.DataFrame(list(MonzoCsvExport.objects.all().values()))
		
		#Remove top ups and bank transfers from my own account
		transactions = df[~(df['category']=='general') | ((df['description'].str.startswith('Payment')) & (df['description']!='Payment from Aleem Ibaad-Ullah'))]#Change name as appropriate
		transactions['amount'] = transactions['amount']*-1
		
	return transactions
	
def set_dicts():
	global colour_dict, category_dict
	colour_dict, category_dict = {}, {}
	
	if MonzoCsvExport.objects.exists():
		colour_list = list(Color('Red').range_to(Color('Purple'),transactions['category'].nunique()))
		for i in range(0, len(transactions['category'].unique())):
			colour_dict[transactions['category'].unique()[i]] = str(colour_list[i])
			
		category_dict['total'] = 'Total'
		for category in transactions['category'].unique():
			name = category
			name = name.replace('_',' ')
			name = name.title()
			category_dict[category] = name
	
	return colour_dict, category_dict
	
def firstpage(request):

	return redirect('visualisation:home')

def index(request):

	return render(request, 'visualisation/index.html')

class Visuals(generic.TemplateView):
	template_name = 'visualisation/visuals.html'
		
	def get_context_data(self, **kwargs):
		context = super(Visuals, self).get_context_data(**kwargs)

		if MonzoCsvExport.objects.exists():
		
			#Plot Bar Chart - Category against Sum(Amount)
			labels_dict = values_dict
			trace = []
			if self.request.GET.get('groupedData'):
				for key in values_dict:
					if key in self.request.GET.keys():
						labels_dict[key]['is_checked'] = 'checked'
					
						data = transactions[transactions['created']>=values_dict[key]['dates']][['category','amount']].groupby('category',as_index=False).sum()
						data = pd.concat([pd.DataFrame({'category':'total','amount':data['amount'].sum()},index=[0]), data]).reset_index(drop=True)
						
						trace.append(go.Bar(x=data['category'].map(category_dict),
											y=data['amount'],
											name=values_dict[key]['start'],
											marker=dict(color=values_dict[key]['color'])))
					else:
						labels_dict[key]['is_checked'] = ''
			else:
				for key in values_dict:
					labels_dict[key]['is_checked'] = 'checked'
					
					data = transactions[transactions['created']>=values_dict[key]['dates']][['category','amount']].groupby('category',as_index=False).sum()
					data = pd.concat([pd.DataFrame({'category':'total','amount':data['amount'].sum()},index=[0]), data]).reset_index(drop=True)
					
					trace.append(go.Bar(x=data['category'].map(category_dict),
										y=data['amount'],
										name=values_dict[key]['start'],
										marker=dict(color=values_dict[key]['color'])))			
					
			data=go.Data(trace)
			layout=go.Layout(title="Grouped Data", 
							 xaxis={'title':'Category'}, 
							 yaxis={'title':'Amount'})
			figure=go.Figure(data=data,layout=layout)
			div = opy.plot(figure, auto_open=False, output_type='div')

			context['barChart'] = div
			context['labels_dict'] = labels_dict
			
			#Plot Scatter Plot - Date against Amount
			trace = []
			if self.request.GET.get('scatterPlot'):
				if not self.request.GET.keys() or self.request.GET['toDate'] == '':
					toDate = datetime.now()
				else:
					toDate = datetime.strptime(self.request.GET['toDate'],'%Y-%m-%d')
				if not self.request.GET.keys() or self.request.GET['fromDate'] == '':
					fromDate = toDate - timezone.timedelta(days=7)
				else:
					fromDate = datetime.strptime(self.request.GET['fromDate'],'%Y-%m-%d')
			else:
				toDate = datetime.now()
				fromDate = toDate - timezone.timedelta(days=7)
				
			date_dict = {'toDate':datetime.strftime(toDate.date(),'%Y-%m-%d'),
			             'fromDate':datetime.strftime(fromDate.date(),'%Y-%m-%d')}
			context['date_dict'] = date_dict

			for category in transactions['category'].unique():
				data = transactions[(transactions['created']>=fromDate) 
								  & (transactions['created']<=toDate) 
								  & (transactions['category']==category)]
								  
				trace.append(go.Scatter(x=data['created'],
										y=data['amount'],
										mode='markers',
										name=category_dict[category],
										marker=dict(size=6,color=data['category'].map(colour_dict)),
										text=data['description'],
										hoverinfo=('text+y')))
				
			data=go.Data(trace)
			layout=go.Layout(title="Scatter Plot", 
							 xaxis=dict(title='Created',showgrid=True,zeroline=True), 
							 yaxis=dict(title='Amount',showgrid=True,zeroline=True),
							 hovermode='closest')
			figure=go.Figure(data=data,layout=layout)
			div = opy.plot(figure, auto_open=False, output_type='div')

			context['scatterPlot'] = div
		
		return context

def analytics(request):
	if MonzoCsvExport.objects.exists():			
		week_start_date = datetime.now().replace(hour=0,minute=0,second=0) - timedelta(days=datetime.now().weekday()) + timedelta(days=7)
		week_date_list = []		
		for i in range(0,8):
			start_date = week_start_date - timedelta(days=(7*(i+1)))
			end_date = week_start_date - timedelta(days=(7*i))
			label = datetime.strftime(start_date,'%d %b') + ' to ' + datetime.strftime(end_date,'%d %b')
			week_date_list.append([start_date, end_date, label])

		month_start_date = (timezone.now() + timezone.timedelta(days=16)).replace(day=1,hour=0,minute=0,second=0)
		month_date_list = []
		for i in range(0, 5):
			start_date = add_month(month_start_date,i+1)
			end_date = add_month(month_start_date,i)
			label = datetime.strftime(start_date, '%B')
			month_date_list.append([start_date, end_date, label])
			
		week_data = create_analytic_df(week_date_list)
		week_data_html = week_data.to_html()
			
		month_data = create_analytic_df(month_date_list)
		month_data_html = month_data.to_html()
		
		return render(request, 'visualisation/analytics.html', {'week_data_html':week_data_html,'month_data_html':month_data_html})

	return render(request, 'visualisation/analytics.html')
	
def create_analytic_df(date_list):
	df = pd.DataFrame(index=transactions['category'].unique())
	
	for i in range(0,len(date_list)):
		df[date_list[i][2]] = transactions[(transactions['created']<=date_list[i][1]) 
		                                 & (transactions['created']>date_list[i][0])].groupby('category').sum()['amount']
		
	df.loc['total'] = df.sum()
	df = df.fillna(0).transpose()	
	df = df.rename(columns=category_dict)
	
	return df
	
def add_month(month_start_date,add_value):
	next_month_start_date = month_start_date - relativedelta.relativedelta(months=add_value)
	
	return next_month_start_date	
	
def upload(request):
	if (request.method == 'POST'):
		if(request.FILES):
			upload_csv_file(request)
		elif(request.POST.get('deleteRecords')):
			delete_all_records()

		#Update global variables
		transactions = set_transactions_df()
		colour_dict, category_dict = set_dicts()
	
		return HttpResponseRedirect(reverse('visualisation:upload'))

	return render(request, 'visualisation/upload.html')

def csv_data(request):
	data = MonzoCsvExport.objects.all().order_by('-created')

	return render(request, 'visualisation/csv_data.html', {'data':data})

def insert_into_database(data):
	for index,row in data.iterrows():
		
		monzo_csv = MonzoCsvExport()

		monzo_csv.monzo_id = row['id']
		monzo_csv.created = row['created']
		monzo_csv.amount = row['amount']
		monzo_csv.currency = row['currency']
		monzo_csv.local_amount = row['local_amount']
		monzo_csv.local_currency = row['local_currency']
		monzo_csv.category = row['category']
		monzo_csv.description = row['description']
		monzo_csv.address = row['address']
		monzo_csv.notes = row['notes']
		monzo_csv.receipt = row['receipt']

		monzo_csv.save()		
		
def upload_csv_file(request):
	form = uploadFileForm(request.POST, request.FILES)

	if form.is_valid():
		if str(request.FILES['uploadCsvFile']).endswith('.csv'):		
			data = pd.read_csv(request.FILES['uploadCsvFile'],parse_dates=True)
			data['created'] = data['created'].apply(lambda x: datetime.strptime(x[:16],'%Y-%m-%d %H:%M')) #Monzo data contains milliseconds that don't play well with pandas, so strip them off			
			
			insert_into_database(data)
		
		return render(request, 'visualisation/upload.html')
	else:
		return render(request, 'visualisation/upload.html')
				
def auto_upload_csv_file():	
	if MonzoCsvExport.objects.exists():
		most_recent_record_date = MonzoCsvExport.objects.all().aggregate(Max('created'))['created__max']
		
		dir = ''
		
		#Work Computer path
		if os.path.exists('C:\\Users\\ialeem\\Google Drive'):
			dir = 'C:\\Users\\ialeem\\Google Drive'#Change name as appropriate
		#add elif statements for any other computers you might want to upload from
		
		if os.path.exists(dir):
			file_list = []
			for file in os.listdir(dir):
				if file.startswith('MonzoDataExport_AllSpending') & file.endswith('.csv'):
					file_list.append([file,datetime.strptime(file.split('_')[2],'%Y-%m-%d')])
					
			if file_list:
				most_recent_file = dir + '\\' + max(file_list, key=lambda list:list[1])[0]
				
				data = pd.read_csv(most_recent_file,parse_dates=True)
				data['created'] = data['created'].apply(lambda x: datetime.strptime(x[:16],'%Y-%m-%d %H:%M')) #Monzo data contains milliseconds that don't play well with pandas, so strip them off			
				data = data[data['created']>most_recent_record_date]
				
				insert_into_database(data)

auto_upload_csv_file()
transactions = set_transactions_df()
colour_dict, category_dict = set_dicts()
	
def delete_all_records():
	MonzoCsvExport.objects.all().delete()
