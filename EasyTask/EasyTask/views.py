from django.http import JsonResponse
from django.db import connection

def health_check(request):
    try:
        # Run a simple DB query
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()

        return JsonResponse({"status": "ok", "database": "connected"}, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "database": str(e)}, status=500)