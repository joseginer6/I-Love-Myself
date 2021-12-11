# -*- coding: UTF-8 -*-
import pymongo, time, traceback
from bson.objectid import ObjectId
from pymongo import MongoClient
from datetime import datetime
from pymongo import IndexModel, ASCENDING, DESCENDING



mg_user = "jmarato"
mg_pass = "jmarato123"
mg_port = "@cluster0.xsnn4.mongodb.net"
mg_name = "JMarato"
mg_host = "JMarato?retryWrites=true&w=majority"



def get_all_documents_mdb(collection, filter = {}, query_limit = 1, skip = 0):	
	try:
		client = pymongo.MongoClient("mongodb+srv://" + mg_user + ":" + mg_pass + mg_port + "/" + mg_host)
		db = client[mg_name]
		coll = db[collection]
		
		# for documento in coll.find(filter):
		# 	print("FOR")
		# 	print(documento)

		return coll.find(filter)
	except Exception as e:
		print ("Could not connect to the database:  ", e, traceback.format_exc())



def update_many_documents_many_fields_mdb(collection,filter = {}, fields = {},upsert = False):
	print(upsert)
	try:
		client = pymongo.MongoClient("mongodb+srv://" + mg_user + ":" + mg_pass + mg_port + "/" + mg_host)
		db = client[mg_name]
		coll = db[collection]
		print(upsert)
		coll.update_many(filter, {"$set": fields}, upsert=False)

	except Exception as e:
		print ("Could not connect to the database:  ", e, traceback.format_exc())



def update_many_documents_mdb(collection,docs,upsert = False):
	print(upsert)
	try:
		client = pymongo.MongoClient("mongodb+srv://" + mg_user + ":" + mg_pass + mg_port + "/" + mg_host)
		db = client[mg_name]
		coll = db[collection]
		print(upsert)

		for doc in docs:
			try:
				coll.update({'_id': doc['_id']}, doc, upsert , False)
			except Exception as e:
				print ("Could not update the apartment:  ", e, traceback.format_exc())
	except Exception as e:
		print ("Could not connect to the database:  ", e, traceback.format_exc())


def insert_many_documents_mdb(collection, docs):
	try:
		client = pymongo.MongoClient("mongodb+srv://" + mg_user + ":" + mg_pass + mg_port + "/" + mg_host)
		db = client[mg_name]
		coll = db[collection]

		coll.insert_many(docs, ordered=False)
		print(str(len(docs)) + ' new docs ')

	except pymongo.errors.BulkWriteError as bwe:
		print(str(bwe.details["nInserted"]) + ' new docs')
	
	# return status


def update_document_mdb(collection, doc):
	try:
		client = pymongo.MongoClient("mongodb+srv://" + mg_user + ":" + mg_pass + mg_port + "/" + mg_host)
		db = client[mg_name]
		coll = db[collection]

		coll.update({'_id': doc['_id']}, {"$set": doc}, True)

	except Exception as e:
		print ('Could not connect to the database:  ', e, traceback.format_exc())


def get_document_mdb(collection, doc_id, ObjectId_format = False):
	try:
		client = pymongo.MongoClient("mongodb+srv://" + mg_user + ":" + mg_pass + mg_port + "/" + mg_host)
		db = client[mg_name]
		coll = db[collection]

		if ObjectId_format:
			doc = coll.find_one({'_id': ObjectId(doc_id)})
		else:
			doc = coll.find_one({'_id': doc_id})

		return doc

	except Exception as e:
		print ("Could not connect to the database:  ", e, traceback.format_exc())


def get_document_with_projection_mdb(collection, doc_id, projection = {}, ObjectId_format = False):

	try:
		client = pymongo.MongoClient("mongodb+srv://" + mg_user + ":" + mg_pass + mg_port + "/" + mg_host)
		db = client[mg_name]
		coll = db[collection]


		if ObjectId_format:
			doc = coll.find_one({'_id': ObjectId(doc_id)},projection)
		else:
			doc = coll.find_one({'_id': doc_id},projection)

		return doc

	except Exception as e:
		print ("Could not connect to the database:  ", e, traceback.format_exc())



def update_document_field_mdb(collection, doc_id, field_name, field_value):

	try:
		client = pymongo.MongoClient("mongodb+srv://" + mg_user + ":" + mg_pass + mg_port + "/" + mg_host)
		db = client[mg_name]
		coll = db[collection]

		coll.update({'_id': doc_id}, {"$set": {field_name: field_value}}, upsert=False)
		
		return True
		
	except Exception as e:
		print ("Could not connect to the database: ", e, traceback.format_exc())
		return False


def update_document_many_fields_mdb(collection, doc_id, fields = {}):
	try:
		client = pymongo.MongoClient("mongodb+srv://" + mg_user + ":" + mg_pass + mg_port + "/" + mg_host)
		db = client[mg_name]
		coll = db[collection]

		coll.update({'_id': doc_id}, {"$set": fields}, upsert=False)
		
		return True
		
	except Exception as e:
		print ("Could not connect to the database: ", e, traceback.format_exc())
		return False


def insert_document_mdb(collection, doc):
	try:
		client = pymongo.MongoClient("mongodb+srv://" + mg_user + ":" + mg_pass + mg_port + "/" + mg_host)
		db = client[mg_name]
		coll = db[collection]

		coll.insert_one(doc)
		return True

	except pymongo.errors.DuplicateKeyError as de:
		if de.code == 11000: print('0 new docs')
		return False



