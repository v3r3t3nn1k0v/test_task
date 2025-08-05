from django.test import TestCase

# Create your tests here.
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Hero

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def hero_data():
    return {
        'name': 'batman',
        'intelligence': 90,
        'strength': 55,
        'speed': 67,
        'power': 74,
        'idHeroApi': '1'
    }

@pytest.fixture
def create_hero(hero_data):
    def _create_hero(**kwargs):
        data = hero_data.copy()
        data.update(kwargs)
        return Hero.objects.create(**data)
    return _create_hero

@pytest.mark.django_db
class TestHeroAPI:
    # POST endpoint tests
    def test_post_hero_success(self, client, mocker):
        mock_response = {
            'results': [{
                'id': '1',
                'powerstats': {
                    'intelligence': '90',
                    'strength': '55',
                    'speed': '67',
                    'power': '74'
                }
            }]
        }
        mocker.patch('api.models.HeroAPi.getHeroByName', return_value=mock_response)
        
        url = reverse('hero-list')
        data = {'name': 'batman'}
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert Hero.objects.count() == 1
        hero = Hero.objects.first()
        assert hero.name == 'batman'
        assert hero.intelligence == 90

    def test_post_hero_invalid_data(self, client):
        url = reverse('hero-list')
        data = {}  # missing name field
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data

    # GET endpoint tests
    def test_get_hero_success(self, client, create_hero):
        create_hero(name='Batman', intelligence=100, strength=80, speed=60, power=70)
        
        url = reverse('hero-list')
        data = {
            'name': 'batman',
            'filters': [
                {
                    'filter_type': 'less',
                    'property': 'power',
                    'value': 50
                }
            ]
        }
        response = client.get(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['result']) == 2
        assert response.data['result'][0]['name'] == 'batman'

    def test_get_hero_with_filters(self, client, create_hero):
        create_hero(name='batman', strength=100)
        create_hero(name='batman', intelligence=90)
        
        url = reverse('hero-list')
        data = {
            'name': 'batman',
            'filters': [
                {
                    'filter_type': 'more',
                    'property': 'strength',
                    'value': 80
                }
            ]
        }
        response = client.get(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['result']) == 1
        assert response.data['result'][0]['strength'] == 100

    def test_get_hero_not_found(self, client):
        url = reverse('hero-list')
        data = {
            'name': 'NonExistentHero',
            'filters': []
        }
        response = client.get(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_get_hero_invalid_filter(self, client, create_hero):
        create_hero(name='batman')
        
        url = reverse('hero-list')
        data = {
            'name': 'batman',
            'filters': [
                {
                    'filter_type': 'invalid',
                    'property': 'strength',
                    'value': 'not_a_number'
                }
            ]
        }
        response = client.get(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'filters' in response.data

    def test_get_hero_multiple_filters(self, client, create_hero):
        create_hero(name='batman', speed=100, intelligence=80)
        create_hero(name='batman', speed=90, intelligence=70)
        
        url = reverse('hero-list')
        data = {
            'name': 'batman',
            'filters': [
                {
                    'filter_type': 'more',
                    'property': 'speed',
                    'value': 95
                },
                {
                    'filter_type': 'less',
                    'property': 'intelligence',
                    'value': 85
                }
            ]
        }
        response = client.get(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['result']) == 1
        hero = response.data['result'][0]
        assert hero['speed'] == 100
        assert hero['intelligence'] == 80