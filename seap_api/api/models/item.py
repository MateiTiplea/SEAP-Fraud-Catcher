from mongoengine import Document, FloatField, ReferenceField, StringField, IntField

from models.acquisition import Acquisition


class Item(Document):
    """
    MongoDB Document for Items
    Usage: from api.models.item import Item
    """

    name = StringField(required=True)
    description = StringField(required=True)
    unit_type = StringField(required=True)
    quantity = FloatField(required=True, min_value=0)
    closing_price = FloatField(required=True, min_value=0)
    cpv_code_id = IntField(required=True)
    cpv_code_text = StringField(required=True)

    acquisition = ReferenceField(Acquisition, required=True)

    meta = {"collection": "items"}
