import json
from bson import json_util
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_restx import Resource, Api

from asset_manager.asset_manager import load_config
from asset_manager.database import Database

app = Flask(__name__)
CORS(app)

api = Api(app)

# load config
config = load_config()

# establish database connection
db = Database(
    user=config["mongodb"]["username"],
    password=config["mongodb"]["password"],
    database=config["mongodb"]["database"],
    cluster=config["mongodb"]["cluster"],
)


@api.route("/portfolio")
class Portfolio(Resource):
    def get(self):
        print("request made")
        portfolio_name = request.args.get("name")
        portfolio = db.get_portfolio_by_name(portfolio_name)
        
        return jsonify(json.loads(
            json_util.dumps(portfolio.to_dict())
        ))


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
