from django.shortcuts import render

app_name = 'pages'


def about(request):
    template = 'pages/about.html'
    context = {'request': request}
    return render(request, template, context)


def rules(request):
    template = 'pages/rules.html'
    context = {'request': request}
    return render(request, template, context)
