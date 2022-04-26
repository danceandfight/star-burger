from django.http import JsonResponse


def get_my_ip(request):
    return JsonResponse({
        'ip': request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR'),
    })
