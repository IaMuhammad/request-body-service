import json
from datetime import datetime, timezone

from django.test import TestCase, override_settings
from django.urls import reverse

from collector.models import Request, RequestBody

TOKEN = "test-token"
CREATED_AT = "2026-10-01T10:00:00+00:00"


def make_payload(**overrides):
    payload = {"env": "qa", "request_id": "abc123", "user_id": 7, "created_at": CREATED_AT, "body": {"distance": 5000}}
    payload.update(overrides)
    return payload


@override_settings(COLLECTOR_TOKEN=TOKEN)
class CollectRequestTests(TestCase):
    url = reverse("collect-request")

    def post(self, body, token=TOKEN):
        headers = {"X-Collector-Token": token} if token else {}
        return self.client.post(
            self.url,
            data=body if isinstance(body, str) else json.dumps(body),
            content_type="application/json",
            headers=headers,
        )

    def test_saves_request_and_body(self):
        response = self.post(make_payload())

        self.assertEqual(response.status_code, 201)
        saved_request = Request.objects.get(env="qa", request_id="abc123")
        self.assertEqual(response.json(), {"id": saved_request.id})
        self.assertEqual(saved_request.user_id, 7)
        self.assertEqual(saved_request.created_at, datetime(2026, 10, 1, 10, tzinfo=timezone.utc))
        self.assertEqual(saved_request.body.body, {"distance": 5000})

    def test_accepts_null_user_id_and_non_object_body(self):
        response = self.post(make_payload(user_id=None, body=None))

        self.assertEqual(response.status_code, 201)
        saved_request = Request.objects.get()
        self.assertIsNone(saved_request.user_id)
        self.assertIsNone(saved_request.body.body)

    def test_repeated_id_keeps_first_copy(self):
        self.post(make_payload())

        response = self.post(make_payload(body={"distance": 1}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Request.objects.count(), 1)
        self.assertEqual(RequestBody.objects.get().body, {"distance": 5000})

    def test_same_request_id_from_another_env_is_a_new_request(self):
        self.post(make_payload(env="qa"))

        response = self.post(make_payload(env="prod"))

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Request.objects.count(), 2)

    def test_rejects_invalid_bodies(self):
        invalid_bodies = [
            "not json",
            [1, 2],
            make_payload(env=""),
            make_payload(env=None),
            make_payload(env="x" * 21),
            make_payload(request_id=""),
            make_payload(request_id=5),
            make_payload(request_id="x" * 65),
            make_payload(user_id="7"),
            make_payload(user_id=True),
            make_payload(created_at="yesterday"),
            {"env": "qa", "request_id": "abc123", "user_id": 7, "created_at": CREATED_AT},
        ]
        for body in invalid_bodies:
            with self.subTest(body=body):
                response = self.post(body)
                self.assertEqual(response.status_code, 400)
                self.assertIn("error", response.json())

        self.assertEqual(Request.objects.count(), 0)
        self.assertEqual(RequestBody.objects.count(), 0)

    def test_rejects_bad_token(self):
        for token in ["wrong-token", None]:
            with self.subTest(token=token):
                response = self.post(make_payload(), token=token)
                self.assertEqual(response.status_code, 401)

        self.assertEqual(Request.objects.count(), 0)

    @override_settings(COLLECTOR_TOKEN="")
    def test_skips_token_check_when_not_configured(self):
        response = self.post(make_payload(), token=None)

        self.assertEqual(response.status_code, 201)

    def test_rejects_non_post_methods(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 405)
