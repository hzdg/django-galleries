# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ImageModel'
        db.create_table(u'galleries_imagemodel', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('original_image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
        ))
        db.send_create_signal(u'galleries', ['ImageModel'])

        # Adding model 'EmbedModel'
        db.create_table(u'galleries_embedmodel', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('embed_code', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'galleries', ['EmbedModel'])


    def backwards(self, orm):
        # Deleting model 'ImageModel'
        db.delete_table(u'galleries_imagemodel')

        # Deleting model 'EmbedModel'
        db.delete_table(u'galleries_embedmodel')


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
            'original_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['galleries']