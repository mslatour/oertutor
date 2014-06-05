from oertutor.tutor.models import *
from oertutor.ga.simulate import *
from oertutor.monitor.helpers import *
import matplotlib.pyplot as plt
from plot import plot

categories = StudentCategory.objects.filter()
for cat in categories:
  print cat.title
  tab = TabularData(labels=['evaluation','theoretical best', 'population best', 'generation best'])
  cumul_data = [cumulativy_data(gather_regret_data(cat, alternative=True)),
                cumulativy_data(gather_regret_data(cat, mode="popbest", alternative=True)),
                cumulativy_data(gather_regret_data(cat, mode="genbest", alternative=True))]
  tab.cast(float)
  
  for index, datum in enumerate(cumul_data[0]):
    tab.append([index+1, datum, cumul_data[1][index], cumul_data[2][index]])
  
  plot(tab, xlabel="Evaluation",ylabel="Cumulative regret",legend_linewidth=4, errorbar=False, fontsize="xx-large")


