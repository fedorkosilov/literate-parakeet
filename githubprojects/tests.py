from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from githubprojects.models import Project
from decimal import Decimal


class ProjectTests(APITestCase):
    """
    Project tests
    """
    def setUp(self):
        user = User.objects.create_user(
            username='testuser', 
            password='12345',
        )
        user_token = Token.objects.create(user=user)
        self.auth_header = 'Token ' + user_token.key
        self.first_project = Project.objects.create(
            name='Project One',
            description='Some basic description',
            url='https://github.com/fedorkosilov/literate-parakeet',
            rating=Decimal('4.99'),
            owner=user,
        )

    def test_we_can_create_project_objects(self):
        """
        Ensure we can create a new Project object with an authenticated request
        """
        pjct_name = 'Project Two'
        pjct_description = "Some basic description"
        pjct_url = 'https://github.com/fedorkosilov/some-project'
        pjct_rating = Decimal('4.97')
        data = {
                "data": {
                    "type": "Project",
                    "attributes": {
                        "name": pjct_name,
                        "description": pjct_description,
                        "url": pjct_url,
                        "rating": pjct_rating,
                    }
                }
            }
        url = reverse('project-list')
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 2)
        project_two = Project.objects.get(id=2)
        self.assertEqual(project_two.name, pjct_name)
        self.assertEqual(project_two.url, pjct_url)

    def test_project_objects_url_validation(self):
        """
        Ensure Project URL validation works as expected
        """
        pjct_id = 1
        url = reverse('project-detail', kwargs={'pk':pjct_id})
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)

        # Test when domain != github.com
        pjct_url = "https://google.com/fedorkosilov/some-project"
        data = {
                "data": {
                    "type": "Project",
                    "id": pjct_id,
                    "attributes": {
                        "url": pjct_url,
                    }
                }
            }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0]['detail'], 'URL must be a valid link to a Project on GitHub.')

        # Test with incomplete URL
        pjct_url = "https://github.com/fedorkosilov"
        data = {
                "data": {
                    "type": "Project",
                    "id": pjct_id,
                    "attributes": {
                        "url": pjct_url,
                    }
                }
            }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0]['detail'], 'URL must be a valid link to a Project on GitHub.')

        # Test with invalid URL
        pjct_url = "htttps://github.com/fedorkosilov"
        data = {
                "data": {
                    "type": "Project",
                    "id": pjct_id,
                    "attributes": {
                        "url": pjct_url,
                    }
                }
            }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0]['detail'], 'URL must be a valid link to a Project on GitHub.')

        # Test with correct URL
        pjct_url = "https://github.com/fedorkosilov/literate-parakeet"
        data = {
                "data": {
                    "type": "Project",
                    "id": pjct_id,
                    "attributes": {
                        "url": pjct_url,
                    }
                }
            }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_project_objects_rating_validation(self):
        """
        Ensure Project Rating validation works as expected
        """
        pjct_id = 1
        url = reverse('project-detail', kwargs={'pk':pjct_id})
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)

        # Test when rating < 1 
        rating = 0
        data = {
                "data": {
                    "type": "Project",
                    "id": pjct_id,
                    "attributes": {
                        "rating": rating,
                    }
                }
            }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0]['detail'].title(), 'Ensure This Value Is Greater Than Or Equal To 1.')

        # Test when rating > 5 
        rating = 6
        data = {
                "data": {
                    "type": "Project",
                    "id": pjct_id,
                    "attributes": {
                        "rating": rating,
                    }
                }
            }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0]['detail'].title(), 'Ensure This Value Is Less Than Or Equal To 5.')

        # Test when rating = 1 (Valid) 
        rating = 1
        data = {
                "data": {
                    "type": "Project",
                    "id": pjct_id,
                    "attributes": {
                        "rating": rating,
                    }
                }
            }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test when rating = 5 (Valid) 
        rating = 5
        data = {
                "data": {
                    "type": "Project",
                    "id": pjct_id,
                    "attributes": {
                        "rating": rating,
                    }
                }
            }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_we_can_modify_project_objects_with_put(self):
        """
        Ensure we can modify existing Project object with an authenticated PUT request
        """
        pjct_id = 1
        pjct_name_modified = "Project Number One"
        pjct_url_modified = "https://github.com/fedorkosilov/literate-parakeet-modified"
        pjct_description_modified = "Some basic description modified"
        pjct_rating_modified = Decimal('4.98')
        data = {
            "data": {
                "type": "Project",
                "id": pjct_id,
                "attributes": {
                    "name": pjct_name_modified,
                    "description": pjct_description_modified,
                    "url": pjct_url_modified,
                    "rating": pjct_rating_modified,
                }
            }
        }
        url = reverse('project-detail', kwargs={'pk':pjct_id})
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Project.objects.count(), 1)
        project_one = Project.objects.get(id=1)
        self.assertEqual(project_one.name, pjct_name_modified)
        self.assertEqual(project_one.url, pjct_url_modified)
        self.assertEqual(project_one.description, pjct_description_modified)
        self.assertEqual(project_one.rating, pjct_rating_modified)        

    def test_we_can_modify_project_objects_with_patch(self):
        """
        Ensure we can modify existing Project object with an authenticated PATCH request
        """
        # Initial values
        pjct_id = 1
        pjct_name = "Project One"
        pjct_url = "https://github.com/fedorkosilov/literate-parakeet"
        pjct_rating = Decimal('4.99')
        # Values to be modified
        pjct_description_modified = "Some basic description modified"
        data = {
            "data": {
                "type": "Project",
                "id": pjct_id,
                "attributes": {
                    "description": pjct_description_modified,
                }
            }
        }
        url = reverse('project-detail', kwargs={'pk':pjct_id})
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Project.objects.count(), 1)
        project_one = Project.objects.get(id=1)
        self.assertEqual(project_one.name, pjct_name)
        self.assertEqual(project_one.url, pjct_url)
        self.assertEqual(project_one.description, pjct_description_modified)
        self.assertEqual(project_one.rating, pjct_rating)

    def test_we_can_delete_project_objects(self):
        """
        Ensure we can delete existing Project object with an authenticated DELETE request
        """
        pjct_id = 1
        data = {
            "data": {
                "type": "Project",
                "id": pjct_id,
            }
        }
        url = reverse('project-detail', kwargs={'pk':pjct_id})
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        response = self.client.delete(url, data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Project.objects.count(), 0)

    def test_we_cannot_create_project_objects_without_authentication(self):
        """
        Ensure CREATE methods for Project objects are not allowed without authentication
        """
        data = {
                "data": {
                    "type": "Project",
                    "attributes": {
                        "name": "Project Two",
                        "url": "https://github.com/fedorkosilov/literate-parakeet",
                    }
                }
            }
        url = reverse('project-list')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_we_cannot_put_patch_and_delete_project_objects_without_authentication(self):
        """
        Ensure PUT, PATCH and DELETE methods for Project objects are not allowed without authentication
        """
        data = {
                "data": {
                    "type": "Project",
                    "id": 1,
                    "attributes": {
                        "name": "Project Two",
                        "description": "Some basic description",
                        "url": "https://github.com/fedorkosilov/literate-parakeet",
                        "rating": Decimal('4.99'),
                    }
                }
            }
        url = reverse('project-detail', kwargs={'pk':1})
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.delete(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_authenticated_user_cannot_put_patch_and_delete_project_objects_he_doesnt_own(self):
        """
        Ensure PUT, PATCH and DELETE methods for Project object are not allowed for authenticated user,
        who is not an owner of this object
        """
        user2 = User.objects.create_user(
            username='testuser2', 
            password='12345',
        )
        user2_token = Token.objects.create(user=user2)
        auth_header2 = 'Token ' + user2_token.key
        data = {
                "data": {
                    "type": "Project",
                    "id": 1,
                    "attributes": {
                        "name": "Project Two",
                        "description": "Some basic description",
                        "url": "https://github.com/fedorkosilov/literate-parakeet",
                        "rating": Decimal('4.99'),
                    }
                }
            }
        url = reverse('project-detail', kwargs={'pk':1})
        self.client.credentials(HTTP_AUTHORIZATION=auth_header2)
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.delete(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_we_can_list_project_objects_without_authentication(self):
        """
        Ensure we can list Project objects without authentication
        """
        url = reverse('project-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)