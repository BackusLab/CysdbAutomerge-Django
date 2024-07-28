from django.shortcuts import render, redirect
from django.conf import settings
from .forms import UploadFileForm
from .models import Ligandable, UploadFile, Hyperreactive
from django.http import HttpResponse
import logging
import csv
import os
logger = logging.getLogger('django')


def homepage(request):
    if request.method == 'POST':
        return handle_upload(request)
    else:
        form = UploadFileForm()
        return render(request, 'blog/homepage.html', {'form': form})

def handle_upload(request):
    form = UploadFileForm(request.POST, request.FILES)
    if form.is_valid():
        upload_file_instance = form.save(commit=False)

        file = UploadFile.objects.last()
        table = form.cleaned_data['table']
        dataset = request.FILES['upload']
        if table == 'ligandable':
            return process_cysdb_file(request, dataset, file)
        elif table == 'hyperreactive':
            return process_hyperreactive_file(request, dataset, file)
    else:
        return render(request, 'blog/homepage.html', {'form': form})
    
def process_cysdb_file(request, dataset, file):
    decoded_dataset = dataset.read().decode('utf-8').splitlines()
    reader = csv.DictReader(decoded_dataset)
    for row in reader:
        for i in Ligandable._meta.get_fields():
            if i.name not in row.keys():
                row[i.name] = ''

        if Ligandable.objects.filter(cysteineid=row['cysteineid']).exists() == False:
            cysdb_data = Ligandable.objects.create(file = file, level= row['level'], proteinid = row['proteinid'], cysteineid = row['cysteineid'],
                                            resid = row['resid'], datasetid = row['datasetid'], identified = row['identified'], 
                                            ligandable_datasets = row['ligandable_datasets'], identified_datasets = row['identified_datasets'],
                                            cell_line_datasets = row['cell_line_datasets'], ligandable = row['ligandable'], hyperreactive = row['hyperreactive'], 
                                            hyperreactive_datasets= row['hyperreactive_datasets'], redox_datasets = row['redox_datasets'])
            cysdb_data.save()
        else:
            cysdb_last = Ligandable.objects.filter(cysteineid = row['cysteineid']).last()
            identified_datasets = cysdb_last.identified_datasets.split(';')
            if row['datasetid'] not in identified_datasets:
                queryset = Ligandable.objects.filter(cysteineid = row['cysteineid']).values()
                new_identified = cysdb_last.identified_datasets + ';' + str(row['datasetid'])
                queryset.update(identified_datasets = new_identified)
            if row['ligandable'] != 'yes':
                row['ligandable'] = 'yes'
            
    file_path = os.path.join(settings.BASE_DIR, 'blog', 'v1p5_data', '240419_cysdb_id_v1p5.csv')
    file_instance, __ = UploadFile.objects.get_or_create(upload=file_path)

    last_30 = Ligandable.objects.order_by('id')[:50]
    merged = Ligandable.objects.filter(file = file) | Ligandable.objects.filter(file = file_instance)

    return render(request,'blog/configure_merge.html', {'cysdb_file': file, 'last_30': last_30, 'merged_dataset': merged, 'table': 'ligandable'})

def process_hyperreactive_file(request, dataset, file):
    decoded_dataset = dataset.read().decode('utf-8').splitlines()
    reader = csv.DictReader(decoded_dataset)
    for row in reader:
        for i in Hyperreactive._meta.get_fields():
            if i.name not in row.keys():
                if i.get_internal_type() == 'FloatField':
                    row[i.name] = 0.0
                else: 
                    row[i.name] = ''
            if i.get_internal_type() == 'FloatField':
                if row[i.name] == '':
                    row[i.name] = None
                else:
                    row[i.name] = float(row[i.name])

        
        if Hyperreactive.objects.filter(cysteineid=row['cysteineid']).exists() == False:
            cysdb_data = Hyperreactive.objects.create(
            file=file, proteinid=row['proteinid'],cysteineid=row['cysteineid'],resid=row['resid'],
            weerapana_mean=row['weerapana_mean'],palafox_mean=row['palafox_mean'], vinogradova_mean = row['vinogradova_mean'], cysdb_mean = row['cysdb_mean'], 
            cysdb_median = row['cysdb_median'],cysdb_stdev = row['cysdb_stdev'], cysdb_reactivity_category = row['cysdb_reactivity_category'], 
            hyperreactive = row['hyperreactive'], castellon_mean = row['castellon_mean']) 
            cysdb_data.save()
        else:
            cysteine = Hyperreactive.objects.filter(cysteineid = row['cysteineid'])
            cysteine_count = len(cysteine)
            row['cysdb_mean'] = update_mean(cysteine_count, row['cysdb_mean'], cysteine.all().values()[0]['cysdb_mean'])
            row['castellon_mean'] = update_mean(cysteine_count, row['castellon_mean'], cysteine.all().values()[0]['castellon_mean'])
            row['vinogradova_mean']= update_mean(cysteine_count, row['vinogradova_mean'], cysteine.all().values()[0]['vinogradova_mean'])
            row['weerapana_mean']= update_mean(cysteine_count, row['weerapana_mean'], cysteine.all().values()[0]['weerapana_mean'])
            row['palafox_mean']= update_mean(cysteine_count, row['palafox_mean'], cysteine.all().values()[0]['palafox_mean'])
            
    #file_path = os.path.join(settings.BASE_DIR, 'blog', 'v1p5_data', '240419_cysdb_id_v1p5.csv')
    #file_instance, __ = UploadFile.objects.get_or_create(upload=file_path)

    last_30 = Hyperreactive.objects.order_by('id')[:50]
    merged = Hyperreactive.objects.filter(file = file)
    #merged = Hyperreactive.objects.filter(file = file) | Cysdb.objects.filter(file = file_instance)

    return render(request,'blog/configure_merge.html', {'cysdb_file': file, 'last_30': last_30, 'merged_dataset': merged, 'table': 'hyperreactive'})
    ### FIX THIS LATERRRR



def update_mean(count, new_val, old_val):
    if new_val == None:
        return old_val
    if old_val == None:
        return new_val

    return (old_val * count + new_val)/(count + 1)

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            cysdb_file = form.save(commit = False)
            cysdb_file.save()
            return redirect('blog/configure_merge.html', {'cysdb_file': cysdb_file})
        else:
            form = UploadFileForm()
    return render(request, 'blog/homepage.html', {'form':form})

def instructions(request):
    return render(request, 'blog/instructions.html')

def download_merged_dataset(request, table):
    # Get the merged dataset
    file = UploadFile.objects.last()
    if table == 'ligandable':
        file_path = os.path.join(settings.BASE_DIR, 'blog', 'v1p5_data', '240419_cysdb_id_v1p5.csv')
        file_instance, __ = UploadFile.objects.get_or_create(upload=file_path)
        merged_dataset = Ligandable.objects.filter(file=file) | Ligandable.objects.filter(file=file_instance)
    else:
        merged_dataset = Hyperreactive.objects.filter(file=file)


    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="merged_dataset.csv"'

    writer = csv.writer(response)
    
    if table == 'ligandable':
        header = [field.name for field in Ligandable._meta.get_fields() if field.concrete]
    elif table == 'hyperreactive':
        header = [field.name for field in Hyperreactive._meta.get_fields() if field.concrete]
    
    writer.writerow(header)

    for record in merged_dataset:
        writer.writerow([getattr(record, field) for field in header])

    return response