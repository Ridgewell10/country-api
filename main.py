from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy, BaseQuery

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class QueryWithSoftDelete(BaseQuery):
    _with_deleted = False

    def __new__(cls, *args, **kwargs):
        obj = super(QueryWithSoftDelete, cls).__new__(cls)
        obj._with_deleted = kwargs.pop('_with_deleted', False)
        if len(args) > 0:
            super(QueryWithSoftDelete, obj).__init__(*args, **kwargs)
            return obj.filter_by(deleted=False) if not obj._with_deleted else obj
        return obj

    def __init__(self, *args, **kwargs):
        pass

    def with_deleted(self):
        return self.__class__(self._only_full_mapper_zero('get'),
                              session=db.session(), _with_deleted=True)

    def _get(self, *args, **kwargs):
        return super(QueryWithSoftDelete, self).get(*args, **kwargs)

    def get(self, *args, **kwargs):
        obj = self.with_deleted()._get(*args, **kwargs)
        return obj if obj is None or self._with_deleted or not obj.deleted else None

class CountryModel(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	country_name = db.Column(db.String(30), nullable=False)
	alpha_2_code = db.Column(db.String(5), nullable=False)
	alpha_3_code = db.Column(db.String(5), nullable=False)
	currencies = db.Column(db.String(5), nullable = False)
	deleted = db.Column(db.Boolean(), default = False)

	query_class = QueryWithSoftDelete

#db.create_all()

	def __repr__(self):
		return f"Country(country_name = {self.country_name}, alpha_2_code = {self.alpha_2_code}, alpha_3_code = {self.alpha_3_code},currencies = {self.currencies})"

country_put_args = reqparse.RequestParser()
country_put_args.add_argument("country_name", type=str, help="Name of the country is required", required=True)
country_put_args.add_argument("alpha_2_code", type=str, help="Alpha 2 code is required", required=True)
country_put_args.add_argument("alpha_3_code", type=str, help="Alpha 3 is required", required=True)
country_put_args.add_argument("currencies", type=str, help="Currencies is required", required=True)

country_update_args = reqparse.RequestParser()
country_update_args.add_argument("country_name", type=str, help="Name of the country is required", required=True)
country_update_args.add_argument("alpha_2_code", type=str, help="Alpha 2 code is required", required=True)
country_update_args.add_argument("alpha_3_code", type=str, help="Alpha 3 is required", required=True)
country_update_args.add_argument("currencies", type=str, help="Currencies is required", required=True)

resource_fields = {
	'id': fields.Integer,
	'country_name': fields.String,
	'alpha_2_code': fields.String,
	'alpha_3_code': fields.String,
	'currencies': fields.String
}

#def abort_if_country_id_doesnt_exist(country_id):
#	if country_id not in CountryModel:
#		abort(404, message="Country id is not valid")

class Country(Resource):
	@marshal_with(resource_fields)
	def get(self, country_id):
		result = CountryModel.query.filter_by(id=country_id).first()
		if not result:
			abort(404, message="Could not find country with that id")
		return result

	@marshal_with(resource_fields)
	def get(self, country):
		result = CountryModel.query.filter_by(country).first()
		if not result:
			abort(404)
		return result

	@marshal_with(resource_fields)
	def put(self, country_id):
		args = country_put_args.parse_args()
		result = CountryModel.query.filter_by(id=country_id).first()
		if result:
			abort(409, message="Country id already exists...")
		country = CountryModel(id=country_id, country_name=args['country_name'], alpha_2_code=args['alpha_2_code'], alpha_3_code=args['alpha_3_code'], currencies= args['currencies'])
		db.session.add(country)
		db.session.commit()
		return country, 201

	@marshal_with(resource_fields)
	def patch(self, country_id):
		args = country_update_args.parse_args()
		result = CountryModel.query.filter_by(id=country_id).first()
		if not result:
			abort(404, message="Country doesn't exist, cannot update")

		if args['country_name']:
			result.country_name = args['country_name']
		if args['alpha_2_code']:
			result.alpha_2_code = args['alpha_2_code']
		if args['alpha_3_code']:
			result.alpha_3code = args['alpha_3_code']
		if args['currencies']:
			result.currencies = args['currencies']
		
##		db.session.add(result) no need to re-add i think read more
		db.session.commit()

		return result

	def delete(self, country_id):
#		abort_if_country_id_doesnt_exist(country_id)
		country = CountryModel.query.filter_by(id=country_id).first()
		if country.deleted:
			abort(404)			
		country.deleted = True		
		db.session.commit()
		return '', 204

api.add_resource(Country, "/country/<int:country_id>")

if __name__ == "__main__":
	app.run(debug=True)