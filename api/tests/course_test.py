# -*- coding: utf-8 -*-

from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model

from api.models import Campus, Course
from api.tests.helpers import create_test_user

UserModel = get_user_model()


class CourseTestCase(APITestCase):
    def setUp(self):
        self.campus = Campus.objects.get_or_create(name="FGA")[0]
        Course.objects.get_or_create(name="Calculo 1", campus=self.campus)
        Course.objects.get_or_create(name="CB", campus=self.campus)

    def test_anyone_can_get_list(self):
        """
        Anyone can make get requests to list
        """
        client = APIClient()
        response = client.get('/api/courses/')
        courses = Course.objects.all()

        self.assertEqual(200, response.status_code)
        self.assertEqual(len(courses), len(response.data['results']))

    def test_anyone_can_get_detail(self):
        """
        Anyone can make get requests to detail
        """
        client = APIClient()
        course = Course.objects.get(name="CB")
        response = client.get('/api/courses/{}/'.format(course.id))

        self.assertEqual(200, response.status_code)
        self.assertEqual(course.id, response.data['id'])

    @create_test_user(email="test@user.com", password="testuser")
    def test_only_admin_can_create(self):
        """
        Only admin members can create new
        """
        client = APIClient()

        self._check_admin_only_access(
            client,
            lambda: client.post('/api/courses/', {
                    "name": "A new course", "campus": self.campus.id
                }),
            "test@user.com", "testuser")

        user = UserModel.objects.get(email="test@user.com")
        user.is_staff = True
        user.save()

        token = self._get_user_token("test@user.com", "testuser")

        client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(token))
        response = client.post('/api/courses/', {
                    "name": "A new course", "campus": self.campus.id
                })

        self.assertEqual(201, response.status_code)
        self.assertEqual("A new course", response.data['name'])

    @create_test_user(email="test@user.com", password="testuser")
    def test_only_admin_can_update(self):
        """
        Only admin members can update
        """
        course = Course.objects.get(name="CB")
        client = APIClient()

        self._check_admin_only_access(
            client,
            lambda: client.patch('/api/courses/{}/'.format(course.id), {
                        "name": "other name"
                    }),
            "test@user.com", "testuser")

        user = UserModel.objects.get(email="test@user.com")
        user.is_staff = True
        user.save()

        token = self._get_user_token("test@user.com", "testuser")

        client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(token))
        response = client.patch('/api/courses/{}/'.format(course.id),
                              {"name": "other name"})

        self.assertEqual(200, response.status_code)
        self.assertEqual("other name", response.data['name'])

    @create_test_user(email="test@user.com", password="testuser")
    def test_only_admin_can_delete(self):
        """
        Only admin members can delete
        """
        course = Course.objects.get(name="CB")
        client = APIClient()

        self._check_admin_only_access(
            client,
            lambda: client.delete('/api/courses/{}/'.format(course.id)),
            "test@user.com", "testuser")

        user = UserModel.objects.get(email="test@user.com")
        user.is_staff = True
        user.save()

        token = self._get_user_token("test@user.com", "testuser")

        client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(token))
        response = client.delete('/api/courses/{}/'.format(course.id))

        self.assertEqual(204, response.status_code)

        self.assertEqual(None, response.data)
        self.assertEqual(0, len(Course.objects.all().filter(name="FGA")))

    def _get_user_token(self, email, password):
        client = APIClient()

        response = client.post("/api/token-auth/", {
            'email': email,
            'password': password
        })

        return response.data['token']

    def _check_admin_only_access(self, client, client_action, user_email,
                                 user_password):
        response = client_action()

        self.assertEqual(401, response.status_code)
        self.assertEqual(
            "As credenciais de autenticação não foram fornecidas.",
            response.data['detail'])

        token = self._get_user_token(user_email, user_password)

        client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(token))
        response = client_action()

        self.assertEqual(403, response.status_code)
        self.assertEqual("Você não tem permissão para executar essa ação.",
                         response.data['detail'])
