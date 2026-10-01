from django.utils.dateparse import parse_datetime

ENV_MAX_LENGTH = 20
REQUEST_ID_MAX_LENGTH = 64


def validate_payload(payload):
    """Return an error message, or None when the payload is valid."""
    if not isinstance(payload, dict):
        return "Body must be a JSON object."

    env = payload.get("env")
    if not isinstance(env, str) or not env.strip():
        return "'env' must be a non-empty string."
    if len(env) > ENV_MAX_LENGTH:
        return f"'env' must be at most {ENV_MAX_LENGTH} characters."

    request_id = payload.get("request_id")
    if not isinstance(request_id, str) or not request_id.strip():
        return "'request_id' must be a non-empty string."
    if len(request_id) > REQUEST_ID_MAX_LENGTH:
        return f"'request_id' must be at most {REQUEST_ID_MAX_LENGTH} characters."

    user_id = payload.get("user_id")
    is_integer = isinstance(user_id, int) and not isinstance(user_id, bool)
    if user_id is not None and not is_integer:
        return "'user_id' must be an integer or null."

    created_at = payload.get("created_at")
    if not isinstance(created_at, str) or parse_datetime(created_at) is None:
        return "'created_at' must be an ISO 8601 datetime."

    if "body" not in payload:
        return "'body' is required."

    return None
