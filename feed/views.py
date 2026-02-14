from django.shortcuts import render

def custom_404_view(request, exception):
    return render(request, 'pages/404.html', status=404)

def custom_500_view(request):
    return render(request, 'pages/500.html', status=500)