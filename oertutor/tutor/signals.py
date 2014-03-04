import django.dispatch

tutor_session_origin = django.dispatch.Signal(
        providing_args=["origin","data","student"])
