from mongoengine import Document, FloatField, ReferenceField, StringField, IntField

from models.acquisition import Acquisition


class Item(Document):
    """
    MongoDB Document for Items
    """

    name = StringField(required=True) # view['directAcquisitionItems'][i]['catalogItemName']
    description = StringField(required=True) # view['directAcquisitionItems'][i]['catalogItemDescription']
    unit_type = StringField(required=True) # view['directAcquisitionItems'][i]['itemMeasureUnit']
    quantity = FloatField(required=True, min_value=0) # view['directAcquisitionItems'][i]['itemQuantity']
    closing_price = FloatField(required=True, min_value=0) # view['directAcquisitionItems'][i]['itemClosingPrice']
    cpv_code_id = IntField(required=True)
    cpv_code_text = StringField(required=True)

    acquisition = ReferenceField(Acquisition, required=True)

    meta = {"collection": "items"}

    def __str__(self):
        """
        Return a string representation of the Item.
        """
        return self.name
