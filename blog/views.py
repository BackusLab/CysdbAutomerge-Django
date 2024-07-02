from django.shortcuts import render, redirect
from django.conf import settings
from .forms import UploadFileForm
from .models import Cysdb, UploadFile
from django.http import HttpResponse
import logging
import csv
import os
logger = logging.getLogger('django')


def homepage(request):
    form = UploadFileForm(request.POST, request.FILES)
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            cysdb_file = form.save(commit = False)
            file = UploadFile.objects.last()
            dataset = request.FILES['upload']
            decoded_dataset = dataset.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_dataset)
            cysdb_file.save()

            for row in reader:
                for i in Cysdb._meta.get_fields():
                    if i.name not in row.keys():
                        row[i.name] = ''

                if Cysdb.objects.filter(cysteineid=row['cysteineid']).exists() == False:
                    cysdb_data = Cysdb.objects.create(file = file, level= row['level'], proteinid = row['proteinid'], cysteineid = row['cysteineid'],
                                                    resid = row['resid'], datasetid = row['datasetid'], identified = row['identified'], 
                                                    ligandable_datasets = row['ligandable_datasets'], identified_datasets = row['identified_datasets'],
                                                    cell_line_datasets = row['cell_line_datasets'], ligandable = row['ligandable'], hyperreactive = row['hyperreactive'], 
                                                    hyperreactive_datasets= row['hyperreactive_datasets'], redox_datasets = row['redox_datasets'])
                    cysdb_data.save()
                else:
                    cysdb_last = Cysdb.objects.filter(cysteineid = row['cysteineid']).last()
                    identified_datasets = cysdb_last.identified_datasets.split(';')
                    if row['datasetid'] not in identified_datasets:
                        queryset = Cysdb.objects.filter(cysteineid = row['cysteineid']).values()
                        new_identified = cysdb_last.identified_datasets + ';' + str(row['datasetid'])
                        queryset.update(identified_datasets = new_identified)
                    if row['ligandable'] != 'yes':
                        row['ligandable'] = 'yes'
            
            # get objects
            file_path = os.path.join(settings.BASE_DIR, 'blog', 'v1p5_data', '240419_cysdb_id_v1p5.csv')
            file_instance, __ = UploadFile.objects.get_or_create(upload=file_path)

            last_30 = Cysdb.objects.order_by('id')[:50]
            merged = Cysdb.objects.filter(file = file) | Cysdb.objects.filter(file = file_instance)

            return render(request,'blog/configure_merge.html', {'cysdb_file': file, 'last_30': last_30, 'merged_dataset': merged})
        else:
            form = UploadFileForm()
    return render(request, 'blog/homepage.html', {'form': form})

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


def download_merged_dataset(request):
    # Get the merged dataset
    file = UploadFile.objects.last()
    file_path = os.path.join(settings.BASE_DIR, 'blog', 'v1p5_data', '240419_cysdb_id_v1p5.csv')
    file_instance, __ = UploadFile.objects.get_or_create(upload=file_path)
    merged_dataset = Cysdb.objects.filter(file=file) | Cysdb.objects.filter(file=file_instance)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="merged_dataset.csv"'

    writer = csv.writer(response)
    
    header = [field.name for field in Cysdb._meta.get_fields() if field.concrete]
    writer.writerow(header)

    for record in merged_dataset:
        writer.writerow([getattr(record, field) for field in header])

    return response
