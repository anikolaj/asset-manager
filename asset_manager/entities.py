from mongoengine import StringField, FloatField, ListField, EmbeddedDocumentField
from mongoengine import Document, EmbeddedDocument
from mongoengine.fields import IntField

class Valuation(EmbeddedDocument):
	currentYear = IntField(required = True)
	yearStartValue = FloatField()
	currentValue = FloatField()
	ytd = FloatField()

class Equity(EmbeddedDocument):
	ticker = StringField(required=True)
	shares = FloatField(required=True)
	weight = FloatField(required=True)
	price = FloatField(required=True)
	yearStartPrice = FloatField()

class Portfolio(Document):
	name = StringField(required=True)
	value = FloatField(required=True)
	equities = ListField(EmbeddedDocumentField(Equity))
	valuation = EmbeddedDocumentField(Valuation)