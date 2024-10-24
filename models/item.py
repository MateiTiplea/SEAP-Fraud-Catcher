from mongoengine import Document, FloatField, ReferenceField, StringField

from models.acquisition import Acquisition


class Item(Document):
    """
    MongoDB Document for Items
    """

    name = StringField(required=True)
    description = StringField(required=True)
    unit_type = StringField(required=True)
    quantity = FloatField(required=True, min_value=0)
    closing_price = FloatField(required=True, min_value=0)

    acquisition = ReferenceField(Acquisition, required=True)

    meta = {"collection": "items"}
