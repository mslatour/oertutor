# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Chromosome.population'
        db.add_column(u'ga_chromosome', 'population',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='chromosomes', to=orm['ga.Population']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Chromosome.population'
        db.delete_column(u'ga_chromosome', 'population_id')


    models = {
        u'ga.chromosome': {
            'Meta': {'object_name': 'Chromosome'},
            'age': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'fitness': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '9'}),
            'genes': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'chromosomes'", 'symmetrical': 'False', 'through': u"orm['ga.ChromosomeMembership']", 'to': u"orm['ga.Gene']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parents': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'parents_rel_+'", 'to': u"orm['ga.Chromosome']"}),
            'population': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'chromosomes'", 'to': u"orm['ga.Population']"})
        },
        u'ga.chromosomemembership': {
            'Meta': {'object_name': 'ChromosomeMembership'},
            'chromosome': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ga.Chromosome']"}),
            'gene': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ga.Gene']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'ga.evaluation': {
            'Meta': {'object_name': 'Evaluation'},
            'chromosome': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['ga.Chromosome']"}),
            'generation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['ga.Generation']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'individual': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['ga.Individual']"}),
            'population': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['ga.Population']"}),
            'value': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '9'})
        },
        u'ga.gene': {
            'Meta': {'object_name': 'Gene'},
            'apriori_value': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'ga.generation': {
            'Meta': {'object_name': 'Generation'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'individuals': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'+'", 'symmetrical': 'False', 'through': u"orm['ga.GenerationMembership']", 'to': u"orm['ga.Individual']"}),
            'population': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'generations'", 'to': u"orm['ga.Population']"})
        },
        u'ga.generationmembership': {
            'Meta': {'object_name': 'GenerationMembership'},
            'age': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'chromosome': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ga.Chromosome']"}),
            'fitness': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '9'}),
            'generation': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ga.Generation']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'individual': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ga.Individual']"})
        },
        u'ga.individual': {
            'Meta': {'object_name': 'Individual'},
            'chromosome': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ga.Chromosome']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.DateField', [], {'null': 'True'})
        },
        u'ga.population': {
            'Meta': {'object_name': 'Population'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'neighbours': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'neighbours_rel_+'", 'null': 'True', 'to': u"orm['ga.Population']"}),
            'pool': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'+'", 'null': 'True', 'to': u"orm['ga.Gene']"})
        }
    }

    complete_apps = ['ga']
