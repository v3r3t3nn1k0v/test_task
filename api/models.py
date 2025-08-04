from django.db import models
from dotenv import load_dotenv
import os 
import requests

load_dotenv()

"""Класс для взаимодействия с API superhero"""
class HeroAPi: 
    ACCES_TOKEN = os.getenv("accestoken")
    DOMAIN = 'https://superheroapi.com/api/'


    def getHeroByName(self, name):
        url = self.DOMAIN + self.ACCES_TOKEN + '/search/' + name
        headers = {'Content-type' : 'application/json'}


        response = requests.post(url , headers=headers)
        return response.json()


# Create your models here.


class Hero(models.Model): 
    name = models.CharField()
    intelligence = models.IntegerField()
    strength = models.IntegerField()
    speed = models.IntegerField()
    power = models.IntegerField()
    idHeroApi = models.IntegerField(unique=True)