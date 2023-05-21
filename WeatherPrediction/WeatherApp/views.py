from django.shortcuts import render, redirect
from django.template import RequestContext
from django.contrib.auth import login
import json
import urllib.request
from django.contrib.auth.models import User
from django.contrib import auth
from datetime import datetime, timedelta


# Create your views here.
def index(request):
    return render(request,'index.html')

def weather(request):
    if request.method == 'POST':
        city = request.POST.get('city', 'True')  

        #api call
        source = urllib.request.urlopen('http://api.openweathermap.org/data/2.5/weather?q=' + city + '&units=imperial&appid=50058b73183278a77d3e5ffa8bd55ae9').read()  

        #data into 
        list_of_data = json.loads(source)  
        temperature_fahrenheit = list_of_data['main']['temp']
        temperature_celsius = (temperature_fahrenheit - 32) * 5 / 9
        
         # API call for forecast
        forecast_source = urllib.request.urlopen(
            'http://api.openweathermap.org/data/2.5/forecast?q=' + city + '&units=imperial&appid=50058b73183278a77d3e5ffa8bd55ae9').read()
        forecast_data = json.loads(forecast_source)
        forecast_list = forecast_data['list'][:7]  # Extract forecast data for up to 7 days

        # Convert forecast temperatures to Celsius
        for forecast_item in forecast_list:
            forecast_item['main']['temp'] = round((forecast_item['main']['temp'] - 32) * 5 / 9, 2)


        # Get current time of the requested place
        timezone_offset = list_of_data['timezone']
        current_time = datetime.utcnow() + timedelta(seconds=timezone_offset)
        
        # create dictionary and convert value in string  
        context = {  
            'city': city,  
            "country_code": str(list_of_data['sys']['country']),  
            "coordinate": str(list_of_data['coord']['lon']) + ' '  
                            + str(list_of_data['coord']['lat']),  
            "temp": "{:.2f}°".format(round(temperature_celsius, 2)),  
            "pressure": str(list_of_data['main']['pressure']),  
            "humidity": str(list_of_data['main']['humidity']), 
            "current_time": current_time, 
            "forecast": forecast_list
        }  
    else:  
        context = {}  
      
    # send dictionary to the index.html  
    return render(request, 'weather.html', context)  

def register(request):
    if request.method == "POST":
        if request.POST['password1'] == request.POST['password2']:
            try:
                User.objects.get(username = request.POST['username'])
                return render (request,'register.html', {'error':'Username is already taken!'})
            except User.DoesNotExist:
                user = User.objects.create_user(request.POST['username'],password=request.POST['password1'])
                auth.login(request,user)
                return redirect('index')
        else:
            return render (request,'register.html', {'error':'Password does not match!'})
    else:
        return render(request,'register.html')

def login(request):
    if request.method == 'POST':
        user = auth.authenticate(username=request.POST['username'],password = request.POST['password'])
        if user is not None:
            auth.login(request,user)
            return redirect('weather')
        else:
            return render (request,'login.html', {'error':'Username or password is incorrect!'})
    else:
        return render(request,'login.html')

def logout(request):
    if request.method == 'POST':
        auth.logout(request)
    return redirect('index')