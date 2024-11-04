import datetime

from mongoengine import DateTimeField, Document, StringField, IntField


class Acquisition(Document):
    """
    MongoDB Document for Acquisitions
    """

    name = StringField(required=True) # directAcquisitionName
    description = StringField(required=False) # view['directAcquisitionDescription']
    identification_code = StringField(required=True) # uniqueIdentificationCode
    aquisition_id = StringField(required=True, unique=True) # directAcquisitionId
    publication_date = DateTimeField(default=datetime.datetime.now) # publicationDate
    finalization_date = DateTimeField(default=datetime.datetime.now) # finalizationDate
    cpv_code_id = IntField(required=True) # cpvCode['id']
    cpv_code_text = StringField(required=True) # cpvCode

    meta = {"collection": "acquisitions"}  # Specify the collection name for Acquisition
