from django.shortcuts import render, redirect
from django.conf import settings
from .forms import UploadFileForm
from .models import Ligandable, UploadFile, Hyperreactive
from django.http import HttpResponse
import logging
import csv
import os
import statistics
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
        known_fields = {field.name for field in Hyperreactive._meta.get_fields()}
        hyperreactive_data = {}
        new_means = {}
        for key, value in row.items():
            if (key in known_fields):
                hyperreactive_data[key] = value
            else:
                new_means[key] = float(value) if value else 0.0
        
        if Hyperreactive.objects.filter(cysteineid=row['cysteineid']).exists() == False:
            cysdb_data = Hyperreactive.objects.create(
                file=file,
                **hyperreactive_data,
                new_means = new_means
            )

            cysdb_data.save()
            
        else:
            cysdb_data = Hyperreactive.objects.filter(cysteineid = row['cysteineid']).get()
            cysdb_data.new_means.update(new_means)
            means = list(cysdb_data.new_means.values()) + list(filter(None, [cysdb_data.castellon_mean, cysdb_data.vinogradova_mean, cysdb_data.weerapana_mean, cysdb_data.palafox_mean]))
            cysdb_data.cysdb_mean= statistics.mean(means)
            cysdb_data.cysdb_median = statistics.median(means)
            if len(means) > 1:
                cysdb_data.cysdb_stdev = statistics.stdev(means)
            cysdb_data.hyperreactive='yes'
            cysdb_data.save()

    last_30 = Hyperreactive.objects.order_by('id')[:50]
    new_means_keys = last_30.values_list('new_means', flat=True)
    keys = {key for obj in new_means_keys for key in obj.keys()}

    merged = Hyperreactive.objects.filter(file = file)
    #merged = Hyperreactive.objects.filter(file = file) | Cysdb.objects.filter(file = file_instance)

    return render(request,'blog/configure_merge.html', {'cysdb_file': file, 'last_30': last_30, 'merged_dataset': merged, 'table': 'hyperreactive', 'new_means': keys})


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
        writer.writerow(header)
        for record in merged_dataset:
            writer.writerow([getattr(record, field) for field in header])

    elif table == 'hyperreactive':
        field_names = [field.name for field in Hyperreactive._meta.fields if field.name != 'new_means']
        extra_field_names = set()
        for data in merged_dataset:
            extra_field_names.update(data.new_means.keys())
        writer.writerow(field_names + list(extra_field_names))
        for data in merged_dataset:
            row = [getattr(data, field) for field in field_names]
            # Add the dynamic fields
            for field in extra_field_names:
                row.append(data.new_means.get(field, ''))  # default to empty if not present
            writer.writerow(row)

    return response