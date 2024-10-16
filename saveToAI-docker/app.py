import os
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
import scrapetube
from documentdb import MyMongoDB
from processor import Processor, RecursiveCharacterTextSplitter
from langchain_community.document_loaders import YoutubeLoader
from bson import json_util
import json

app = Flask(__name__)
OUTPUT_FOLDER = "output"
SAVE_TO_FILE = False

def sanitize_for_windows_path(input_string):
    # Define a regular expression pattern to match characters not allowed in Windows file paths
    illegal_chars_pattern = r'[<>:"/\\|?*]'

    # Use re.sub to remove all illegal characters
    sanitized_string = re.sub(illegal_chars_pattern, '', input_string)

    return sanitized_string


def try_get_youtube_transcript(processor: Processor, video_id: str, collection: str, vectorize: bool):
    # text_splitter = RecursiveCharacterTextSplitter(chunk_size=2048, chunk_overlap=80, add_start_index=True)
    # try:
    loader = YoutubeLoader(
        video_id=video_id,
        add_video_info=True,
        language=['en', 'en-CA', 'en-US', 'en-UK'],
        translation="en",
    )
    docs = loader.load()
    # for doc in docs:
    #     print("======")
    #     print(doc.page_content)
    #     print(doc.metadata)
    #     print("======")
    processor.process_youtube(collection_name=collection, video_id=video_id, transcript=docs[0].page_content, metadata=docs[0].metadata)
    
    # if vectorize:
    #     video_metadata = processor.process_document(
    #         collection_name=collection,
    #         documents=docs
    #     )

    #     if SAVE_TO_FILE:
    #         author_string = sanitize_for_windows_path(video_metadata["author"])
    #         title_string = sanitize_for_windows_path(video_metadata["title"])
    #         folder_path = os.path.join(os.getcwd(), OUTPUT_FOLDER)
    #         os.makedirs(folder_path, exist_ok=True)
    #         author_path = os.path.join(folder_path, author_string)
    #         os.makedirs(author_path, exist_ok=True)

    #         file_path = os.path.join(author_path, f"{video_id}-{title_string}.txt")
    #         save_to_file(file_path, docs[0].page_content)

    

def save_to_file(file_path: str, content: str):
    try:
        with open(file_path, 'w') as file:
            # print(f"writing: {content}")
            file.write(content)
        print("File written successfully.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    # except Exception as e:
    #     print("Exception: " + str(e))


@app.route('/new_channel_id', methods=['POST'])
def new_youtube_channel():
    data = request.json['message']
    collection = request.json['collection']
    vectorize = request.json['vectorize']
    if collection is None or collection == "":
        collection = "ai_agent"
    if data is not None:
        videos = scrapetube.get_channel(channel_id=data, sort_by="newest", limit=200)
        processor = Processor()

        for video in videos:
            print("processing video_id: " + video['videoId'] + " to collection " + collection)
            try_get_youtube_transcript(processor, video['videoId'], collection, vectorize)

    print("Finished processing youtube channel: " + data)
    return jsonify({"status": "success"}), 200


@app.route('/new_video_id', methods=['POST'])
def new_video_id():
    data = request.json['message']
    collection = request.json['collection']
    vectorize = request.json['vectorize']
    if collection is None or collection == "":
        collection = "ai_agent"
    if data is not None:
        video_id = data
        processor = Processor()
        print("processing video_id: " + video_id + " to collection " + collection)
        try_get_youtube_transcript(processor, video_id, collection, vectorize)
        print("Finished processing youtube video: " + data)
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "error", "message": "No video_id provided"}), 400


@app.route('/new_url', methods=['POST'])
def new_url():
    data = request.json['message']
    collection = request.json['collection']
    vectorize = request.json['vectorize']
    if collection is None or collection == "":
        collection = "ai_agent"
    print("----")
    print("adding url: " + data + " to collection: " + collection)
    print("----")
    if data is not None:
        processor = Processor()
        # save data to mongo
        processor.save_web_content_no_vectorize(collection_name=collection, url=data)
        if vectorize is not None and vectorize == True:
            processor.save_web_content_to_chromadb(collection_name=collection, url=data)
    print("Finished processing url: " + data)
    return jsonify({"status": "success"}), 200


@app.route('/new_text', methods=['POST'])
def new_text():
    data = request.json['message']
    collection = request.json['collection']
    vectorize = request.json['vectorize']
    url = request.json['url']
    if collection is None or collection == "":
        collection = "ai_agent"
    print("----")
    print("adding text: " + data[:50] + " to collection: " + collection)
    print("----")
    if data is not None:
        processor = Processor()
        # save text to mongo
        processor.save_text_no_vectorize(collection_name=collection, text=data, source=url)
        if vectorize is not None and vectorize == True:
            processor.save_text_content_to_chromadb(collection_name=collection, text=data, source=url)
    return jsonify({"status": "success"}), 200


@app.route('/test_insert_mongo', methods=['POST'])
def test_insert_mongo():
    data = request.json
    if not data:
        return jsonify({"error": "an object is required"}), 400
    
    mongo = MyMongoDB()
    inserted_id = mongo.insert(data)
    return jsonify({"status": "success", "inserted_id": inserted_id}), 200

@app.route('/test_query_mongo_id', methods=['GET'])
def test_query_mongo_id():
    id = request.args.get('_id')
    if not id:
        return jsonify({"error": "_id is required"}), 400
    
    mongo = MyMongoDB()
    result = mongo.query_id(id)
    if result:
        # Convert the result to a JSON-serializable format
        result = json.loads(json_util.dumps(result))
        return jsonify({"status": "success", "result": result}), 200
    else:
        return jsonify({"status": "not found"}), 404
    

@app.route('/test_query_mongo_field', methods=['GET'])
def test_query_mongo_field():
    field_name = request.args.get('field_name')
    field_value = request.args.get('field_value')
    if not field_name or not field_value:
        return jsonify({"error": "field_name and field_value are required"}), 400
    
    mongo = MyMongoDB()
    result = mongo.query_field(field_name, field_value)

    if result:
        result = json.loads(json_util.dumps(result))
        return jsonify({"status": "success", "result": result}), 200
    else:
        return jsonify({"status": "not found"}), 404


@app.route('/test_delete_mongo/<document_id>', methods=['DELETE'])
def test_delete_mongo(document_id):
    mongo = MyMongoDB()
    deleted_count = mongo.delete(document_id)
    if deleted_count > 0:
        return jsonify({"status": "success", "deleted_count": deleted_count}), 200
    else:
        return jsonify({"status": "not found"}), 404




if __name__ == "__main__":
    mongo = MyMongoDB()
    CORS(app.run(port=5050, debug=True, use_reloader=False))
