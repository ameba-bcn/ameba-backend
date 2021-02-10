from django.db import models


class Payment(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    amount = models.IntegerField()
    chart_record = models.JSONField()
    details = models.JSONField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
