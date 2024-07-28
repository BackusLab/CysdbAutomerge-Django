import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from blog.models import Ligandable, UploadFile

class Command(BaseCommand):
    help = 'Load initial data from CSV file'

    def handle(self, *args, **kwargs):
        if Ligandable.objects.exists():
            self.stdout.write(self.style.SUCCESS('Initial data already loaded'))
            return

        file_path = os.path.join(settings.BASE_DIR, 'blog', 'v1p5_data', '240419_cysdb_id_v1p5.csv')
        file_instance, created = UploadFile.objects.get_or_create(
            upload=file_path
        )
        print('Loading Initial Data')
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                for i in Ligandable._meta.get_fields():
                    if i.name not in row.keys():
                        row[i.name] = ''

                Ligandable.objects.create(file = file_instance, level= row['level'], proteinid = row['proteinid'], cysteineid = row['cysteineid'],
                                                    resid = row['resid'], datasetid = row['datasetid'], identified = row['identified'], 
                                                    ligandable_datasets = row['ligandable_datasets'], identified_datasets = row['identified_datasets'],
                                                    cell_line_datasets = row['cell_line_datasets'], ligandable = row['ligandable'], hyperreactive = row['hyperreactive'], 
                                                    hyperreactive_datasets= row['hyperreactive_datasets'], redox_datasets = row['redox_datasets'])
        self.stdout.write(self.style.SUCCESS('Successfully loaded initial data'))
