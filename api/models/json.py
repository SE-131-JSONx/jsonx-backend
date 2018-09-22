from sqlalchemy import ForeignKeyConstraint
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
from api.utils.database import db

db = SQLAlchemy(app)

class Json(db.Model):
	__tablename__='json_table'

	id = db.Column(db.BigInteger, primary_key = True, autoincrement=True)
	data = db.Column(db.String(10000))
	created = db.Column(db.DateTime, server_default=db.func.now())
	updated = db.Column(db.DateTime, onupdate=db.func.now())

	def __init__(self,data):
		self.data=data

	def create(self):
		db.session.add(self)
		db.session.commit()
		return self

class JsonSchema(ModelSchema):
	class Meta(ModelSchema.Meta):
		model = Json
		sqla_session = db.session

	id = fields.Integer(dump_onyl=True)
	data = fields.String(required=True)
	created = fields.DateTime(dump_only=True)
	updated = fields.DateTIme(dump_only=True)