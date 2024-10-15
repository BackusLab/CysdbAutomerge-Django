import csv
import os
import zipfile
import re
from django.core.management.base import BaseCommand
from django.conf import settings
from blog.models import Identified, UploadFile, Hyperreactive, Ligandable

class Command(BaseCommand):
    help = 'Load initial data from CSV file'

    def handle(self, *args, **kwargs):
        if Identified.objects.exists() and Hyperreactive.objects.exists() and Ligandable.objects.exists():
            self.stdout.write(self.style.SUCCESS('Initial data already loaded'))
            return

        file_path = os.path.join(settings.BASE_DIR, 'blog', 'v1p5_data', 'cysdb_master.zip') 
        print('Loading Initial Data')

        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            for csv_filename in zip_ref.namelist():
                print(f'Processing {csv_filename}')
                if 'MACOSX' in csv_filename:
                    continue
                file_instance, created = UploadFile.objects.get_or_create(upload=csv_filename)
                with zip_ref.open(csv_filename) as csvfile:
                    reader = csv.DictReader(csvfile.read().decode('utf-8').splitlines())
                # Process identified file
                    if ('id' in csv_filename) and (Identified.objects.exists() == False):  
                        for row in reader:
                            for i in Identified._meta.get_fields():
                                if i.name not in row.keys():
                                    row[i.name] = ''
                            Identified.objects.create(file = file_instance, level= row['level'], proteinid = row['proteinid'], cysteineid = row['cysteineid'],
                                                    resid = row['resid'], datasetid = row['datasetid'], identified = row['identified'], 
                                                    ligandable_datasets = row['ligandable_datasets'], identified_datasets = row['identified_datasets'],
                                                    cell_line_datasets = row['cell_line_datasets'], ligandable = row['ligandable'], hyperreactive = row['hyperreactive'], 
                                                    hyperreactive_datasets= row['hyperreactive_datasets'], redox_datasets = row['redox_datasets'])
                # Process Hyperreactive file
                    elif 'hyperreactive' in csv_filename:
                        for row in reader:
                            known_fields = {field.name for field in Hyperreactive._meta.get_fields()}
                            hyperreactive_data = {}
                            for key, value in row.items():
                                if (key in known_fields):
                                    if key == 'proteinid' or key == 'cysteineid' or key == 'resid' or key =='file':
                                        hyperreactive_data[key] = value
                                    else:
                                        hyperreactive_data[key] = float(value) if value else None


                    elif 'ligandable' in csv_filename:
                        for row in reader:
                            known_fields = {field.name for field in Ligandable._meta.get_fields()}
                            ligandable_data = {}
                            new_cols = {}
                            datasets = {}
                            for key, value in row.items():
                                if (key in known_fields):
                                    ligandable_data[key] = value
                                elif re.match(r'^[a-zA-Z]+_[a-zA-Z]+_ligandable$', key):
                                    datasets[key] = value
                                elif re.match(r'^CL_\d+$', key):
                                    ligandable_data['chloroacetamide'] = 'yes'
                                    new_cols[key] = float(value) if value != '' else None
                                elif re.match(r'^ACRYL_\d+$', key):
                                    ligandable_data['acrylamide'] = 'yes'
                                    new_cols[key] = float(value) if value != '' else None
                                elif re.match(r'^BR_\d+$', key):
                                    ligandable_data['bromoacetamide'] = 'yes'
                                    new_cols[key] = float(value) if value != '' else None
                                elif re.match(r'^DMF_\d+$', key):
                                    ligandable_data['dimethylfumarate'] = 'yes'
                                    new_cols[key] = float(value) if value != '' else None
                                elif re.match(r'^OTHER_\d+$', key):
                                    ligandable_data['other'] = 'yes'
                                    new_cols[key] = float(value) if value != '' else None
                            Ligandable.objects.create(file=file_instance,**ligandable_data, datasets = datasets, compounds = new_cols)
                            

        self.stdout.write(self.style.SUCCESS('Successfully loaded initial data'))
