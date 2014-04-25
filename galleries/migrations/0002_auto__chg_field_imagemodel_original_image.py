# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'ImageModel.original_image'
        db.alter_column(u'galleries_imagemodel', 'original_image', self.gf('django.db.models.fields.files.ImageField')(max_length=255))

    def backwards(self, orm):

        # Changing field 'ImageModel.original_image'
        db.alter_column(u'galleries_imagemodel', 'original_image', self.gf('django.db.models.fields.files.ImageField')(max_length=100))

    models = {
        u'galleries.embedmodel': {
            'Meta': {'object_name': 'EmbedModel'},
            'embed_code': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'galleries.imagemodel': {
            'Meta': {'ordering': "['title']", 'object_name': 'ImageModel'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'original_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['galleries']