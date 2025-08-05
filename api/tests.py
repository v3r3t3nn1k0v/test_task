import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Hero
from unittest.mock import patch, MagicMock

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def batman_data():
    return {
        'name': 'batman',
        'intelligence': 100,
        'strength': 26,
        'speed': 27,
        'power': 47,
        'idHeroApi': 69
    }

@pytest.fixture
def create_batman(batman_data):
    def _create_batman(**kwargs):
        data = batman_data.copy()
        data.update(kwargs)
        return Hero.objects.create(**data)
    return _create_batman

@pytest.fixture
def mock_batman_api_response():
    return {
        'results': [{
            'id': '69',
            'name': 'batman',
            'powerstats': {
                'intelligence': '100',
                'strength': '26',
                'speed': '27',
                'power': '47'
            }
        }]
    }

@pytest.mark.django_db
class TestBatmanAPI:
    # POST endpoint tests for Batman
    @patch('requests.post')
    def test_post_batman_success(self, mock_post, client, mock_batman_api_response):
        mock_response = MagicMock()
        mock_response.json.return_value = mock_batman_api_response
        mock_post.return_value = mock_response

        url = reverse('hero-list')
        data = {'name': 'Batman'}
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert Hero.objects.count() == 1
        hero = Hero.objects.first()
        assert hero.name == 'Batman'
        assert hero.idHeroApi == 69
        assert hero.intelligence == 100

    # GET endpoint tests for Batman
    def test_get_batman_by_id(self, client, create_batman):
        create_batman(idHeroApi=69)
        
        url = reverse('hero-list')
        data = {
            'name': 'batman',
            'filters': [
                {
                    'filter_type': 'exact',
                    'property': 'idHeroApi',
                    'value': 69
                }
            ]
        }
        response = client.get(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['result']) == 1
        assert response.data['result'][0]['name'] == 'Batman'
        assert response.data['result'][0]['id'] == 69

    def test_get_batman_by_intelligence(self, client, create_batman):
        create_batman(idHeroApi=69, intelligence=100)
        create_batman(idHeroApi=70, intelligence=90)  # Another Batman variant
        
        url = reverse('hero-list')
        data = {
            'name': 'batman',
            'filters': [
                {
                    'filter_type': 'exact',
                    'property': 'intelligence',
                    'value': 100
                }
            ]
        }
        response = client.get(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['result']) == 1
        assert response.data['result'][0]['id'] == 69
        assert response.data['result'][0]['intelligence'] == 100

    def test_get_batman_with_multiple_filters(self, client, create_batman):
        # Create different Batman versions
        create_batman(idHeroApi=69, intelligence=100, strength=26)  # Original
        create_batman(idHeroApi=70, intelligence=90, strength=30)   # Variant 1
        create_batman(idHeroApi=71, intelligence=80, strength=35)    # Variant 2
        
        url = reverse('hero-list')
        data = {
            'name': 'batman',
            'filters': [
                {
                    'filter_type': 'more',
                    'property': 'intelligence',
                    'value': 85
                },
                {
                    'filter_type': 'less',
                    'property': 'strength',
                    'value': 30
                }
            ]
        }
        response = client.get(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        results = response.data['result']
        assert len(results) == 2  # Should match id 69 and 70
        assert any(hero['id'] == 69 for hero in results)
        assert any(hero['id'] == 70 for hero in results)
        assert all(hero['strength'] < 30 for hero in results)

    def test_get_batman_not_found(self, client):
        url = reverse('hero-list')
        data = {
            'name': 'batman',
            'filters': [
                {
                    'filter_type': 'exact',
                    'property': 'idHeroApi',
                    'value': 99  # Non-existing ID
                }
            ]
        }
        response = client.get(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data