"""
Generic utility functions for the genetic algorithm package.
"""
import random
from decimal import Decimal
from datetime import datetime
from pytz import timezone

DEBUG_PROG = 0x1
DEBUG_STEP = 0x2
DEBUG_VALUE = 0x4
DEBUG_SUITE = 0x8
DEBUG_ALL = DEBUG_PROG | DEBUG_STEP | DEBUG_VALUE | DEBUG_SUITE

def debug(message, show):
    if show:
        print "[%s] %s" % (datetime.now(timezone('Europe/Amsterdam')), message)

def pdf_sample(num, individuals, pdf):
    """
    Take num samples out of the list of individuals given a particular pdf.
    The sample is performed by a wheel divided into surfaces corresponding to
    the relative probabilities of each individual. A random pin is placed on
    the wheel and the surface in which the pin ends up determines the sample.
    The pdf doesn't have to be normalized. It will be normalized by dividing
    all the values by the sum. The sum must not be zero.

    Arguments:
      num - The number of samples.
      individuals - The pool of individuals to sample from.
      pdf - The distribution of the individual probabilities.

    Raises:
      ValueError when the sum of the pdf is zero

    Returns:
      A list of num samples.
    """
    # Determine total, for normalizing
    total = sum([pdf(individual) for individual in individuals])
    samples = []
    # Take num samples
    for _ in range(num):
        # Sum must be a nonzero and positive number for the wheel
        if not total > 0:
            # If this is not the case, take a random sample
            samples.append(random.choice(individuals))
        else:
            # Wheel pin
            pin = random.random()
            # Wheel turn
            turn = 0
            for individual in individuals:
                turn += Decimal(pdf(individual))/Decimal(total)
                if turn >= pin:
                    samples.append(individual)
                    break
    return samples
