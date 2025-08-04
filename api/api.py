from rest_framework.generics import ListAPIView
from .serialaizers import GetHeroSerializer, PostHeroSerializer
from rest_framework.response import Response
from rest_framework import status
from .models import Hero , HeroAPi
from django.db.models import Q

class heroView(ListAPIView):

    """
    Формат запроса
    GET: /hero/
    Тело запроса: 
    {
        "name" : <имя героя> // проверка на точное совпадение
        'filters' : // список словарей(фильтров) 
        [
            {
                filter_type: <тип фильтра> // поле на выбор: less (меньше или равно), more(больше или равно), exact(точное сравнение)
                property: <свойство героя> // поле на выбор: strength,intelligence,speed,power
                value: <значение> // значение для фильтра
            }
        ]
    }
    """
    def get(self, request):
        data = request.data
        serializer = PostHeroSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        name = data['name']
        filters = data.get('filters', [])
        q_objects = Q(name=name)

        for filter in filters: 
            property_name = filter['property']
            value = filter['value']
            filter_type = filter['filter_type']

            if filter_type == 'exact':
                q_objects &= Q(**{property_name: value})
            elif filter_type == 'less':
                q_objects &= Q(**{f"{property_name}__lt": value})
            elif filter_type == 'more':
                q_objects &= Q(**{f"{property_name}__gt": value})
        
        queryset = Hero.objects.filter(q_objects)

        if not queryset.exists():
            details = {"error" : "Нет героев с таким именем и фильтрами"}
            return Response(details, status=status.HTTP_400_BAD_REQUEST)

        response = {}
        response['result'] = []
        for heroInfo in queryset:
            heroInfoData = {
                "id" : heroInfo.idHeroApi , 
                "name" : heroInfo.name , 
                "power" : heroInfo.power, 
                "intelligence" : heroInfo.intelligence, 
                "speed" : heroInfo.speed, 
                "strength" : heroInfo.strength
            }
            response['result'].append(heroInfoData)

        return Response(response, status=200)

    def post(self, request): 

        """
        Формат запроса 
        POST: /hero/
        Тело запроса 
        {
            'name' : <имя героя>
        }
        """
        data = request.data 
        serializer = GetHeroSerializer(data=data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        apiManager = HeroAPi()
        heroName = data['name']
        apiResponse = apiManager.getHeroByName(heroName)
        for hero in apiResponse['results']:
                try:
                    Hero.objects.create(name=heroName , 
                                        intelligence = hero['powerstats']['intelligence'], 
                                        strength = hero['powerstats']['strength'], 
                                        speed = hero['powerstats']['speed'], 
                                        power = hero['powerstats']['power'],
                                        idHeroApi = hero["id"] )
                except:
                     pass
        return Response(apiResponse, status=200)
