from django.db import models
from django.conf import settings
from django.utils import timezone


class UploadFile(models.Model):
    def directory(instance, filename):
        return '/'.join(['cysdb', filename])

    upload = models.FileField(upload_to=directory)


class Cysdb(models.Model):
    file = models.ForeignKey(
        'UploadFile',
        on_delete=models.CASCADE,
    )
    level = models.CharField(max_length= 20, )
    proteinid = models.CharField(max_length=20,)
    cysteineid = models.CharField(max_length=20,)
    resid = models.CharField(max_length=20)
    datasetid = models.CharField(max_length=20,)
    identified = models.CharField(max_length=20,
    )
    identified_datasets = models.CharField(max_length=20,
    )
    ligandable_datasets = models.CharField(max_length=20,)
    ligandable = models.CharField(max_length=20,)
    cell_line_datasets = models.CharField(max_length=20, )
    hyperreactive = models.CharField(max_length=20,null=True,)
    hyperreactive_datasets = models.CharField(max_length=20,null=True,)
    redox_datasets = models.CharField(max_length=20,null=True,)