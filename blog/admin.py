from django.contrib import admin
from .models import UploadFile, Cysdb

def download_csv(modeladmin, request, queryset):
    import csv
    f = open('some.csv', 'wb')
    writer = csv.writer(f)
    writer.writerow(['level', 'proteinid', 'cysteineid', 'ligandable', 'ligandable_datasets', 'resid', 'identified', 'identified_datasets',
                     'datasetid','cell_line_datasets'])
    for s in queryset:
        writer.writerow([s.level, s.proteinid, s.cysteineid, s.url, s.count])
    

class CysdbDisplay(admin.ModelAdmin):
    list_display = ('level', 'proteinid', 'cysteineid', 'ligandable', 'ligandable_datasets', 'resid', 'identified', 'identified_datasets',
                     'datasetid','cell_line_datasets', 'hyperreactive', 'hyperreactive_datasets', 'redox_datasets')
    search_fields = ['proteinid', 'cysteineid']

admin.site.register(UploadFile)
admin.site.register(Cysdb, CysdbDisplay)