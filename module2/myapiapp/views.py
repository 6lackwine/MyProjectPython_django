from rest_framework.generics import ListCreateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from django.contrib.auth.models import Group

from myapiapp.serializers import GroupSerializer


@api_view()
def hello_world_view(request: Request) -> Response:
    return Response({"message": "Hello World!"})

class GroupsListView(APIView):
    def get(self, request: Request) -> Response:
        groups = Group.objects.all()
        serialized = GroupSerializer(groups, many=True)
        return Response({"groups": serialized.data})


class GroupListView(ListCreateAPIView, GenericAPIView):
    # ListCreateAPIView - Возвращает запрошенный список и позволяет добавлять новые элементы в БД.
    queryset = Group.objects.all()
    serializer_class = GroupSerializer