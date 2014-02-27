import django.dispatch

ga_next_generation = django.dispatch.Signal(providing_args=["generation"])
ga_immigrate = django.dispatch.Signal(providing_args=["generation",
    "worst_individual", "immigrant"])
