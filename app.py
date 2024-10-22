# import uuid
# from flask import Flask, request
# from flask_smorest import abort
# from db import items, stores
from flask import Flask
from flask_smorest import Api
from flask import Flask, jsonify
from blocklist import BLOCKLIST
from flask_migrate import Migrate
import os

from db import db
import models
from flask_jwt_extended import JWTManager

from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint


def create_app(db_url=None):
    app = Flask(__name__)

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url or os.getenv(
        "DATABASE_URL", "sqlite:///data_empty.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate = Migrate(app, db)

    api = Api(app)

    app.config["JWT_SECRET_KEY"] = "daniel"
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "description": "The token is not fresh.",
                    "error": "fresh_token_required",
                }
            ),
            401,
        )

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The token has been revoked.",
                    "error": "token_revoked"}
            ),
            401,
        )

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "The token has expired.",
                    "error": "token_expired"}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed.", "error": "invalid_token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token.",
                    "error": "authorization_required",
                }
            ),
            401,
        )

    with app.app_context():
        db.create_all()
    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)

    return app


# @app.get("/stores")
# def getStores():
#     return {"stores": list(stores.values())}


# @app.get("/store/<string:id>")
# def getStore(id):
#     try:
#         return {"name": stores[id]}, 200
#     except KeyError:
#         abort(404, message="Store not found")


# @app.post("/store")
# def addStore():
#     json = request.get_json()
#     id = uuid.uuid4().hex
#     new_store = {**json, "id": id}
#     stores[id] = new_store
#     return new_store, 201


# @app.delete("/store/<string:id>")
# def deleteStore(id):
#     try:
#         del stores[id]
#         return {"message": "Store deleted"}, 201
#     except KeyError:
#         abort(404, message="Store not found")


# @app.get("/items")
# def getItems():
#     return {"items": list(items.values())}


# @app.post("/item")
# def createItem():
#     json = request.get_json()
#     if json["id"] not in stores:
#         abort(404, message="Store not found")
#     item_id = uuid.uuid4().hex
#     new_item = {**json, "id": item_id}
#     items[item_id] = new_item
#     return new_item, 201


# @app.get("/item/<string:id>")
# def getItem(id):
#     try:
#         return items[id], 200
#     except KeyError:
#         abort(404, message="Item not found")


# @app.put("/item/<string:id>")
# def updateItem(id):
#     try:
#         json = request.get_json()
#         item = items[id]
#         item |= json
#         return item
#     except KeyError:
#         abort(404, message="Store not found")


# @app.delete("/item/<string:id>")
# def deleteItem(id):
#     try:
#         del items[id]
#         return {"message": "Item deleted"}, 201
#     except KeyError:
#         abort(404, message="Item not found")
