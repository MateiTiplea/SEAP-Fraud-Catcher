from django_mongoengine import Document
import datetime
from mongoengine import DateTimeField, IntField, LongField, StringField


class Acquisition(Document):
    """
    MongoDB Document for Acquisitions
    Usage: from api.models.acquisition import Acquisition
    """

    name = StringField(required=True)
    description = StringField(required=False)
    identification_code = StringField(required=True)
    acquisition_id = LongField(required=True, unique=True)
    publication_date = DateTimeField(default=datetime.datetime.now)
    finalization_date = DateTimeField(default=datetime.datetime.now)
    cpv_code_id = IntField(required=True)
    cpv_code_text = StringField(required=True)

    meta = {"collection": "acquisitions"}
