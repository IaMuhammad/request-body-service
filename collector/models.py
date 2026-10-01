from django.db import models


class Request(models.Model):
    # The backend that sent the request (its MODE setting, e.g. "qa" or "prod").
    env = models.CharField(max_length=20, db_index=True)
    # The request id assigned by the sending backend (its X-Request-ID).
    request_id = models.CharField(max_length=64)
    user_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(db_index=True)

    class Meta:
        db_table = "request"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["env", "request_id"], name="unique_request_per_env"),
        ]

    def __str__(self):
        return f"Request {self.env}/{self.request_id} (user {self.user_id})"


class RequestBody(models.Model):
    request = models.OneToOneField(Request, on_delete=models.CASCADE, related_name="body")
    body = models.JSONField()

    class Meta:
        db_table = "request_body"

    def __str__(self):
        return f"Body of request {self.request_id}"
