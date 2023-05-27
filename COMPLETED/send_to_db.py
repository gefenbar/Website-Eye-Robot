from pymongo import MongoClient


class MongoDBClient:
    def __init__(self, connection_string, database_name):
        self.client = MongoClient(connection_string)
        self.db = self.client[database_name]

    def insert_document(self, collection_name, document):
        collection = self.db[collection_name]
        exists = collection.find_one_and_delete({'webpageUrl': document['webpageUrl']})
        # Insert the document
        insert_result = collection.insert_one(document)
        inserted_id = insert_result.inserted_id

    def update_array(self, collection_name, webpage_url, resolution, scanner_name, imgUrl, pageUrl):
        collection = self.db[collection_name]
        updated = collection.find_one_and_update(
            {'webpageUrl': webpage_url},  {
                '$push': {
                    'issuesFound': {
                        'resolution': resolution,
                        'scannerName': scanner_name,
                        'img': imgUrl,
                        'pageUrl': pageUrl

                    }
                }
            })

    def find(self, collection_name):
        collection = self.db[collection_name]
        ret = []
        for item in collection.find():
            ret.append(item)
        # print(ret)
        return ret
