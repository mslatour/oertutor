import django.dispatch

ga_err = django.dispatch.Signal(providing_args=["msg","location"])
ga_next_generation = django.dispatch.Signal(providing_args=["generation"])
ga_immigrate = django.dispatch.Signal(providing_args=["generation",
    "worst_individual", "immigrant"])
ga_elite = django.dispatch.Signal(providing_args=["generation", "elite"])
