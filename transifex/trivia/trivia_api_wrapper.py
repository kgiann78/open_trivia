from django.http import JsonResponse

import requests
from . import transifex_api_wrapper
from . import trivia_data_wrapper

class TriviaAPIWrapper():
    
    def get_categories(self):
        url = 'https://opentdb.com/api_category.php'
        response = requests.get(url)

        if response.status_code == 200:
            self.__write_category_to_db(response.json())

        return (response.status_code, response.json())

    def get_questions(self, category = 9, amount = 10):
        url = f'https://opentdb.com/api.php?category={category}&amount={amount}'

        if category == 0:
            url = f'https://opentdb.com/api.php?amount={amount}'
        
        response = requests.get(url)
        if response.status_code == 200:
            self.__write_questions_to_db(response.json())

        return (response.status_code, response.json())

    def __write_category_to_db(self, data):
        categoryDao = trivia_data_wrapper.CategoryDao()
        for item in data['trivia_categories']:
            categoryDao.insert(item)

    def __write_questions_to_db(self, data):
        questionDao = trivia_data_wrapper.QuestionDao()
        answerDao = trivia_data_wrapper.AnswerDao()
        if data['response_code'] == 0:
            for item in data['results']:
                is_inserted = questionDao.insert(item)
                if is_inserted == True:
                    answerDao.insert(item)