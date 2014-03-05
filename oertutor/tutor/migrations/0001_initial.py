# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Student'
        db.create_table(u'tutor_student', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('phase', self.gf('django.db.models.fields.CharField')(default='new', max_length=4)),
            ('started', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'tutor', ['Student'])

        # Adding model 'Curriculum'
        db.create_table(u'tutor_curriculum', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('exam', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['tutor.Test'])),
        ))
        db.send_create_signal(u'tutor', ['Curriculum'])

        # Adding model 'KnowledgeComponent'
        db.create_table(u'tutor_knowledgecomponent', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('pretest', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['tutor.Test'])),
            ('posttest', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['tutor.Test'])),
            ('curriculum', self.gf('django.db.models.fields.related.ForeignKey')(related_name='kcs', to=orm['tutor.Curriculum'])),
        ))
        db.send_create_signal(u'tutor', ['KnowledgeComponent'])

        # Adding M2M table for field antecedents on 'KnowledgeComponent'
        m2m_table_name = db.shorten_name(u'tutor_knowledgecomponent_antecedents')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_knowledgecomponent', models.ForeignKey(orm[u'tutor.knowledgecomponent'], null=False)),
            ('to_knowledgecomponent', models.ForeignKey(orm[u'tutor.knowledgecomponent'], null=False))
        ))
        db.create_unique(m2m_table_name, ['from_knowledgecomponent_id', 'to_knowledgecomponent_id'])

        # Adding model 'StudentCategory'
        db.create_table(u'tutor_studentcategory', (
            (u'population_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['ga.Population'], unique=True, primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('kc', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['tutor.KnowledgeComponent'])),
            ('lower_score', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=4, decimal_places=2)),
            ('upper_score', self.gf('django.db.models.fields.DecimalField')(default=1.0, max_digits=4, decimal_places=2)),
        ))
        db.send_create_signal(u'tutor', ['StudentCategory'])

        # Adding model 'Trial'
        db.create_table(u'tutor_trial', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('kc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tutor.KnowledgeComponent'])),
            ('curriculum', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['tutor.Curriculum'])),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(related_name='trials', to=orm['tutor.Student'])),
            ('pretest_result', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['tutor.TestResult'])),
            ('sequence', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['ga.Individual'])),
            ('sequence_position', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('posttest_result', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['tutor.TestResult'])),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tutor.StudentCategory'], null=True)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'tutor', ['Trial'])

        # Adding model 'Resource'
        db.create_table(u'tutor_resource', (
            (u'gene_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['ga.Gene'], unique=True, primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('source', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('kc', self.gf('django.db.models.fields.related.ForeignKey')(related_name='resources', to=orm['tutor.KnowledgeComponent'])),
        ))
        db.send_create_signal(u'tutor', ['Resource'])

        # Adding model 'Exercise'
        db.create_table(u'tutor_exercise', (
            (u'resource_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['tutor.Resource'], unique=True, primary_key=True)),
            ('params', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'tutor', ['Exercise'])

        # Adding model 'ExerciseResult'
        db.create_table(u'tutor_exerciseresult', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('exercise', self.gf('django.db.models.fields.related.ForeignKey')(related_name='result', to=orm['tutor.Exercise'])),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tutor.Student'])),
            ('data', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'tutor', ['ExerciseResult'])

        # Adding model 'Observation'
        db.create_table(u'tutor_observation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('handle', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'tutor', ['Observation'])

        # Adding model 'Test'
        db.create_table(u'tutor_test', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('template', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal(u'tutor', ['Test'])

        # Adding M2M table for field questions on 'Test'
        m2m_table_name = db.shorten_name(u'tutor_test_questions')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('test', models.ForeignKey(orm[u'tutor.test'], null=False)),
            ('question', models.ForeignKey(orm[u'tutor.question'], null=False))
        ))
        db.create_unique(m2m_table_name, ['test_id', 'question_id'])

        # Adding model 'Question'
        db.create_table(u'tutor_question', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('handle', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('question', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('answer', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('weight', self.gf('django.db.models.fields.SmallIntegerField')(default=1)),
            ('template', self.gf('django.db.models.fields.CharField')(default='question/generic.html', max_length=255)),
        ))
        db.send_create_signal(u'tutor', ['Question'])

        # Adding model 'NimQuestion'
        db.create_table(u'tutor_nimquestion', (
            (u'question_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['tutor.Question'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'tutor', ['NimQuestion'])

        # Adding model 'MultipleChoiceQuestion'
        db.create_table(u'tutor_multiplechoicequestion', (
            (u'question_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['tutor.Question'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'tutor', ['MultipleChoiceQuestion'])

        # Adding M2M table for field answers on 'MultipleChoiceQuestion'
        m2m_table_name = db.shorten_name(u'tutor_multiplechoicequestion_answers')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('multiplechoicequestion', models.ForeignKey(orm[u'tutor.multiplechoicequestion'], null=False)),
            ('answer', models.ForeignKey(orm[u'tutor.answer'], null=False))
        ))
        db.create_unique(m2m_table_name, ['multiplechoicequestion_id', 'answer_id'])

        # Adding model 'Answer'
        db.create_table(u'tutor_answer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('handle', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('body', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'tutor', ['Answer'])

        # Adding model 'TestResult'
        db.create_table(u'tutor_testresult', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('test', self.gf('django.db.models.fields.related.ForeignKey')(related_name='results', to=orm['tutor.Test'])),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tutor.Student'])),
            ('score', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=4, decimal_places=2)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'tutor', ['TestResult'])

        # Adding model 'StudentAnswer'
        db.create_table(u'tutor_studentanswer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tutor.Question'])),
            ('testresult', self.gf('django.db.models.fields.related.ForeignKey')(related_name='answers', to=orm['tutor.TestResult'])),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tutor.Student'])),
            ('answer', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'tutor', ['StudentAnswer'])


    def backwards(self, orm):
        # Deleting model 'Student'
        db.delete_table(u'tutor_student')

        # Deleting model 'Curriculum'
        db.delete_table(u'tutor_curriculum')

        # Deleting model 'KnowledgeComponent'
        db.delete_table(u'tutor_knowledgecomponent')

        # Removing M2M table for field antecedents on 'KnowledgeComponent'
        db.delete_table(db.shorten_name(u'tutor_knowledgecomponent_antecedents'))

        # Deleting model 'StudentCategory'
        db.delete_table(u'tutor_studentcategory')

        # Deleting model 'Trial'
        db.delete_table(u'tutor_trial')

        # Deleting model 'Resource'
        db.delete_table(u'tutor_resource')

        # Deleting model 'Exercise'
        db.delete_table(u'tutor_exercise')

        # Deleting model 'ExerciseResult'
        db.delete_table(u'tutor_exerciseresult')

        # Deleting model 'Observation'
        db.delete_table(u'tutor_observation')

        # Deleting model 'Test'
        db.delete_table(u'tutor_test')

        # Removing M2M table for field questions on 'Test'
        db.delete_table(db.shorten_name(u'tutor_test_questions'))

        # Deleting model 'Question'
        db.delete_table(u'tutor_question')

        # Deleting model 'NimQuestion'
        db.delete_table(u'tutor_nimquestion')

        # Deleting model 'MultipleChoiceQuestion'
        db.delete_table(u'tutor_multiplechoicequestion')

        # Removing M2M table for field answers on 'MultipleChoiceQuestion'
        db.delete_table(db.shorten_name(u'tutor_multiplechoicequestion_answers'))

        # Deleting model 'Answer'
        db.delete_table(u'tutor_answer')

        # Deleting model 'TestResult'
        db.delete_table(u'tutor_testresult')

        # Deleting model 'StudentAnswer'
        db.delete_table(u'tutor_studentanswer')


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
        u'ga.gene': {
            'Meta': {'object_name': 'Gene'},
            'apriori_value': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phase': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '4'}),
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