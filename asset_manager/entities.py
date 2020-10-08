from mongoengine import *

class Equity(EmbeddedDocument):
	ticker = StringField(required=True)
	shares = FloatField(required=True)
	weight = FloatField(required=True)
	price = FloatField(required=True)

class Portfolio(Document):
	name = StringField(required=True)
	value = FloatField(required=True)
	equities = ListField(EmbeddedDocumentField(Equity))