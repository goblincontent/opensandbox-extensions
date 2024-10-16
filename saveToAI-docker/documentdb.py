from pymongo import MongoClient
from urllib.parse import quote_plus
from bson import ObjectId

class MyMongoDB:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MyMongoDB, cls).__new__(cls)
            cls._instance.client = cls._instance.connect_to_mongo()
            cls._instance.database = "database"
        return cls._instance

    @staticmethod
    def connect_to_mongo():
        username = quote_plus("henryc234")
        password = quote_plus("CZxuF9b8UaRh'qP")
        # cluster_endpoint = "documentdb.cluster-ctwiwi844b3c.ap-southeast-2.docdb.amazonaws.com"
        cluster_endpoint = "localhost"
        port = 27017
        ca_cert = "global-bundle.pem"
        uri = f"mongodb://{username}:{password}@{cluster_endpoint}:{port}"

        return MongoClient(uri,
                           serverSelectionTimeoutMS=5000,
                           tls=True,
                           tlsCAFile=ca_cert,
                           tlsInsecure=True,
                           directConnection=True,
                           replicaSet="rs0",
                           readPreference="secondaryPreferred",
                           retryWrites=False)
    
    def save_text_content_to_mongo(self, collection_name, text, source):
        collection = self.client[self.database][collection_name]
        collection.insert_one({"text": text, "source": source})

    def save_youtube_transcript(self, collection_name, video_id, transcript, metadata):
        collection = self.client[self.database][collection_name]
        document = {
            "video_id": video_id,
            "transcript": transcript,
            "metadata": metadata
        }
        collection.insert_one(document)

    def insert(self, data):
        collection = self.client[self.database]["test_collection"]
        result = collection.insert_one(data)
        return str(result.inserted_id)

    def query_id(self, document_id):
        collection = self.client[self.database]["test_collection"]
        result = collection.find_one({"_id": ObjectId(document_id)})
        return result
    
    def query_field(self, field_name, field_value):
        collection = self.client[self.database]["test_collection"]
        result = collection.find({field_name: field_value})
        return list(result)

    def delete(self, document_id):
        collection = self.client[self.database]["test_collection"]
        result = collection.delete_one({"_id": ObjectId(document_id)})
        return result.deleted_count
