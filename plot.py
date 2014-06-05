#!/usr/bin/python

# plotscript for joined indexed lines
import cPickle as pickle
import numpy as np
import matplotlib.pyplot as plt
import sys
import time
import glob

directory = "/home/sander/projects/thesis/dissemination/thesis/results"

def plotall(subdir, *args, **kwargs):
    for index, filename in enumerate(
            glob.glob("%s/%s/*.pickle" % (directory,subdir))):
        plt.figure(index+1)
        print "Showing %s" % (filename,)
        plot(filename, *args, **kwargs)

def plot(tab_or_filename, every=20, loc=2, errorbar=True, fontsize="x-large",
        legend_linewidth=4, xlabel=None, ylabel=None, **kwargs):
    if isinstance(tab_or_filename,str):
        f = open(tab_or_filename,"r")
        tab = pickle.load(f)
    else:
        tab = tab_or_filename
    x = []
    cols = 0
    ylist = None
    elist = None
    plt.minorticks_on()
    if xlabel is not None:
        plt.gca().set_xlabel(xlabel, fontsize=fontsize)
    if ylabel is not None:
        plt.gca().set_ylabel(ylabel, fontsize=fontsize)
    if len(tab) == 1:
        ind = np.arange(len(tab[0]))
        means = [float(value) for value in tab[0]]
        stds = [(float(value)-float(min(value)),float(max(value))-float(value)) for value in tab[0]]
        width = 0.35
        plt.bar(ind, means, width, color='w', edgecolor='b', yerr=zip(*stds),
                **kwargs)
        plt.xticks(ind+width/2., tuple(tab.labels) )
        #plt.yticks(np.arange(0,81,10))
    else:
        for row in tab:
            if ylist is None:
                cols = (len(row)-1)
                ylist = [None]*cols
                elist = [None]*cols
            x.append(int(row[0]))
            for i in range(cols):
                if ylist[i] is None:
                    ylist[i] = []
                    elist[i] = []
                try:
                    value = row[i+1]
                except IndexError:
                    print "IndexError, %d in %s" % (i+1,row) 
                value.cast(float)
                ylist[i].append(float(value))
                elist[i].append((float(value)-min(value),max(value)-float(value)))

        for col in range(cols):
            if errorbar:
                plt.errorbar(x,ylist[col], yerr=zip(*elist[col]),
                      errorevery=every+(every*col/10.0), **kwargs)
            else:
                plt.plot(x, ylist[col], **kwargs)
        if len(tab.labels[1:]) > 1:
            legend = plt.legend(tab.labels[1:],loc=loc, fontsize=fontsize)
            for line in legend.get_lines():
                line.set_linewidth(legend_linewidth)
    for label in plt.gca().get_xticklabels():
        label.set_fontsize(fontsize)
    for label in plt.gca().get_yticklabels():
        label.set_fontsize(fontsize)
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) == 2:
        plot(sys.argv[1])
    else:
        print "Usage: %s <filename>" % (sys.argv[0],)
