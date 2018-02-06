import random
from datetime import datetime

import pymongo.errors
from bson.objectid import ObjectId
from flask_pymongo import PyMongo


class DataMgr(object):

    def __init__(self, flask_app):
        self.__mongo_db = PyMongo(flask_app)

    def add_record(self, user_id, question_id, answer, result):
        record = dict(time=datetime.utcnow(), answer=answer, question=ObjectId(question_id), result=result)
        result = self.__mongo_db.db.users.update_one(dict(_id=user_id), {'$push': dict(records=record),
                                                                         '$currentDate': dict(lastModified=True)})
        if result.modified_count == 1:
            return True
        return False

    def add_question(self, author, stem, options, answer, analysis):
        result = self.__mongo_db.db.questions.insert_one(
            dict(author=author, stem=stem, options=options, answer=answer, analysis=analysis))
        return result.inserted_id

    def add_user(self, user_id):
        try:
            self.__mongo_db.db.users.insert_one(dict(_id=user_id, records=[], lastModified=datetime(1970, 1, 1)))
            return True
        except pymongo.errors.DuplicateKeyError:
            return False

    def is_user_exist(self, user_id):
        result = self.__mongo_db.db.users.find_one(dict(_id=user_id), [])
        return result is None

    def can_user_quiz_today(self, user_id):
        current = datetime.utcnow()
        today = datetime(current.year, current.month, current.day)
        result = self.__mongo_db.db.users.find_one(dict(_id=user_id, lastModified={'$gt': today}), [])
        return result is None

    def get_new_question(self, user_id):
        current = datetime.utcnow()
        today = datetime(current.year, current.month, current.day)
        old_question_id = self.__mongo_db.db.users.distinct('records.question',
                                                            dict(_id=user_id, lastModified={'$gt': today}))
        result = self.__mongo_db.db.questions.find(dict(_id={'$nin': old_question_id}), [])
        count = result.count()
        if count <= 0:
            return None
        return self.__mongo_db.db.questions.find_one(dict(_id=result[random.randint(0, count - 1)]['_id']))

    def get_records(self, user_id):
        pass
