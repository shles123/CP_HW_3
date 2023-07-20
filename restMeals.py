from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource, reqparse

import requests
import json
import sys

app = Flask(__name__)
api = Api(app)

class DishCollection:
    def __init__(self):
        self.uniqueKey = 0
        self.dshCol = []
        self.formatedCol = {}

    def insertDish(self, dish, data):
        if dish in self.dshCol: 
            print("WordCollection: word ", dish, " already exists")
            return 0
        self.uniqueKey += 1
        self.dshCol.append(dish)
        updatedData = {
            'calories': 0,
            'size': 0,
            'sodium': 0,
            'sugar': 0
        }
        for value in data:
            updatedData['calories'] += value['calories']
            updatedData['size'] += value['serving_size_g']
            updatedData['sodium'] += value['sodium_mg']
            updatedData['sugar'] += value['sugar_g']

        self.formatedCol[str(self.uniqueKey)] = {
            "name": dish,
            "ID": self.uniqueKey,
            "cal": updatedData['calories'],
            "size": updatedData['size'],
            "sodium": updatedData['sodium'],
            "sugar": updatedData['sugar']
        }
        print("DishCollection: inserted the dish: ", dish, " with key ", self.uniqueKey)
        return self.uniqueKey

    def getDishes(self):
        return self.formatedCol
    
    def getDishByName(self, dish):
        if dish not in self.dshCol:
            return make_response("-5", 404)
        for value in self.formatedCol.values():
            if value['name'] == dish:
                return value
        
    def getDishById(self , id):
        if id not in self.formatedCol:
            return make_response("-5", 404)
        return self.formatedCol[id]
    
    def deleteByName(self, dish):
        if dish not in self.dshCol:
            return make_response("-5", 404)
        for value in self.formatedCol.values():
            if value['name'] == dish:
                key = value['ID']
                self.formatedCol.pop(str(key))
                self.dshCol.remove(value['name'])
                return key

    def deleteById(self, id):
        if str(id) not in self.formatedCol:
            return make_response("-5", 404)
        name = self.formatedCol[id]['name']
        self.formatedCol.pop(id)
        self.dshCol.remove(name)
        return int(id)



collection = DishCollection()

class Dishes(Resource):
    global collection
 
    def post(self):
        if(request.query_string != b''):
            return 0, 415

        if request.content_type != "application/json":
            return 0, 415

        if 'name' not in request.json:
            return -1, 422
        
        queryName = request.json['name']
        api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(queryName)
        response = requests.get(api_url, headers={'X-Api-Key': 'NgeE6AEhocxkbf6ZQ7bVlA==WlaPWpPTco54UFUk'})
        ninjaData = response.json()

        if not ninjaData:
            return -3, 422
        
        key = collection.insertDish(queryName, ninjaData)
        if key == 0:
            return make_response("-2", 422)
        return make_response(str(key), 201)
    
    def get(self):
        return collection.getDishes()

class DishesKey(Resource):
        def get(self, key):
            return collection.getDishById(str(key))

        def delete(self, key):
            return collection.deleteById(str(key))
        
class DishesName(Resource):
        def get(self, name):
            return collection.getDishByName(name)
        
        def  delete(self, name):
            return collection.deleteByName(name)

class mealCollection:
    def __init__(self):
        self.uniqueKey = 0
        self.mealColFormated = {}
        self.mealList = []

    def insertMeal(self, mealData):
        if(request.query_string != b''):
            return 0, 415
        
        if request.content_type != "application/json":
            return 0, 415
        
        if ('name' not in request.json) or ('appetizer' not in request.json) or ('dessert' not in request.json) or ('main' not in request.json):
            return -1, 422

        if mealData['name'] in self.mealList: 
            return -2, 422

        ingredientSizes = self.calcIngredientsAmt(mealData)
        
        if(ingredientSizes == 0):
            return -6, 422

        self.uniqueKey += 1
        self.mealList.append(mealData['name'])

        key =  self.insertFormated(mealData, ingredientSizes, str(self.uniqueKey))
        return int(key), 201
    

    def calcIngredientsAmt(self, mealData):
        a  = str(mealData['dessert']) not in collection.formatedCol
        if (str(mealData['appetizer']) not in collection.formatedCol) or (str(mealData['main']) not in collection.formatedCol) or (str(mealData['dessert']) not in collection.formatedCol):
            return 0

        dishes = collection.getDishes() 
        numSodium = dishes[str(mealData['appetizer'])]['sodium'] + dishes[str(mealData['main'])]['sodium'] + dishes[str(mealData['dessert'])]['sodium']
        numcalories = dishes[str(mealData['appetizer'])]['cal'] + dishes[str(mealData['main'])]['cal'] + dishes[str(mealData['dessert'])]['cal']
        numSugar = dishes[str(mealData['appetizer'])]['sugar'] + dishes[str(mealData['main'])]['sugar'] + dishes[str(mealData['dessert'])]['sugar']
        return [numcalories, numSodium, numSugar]

    def insertFormated(self, mealData, ingredientAmit, key):
        self.mealColFormated[key] = {
            "name": mealData['name'],
            "ID": key,
            "appetizer": mealData['appetizer'],
            "main": mealData['main'],
            "dessert": mealData['dessert'],
            "cal": ingredientAmit[0], #numcalories
            "sodium": ingredientAmit[1], #numSodium
            "sugar": ingredientAmit[2] #numSugar
        }
        return key
    
    def getMeals(self):
        return self.mealColFormated
    
    def getMealByName(self, mealName):
        if mealName not in self.mealList:
            return make_response("-5", 404)
        for value in self.mealColFormated.values():
            if value['name'] == mealName:
                return value

    def getMealByID(self, mealID):
        if mealID not in self.mealColFormated:
            return make_response("-5", 404)
        return self.mealColFormated[mealID]
    
    def deleteMealByName(self, meal):
        if meal not in self.mealList:
            return make_response("-5", 404)
        for value in self.mealColFormated.values():
            if value['name'] == meal:
                key = value['ID']
                self.mealColFormated.pop(str(key))
                self.mealList.remove(value['name'])
                return int(key)

    def deleteMealById(self, id):
        if id not in self.mealColFormated:
            return -5, 404
        name = self.mealColFormated[id]['name']
        self.mealColFormated.pop(id)
        self.mealList.remove(name)
        return int(id), 200
    
    def replaceMeal(self, key):
        if request.content_type != "application/json":
            return 0, 415
        
        if ('name' not in request.json) or ('appetizer' not in request.json) or ('dessert' not in request.json) or ('main' not in request.json):
            return -1, 422
        
        for i_key, values in self.mealColFormated.items():
            if (values['name'] == request.json['name']) and (i_key != key):
                return -2, 422

        meal = self.mealColFormated[key]

        if (request.json['appetizer'] != meal['appetizer']) or (request.json['main']) != meal['main'] or (request.json['dessert'] != meal['dessert']):
            ingredientAmt = self.calcIngredientsAmt(request.json)
            if ingredientAmt == 0:
                return -6, 422
            key = self.insertFormated(request.json, ingredientAmt, key)
        if request.json['name'] != meal['name']:
            self.mealList.remove(meal['name'])
            self.mealList.append(request.json['name'])
            meal['name'] = request.json['name']
        
        return int(key), 200

mealCol = mealCollection()

class Meals(Resource):
    global mealCol
    
    def post(self):
        if request.content_type != "application/json":
            return 0, 415
        keys = mealCol.insertMeal(request.json)
        return keys[0], keys[1]
    
    def get(self):
        return mealCol.getMeals()
    
    def delete(self):
        return make_response("This method is not allowed for the requested URL", 405)



class MealsKey(Resource):
    def get(self , key):
        return mealCol.getMealByID(str(key))
    
    def  delete(self, key):
        return mealCol.deleteMealById(str(key))
    
    def put(self, key):
        if str(key) in mealCol.mealColFormated:
            return mealCol.replaceMeal(str(key))
        return make_response(-2, 422)

class MealsName(Resource):
    def get(self, name):
        return mealCol.getMealByName(name)
    
    def  delete(self, name):
        return mealCol.deleteMealByName(name)
#comment so maybe there will be a
api.add_resource(Dishes, '/dishes')
api.add_resource(DishesKey, '/dishes/<int:key>')
api.add_resource(DishesName, '/dishes/<string:name>')

api.add_resource(Meals, '/meals')
api.add_resource(MealsKey, '/meals/<int:key>')
api.add_resource(MealsName, '/meals/<string:name>')

if __name__ == '__main__':
    # create collection dictionary and keys list
    print("running restMeals.py")
    # run Flask app.   default part is 5000
    app.run(host='0.0.0.0', port=8000, debug=True)
    # export FLASK_APP=restMeals.py




