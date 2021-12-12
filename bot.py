import copy
import datetime
import glob
import os
import time
import traceback

import pytz
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
					  KeyboardButton, LabeledPrice, ParseMode,
					  ReplyKeyboardMarkup, TelegramObject, replymarkup)
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
						  JobQueue, MessageHandler, PreCheckoutQueryHandler,
						  ShippingQueryHandler, Updater)

import connect_to_mongodb
import random


iconoAcabados = ' ☑'
spanish = ' 🇪🇸'
english = ' 🇬🇧'
catalan = ' 🏴󠁥󠁳󠁣󠁴󠁿'

veryHappy = ' 😊'
happy = ' 🙂'
notHappy = ' 😐'
sad = ' 😔'

def generateKeyBoards(options):
	final_keyboard = []
	for i in options:
		final_keyboard.append([KeyboardButton(i)])
	return final_keyboard

def generateInlineKeyBoards(optionsText, optionsID):
	final_keyboard = []
	for (text,id) in zip(optionsText, optionsID):
		final_keyboard.append([InlineKeyboardButton(text, callback_data=id)])
	return final_keyboard

'''
Inicialización del diccionario y preparándolo con las entradas para los usuarios ya existentes.
'''
allInfo = {}
allMessages = connect_to_mongodb.get_document_mdb("botMessages", "Spanish")
helpMessages = connect_to_mongodb.get_document_mdb("help", "Spanish")

arrayActividades = ["Ir en bici", "Montar a caballo", "Hacer yoga", "Ver un capítulo de tu serie favorita", "Echar una siesta", "Ir al gimnasio", "Salir a dar un paseo", "Escribir", "Escuchar música", "Bailar", "Leer"]
#Opciones de configuracion de cuenta
defaultOptions = [allMessages["name"], allMessages["age"], allMessages["email"], allMessages["phone"], allMessages["language"], allMessages["access"]]

#Opciones de editar de editar cuenta
editingtOptions = [allMessages["name"], allMessages["age"], allMessages["email"], allMessages["phone"], allMessages["language"], allMessages["save"]]

#Oopciones del teclado estandar
initialOptions = [allMessages["quotes"], allMessages["hobbies"], allMessages["changeData"]]

#Opciones de frase
quotesOptions = [allMessages["addQ"], allMessages["removeQ"], allMessages["seeQ"], allMessages["seeQR"]]

#Opciones de aficiones
hobbiesOptions = [allMessages["addH"], allMessages["removeH"], allMessages["seeH"]]

def translate(param):
	translation = ""
	if param == allMessages["name"]:
		translation = "name"
	elif param == allMessages["age"]:
		translation = "age"
	elif param == allMessages["email"]:
		translation = "email"
	elif param == allMessages["phone"]:
		translation = "phone"
	elif param == allMessages["language"]:
		translation = "language"
	return translation 

def defaultConf(dic):
	options = [allMessages["name"], allMessages["age"], allMessages["email"], allMessages["phone"], allMessages["language"], allMessages["access"]]
	main = generateInlineKeyBoards(options, options)
	dic["reminder"] = False
	dic["language"] = "Spanish"
	dic["userInfo"] = {}
	dic["idMessageTractat"] = -1
	dic["keyboard"] = main

def establishConf(dic, config):
	options = [allMessages["name"], allMessages["age"], allMessages["email"], allMessages["phone"], allMessages["language"], allMessages["access"]]
	main = generateInlineKeyBoards(options, options)
	dic["language"] = config["language"]
	dic["userInfo"] = {
		"language": config["language"],
		"name": config["name"],
		"age": config["age"],
		"email": config["email"],
		"phone": config["phone"],
		"sadDays": config["sadDays"],
		"happyDays": config["happyDays"],
		"myQuotes": config["myQuotes"],
		"hobbies": config["hobbies"],
	}
	dic["idMessageTractat"] = -1
	dic["keyboard"] = main

glob.os.makedirs('USERS', exist_ok=True)
files = glob.glob("USERS/*")
for f in files:
	if glob.os.path.isdir(f):
		allInfo[int(f[6:])] = {}
		defaultConf(allInfo[int(f[6:])])



def deleteOptions(update, context, allInfo, registered=False):
	erasables = []
	for i in allInfo:
		if i != "keyboard" and i != "reminder" and i != "language" and i!= "idMessageTractat" and i != "userInfo":
			erasables.append(i)
		elif i == "userInfo" and registered==False:
			allInfo[i] = {}
	for i in erasables:
		del allInfo[i]

def start(update, context, firstTime=False):
	''' Función que saluda, crea una carpeta para guardar los identificadores y que se ejecutará cuando el bot reciba la comanda /start'''
	idMessage = update.message.message_id
	user = update.effective_chat.first_name
	id1 = update.effective_chat.id

	if not id1 in allInfo:
		glob.os.makedirs('USERS/'+str(id1), exist_ok=True)
		allInfo[int(id1)] = {}
		defaultConf(allInfo[int(id1)])

	if allInfo[id1]["idMessageTractat"] == idMessage:
		pass
	else:
		deleteOptions(update, context, allInfo[id1])
		if checkForAccount(id1) == False:
			mensaje = allMessages["hello_with_space"] + user + allMessages["welcome_with_space"] + allMessages["access"]
			reply_kb_markup = InlineKeyboardMarkup(allInfo[id1]["keyboard"], row_width = 3, resize_keyboard=True, one_time_keyboard=True)
			context.bot.send_message(chat_id=update.effective_chat.id, text=mensaje, reply_markup=reply_kb_markup, parse_mode=ParseMode.HTML)
		else:
			message = allMessages["hello_with_space"] + user + allMessages["welcomeAfterRegister"]
			result = loadAccount(id1)
			establishConf(allInfo[id1], result)
			main = generateInlineKeyBoards(initialOptions, initialOptions)
			allInfo[id1]["keyboard"] = main
			reply_kb_markup = InlineKeyboardMarkup(allInfo[id1]["keyboard"], row_width = 3, resize_keyboard=True, one_time_keyboard=True)
			context.bot.send_message(chat_id=update.effective_chat.id,text=message, reply_markup = reply_kb_markup)


def loadAccount(id1):
	filter = {"_id": id1}
	dic2 = ""
	dic3 = connect_to_mongodb.get_all_documents_mdb("users", filter)
	for i in dic3:
		dic2 = i
	return dic2


def checkForAccount(id1):
	found = False
	filter = {"_id": id1}
	dic3 = connect_to_mongodb.get_all_documents_mdb("users", filter)
	for i in dic3:
		found = True
	return found

def normalize(s):
    replacements = (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
    )
    for a, b in replacements:
        s = s.replace(a, b).replace(a.upper(), b.upper())
    return s

def defaultSelection(update, context, dic, text, id1):
	if text == allMessages["language"]:
		options = ["Spanish" + spanish, "Catalan" + catalan, "English" + english]
		main = generateInlineKeyBoards(options, ["Spanish", "English", "Catalan"])
		dic["editingRegister"] = {}
		dic["editingRegister"]["field"] = text
		dic["editingRegister"]["value"] = ""


		dic["keyboard"] = main
		reply_kb_markup = InlineKeyboardMarkup(main, row_width = 3, resize_keyboard=True, one_time_keyboard=True)
		message = allMessages["introduceLanguage"]
		context.bot.send_message(chat_id=update.effective_chat.id,text=message, reply_markup = reply_kb_markup)
		
	elif text == allMessages["access"]:
		error = False
		if "userInfo" in dic:
			count = 0
			for i in dic["userInfo"]:
				count = count + 1
			if count != 5:
				error = True
			else:
				dic3 = {}
				for i in dic["userInfo"]:
					dic3[translate(i)] = copy.deepcopy(dic["userInfo"][i])
				#dic3 = copy.deepcopy(dic["userInfo"])
				dic3["_id"] = id1 
				dic3["sadDays"] = 0
				dic3["happyDays"] = 0
				dic3["myQuotes"] = []
				dic3["hobbies"] = []
				connect_to_mongodb.insert_document_mdb("users", dic3)
		else:
			error = True
		if error == True:
			message = allMessages["missingFields"]
			reply_kb_markup = InlineKeyboardMarkup(dic["keyboard"], row_width = 3, resize_keyboard=True, one_time_keyboard=True)
			context.bot.send_message(chat_id=update.effective_chat.id,text=message, reply_markup = reply_kb_markup)
		else:			
			message = allMessages["finishedR"]
			main = generateInlineKeyBoards(initialOptions, initialOptions)
			allInfo[id1]["keyboard"] = main
			reply_kb_markup = InlineKeyboardMarkup(allInfo[id1]["keyboard"], row_width = 3, resize_keyboard=True, one_time_keyboard=True)
			context.bot.send_message(chat_id=update.effective_chat.id,text=message, reply_markup = reply_kb_markup)
	else:
		message = ""
		if text == allMessages["name"]:
			message = allMessages["introduceName"]
		elif text == allMessages["age"]:
			message = allMessages["introduceAge"]
		elif text == allMessages["email"]:
			message = allMessages["introduceEmail"]
		elif text == allMessages["phone"]:
			message = allMessages["introducePhone"]

		dic["editingRegister"] = {}
		dic["editingRegister"]["field"] = text
		dic["editingRegister"]["value"] = ""
		context.bot.send_message(chat_id=update.effective_chat.id,text=message)

def editSelection(update, context, dic, text, id1):
	if text == allMessages["language"]:
		options = ["Spanish" + spanish, "Catalan" + catalan, "English" + english]
		main = generateInlineKeyBoards(options, ["Spanish", "English", "Catalan"])
		dic["editingRegister"] = {}
		dic["editingRegister"]["field"] = text
		dic["editingRegister"]["value"] = ""


		dic["keyboard"] = main
		reply_kb_markup = InlineKeyboardMarkup(main, row_width = 3, resize_keyboard=True, one_time_keyboard=True)
		message = allMessages["introduceLanguage"]
		context.bot.send_message(chat_id=update.effective_chat.id,text=message, reply_markup = reply_kb_markup)
		
	elif text == allMessages["save"]:
		error = False
		if "userInfo" in dic:
			dic3 = {}
			name = ""
			age = ""
			email = ""
			phone = ""
			language = ""
			if allMessages["name"] in dic["userInfo"]:
				name = dic["userInfo"][allMessages["name"]]
			else:
				name = dic["userInfo"]["name"]
			if allMessages["age"] in dic["userInfo"]:
				age = dic["userInfo"][allMessages["age"]]
			else:
				age = dic["userInfo"]["age"]
			if allMessages["email"] in dic["userInfo"]:
				email = dic["userInfo"][allMessages["email"]]
			else:
				email = dic["userInfo"]["email"]
			if allMessages["phone"] in dic["userInfo"]:
				phone = dic["userInfo"][allMessages["phone"]]
			else:
				phone = dic["userInfo"]["phone"]
			if allMessages["language"] in dic["userInfo"]:
				language = dic["userInfo"][allMessages["language"]]
			else:
				language = dic["userInfo"]["language"]
			#dic3 = copy.deepcopy(dic["userInfo"])
			dic3["_id"] = id1
			dic3["name"] = name
			dic3["age"] = age
			dic3["email"] = email
			dic3["phone"] = phone
			dic3["language"] = language
			dic3["sadDays"] = copy.deepcopy(dic["userInfo"]["sadDays"]) 
			dic3["happyDays"] = copy.deepcopy(dic["userInfo"]["happyDays"])
			dic3["myQuotes"] = copy.deepcopy(dic["userInfo"]["myQuotes"])
			dic3["hobbies"] = copy.deepcopy(dic["userInfo"]["hobbies"])

			connect_to_mongodb.update_document_mdb("users", dic3)
		else:
			error = True

		if error == True:
			message = allMessages["missingFields"]
			reply_kb_markup = InlineKeyboardMarkup(dic["keyboard"], row_width = 3, resize_keyboard=True, one_time_keyboard=True)
			context.bot.send_message(chat_id=update.effective_chat.id,text=message, reply_markup = reply_kb_markup)
		else:

			message = allMessages["savedCorrectly"]
			main = generateInlineKeyBoards(initialOptions, initialOptions)
			allInfo[id1]["keyboard"] = main
			reply_kb_markup = InlineKeyboardMarkup(allInfo[id1]["keyboard"], row_width = 3, resize_keyboard=True, one_time_keyboard=True)
			context.bot.send_message(chat_id=update.effective_chat.id,text=message, reply_markup = reply_kb_markup)
	else:
		message = ""
		if text == allMessages["name"]:
			message = allMessages["introduceName"]
		elif text == allMessages["age"]:
			message = allMessages["introduceAge"]
		elif text == allMessages["email"]:
			message = allMessages["introduceEmail"]
		elif text == allMessages["phone"]:
			message = allMessages["introducePhone"]

		dic["editingRegister"] = {}
		dic["editingRegister"]["field"] = text
		dic["editingRegister"]["value"] = ""
		context.bot.send_message(chat_id=update.effective_chat.id,text=message)

def wantingToAdd(update, context, dic, id1, text):
	dic["adding"] = {}
	dic["adding"]["field"] = text
	message = ""
	options = []
	result = connect_to_mongodb.get_all_documents_mdb("users", {"_id": id1})
	for i in result:
		if text == "hobby":
			options = i["hobbies"]
		elif text == "quote":
			options = i["myQuotes"]
		dic["adding"]["options"] = options

	message = allMessages["adding"]
	main = generateInlineKeyBoards(options, options)
	reply_kb_markup = InlineKeyboardMarkup(main, row_width = 3, resize_keyboard=True, one_time_keyboard=True)
	context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_kb_markup)


def wantingToRemove(update, context, dic, id1, text):
	dic["removing"] = {}
	dic["removing"]["field"] = text
	message = ""
	options = []
	result = connect_to_mongodb.get_all_documents_mdb("users", {"_id": id1})
	for i in result:
		if text == "hobby":
			options = i["hobbies"]
		elif text == "quote":
			options = i["myQuotes"]
		dic["removing"]["options"] = options
	if len(options) != 0:
		message = allMessages["selectToRemove"]
	else:
		message = allMessages["notEnough"]
		options = initialOptions
		del dic["removing"]
	
	main = generateInlineKeyBoards(options, options)
	reply_kb_markup = InlineKeyboardMarkup(main, row_width = 3, resize_keyboard=True, one_time_keyboard=True)
	context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_kb_markup)

def quotesSelection(update, context, dic, text, user_id):
	main = ""
	if text == allMessages["seeQR"]:
		main = generateInlineKeyBoards(initialOptions,initialOptions)
		allInfo[user_id]["keyboard"] = main
		reply_kb_markup = InlineKeyboardMarkup(allInfo[user_id]["keyboard"], row_width = 3, resize_keyboard=True, one_time_keyboard=True)
		message = allMessages["hopeYouLike"]
		context.bot.send_message(chat_id=update.effective_chat.id, text=message)
		arrayFrases = []
		result = connect_to_mongodb.get_all_documents_mdb("quotes", {"_id": "Spanish"})
		for i in result:
			arrayFrases = i["quotes"]
		random.shuffle(arrayFrases)
		message = '"' + arrayFrases[0] + '"'
		context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup = reply_kb_markup)
		del dic["quotes"]

	elif text == allMessages["seeQ"]:
		main = generateInlineKeyBoards(initialOptions,initialOptions)
		allInfo[user_id]["keyboard"] = main
		reply_kb_markup = InlineKeyboardMarkup(allInfo[user_id]["keyboard"], row_width = 3, resize_keyboard=True, one_time_keyboard=True)
		message = allMessages["hopeYouLike"]
		context.bot.send_message(chat_id=update.effective_chat.id, text=message)
		arrayFrases = []
		result = connect_to_mongodb.get_all_documents_mdb("users", {"_id": user_id})
		for i in result:
			arrayFrases = i["myQuotes"]
		random.shuffle(arrayFrases)
		message = '"' + arrayFrases[0] + '"'
		context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup = reply_kb_markup)
		del dic["quotes"]
	elif text == allMessages["addQ"]:
		wantingToAdd(update, context, dic, user_id, "quote")
	elif text == allMessages["removeQ"]:
		wantingToRemove(update, context, dic, user_id, "quote")
	else:
		print("Inside this else")

def hobbySelection(update, context, dic, text, user_id):
	main = ""
	if text == allMessages["seeH"]:
		main = generateInlineKeyBoards(initialOptions,initialOptions)
		allInfo[user_id]["keyboard"] = main
		reply_kb_markup = InlineKeyboardMarkup(allInfo[user_id]["keyboard"], row_width = 3, resize_keyboard=True, one_time_keyboard=True)
		message = allMessages["hopeYouLikeHobby"]
		arrayHobbies = []
		result = connect_to_mongodb.get_all_documents_mdb("users", {"_id": user_id})
		for i in result:
			arrayHobbies = i["hobbies"]
		random.shuffle(arrayHobbies)
		message += " " + arrayHobbies[0]
		context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup = reply_kb_markup)
	elif text == allMessages["addH"]:
		wantingToAdd(update, context, dic, user_id, "hobby")
	elif text == allMessages["removeH"]:
		wantingToRemove(update, context, dic, user_id, "hobby")
	else:
		print("Inside the else")

def processingCallback(update, context):
	user_id = update.effective_chat.id
	text = update.callback_query.data
	''' Eliminem sempre el xat anterior per donar la sensacio a l'usuari que la pantalla sempre és la mateixa'''
	idMessage = update.callback_query.message.message_id
	#delete(update, context, update.effective_chat.id, idMessage-2)
	#delete(update, context, update.effective_chat.id, idMessage-1)
	#delete(update, context, update.effective_chat.id, idMessage)

	if not ("keyboard") in allInfo[user_id]:
		options = [allMessages["name"], allMessages["age"], allMessages["email"], allMessages["phone"], allMessages["language"], allMessages["access"]]
		main = generateInlineKeyBoards(options, options)
		allInfo[user_id]["keyboard"] = main
		
	if not ("reminder") in allInfo[user_id]:
		allInfo[user_id]["reminder"] = True
		reminder(update, context)
	
	if allInfo[user_id]["idMessageTractat"] != idMessage:
		reply_kb_markup = InlineKeyboardMarkup(allInfo[user_id]["keyboard"], row_width = 3, resize_keyboard=True, one_time_keyboard=True)
		context.bot.send_message(chat_id=update.effective_chat.id,text=allMessages["choosen_with_space"] + text)
		allInfo[user_id]["idMessageTractat"] = idMessage
		if checkForAccount(user_id) == False:
			if text in defaultOptions:
				defaultSelection(update, context, allInfo[user_id], text, user_id), 

			elif "editingRegister" in allInfo[user_id]:
					if allInfo[user_id]["editingRegister"]["field"] == allMessages["language"]:
						#field = translate(allInfo[id1]["editingRegister"]["field"])
						field = allInfo[user_id]["editingRegister"]["field"]
						allInfo[user_id]["userInfo"][field] = text
						del allInfo[user_id]["editingRegister"]
						message = allMessages["updated"]
						
						options = [allMessages["name"], allMessages["age"], allMessages["email"], allMessages["phone"], allMessages["language"], allMessages["access"]]
						main = generateInlineKeyBoards(options, options)
						allInfo[user_id]["keyboard"] = main
						reply_kb_markup = InlineKeyboardMarkup(allInfo[user_id]["keyboard"], row_width = 3, resize_keyboard=True, one_time_keyboard=True)
						context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_kb_markup)
			else:
				print("Inside the else")				
		else:
			if not ("keyboard") in allInfo[user_id]:
				options = [allMessages["name"], allMessages["age"], allMessages["email"], allMessages["phone"], allMessages["language"], allMessages["access"]]
				main = generateInlineKeyBoards(options, options)
				allInfo[user_id]["keyboard"] = main
			if not "userInfo" in allInfo[user_id] or len(allInfo[user_id]) == 0:
				result = loadAccount(user_id)
				establishConf(allInfo[user_id], result)

			if text.__eq__("ayuda") or text.__eq__("help") or text.__eq__("ajuda"):
					esperanza = helpMessages["numeroEsperanza"]
					descripcionEsperanza = helpMessages["descripciónEsperanza"]
					emergencias = helpMessages["numeroEmergencias"]
					descripcionEmergencias = helpMessages["descripciónEmergencias"]
					saludMental = helpMessages["numeroSaludMental"]
					descripcionSaludMental = helpMessages["descripciónSaludMental"]
					message = allMessages["help"]
					main = generateInlineKeyBoards(initialOptions, initialOptions)
					reply_kb_markup = InlineKeyboardMarkup(main, row_width = 3, resize_keyboard=True, one_time_keyboard=True)
					#reply_kb_markup = ""
					context.bot.send_message(chat_id=update.effective_chat.id, text=message + "\n\n" + descripcionEsperanza + "\n\n" + esperanza + "\n\n" + descripcionEmergencias + "\n\n" + emergencias + "\n\n" + descripcionSaludMental + "\n\n" + saludMental, reply_markup=reply_kb_markup)

			elif "feeling" in allInfo[user_id]:
				if allMessages["veryHappy"] in text:
					allInfo[user_id]["userInfo"]["happyDays"] += 1
					if allInfo[user_id]["userInfo"]["sadDays"] >=1:
						allInfo[user_id]["userInfo"]["sadDays"] -= 1 
					else:
						allInfo[user_id]["userInfo"]["sadDays"] = 0 
				elif allMessages["happy"] in text:
					allInfo[user_id]["userInfo"]["happyDays"] += 0.5
					if allInfo[user_id]["userInfo"]["sadDays"] >=0.5:
						allInfo[user_id]["userInfo"]["sadDays"] -= 0.5
					else:
						allInfo[user_id]["userInfo"]["sadDays"] = 0   
				elif allMessages["notHappy"] in text:
					if allInfo[user_id]["userInfo"]["happyDays"] >= 0.5:
						allInfo[user_id]["userInfo"]["happyDays"] -= 0.5
					else:
						allInfo[user_id]["userInfo"]["happyDays"] = 0
					allInfo[user_id]["userInfo"]["sadDays"] += 0.5  
				elif allMessages["sad"] in text:
					if allInfo[user_id]["userInfo"]["happyDays"] >= 1:
						allInfo[user_id]["userInfo"]["happyDays"] -= 1
					else:
						allInfo[user_id]["userInfo"]["happyDays"] = 0
					allInfo[user_id]["userInfo"]["sadDays"] += 1  
				
				arrayFrases = []
				result = connect_to_mongodb.get_all_documents_mdb("quotes", {"_id": "Spanish"})
				for i in result:
					arrayFrases = i["quotes"]
				random.shuffle(arrayFrases)
				random.shuffle(arrayActividades)
				arrayAuxActividades = copy.deepcopy(arrayActividades)
				message = ""
				if allInfo[user_id]["userInfo"]["happyDays"] == 7 or allInfo[user_id]["userInfo"]["happyDays"] == 7.5:
					message = allMessages["felicitacion7dias"] + "\n\n" + '"' + arrayFrases[0] + '"'
				elif allInfo[user_id]["userInfo"]["sadDays"] == 7 or allInfo[user_id]["userInfo"]["sadDays"] == 7.5:
					arrayHobbies = []
					result = connect_to_mongodb.get_all_documents_mdb("users", {"_id": user_id})
					for i in result:
						arrayHobbies = i["hobbies"]
					for j in arrayHobbies:
						arrayAuxActividades.append(j)
					random.shuffle(arrayAuxActividades)
					message = allMessages["aviso7diastriste"] + " " + arrayAuxActividades[0]

				elif allInfo[user_id]["userInfo"]["happyDays"] >= 30:
					allInfo[user_id]["userInfo"]["happyDays"] = 0
					message = allMessages["felicitacion30dias"] + "\n\n" + '"' + arrayFrases[0] + '"'

				elif allInfo[user_id]["userInfo"]["sadDays"] >= 30:
					allInfo[user_id]["userInfo"]["sadDays"] = 0
					message = allMessages["aviso30diastriste"]
					esperanza = helpMessages["numeroEsperanza"]
					descripcionEsperanza = helpMessages["descripciónEsperanza"]
					emergencias = helpMessages["numeroEmergencias"]
					descripcionEmergencias = helpMessages["descripciónEmergencias"]
					saludMental = helpMessages["numeroSaludMental"]
					descripcionSaludMental = helpMessages["descripciónSaludMental"]
					message += allMessages["help"]
					message += "\n\n" + descripcionEsperanza + "\n\n" + esperanza + "\n\n" + descripcionEmergencias + "\n\n" + emergencias + "\n\n" + descripcionSaludMental + "\n\n" + saludMental

				else:
					if allMessages["veryHappy"] in text or allMessages["happy"] in text:
						message = "¡Nos alegramos de que estés teniendo un buen día! ¡Esperamos que siga así!"
					elif allMessages["notHappy"] in text or allMessages["sad"] in text:
						message = "Sentimos oír eso... ¡Pero aún queda día para mejorar!"
					else:
						print("This else")
				doc = {
					"_id": user_id,
					"language": allInfo[user_id]["userInfo"]["language"],
					"name": allInfo[user_id]["userInfo"]["name"],
					"age": allInfo[user_id]["userInfo"]["age"],
					"email": allInfo[user_id]["userInfo"]["email"],
					"phone": allInfo[user_id]["userInfo"]["phone"],
					"sadDays": allInfo[user_id]["userInfo"]["sadDays"],
					"happyDays": allInfo[user_id]["userInfo"]["happyDays"],
					"myQuotes": allInfo[user_id]["userInfo"]["myQuotes"],
					"hobbies": allInfo[user_id]["userInfo"]["hobbies"],
				}
				del allInfo[user_id]["feeling"]
				connect_to_mongodb.update_document_mdb("users", doc)
				main = generateInlineKeyBoards(initialOptions, initialOptions)
				reply_kb_markup = InlineKeyboardMarkup(main, row_width = 3, resize_keyboard=True, one_time_keyboard=True)
				context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_kb_markup)

			elif text == allMessages["changeData"]:
				message = allMessages["editing"] + allMessages["save"]
				allInfo[user_id]["changeData"] = True				
				main = generateInlineKeyBoards(editingtOptions, editingtOptions)
				reply_kb_markup = InlineKeyboardMarkup(main, row_width = 3, resize_keyboard=True, one_time_keyboard=True)
				context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup = reply_kb_markup)
			elif "changeData" in allInfo[user_id]:
				if text in editingtOptions:
					editSelection(update, context, allInfo[user_id], text, user_id)
				elif "editingRegister" in allInfo[user_id]:
					if allInfo[user_id]["editingRegister"]["field"] == allMessages["language"]:
						#field = translate(allInfo[id1]["editingRegister"]["field"])
						field = allInfo[user_id]["editingRegister"]["field"]
						allInfo[user_id]["userInfo"][field] = text
						del allInfo[user_id]["editingRegister"]
						message = allMessages["updated"]						
						main = generateInlineKeyBoards(editingtOptions, editingtOptions)
						allInfo[user_id]["keyboard"] = main
						reply_kb_markup = InlineKeyboardMarkup(allInfo[user_id]["keyboard"], row_width = 3, resize_keyboard=True, one_time_keyboard=True)
						context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_kb_markup)
				else:
					print("Inside the else")

			elif "removing" in allInfo[user_id]:
				field = allInfo[user_id]["removing"]["field"]
				whichBDField = ""
				if field == "quote":
					whichBDField = "myQuotes" 
				elif field == "hobby":
					whichBDField = "hobbies"

				optionstoREmove = allInfo[user_id]["removing"]["options"]
				value = text
				message = allMessages["deleted"]

				optionstoREmove.remove(value)
				connect_to_mongodb.update_document_field_mdb("users",user_id, whichBDField, optionstoREmove)
				main = generateInlineKeyBoards(initialOptions, initialOptions)
				reply_kb_markup = InlineKeyboardMarkup(main, row_width = 3, resize_keyboard=True, one_time_keyboard=True)
				context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_kb_markup)
				del allInfo[user_id]["removing"]
				if field == "quote":
					del allInfo[user_id]["quotes"]
				else:
					del allInfo[user_id]["hobbies"]

			elif "adding" in allInfo[user_id]:
					optionsToAdd = allInfo[user_id]["adding"]["options"]
					value = text
					message = allMessages["repeat"]
					main = generateInlineKeyBoards(optionsToAdd, optionsToAdd)
					reply_kb_markup = InlineKeyboardMarkup(main, row_width = 3, resize_keyboard=True, one_time_keyboard=True)

					context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_kb_markup)

			elif text == allMessages["quotes"]:
				message = allMessages["select"]
				allInfo[user_id]["quotes"] = True				
				main = generateInlineKeyBoards(quotesOptions, quotesOptions)
				reply_kb_markup = InlineKeyboardMarkup(main, row_width = 3, resize_keyboard=True, one_time_keyboard=True)
				context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup = reply_kb_markup)
			
			elif "quotes" in allInfo[user_id]:
				if text in quotesOptions:
					quotesSelection(update, context, allInfo[user_id], text, user_id)
			

			elif text == allMessages["hobbies"]:
				message = allMessages["select"]
				allInfo[user_id]["hobbies"] = True				
				main = generateInlineKeyBoards(hobbiesOptions, hobbiesOptions)
				reply_kb_markup = InlineKeyboardMarkup(main, row_width = 3, resize_keyboard=True, one_time_keyboard=True)
				context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup = reply_kb_markup)
			
			elif "hobbies" in allInfo[user_id]:
				if text in hobbiesOptions:
					hobbySelection(update, context, allInfo[user_id], text, user_id)
			
			else:	
				message = allMessages["operationError"]
				#reply_kb_markup = ReplyKeyboardMarkup(allInfo[user_id]["main_menu_keyboard"], row_width = 3, resize_keyboard=True, one_time_keyboard=False)
				#reply_kb_markup = chooseDic(update, context, update.effective_chat.id, allInfo[user_id])
				reply_kb_markup = ""
				context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_kb_markup)
			
			#time.sleep(3)
			#delete(update, context, update.effective_chat.id, idMessage+1)  
	#context.bot.delete_message(chat_id=update.effective_chat.id, message_id=idMessage)
	
	elif (allInfo[user_id]["idMessageTractat"] == idMessage):
		pass
	


def correctOption(text, options):
	for i in options:
		if i.lower() == text.lower() :
			return True
	return False


def howAreYou(context, id=False):
	#veryHappy = '😊'
	#happy = '🙂'
	#notHappy = '😐'
	#sad = '😔'
	if id==False:
		id1 = context.job.context
	else:
		id1 = id
	message = allMessages["howAreU"]
	options = [allMessages["veryHappy"] + veryHappy, allMessages["happy"] + happy, allMessages["notHappy"] + notHappy, allMessages["sad"] + sad ]
	main = generateInlineKeyBoards(options, options)
	allInfo[id1]["keyboard"] = main
	allInfo[id1]["feeling"] = True
	reply_kb_markup = InlineKeyboardMarkup(main, row_width = 3, resize_keyboard=True, one_time_keyboard=True)
	context.bot.send_message(chat_id=id1, text=message, reply_markup = reply_kb_markup)

def reminder(update, context):
	print("Activando reminder")
	id = update.effective_chat.id        
	context.job_queue.run_daily(howAreYou, datetime.time(hour=12, minute=1, tzinfo=pytz.timezone('Europe/Madrid')), days=(0, 1, 2, 3, 4, 5, 6), context=id)
	
def delete(update, context, idChat, idMessage):
	try:
		context.bot.delete_message(chat_id=idChat, message_id=idMessage)
	except Exception as e:
		if str(e) == "Message to delete not found" or "Message can't be deleted for everyone":
			print("Deleting message error")
			pass
		print("error es... " + str(e))



def default(update, context):
	''' Función que trata los mensajes por defecto.'''
	try:
		id1 = update.effective_chat.id
		idMessage = update.message.message_id
		# context.bot.delete_message(chat_id=id1, message_id=idMessage)
		text = str(update.message.text)
		#context.bot.send_message(chat_id=id1,text="Ha escogido la opción/valor: " + text, reply_markup=reply_kb_markup)

		if not id1 in allInfo:
			glob.os.makedirs('USERS/'+str(id1), exist_ok=True)
			allInfo[int(id1)] = {}
			allInfo[id1]["idMessageTractat"] = -1

		if allInfo[id1]["idMessageTractat"] == idMessage:
			pass
		
		else:

			if checkForAccount(id1) == False:
				if "editingRegister" in allInfo[id1]:
					if allInfo[id1]["editingRegister"]["field"] == allMessages["language"]:
						message = allMessages["chooseLanguage"]
						reply_kb_markup = InlineKeyboardMarkup(allInfo[id1]["keyboard"], row_width = 3, resize_keyboard=True, one_time_keyboard=True)
						context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_kb_markup)
					else:
						#field = translate(allInfo[id1]["editingRegister"]["field"])
						field = allInfo[id1]["editingRegister"]["field"]
						allInfo[id1]["userInfo"][field] = text
						del allInfo[id1]["editingRegister"]
						message = allMessages["updated"]
						
						options = [allMessages["name"], allMessages["age"], allMessages["email"], allMessages["phone"], allMessages["language"], allMessages["access"]]
						main = generateInlineKeyBoards(options, options)
						allInfo[id1]["keyboard"] = main
						reply_kb_markup = InlineKeyboardMarkup(allInfo[id1]["keyboard"], row_width = 3, resize_keyboard=True, one_time_keyboard=True)
						context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_kb_markup)
				else:
					message = allMessages["error"]
					options = [allMessages["name"], allMessages["age"], allMessages["email"], allMessages["phone"], allMessages["language"], allMessages["access"]]
					main = generateInlineKeyBoards(options, options)
					allInfo[id1]["keyboard"] = main
					reply_kb_markup = InlineKeyboardMarkup(allInfo[id1]["keyboard"], row_width = 3, resize_keyboard=True, one_time_keyboard=True)
					context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_kb_markup)
			else:
				
				if not "userInfo" in allInfo[id1] or len(allInfo[id1]["userInfo"]) == 0:
					result = loadAccount(id1)
					establishConf(allInfo[id1], result)
				if not ("reminder") in allInfo[id1]:
					allInfo[id1]["reminder"] = True
					reminder(update, context)

				if text == "howAreYou":
					howAreYou(context, id1)

				elif "adding" in allInfo[id1]:
					field = allInfo[id1]["adding"]["field"]
					whichBDField = ""
					if field == "quote":
						whichBDField = "myQuotes" 
					elif field == "hobby":
						whichBDField = "hobbies"

					optionsToAdd = allInfo[id1]["adding"]["options"]
					value = text

					if value in optionsToAdd:
						message = allMessages["repeat"]
						main = generateInlineKeyBoards(optionsToAdd, optionsToAdd)
						reply_kb_markup = InlineKeyboardMarkup(main, row_width = 3, resize_keyboard=True, one_time_keyboard=True)
					else:
						message = allMessages["added"]
						optionsToAdd.append(value)
						connect_to_mongodb.update_document_field_mdb("users",id1, whichBDField, optionsToAdd)
						main = generateInlineKeyBoards(initialOptions, initialOptions)
						reply_kb_markup = InlineKeyboardMarkup(main, row_width = 3, resize_keyboard=True, one_time_keyboard=True)
						del allInfo[id1]["adding"]
						if field == "quote":
							del allInfo[id1]["quotes"]
						else:
							del allInfo[id1]["hobbies"]
					context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_kb_markup)
					
				elif "removing" in allInfo[id1]:
					optionsToAdd = allInfo[id1]["removing"]["options"]
					value = text
					message = allMessages["select"]
					main = generateInlineKeyBoards(optionsToAdd, optionsToAdd)
					reply_kb_markup = InlineKeyboardMarkup(main, row_width = 3, resize_keyboard=True, one_time_keyboard=True)

					context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_kb_markup)
				elif "feeling" in allInfo[id1]:
					message = allMessages["chooseFeeling"]
					reply_kb_markup = InlineKeyboardMarkup(allInfo[id1]["keyboard"], row_width = 3, resize_keyboard=True, one_time_keyboard=True)
					context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_kb_markup)

				elif "changeData" in allInfo[id1]:
					if "editingRegister" in allInfo[id1]:
						if allInfo[id1]["editingRegister"]["field"] == allMessages["language"]:
							message = allMessages["chooseLanguage"]
							reply_kb_markup = InlineKeyboardMarkup(allInfo[id1]["keyboard"], row_width = 3, resize_keyboard=True, one_time_keyboard=True)
							context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_kb_markup)
						else:
							#field = translate(allInfo[id1]["editingRegister"]["field"])
							field = allInfo[id1]["editingRegister"]["field"]
							allInfo[id1]["userInfo"][field] = text
							del allInfo[id1]["editingRegister"]
							message = allMessages["updated"]
							main = generateInlineKeyBoards(editingtOptions, editingtOptions)
							allInfo[id1]["keyboard"] = main
							reply_kb_markup = InlineKeyboardMarkup(allInfo[id1]["keyboard"], row_width = 3, resize_keyboard=True, one_time_keyboard=True)
							context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_kb_markup)
					else:
						message = allMessages["error"]
						main = generateInlineKeyBoards(editingtOptions, editingtOptions)
						allInfo[id1]["keyboard"] = main
						reply_kb_markup = InlineKeyboardMarkup(allInfo[id1]["keyboard"], row_width = 3, resize_keyboard=True, one_time_keyboard=True)
						context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_kb_markup)
				else:
					print("In the Else")
					message = allMessages["available"]
					main = generateInlineKeyBoards(initialOptions, initialOptions)
					allInfo[id1]["keyboard"] = main
					reply_kb_markup = InlineKeyboardMarkup(allInfo[id1]["keyboard"], row_width = 3, resize_keyboard=True, one_time_keyboard=True)
					context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_kb_markup)


			allInfo[id1]["idMessageTractat"] = idMessage
			# delete(update, context, update.effective_chat.id, idMessage-2)
			# delete(update, context, update.effective_chat.id, idMessage-1)
			# delete(update, context, update.effective_chat.id, idMessage)
	except Exception as e:
		print("error es... " + str(e))
		print(traceback.format_exc())
		reply_kb_markup = ""
		message = "Se ha producido un error. Por favor utilice /start para reiniciar."
		context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_kb_markup)  

def main():
	# declara una constante con el access-token que lee de token.txt
	TOKEN = open('token.txt').read().strip()

	# crea objetos para trabajar con Telegram
	updater = Updater(token=TOKEN, use_context=True)
	dispatcher = updater.dispatcher

	# indica que cuando el bot reciba la comanda /start se ejecute la función start
	dispatcher.add_handler(CommandHandler('start', start))
	dispatcher.add_handler(CallbackQueryHandler(processingCallback))
	dispatcher.add_handler(MessageHandler(Filters.update, default))
	# enciende el bot
	updater.start_polling()    

	print("The bot is running!")

if __name__ == "__main__":
	main()
	