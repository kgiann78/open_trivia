import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'transifex.settings')
os.environ["DJANGO_SETTINGS_MODULE"] = "transifex.settings"

import django
from django.db.models.functions import Coalesce

import logging
django.setup()
logger = logging.getLogger(__name__)

from .models import Category, Question, Answer

class CategoryDao():
    def insert(self, category):
        if not Category.objects.filter(id=category['id']):
            category_model = Category(id=category['id'], name=category['name'])
            category_model.save()
    
    def insert_all(self, categories):
        for category in categories:
            self.insert(category)


    def get_all(self):
        return Category.objects.all()

    def get_by_name(self, name):
        return Category.objects.get(name=name)

class QuestionDao():
    def insert(self, question):

        try:
            qst = Question.objects.get(name=question['question'])
            logger.debug('This question already exists in the DB')
            return False
        except Question.DoesNotExist as question_does_not_exist_exception:
            logger.debug(str(question_does_not_exist_exception))
            try:
                category = Category.objects.get(name=question['category'])
                qst = Question(category=category, name=question['question'])
                qst.save()
            except Category.DoesNotExist as category_does_not_exist_exception:
                logger.error(str(category_does_not_exist_exception))
                return False
            return True
    
    def insert_all(self, questions):
        for question in questions:
            self.insert(question)

    def get_all(self):
        return Question.objects.all().order_by('-id')
    
    def get(self, id):
        return Question.objects.get(id=id)

    def get_by_name(self, name):
        return Question.objects.get(name=name)

    def get_all_uploaded(self, category_id):
        return Question.objects.filter(category__id=category_id,is_uploaded=True)

    
    def get_answers(self, question):
        question_model = Question.objects.get(name=question.name)

        return question_model.answer_set.all()
        

class AnswerDao():
    def insert(self, question):
        qst = Question.objects.get(name=question['question'])
        self.__insert_correct_answer(qst, question['correct_answer'])

        for wrong_answer in question['incorrect_answers']:
            self.__insert_wrong_answer(qst, wrong_answer)

    def __insert_correct_answer(self, question, answer):
        ans = Answer(question=question, name=answer, is_correct_answer=True)
        ans.save()

    def __insert_wrong_answer(self, question, answer):
        ans = Answer(question=question, name=answer, is_correct_answer=False)
        ans.save()