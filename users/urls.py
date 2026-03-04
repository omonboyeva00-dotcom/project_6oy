from django.urls import path


from .views import SignUpView

urlpattern=[
    path('signup/',SignUpView.as_view())
]