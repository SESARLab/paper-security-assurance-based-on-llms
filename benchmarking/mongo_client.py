import os, re
from dotenv import load_dotenv 
from pymongo import MongoClient

load_dotenv()

# API to interact with the Probe DB (it contains probes info + prompt templates) and do RAG

def connect_to_probedb():
    try:
        client = MongoClient("mongodb://confgen:confgen@localhost:27017/admin")
        return client
    except Exception as e:
        print(f"Error: {e}")
        return 0


def upload(collection, document):
    try:
        result = collection.insert_one(document)
        print(f"Document inserted with ID: {result.inserted_id}")
    except Exception as e:
        print(f"Error uploading document: {e}")

def update(collection, probe_name, update_fields):
    try:
        query = {"probeName": probe_name}
        
        update = {"$set": update_fields}
        
        result = collection.update_one(query, update)
        
        if result.matched_count > 0:
            print(f"Document with probeName '{probe_name}' updated successfully.")
        else:
            print(f"No document found with probeName '{probe_name}'.")
    except Exception as e:
        print(f"Error updating document: {e}")


def drop_collection(collection):
    try:
        collection.drop()
        print("Collection dropped successfully.")
    except Exception as e:
        print(f"Error dropping collection: {e}")


def get_document(collection, query={}, multiple=False):
    try:
        if multiple:
            # Return all matching documents as a list
            return list(collection.find(query))
        else:
            # Return a single matching document
            return collection.find_one(query)
    except Exception as e:
        print(f"Error retrieving document(s): {e}")
        return None

