#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.db import models


# Create your models here.
class Reporter(models.Model):
    taskid = models.CharField(max_length=225)
    description = models.TextField()
    label = models.CharField(max_length=10)
    code = models.CharField(max_length=10)
    msg = models.TextField()

    def __str__(self):
        return self.taskid
