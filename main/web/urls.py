from django.urls import path

from .views import CVDetailView, CVListView, LoginView, LogoutView, RegisterView, HomeView, CVCreateView, CVUpdateView, CVDeleteView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('cvs/', CVListView.as_view(), name='cv_list'),
    path('cv/create/', CVCreateView.as_view(), name='cv_create'),
    path('cv/<int:pk>/', CVDetailView.as_view(), name='cv_detail'),
    path('cv/<int:pk>/edit/', CVUpdateView.as_view(), name='cv_update'),
    path('cv/<int:pk>/delete/', CVDeleteView.as_view(), name='cv_delete'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
]
