# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2016-12-22 18:30
from __future__ import unicode_literals
from operator import mul, itemgetter

from django.db import migrations, models
from django.conf import settings
from django.db.models import Max


def gen_pp(apps, schema_editor):
    Profile = apps.get_model('judge', 'Profile')
    Submission = apps.get_model('judge', 'Submission')
    table = (lambda x: [pow(x, i) for i in xrange(100)])(getattr(settings, 'PP_STEP', 0.95))
    for row in Profile.objects.all():
        data = (Submission.objects.filter(user=row, points__isnull=False, problem__is_public=True)
                .annotate(max_points=Max('points')).order_by('-points')
                .values_list('problem_id', 'max_points').distinct())
        size = min(len(data), len(table))
        row.performance_points = sum(map(mul, table[:size], map(itemgetter(1), data[:size])))
        row.save()


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0054_tickets'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='performance_points',
            field=models.FloatField(db_index=True, default=0),
        ),
        migrations.RunPython(gen_pp, reverse_code=migrations.RunPython.noop),
    ]
