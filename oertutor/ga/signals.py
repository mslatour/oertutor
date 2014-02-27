import django.dispatch

ga_next_generation = django.dispatch.Signal(providing_args=["generation"])
