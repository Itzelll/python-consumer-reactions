# Import some necessary modules
# pip install kafka-python
# pip install pymongo
# pip install "pymongo[srv]"
from kafka import KafkaConsumer
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import json
import subprocess


# replace here with your mongodb url
uri = "mongodb+srv://itzelll:NtWMhS9DNb1RzPp0@comidas.tv394y9.mongodb.net/?retryWrites=true&w=majority"
# uri = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.8.2"


# Create a new client and connect to the server
# client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection

# try:
#    client.admin.command('ping')
#    print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#    print(e)

# Connect to MongoDB and pizza_data database

try:
    client = MongoClient(uri, server_api=ServerApi("1"))
    client.admin.command("ping")
    print("Pinged your deployment. You successfully connected to MongoDB!")

    db = client.memes
    print("MongoDB Connected successfully!")
except:
    print("Could not connect to MongoDB")

consumer = KafkaConsumer(
    "reactions",
    bootstrap_servers=[
        "comida-kafka-0.comida-kafka-headless.itzel2-itzelll.svc.cluster.local:9092"
        #'localhost:9092'
    ],
)

for msg in consumer:
    record = json.loads(msg.value)
    print(record)
    userId = record["userId"]
    objectId = record["objectId"]
    reactionId = record["reactionId"]

    # Create dictionary and ingest data into MongoDB
    try:
       reaction_rec = {
            'userId': userId,
            'objectId': objectId,
            'reactionId': reactionId
        }
       print (reaction_rec)
       reaction_id = db.memes_reactions.insert_one(reaction_rec)
       print("Data inserted with record ids", reaction_id)
    except:
       print("Could not insert into MongoDB")

  # Create bdnosql_sumary and insert groups into mongodb
    try:
        agg_result = db.memes_reactions.aggregate([
        {
            "$group": {
                "_id": {
                    "objectId": "$objectId",
                    "reactionId": "$reactionId"
                },
                "n": {"$sum": 1}
            }
        }
    ])
        db.memes_sumaryReactions.delete_many({})
        for i in agg_result:
            print(i)
            sumary_id = db.memes_sumaryReactions.insert_one(i)
            print("Sumary Reactions inserted with record ids: ", sumary_id)
            
    except Exception as e:
        print(f'group vy cought {type(e)}: ')
        print(e)

