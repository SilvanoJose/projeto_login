from django.urls import path
from .views import SignUpView, CustomLoginView, home, AliexpressAuthView, AliexpressCallbackView, aliexpress_dashboard
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', home, name='home'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('aliexpress/auth/', AliexpressAuthView.as_view(), name='aliexpress_auth'),
    path('aliexpress/callback/', AliexpressCallbackView.as_view(), name='aliexpress_callback'),
    path('aliexpress/dashboard/', aliexpress_dashboard, name='aliexpress_dashboard'),
]
