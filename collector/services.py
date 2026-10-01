from django.db import models, transaction

from collector.models import Request, RequestBody


def as_storable_json(value):
    # Django saves a plain None in a JSONField as SQL NULL; wrap it to keep JSON null.
    if value is None:
        return models.Value(None, output_field=models.JSONField())
    return value


def save_request(env, request_id, user_id, created_at, body):
    """Save a request and its body. Returns ``(request, created)``.

    A repeated ``request_id`` from the same ``env`` (the sender retrying)
    keeps the first copy.
    """
    with transaction.atomic():
        saved_request, created = Request.objects.get_or_create(
            env=env,
            request_id=request_id,
            defaults={"user_id": user_id, "created_at": created_at},
        )
        if created:
            RequestBody.objects.create(request=saved_request, body=as_storable_json(body))
    return saved_request, created
