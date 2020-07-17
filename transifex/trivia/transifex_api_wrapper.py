from django.conf import settings
from django.utils.text import slugify

import requests
import json
import time

from . import convert_nested_json
from .trivia_data_wrapper import QuestionDao

class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token
    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r

class TransifexAPIWrapper():
    questionDao = QuestionDao()

    def sanitize(self, subject):
        return slugify(subject.replace("/", "-").replace("_", "-"))

    def manage_source_uploading(self, questions_list):
        questions_per_resources = self.__prepare_resources(questions_list)
        resources_strings = self.__convert_paths(questions_per_resources)
        uploaded_ids = self.__upload_files(self.__create_resource_files(resources_strings))

        if len(uploaded_ids) > 0:
            for source_id in uploaded_ids:
                self.__check_for_source_string(source_id)

    def upload(self, resource):
        url = 'https://rest.api.transifex.com/resource_strings_async_uploads'
        
        content = "{}"
        with open(f'/tmp/{resource}.json', 'r') as resources_file:
            content = resources_file.readline()
            resources_file.close()

        payload = {
                    "data": {
                            "attributes": {
                            "content": content,
                            "content_encoding": "text"
                        },
                        "relationships": {
                            "resource": {
                                "data": {
                                    "id": "o:" + settings.TRANSIFEX_ORGANIZATION + ":p:" + settings.TRANSIFEX_PROJECT + ":r:" + resource,
                                    "type": "resources"
                                }
                            }
                        },
                        "type": "resource_strings_async_uploads"
            }
        }
        response = self.__post_message(url, payload)
        return response.json()['data']['id']

    def get_resources(self, organization, project):
        url = f'https://rest.api.transifex.com/resources?filter[project]=o:{organization}:p:{project}'
        response = requests.get(url, auth=BearerAuth(settings.TRANSIFEX_TOKEN))

        return (response.status_code, response.json())

    def create_resource(self, organization, project, resource_name):
        resource_name_slug = self.sanitize(resource_name)

        url = 'https://rest.api.transifex.com/resources'
        payload = {
            "data": {
                "attributes": {
                    "accept_translations": True,
                    "categories": [
                        "test"
                    ],
                    "i18n_type": "KEYVALUEJSON",
                    "name": resource_name,
                    "priority": "normal",
                    "slug": resource_name_slug
                },
                "relationships": {
                    "project": {
                        "data": {
                            "id": "o:" + organization + ":p:" + project,
                            "type": "projects"
                        }
                    }
                },
                "type": "resources"
            }
        }

        self.__post_message(url, payload)

    def __check_resources_for_category(self, organization, project, category_name):
        status_code, resources = self.get_resources(organization, project)
        found = False
        if status_code == 200:
            for resource in resources['data']:
                if resource['attributes']['name'] == category_name:
                    found = True
                    break
        
        return found

    def __prepare_resources(self, questions):
        questions_per_resources = {}

        for question in questions:
            fields_for_translation = {}

            if not self.__check_resources_for_category(settings.TRANSIFEX_ORGANIZATION, settings.TRANSIFEX_PROJECT, question.category.name):
                self.create_resource(settings.TRANSIFEX_ORGANIZATION, settings.TRANSIFEX_PROJECT, question.category.name)
            
            if question.category.name not in questions_per_resources:
                questions_per_resources[question.category.name] = []
            
            self.__append_fields_for_translation(fields_for_translation, question)

            questions_per_resources[question.category.name].append(fields_for_translation)

        return questions_per_resources

    def __append_fields_for_translation(self, fields_for_translation, question):
        fields_for_translation['question']=question.name
        fields_for_translation['incorrect_answers'] = []

        for answer in question.answer_set.all():
            if not answer.name.isnumeric() and not answer.name.isdecimal():
                if answer.is_correct_answer:
                    fields_for_translation['correct_answer'] = answer.name
                else:
                    fields_for_translation['incorrect_answers'].append(answer.name)


    def __convert_paths(self, questions_per_resources):

        resources_strings = {}

        for key in questions_per_resources:
            if key not in resources_strings:
                resources_strings[key] = []

            for item in convert_nested_json.generate_hashes_with_strings(questions_per_resources[key]):
                resources_strings[key].append(item)

        return resources_strings

    def __create_resource_files(self, questions):
        resources = []
        for category in questions.keys():    
            category_slug = self.sanitize(category)
            
            with open(f'/tmp/{category_slug}.json', 'w') as resources_file:
                resources_file.write('{')
                length = len(questions[category])
                for i in range(0, length-1):
                    item = questions[category][i]
                    resources_file.write(f'\"{item[0]}\":\"{item[1]}\",')
                item = questions[category][length-1]
                resources_file.write(f'\"{item[0]}\":\"{item[1]}\"')
                resources_file.write('}')
                resources_file.close()
                resources.append(category_slug)

        return resources

    def __upload_files(self, resources):
        uploaded_ids = []

        for resource in resources:
            resource_strings_async_upload_id = self.upload(resource)
            uploaded_ids.append(resource_strings_async_upload_id)
        
        return uploaded_ids

    def __check_for_source_string(self, source_id):
            if source_id == 0:
                return
            else:
                data = self.__check_resources_uploading_status(source_id)
                if data:
                    status = self.__check_resource_status(data['data'])
                    while status and status == 'processing':
                        time.sleep(.5)
                        data = self.__check_resources_uploading_status(source_id)
                        
                        status = self.__check_resource_status(data['data'])
                        if not status:
                            return

    def __check_resource_status(self, data):      
        if isinstance(data, list):
            self.__mark_question_as_uploaded(data)    
            return
        elif isinstance(data, dict):
            if 'status' in data['attributes']:
                status = data['attributes']['status']
                return status                     

    def __mark_question_as_uploaded(self, sources):
        for source in sources:
            if source['attributes']['key'] == 'b\'\\.\\.0\\.\\.\\.question:\'':
                name = source['attributes']['strings']['other']
                question = self.questionDao.get_by_name(name)
                question.is_uploaded = True
                question.save()

    def __check_resources_uploading_status(self, resource_strings_async_upload_id):
        url = f'https://rest.api.transifex.com/resource_strings_async_uploads/{resource_strings_async_upload_id}'
        response = requests.get(url, auth=BearerAuth(settings.TRANSIFEX_TOKEN))
        return response.json()

    def __post_message(self, url, payload, content_type='application/vnd.api+json'):
        datum = json.dumps(payload)
        response = requests.post(url, auth=BearerAuth(settings.TRANSIFEX_TOKEN), data=datum, headers={'content-type': content_type})
        return response