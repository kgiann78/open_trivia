from django.shortcuts import render
from django.shortcuts import redirect
from django.http import JsonResponse
from django.template.loader import render_to_string

import json
import logging

from .trivia_api_wrapper import TriviaAPIWrapper
from .transifex_api_wrapper import TransifexAPIWrapper
from .trivia_data_wrapper import CategoryDao, QuestionDao
from .models import Category

logger = logging.getLogger(__name__)

def categories(request):
    categoryDao = CategoryDao()

    categories = categoryDao.get_all()
    context = {
        "categories": categories
    }
    return render(request, 'pages/categories.html', context)

def rest_fetch_categories(request):
    trivia = TriviaAPIWrapper()
    categoryDao = CategoryDao()

    status, data = trivia.get_categories()

    if status == 200:
        categoryDao.insert_all(data['trivia_categories'])

    return redirect('trivia_categories')

def questions(request):
    questionDao = QuestionDao()
    categoryDao = CategoryDao()

    questions = questionDao.get_all()
    categories = categoryDao.get_all()

    if request.method == 'POST':
        default_category_id = request.POST.get('category')
        return redirect('trivia_rest_fetch_questions', category=default_category_id, amount=10)

    else:
        try:
            default_category = categoryDao.get_by_name('General Knowledge')
            if default_category:
                default_category_id = default_category.id
                context = {
                    "default_category_id": default_category_id,
                    "categories": categories,
                    "questions": questions
                }

        except Category.DoesNotExist as question_does_not_exist_exception:
            logger.debug(str(question_does_not_exist_exception))
            context = {}

    return render(request, 'pages/questions.html', context)


def rest_fetch_questions(request, category, amount):
    trivia = TriviaAPIWrapper()
    questionDao = QuestionDao()

    status, data = trivia.get_questions(category = category, amount = amount)

    if status == 200 and data['response_code'] == 0:
        questionDao.insert_all(data['results'])
        return redirect('trivia_questions')
    else:
        return JsonResponse({'error':data})

def translate_questions(request, question_id):
    questionDao = QuestionDao()
    transifex = TransifexAPIWrapper()
    question = questionDao.get(question_id)
    questions_list = []

    questions_list.append(question)
    for uploaded_question in questionDao.get_all_uploaded(question.category.id):
        questions_list.append(uploaded_question)

    transifex.manage_source_uploading(questions_list)

    return redirect('trivia_questions')