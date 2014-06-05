import numpy as np
from oertutor.ga.models import *
from oertutor.tutor.models import *
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter
from decimal import Decimal

nullfmt   = NullFormatter()         # no labels

# definitions for the axes
left, width = 0.1, 0.65
bottom, height =0.1, 0.65
bottom_h = left_h = left+width+0.02

rect_scatter = [left, bottom, width, height]
rect_histx = [left, bottom_h, width, 0.2]
rect_histy = [left_h, bottom, 0.2, height]

game = Test.objects.get(title='Game')
students = [r.student for r in game.results.order_by('pk').all()]
scores = [r.score for r in game.results.order_by('pk').all()]
kcs = KnowledgeComponent.objects.all()
print "Evaluations as black, game scores are red"
for index, kc in enumerate(kcs):
    x = []
    y = []
    for student in students:
        try:
            trial = Trial.objects.get(kc=kc, student=student)
        except Trial.MultipleObjectsReturned:
            print "Two trials returned for kc %d and student %d" % (kc.pk,
                    student.pk)
        if trial.evaluation is not None:
            x.append(trial.evaluation.value)
            y.append(game.results.get(student=student).score)
    if min(x) < 0:
        minimum = min(x)
        evaluations = [v+abs(minimum) for v in x]
    maximum = max(x)
    evaluations = [v/Decimal(maximum) for v in x]

    x = np.array([float(v) for v in x])
    y = np.array([float(v) for v in y])
    # start with a rectangular Figure
    plt.figure(index+1, figsize=(8,8))
    plt.suptitle(kc.title)
    axScatter = plt.axes(rect_scatter)
    axHistx = plt.axes(rect_histx)
    axHisty = plt.axes(rect_histy)

    # no labels
    axHistx.xaxis.set_major_formatter(nullfmt)
    axHisty.yaxis.set_major_formatter(nullfmt)

    # the scatter plot:
    axScatter.scatter(x, y)

    # now determine nice limits by hand:
    binwidth = 0.25
    xymax = np.max( [np.max(np.fabs(x)), np.max(np.fabs(y))] )
    lim = ( int(xymax/binwidth) + 1) * binwidth

    axScatter.set_xlim( (0, lim) )
    axScatter.set_ylim( (0, lim) )

    bins = np.arange(-lim, lim + binwidth, binwidth)
    axHistx.hist(x, bins=bins)
    axHisty.hist(y, bins=bins, orientation='horizontal')

    axHistx.set_xlim( axScatter.get_xlim() )
    axHisty.set_ylim( axScatter.get_ylim() )

import time
time.sleep(1)
plt.show()
