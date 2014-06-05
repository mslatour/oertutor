from oertutor.ga.models import *
from oertutor.tutor.models import *
import matplotlib.pyplot as plt
from decimal import Decimal

game = Test.objects.get(title='Game')
students = [r.student for r in game.results.all()]
X = range(1,len(students)+1)
scores = [r.score for r in game.results.all()]
kcs = KnowledgeComponent.objects.all()
print "Evaluations as black, game scores are red"
for index, kc in enumerate(kcs):
    evaluations = []
    colors = []
    for student in students:
        try:
            trial = Trial.objects.get(kc=kc, student=student)
        except Trial.MultipleObjectsReturned:
            print "Two trials returned for kc %d and studend %d" % (kc.pk,
                    student.pk)
        evaluations.append(trial.evaluation.value
                if trial.evaluation is not None else 1)
        colors.append('k' if trial.evaluation is not None else 'g')
    if min(evaluations) < 0:
        minimum = min(evaluations)
        evaluations = [x+abs(minimum) for x in evaluations]
    maximum = max(evaluations)
    evaluations = [x/Decimal(maximum) for x in evaluations]
    plt.figure(index+1)
    plt.bar(X, evaluations, color=colors)
    plt.bar(X, scores, color='r', bottom=evaluations)
    plt.title(kc.title)
import time
time.sleep(1)
plt.show()
#    plt.figure(1)
#    plt.subplot(2,2,index+1)
#    plt.plot(X, evaluations, 'ko-')
#    plt.plot(X, scores, 'ro-')
#    plt.title(kc.title)
