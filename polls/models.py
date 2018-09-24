import datetime

from django.db import models
from django.utils import timezone

class Question(models.Model):
  question_text = models.CharField(max_length=200)
  pub_date = models.DateTimeField('date published')
  def __str__(self):
    return self.question_text
  def was_published_recently(self):
    return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

class Choice(models.Model):
  question = models.ForeignKey(Question, on_delete=models.CASCADE)
  choice_text = models.CharField(max_length=200)
  votes = models.IntegerField(default=0)
  def __str__(self):
    return self.choice_text

class Algo(models.Model):
  name = models.CharField(max_length=200)
  signal = models.CharField(max_length=200)
  trade = models.CharField(max_length=200)
  ticker = models.CharField(max_length=200)

class Trend(models.Model):
  algo = models.ForeignKey(Algo, on_delete=models.CASCADE)
  position = models.IntegerField(default=0)
  pnl = models.FloatField(default=0)
