from django.urls import include, path

from . import views

urlpatterns = [
    path('', include('user_auth_app.api.urls'))
]