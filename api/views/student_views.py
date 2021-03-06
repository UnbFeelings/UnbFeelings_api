from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import api_view, list_route
from django.shortcuts import get_object_or_404

from api.serializers import StudentSerializer, CourseSerializer
from api.models import Student, Course
from api.permissions import StudentPermissions, BlockPermissions

import json
import random


class StudentViewSet(ModelViewSet):
    """Description: StudentViewSet.

    API endpoint that allows users to be viewed, created, deleted or edited.
    """
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = (StudentPermissions, )

    def list(self, request):
        """
        API endpoint that allows all users to be viewed.
        ---
        Response example:
        ```
        {
          "count": 2,
          "next": null,
          "previous": null,
          "results": [
            {
              "id": 1,
              "email": "johndoe_1@email.com",
              "course": {
                "id": 1,
                "name": "Engenharia de Software",
                "campus": 1
              }
            },
            {
              "id": 2,
              "email": "johndoe_2@email.com",
              "course": {
                "id": 3,
                "name": "Engenharia Eletrônica",
                "campus": 1
              }
            }
          ]
        }
        ```
        """
        response = super(StudentViewSet, self).list(request)
        for student in response.data['results']:
            course = Course.objects.get(id=student['course'])
            course_serializer = CourseSerializer(course)
            student['course'] = course_serializer.data
        return response

    def create(self, request):
        """
        API endpoint that allows users to be created.
        ---
        Body example:
        ```
        {
          "email": "johndoe@email.com",
          "password": "string123",
          "course": 1
        }
        ```
        Response example:
        ```
        {
          "id": 1,
          "email": "johndoe@email.com",
          "course": {
            "id": 1,
            "name": "Engenharia de Software",
            "campus": 1
          }
        }
        ```
        """
        response = super(StudentViewSet, self).create(request)
        course = Course.objects.get(id=response.data['course'])
        course_serializer = CourseSerializer(course)
        response.data['course'] = course_serializer.data
        return response

    def destroy(self, request, pk=None):
        """
        API endpoint that allows users to be deleted.
        """
        response = super(StudentViewSet, self).destroy(request, pk)
        return response

    def retrieve(self, request, pk=None):
        """
        API endpoint that allows a specific user to be viewed.
        ---
        Response example:
        ```
        {
          "id": 1,
          "email": "johndoe@email.com",
          "course": {
            "id": 1,
            "name": "Engenharia de Software",
            "campus": 1
          }
        }
        ```
        """
        response = super(StudentViewSet, self).retrieve(request, pk)
        course = Course.objects.get(id=response.data['course'])
        course_serializer = CourseSerializer(course)
        response.data['course'] = course_serializer.data
        return response

    def partial_update(self, request, pk=None, **kwargs):
        """
        API endpoint that allows a user to be partial edited.
        ---
        Body example:
        ```
        {
          "email": "string@email.com"
        }
        ```
        Response example:
        ```
        {
          "id": 1,
          "email": "string@email.com",
          "course": {
            "id": 1,
            "name": "Engenharia de Software",
            "campus": 1
          }
        }
        ```
        """
        response = \
            super(StudentViewSet, self).partial_update(request, pk, **kwargs)
        return response

    def update(self, request, pk=None, **kwargs):
        """
        API endpoint that allows a user to be edited.
        ---
        Body example:
        ```
        {
          "email": "string@email.com",
          "password": "string123",
          "course": 3
        }
        ```
        Response example:
        ```
        {
          "id": 1,
          "email": "string@email.com",
          "course": {
            "id": 3,
            "name": "Engenharia Eletrônica",
            "campus": 1
          }
        }
        ```
        """
        response = super(StudentViewSet, self).update(request, pk, **kwargs)
        course = Course.objects.get(id=response.data['course'])
        course_serializer = CourseSerializer(course)
        response.data['course'] = course_serializer.data
        return response

    @list_route(
        permission_classes=[BlockPermissions],
        methods=['GET'],
        url_path='blocks')
    def user_blocks(self, request, user_id=None):
        """
        API endpoint that gets all users blockeds from a user
        """
        blockeds = self.request.user.list_blocked_users()

        blockeds_paginated = self.paginate_queryset(blockeds)

        if blockeds_paginated is not None:
            serializer = StudentSerializer(
                data=blockeds_paginated, many=True, context={'request': request})

            serializer.is_valid()
            return self.get_paginated_response(serializer.data)
        else:

            data = PostSerializer(
                data=blockeds, many=True, context={'request': request})

            data.is_valid()
            return Response(data.data)

    @api_view(['GET'])
    def anonymous_name(request):
        """
        API endpoint that allows getting an anonymous name to a student.
        ---
        Response example:
        ```
        {
            "anonymous_name": "Rio"
        }
        ```
        """
        # The city names are sorted in alphabetic order
        CITY_NAMES = json.loads(open("api/fixtures/city_names.json").read())
        anonymous_name = {'anonymous_name': random.choice(CITY_NAMES)}
        return Response(anonymous_name, status=status.HTTP_200_OK)
