from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models import StoreModel
from schemas import StoreSchema, ItemSchema


blp = Blueprint("Stores", __name__, description="Operations on stores")


@blp.route("/store/<string:store_id>")
class Store(MethodView):
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store

    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        return {"message": "store deleted"}

# @blp.route("/store")
# class StoreList(MethodView):
#     @blp.response(200, ItemSchema(many=True))
#     def get(self):
#         raise NotImplementedError("Listing stores is not implemented.")

#     @blp.arguments(StoreSchema)
#     @blp.response(201, StoreSchema)
#     def post(self, store_data):
#         raise NotImplementedError("Creating a store is not implemented.")


@blp.route("/store")
class StoreList(MethodView):
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()

    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, store_data):
        # store_data = request.get_json()
        # if "name" not in store_data:
        #     abort(
        #         400,
        #         message="Bad request. Ensure 'name' is included in the JSON payload.",
        #     )
        # for store in stores.values():
        #     if store_data["name"] == store["name"]:
        #         abort(400, message=f"Store already exists.")

        # store_id = uuid.uuid4().hex
        # store = {**store_data, "id": store_id}
        # stores[store_id] = store
        store = StoreModel(**store_data)
        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(500, message="That name already exist")
        except SQLAlchemyError:
            abort(500, message="An error occurred")
        return store


# import uuid
# from flask import request
# from flask.views import MethodView
# from flask_smorest import Blueprint, abort

# from db import db
# from models import ItemModel
# from schemas import ItemSchema, ItemUpdateSchema

# from schemas import StoreSchema

# blp = Blueprint("stores", __name__, description="operations on stores")


# @blp.route("/store/<string:store_id>")
# class Store(MethodView):
#     @blp.response(200, StoreSchema)
#     def get(self, store_id):
#         try:
#             # You presumably would want to include the store's items here too
#             # More on that when we look at databases
#             return stores[store_id]
#         except KeyError:
#             abort(404, message="Store not found.")

#     def delete(self, store_id):
#         try:
#             del stores[store_id]
#             return {"message": "Store deleted."}
#         except KeyError:
#             abort(404, message="Store not found.")
