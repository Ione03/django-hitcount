from __future__ import unicode_literals
from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from hitcount.models import HitCountMixin
from hitcount.settings import MODEL_HITCOUNT


class Post(models.Model, HitCountMixin):
    title = models.CharField(max_length=200)
    content = models.TextField()
    hit_count_generic = GenericRelation(MODEL_HITCOUNT, object_id_field=
        'object_pk', related_query_name='hit_count_generic_relation')

    def __str__(self):
        return 'Post title: %s' % self.title
