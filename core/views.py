import requests
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth import views as auth_views
from django.utils.decorators import method_decorator
import json

#ALIEXPRESS_API_URL = 'https://api.aliexpress.com/endpoint'  # URL base da API

@login_required
def home(request):
    return render(request, 'home.html')


class SignUpView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'registration/signup.html', {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        return render(request, 'registration/signup.html', {'form': form})
    

class CustomLoginView(auth_views.LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'registration/login.html'


class AliexpressAuthView(View):
    @method_decorator(login_required)
    def get(self, request):
        auth_url = (
            f"https://api-sg.aliexpress.com/oauth/authorize?"
            f"response_type=code&"
            f"force_auth=true&"
            f"redirect_uri={settings.ALIEXPRESS_REDIRECT_URI}&"
            f"client_id={settings.ALIEXPRESS_CLIENT_ID}"
        )
        return redirect(auth_url)

class AliexpressCallbackView(View):
    @method_decorator(login_required)
    def get(self, request):
        code = request.GET.get('code')
        if not code:
            return render(request, 'error.html', {'error': 'Authorization code not found'})
        
        print(f"Authorization Code: {code}")  # Debugging line
        token_url = "https://oauth.aliexpress.com/token"
        payload = {
            'grant_type': 'authorization_code',
            'client_id': settings.ALIEXPRESS_CLIENT_ID,
            'client_secret': settings.ALIEXPRESS_CLIENT_SECRET,
            'code': code,
            'redirect_uri': settings.ALIEXPRESS_REDIRECT_URI,
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        # Test connection to the token endpoint
        try:
            response = requests.post(token_url, data=payload, headers=headers)
            print(f"Response Status Code: {response.status_code}")  # Debugging line
            print(f"Response Content: {response.content}")  # Debugging line

            try:
                response_data = response.json()
                print(f"Token Response JSON: {response_data}")  # Debugging line

                if 'access_token' in response_data:
                    access_token = response_data['access_token']
                    request.session['aliexpress_access_token'] = access_token
                    return redirect('aliexpress_dashboard')
                else:
                    return render(request, 'error.html', {'error': response_data})
            except json.JSONDecodeError as e:
                print(f"JSON Decode Error: {e}")  # Debugging line
                return render(request, 'error.html', {'error': f'Failed to decode JSON response: {response.content}'})
        except requests.exceptions.RequestException as e:
            print(f"Request Exception: {e}")  # Debugging line
            return render(request, 'error.html', {'error': f'Failed to connect to token endpoint: {e}'})

@login_required
def aliexpress_dashboard(request):
    access_token = request.session.get('aliexpress_access_token')
    if not access_token:
        return redirect('aliexpress_auth')

    # Faça chamadas de API usando o access_token
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    product_list_url = 'https://api.aliexpress.com/v1/products'
    response = requests.get(product_list_url, headers=headers)
    products = response.json()

    return render(request, 'aliexpress_dashboard.html', {'products': products})