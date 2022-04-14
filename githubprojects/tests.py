from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from decimal import Decimal
from .models import Project

class ProjectTests(APITestCase):
    def setUp(self):
        self.first_project = Project.objects.create(
            name='Project One',
            description='Some basic description',
            url='https://github.com/fedorkosilov/literate-parakeet',
            rating=Decimal('4.99'),
        )

    def test_create_project(self):
        """
        Ensure we can create a new Project object
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
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 2)
        project_two = Project.objects.get(id=2)
        self.assertEqual(project_two.name, pjct_name)
        self.assertEqual(project_two.url, pjct_url)

    def test_project_url_validation(self):
        """
        Ensure Project URL validation works as expected
        """
        pjct_id = 1
        url = reverse('project-detail', kwargs={'pk':pjct_id})
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

    def test_modify_project_with_put(self):
        """
        Ensure we can modify existing Project object with PUT request
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
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Project.objects.count(), 1)
        project_one = Project.objects.get(id=1)
        self.assertEqual(project_one.name, pjct_name_modified)
        self.assertEqual(project_one.url, pjct_url_modified)
        self.assertEqual(project_one.description, pjct_description_modified)
        self.assertEqual(project_one.rating, pjct_rating_modified)        

    def test_modify_project_with_patch(self):
        """
        Ensure we can modify existing Project object with PATCH request
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
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Project.objects.count(), 1)
        project_one = Project.objects.get(id=1)
        self.assertEqual(project_one.name, pjct_name)
        self.assertEqual(project_one.url, pjct_url)
        self.assertEqual(project_one.description, pjct_description_modified)
        self.assertEqual(project_one.rating, pjct_rating)

    def test_delete_project(self):
        """
        Ensure we can delete existing Project object with DELETE request
        """
        pjct_id = 1
        data = {
            "data": {
                "type": "Project",
                "id": pjct_id,
            }
        }
        url = reverse('project-detail', kwargs={'pk':pjct_id})
        response = self.client.delete(url, data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Project.objects.count(), 0)


        # TODO: Remove comments
        # print(dir(response))
        # print(data)
        # print(response.data)        