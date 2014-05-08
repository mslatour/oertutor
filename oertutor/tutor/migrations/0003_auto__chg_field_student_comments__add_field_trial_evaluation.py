# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Student.comments'
        db.alter_column(u'tutor_student', 'comments', self.gf('django.db.models.fields.TextField')(null=True))
        # Adding field 'Trial.evaluation'
        db.add_column(u'tutor_trial', 'evaluation',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['ga.Evaluation']),
                      keep_default=False)


    def backwards(self, orm):

        # Changing field 'Student.comments'
        db.alter_column(u'tutor_student', 'comments', self.gf('django.db.models.fields.TextField')(default=''))
        # Deleting field 'Trial.evaluation'
        db.delete_column(u'tutor_trial', 'evaluation_id')


    models = {
        u'ga.chromosome': {
            'Meta': {'object_name': 'Chromosome'},
            'age': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'fitness': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '9'}),
            'genes': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'chromosomes'", 'symmetrical': 'False', 'through': u"orm['ga.ChromosomeMembership']", 'to': u"orm['ga.Gene']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parents': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'children'", 'symmetrical': 'False', 'to': u"orm['ga.Chromosome']"}),
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
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
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
        },
        u'tutor.answer': {
            'Meta': {'object_name': 'Answer'},
            'body': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'handle': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'tutor.curriculum': {
            'Meta': {'object_name': 'Curriculum'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'exam': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': u"orm['tutor.Test']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'tutor.exercise': {
            'Meta': {'object_name': 'Exercise', '_ormbases': [u'tutor.Resource']},
            'params': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'resource_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['tutor.Resource']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'tutor.exerciseresult': {
            'Meta': {'object_name': 'ExerciseResult'},
            'data': ('django.db.models.fields.TextField', [], {}),
            'exercise': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'result'", 'to': u"orm['tutor.Exercise']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tutor.Student']"})
        },
        u'tutor.knowledgecomponent': {
            'Meta': {'object_name': 'KnowledgeComponent'},
            'antecedents': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'consequent'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['tutor.KnowledgeComponent']"}),
            'curriculum': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'kcs'", 'to': u"orm['tutor.Curriculum']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'posttest': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['tutor.Test']"}),
            'pretest': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['tutor.Test']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'tutor.multiplechoicequestion': {
            'Meta': {'object_name': 'MultipleChoiceQuestion', '_ormbases': [u'tutor.Question']},
            'answers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'+'", 'symmetrical': 'False', 'to': u"orm['tutor.Answer']"}),
            u'question_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['tutor.Question']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'tutor.nimquestion': {
            'Meta': {'object_name': 'NimQuestion', '_ormbases': [u'tutor.Question']},
            u'question_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['tutor.Question']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'tutor.observation': {
            'Meta': {'object_name': 'Observation'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'handle': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'tutor.question': {
            'Meta': {'object_name': 'Question'},
            'answer': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'handle': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'template': ('django.db.models.fields.CharField', [], {'default': "'question/generic.html'", 'max_length': '255'}),
            'weight': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'})
        },
        u'tutor.resource': {
            'Meta': {'object_name': 'Resource', '_ormbases': [u'ga.Gene']},
            u'gene_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['ga.Gene']", 'unique': 'True', 'primary_key': 'True'}),
            'kc': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'resources'", 'to': u"orm['tutor.KnowledgeComponent']"}),
            'source': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'tutor.student': {
            'Meta': {'object_name': 'Student'},
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phase': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '4'}),
            'postskill': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'preskill': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'started': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'tutor.studentanswer': {
            'Meta': {'object_name': 'StudentAnswer'},
            'answer': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tutor.Question']"}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tutor.Student']"}),
            'testresult': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'answers'", 'to': u"orm['tutor.TestResult']"})
        },
        u'tutor.studentcategory': {
            'Meta': {'object_name': 'StudentCategory', '_ormbases': [u'ga.Population']},
            'kc': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['tutor.KnowledgeComponent']"}),
            'lower_score': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '4', 'decimal_places': '2'}),
            u'population_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['ga.Population']", 'unique': 'True', 'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'upper_score': ('django.db.models.fields.DecimalField', [], {'default': '1.0', 'max_digits': '4', 'decimal_places': '2'})
        },
        u'tutor.test': {
            'Meta': {'object_name': 'Test'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'questions': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'test'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['tutor.Question']"}),
            'template': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'tutor.testresult': {
            'Meta': {'object_name': 'TestResult'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'score': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '4', 'decimal_places': '2'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tutor.Student']"}),
            'test': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'results'", 'to': u"orm['tutor.Test']"})
        },
        u'tutor.trial': {
            'Meta': {'object_name': 'Trial'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tutor.StudentCategory']", 'null': 'True'}),
            'curriculum': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['tutor.Curriculum']"}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'evaluation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': u"orm['ga.Evaluation']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kc': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tutor.KnowledgeComponent']"}),
            'posttest_result': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': u"orm['tutor.TestResult']"}),
            'pretest_result': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': u"orm['tutor.TestResult']"}),
            'sequence': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': u"orm['ga.Individual']"}),
            'sequence_position': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'trials'", 'to': u"orm['tutor.Student']"})
        }
    }

    complete_apps = ['tutor']
