import pymongo

def get_databse():

    CONNECTION_STRING = "mongodb://localhost:27017/"

    client = pymongo.MongoClient(CONNECTION_STRING)


    return client['Expences tracker']

if __name__ == "__main__":
    db = get_databse()
    print("Successfully connected to:", db.name)
  