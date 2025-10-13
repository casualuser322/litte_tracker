from django.http import JsonResponse

def healthch(request):
    return JsonResponse({"status": "ok"})