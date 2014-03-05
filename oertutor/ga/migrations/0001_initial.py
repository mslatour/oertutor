# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Gene'
        db.create_table(u'ga_gene', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('apriori_value', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'ga', ['Gene'])

        # Adding model 'Chromosome'
        db.create_table(u'ga_chromosome', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('fitness', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=9)),
            ('age', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal(u'ga', ['Chromosome'])

        # Adding M2M table for field parents on 'Chromosome'
        m2m_table_name = db.shorten_name(u'ga_chromosome_parents')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_chromosome', models.ForeignKey(orm[u'ga.chromosome'], null=False)),
            ('to_chromosome', models.ForeignKey(orm[u'ga.chromosome'], null=False))
        ))
        db.create_unique(m2m_table_name, ['from_chromosome_id', 'to_chromosome_id'])

        # Adding model 'ChromosomeMembership'
        db.create_table(u'ga_chromosomemembership', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('gene', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga.Gene'])),
            ('chromosome', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga.Chromosome'])),
            ('index', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'ga', ['ChromosomeMembership'])

        # Adding model 'Individual'
        db.create_table(u'ga_individual', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('chromosome', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga.Chromosome'])),
            ('locked', self.gf('django.db.models.fields.DateField')(null=True)),
        ))
        db.send_create_signal(u'ga', ['Individual'])

        # Adding model 'Evaluation'
        db.create_table(u'ga_evaluation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('chromosome', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['ga.Chromosome'])),
            ('individual', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['ga.Individual'])),
            ('generation', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['ga.Generation'])),
            ('population', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['ga.Population'])),
            ('value', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=9)),
        ))
        db.send_create_signal(u'ga', ['Evaluation'])

        # Adding model 'GenerationMembership'
        db.create_table(u'ga_generationmembership', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('individual', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga.Individual'])),
            ('chromosome', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga.Chromosome'])),
            ('generation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga.Generation'])),
            ('fitness', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=9)),
            ('age', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal(u'ga', ['GenerationMembership'])

        # Adding model 'Generation'
        db.create_table(u'ga_generation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('population', self.gf('django.db.models.fields.related.ForeignKey')(related_name='generations', to=orm['ga.Population'])),
        ))
        db.send_create_signal(u'ga', ['Generation'])

        # Adding model 'Population'
        db.create_table(u'ga_population', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'ga', ['Population'])

        # Adding M2M table for field pool on 'Population'
        m2m_table_name = db.shorten_name(u'ga_population_pool')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('population', models.ForeignKey(orm[u'ga.population'], null=False)),
            ('gene', models.ForeignKey(orm[u'ga.gene'], null=False))
        ))
        db.create_unique(m2m_table_name, ['population_id', 'gene_id'])

        # Adding M2M table for field neighbours on 'Population'
        m2m_table_name = db.shorten_name(u'ga_population_neighbours')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_population', models.ForeignKey(orm[u'ga.population'], null=False)),
            ('to_population', models.ForeignKey(orm[u'ga.population'], null=False))
        ))
        db.create_unique(m2m_table_name, ['from_population_id', 'to_population_id'])


    def backwards(self, orm):
        # Deleting model 'Gene'
        db.delete_table(u'ga_gene')

        # Deleting model 'Chromosome'
        db.delete_table(u'ga_chromosome')

        # Removing M2M table for field parents on 'Chromosome'
        db.delete_table(db.shorten_name(u'ga_chromosome_parents'))

        # Deleting model 'ChromosomeMembership'
        db.delete_table(u'ga_chromosomemembership')

        # Deleting model 'Individual'
        db.delete_table(u'ga_individual')

        # Deleting model 'Evaluation'
        db.delete_table(u'ga_evaluation')

        # Deleting model 'GenerationMembership'
        db.delete_table(u'ga_generationmembership')

        # Deleting model 'Generation'
        db.delete_table(u'ga_generation')

        # Deleting model 'Population'
        db.delete_table(u'ga_population')

        # Removing M2M table for field pool on 'Population'
        db.delete_table(db.shorten_name(u'ga_population_pool'))

        # Removing M2M table for field neighbours on 'Population'
        db.delete_table(db.shorten_name(u'ga_population_neighbours'))


    models = {
        u'ga.chromosome': {
            'Meta': {'object_name': 'Chromosome'},
            'age': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'fitness': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '9'}),
            'genes': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'chromosomes'", 'symmetrical': 'False', 'through': u"orm['ga.ChromosomeMembership']", 'to': u"orm['ga.Gene']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parents': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'parents_rel_+'", 'to': u"orm['ga.Chromosome']"})
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