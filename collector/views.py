import json

from django.conf import settings
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from collector.services import save_request
from collector.validators import validate_payload

TOKEN_HEADER = "X-Collector-Token"


def has_valid_token(request):
    expected_token = settings.COLLECTOR_TOKEN
    if not expected_token:
        return True
    return request.headers.get(TOKEN_HEADER) == expected_token


@csrf_exempt
@require_POST
def collect_request(request):
    if not has_valid_token(request):
        return JsonResponse({"error": "Invalid token."}, status=401)

    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Body must be valid JSON."}, status=400)

    error_message = validate_payload(payload)
    if error_message:
        return JsonResponse({"error": error_message}, status=400)

    saved_request, created = save_request(
        env=payload["env"],
        request_id=payload["request_id"],
        user_id=payload.get("user_id"),
        created_at=parse_datetime(payload["created_at"]),
        body=payload["body"],
    )
    return JsonResponse({"id": saved_request.id}, status=201 if created else 200)
