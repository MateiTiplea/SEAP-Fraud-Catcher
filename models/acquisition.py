import datetime

from mongoengine import DateTimeField, Document, StringField


class Acquisition(Document):
    """
    MongoDB Document for Acquisitions
    """

    name = StringField(required=True)
    description = StringField(required=False)
    identification_code = StringField(required=True)
    aquisition_id = StringField(required=True, unique=True)
    publication_date = DateTimeField(default=datetime.datetime.now)
    finalization_date = DateTimeField(default=datetime.datetime.now)

    meta = {"collection": "acquisitions"}  # Specify the collection name for Acquisition
