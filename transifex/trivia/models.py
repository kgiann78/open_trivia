from django.db import models
from django.core.validators import validate_comma_separated_integer_list

class Category(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Question(models.Model):
    name = models.CharField(max_length=256)
    is_uploaded = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.name

class Answer(models.Model):
    name = models.CharField(max_length=256)
    is_correct_answer = models.BooleanField()
    question = models.ForeignKey(Question, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.name
