from django.contrib import admin
from .models import UploadFile, Ligandable, Hyperreactive

class LigandableDisplay(admin.ModelAdmin):
    list_display = ('level', 'proteinid', 'cysteineid', 'ligandable', 'ligandable_datasets', 'resid', 'identified', 'identified_datasets',
                     'datasetid','cell_line_datasets', 'hyperreactive', 'hyperreactive_datasets', 'redox_datasets')
    search_fields = ['proteinid', 'cysteineid']

class HyperreactiveDisplay(admin.ModelAdmin):
    list_display = ('proteinid', 'cysteineid', 'resid', 'weerapana_mean', 'palafox_mean', 'vinogradova_mean', 'cysdb_mean', 'cysdb_median', 
                    'cysdb_reactivity_category', 
                    'hyperreactive', 'castellon_mean')

admin.site.register(UploadFile)
admin.site.register(Hyperreactive, HyperreactiveDisplay)
admin.site.register(Ligandable, LigandableDisplay)
