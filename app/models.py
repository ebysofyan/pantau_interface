from django.db import models

# Create your models here.


class TimeCrawling(models.Model):
    """
    Time Crawling
    """
    time_server = models.CharField(max_length=45)
    total_nolsatu = models.CharField(max_length=100, default='0')
    total_noldua = models.CharField(max_length=100, default='0')
    create_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    modify_at = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return self.time_server

    class Meta:
        db_table = 'time_crawling'
        ordering = ['-time_server']


class Voting(models.Model):
    """
    Voting table schema
    """
    code = models.CharField(max_length=45)
    region = models.CharField(max_length=100)
    value1 = models.CharField(max_length=20)
    value2 = models.CharField(max_length=20)
    time = models.ForeignKey(TimeCrawling, on_delete=models.SET_NULL, null=True, related_name='votings')

    def __str__(self):
        return f'{self.region} : {self.value1}, {self.value2}'

    class Meta:
        db_table = 'voting'
