from django.urls import path

from . import views as page_views
from trivia import views as trivia_views

urlpatterns = [
    path('', page_views.index, name='index'),
    path('trivia/questions/', trivia_views.questions, name='trivia_questions'),
    path('trivia/categories/', trivia_views.categories, name='trivia_categories'),
    path('trivia/categories/fetch', trivia_views.rest_fetch_categories, name='trivia_rest_fetch_categories'),
    path('trivia/questions/fetch/<int:category>/<int:amount>/', trivia_views.rest_fetch_questions, name='trivia_rest_fetch_questions'),
    path('trivia/translate_questions/<int:question_id>/', trivia_views.translate_questions, name='trivia_translate')
]