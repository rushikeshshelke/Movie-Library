import os

from flask import Flask
from dotenv import load_dotenv
from moviewatchlist.routes import routes
from moviewatchlist.commonLibs.globalVariables import GlobalVariables
from moviewatchlist.commonLibs.initialiseLogging import InitialiseLogging
from pymongo import MongoClient

load_dotenv()
app = Flask(__name__)
InitialiseLogging().setupLogging()
app.secret_key = os.environ.get("SECRET_KEY")
app.register_blueprint(routes.pages)
GlobalVariables.LOGGER.info("Movie Watch List App")
client = MongoClient(os.environ.get("MONGODB_URI"))
app.db = client.get_database(os.environ.get("DATABASE_NAME"))

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT")),debug=True)