from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APISimpleTestCase
from rest_framework.authtoken.models import Token
from webhooks.models import Webhook
from githubprojects.models import Project
from django.test import SimpleTestCase
from celery.contrib.testing.worker import start_worker
from djangochallenge.celery import app
from decimal import Decimal
from unittest.mock import patch
import json


class WebhookTests(APITestCase):
    """
    Webhook tests
    """
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='testuser1', 
            password='12345',
        )
        user1_token = Token.objects.create(user=self.user1)
        self.user1_auth_header = 'Token ' + user1_token.key

        self.user1_webhook = Webhook.objects.create(
            url='https://example.com/0abb8ad2-48db-47bf-9eef-c653ee36ff32-test',
            comment='User 1 Webhook',
            owner=self.user1,
        )

    def test_user_can_create_webhook_objects(self):
        """
        Ensure user can create a new Webhook object with an authenticated request
        """
        webhook_url = 'https://example.com/0abb8ad2-48db-47bf-9eef-c653ee36ff32-WEBHOOK-2'
        comment = 'Some comment'
        data = {
                'data': {
                    'type': 'Webhook',
                    'attributes': {
                        'url': webhook_url,
                        'comment': comment,
                    }
                }
            }
        url = reverse('webhook-list')
        self.client.credentials(HTTP_AUTHORIZATION=self.user1_auth_header)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Webhook.objects.count(), 2)
        webhook2 = Webhook.objects.get(id=2)
        self.assertEqual(webhook2.url, webhook_url)
        self.assertEqual(webhook2.comment, comment)
        self.assertEqual(webhook2.owner, self.user1)

    def test_we_can_modify_webhook_objects_with_put(self):
        """
        Ensure we can modify existing Webhook object with an authenticated PUT request
        """
        webhook_id = 1
        webhook_url_modified = 'https://example.com/0abb8ad2-48db-47bf-9eef-c653ee36ff32-WEBHOOK-2'
        comment_modified = 'Some comment'
        data = {
                'data': {
                    'type': 'Webhook',
                    'id': webhook_id,
                    'attributes': {
                        'url': webhook_url_modified,
                        'comment': comment_modified,
                    }
                }
            }
        url = reverse('webhook-detail', kwargs={'pk':webhook_id})
        self.client.credentials(HTTP_AUTHORIZATION=self.user1_auth_header)
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Webhook.objects.count(), 1)
        webhook1 = Webhook.objects.get(id=1)
        self.assertEqual(webhook1.url, webhook_url_modified)
        self.assertEqual(webhook1.comment, comment_modified)
        self.assertEqual(webhook1.owner, self.user1)

    def test_we_can_modify_webhook_objects_with_patch(self):
        """
        Ensure we can modify existing Webhook object with an authenticated PATCH request
        """
        # Initial values
        webhook_id = 1
        webhook_url='https://example.com/0abb8ad2-48db-47bf-9eef-c653ee36ff32-test'
        # Values to be modified
        comment_modified = 'Some comment'
        data = {
                'data': {
                    'type': 'Webhook',
                    'id': webhook_id,
                    'attributes': {
                        'comment': comment_modified,
                    }
                }
            }
        url = reverse('webhook-detail', kwargs={'pk':webhook_id})
        self.client.credentials(HTTP_AUTHORIZATION=self.user1_auth_header)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Webhook.objects.count(), 1)
        webhook1 = Webhook.objects.get(id=1)
        self.assertEqual(webhook1.url, webhook_url)
        self.assertEqual(webhook1.comment, comment_modified)
        self.assertEqual(webhook1.owner, self.user1)

    def test_we_can_delete_webhook_objects(self):
        """
        Ensure we can delete existing Webhook object with an authenticated DELETE request
        """
        webhook_id = 1
        data = {
            'data': {
                'type': 'Webhook',
                'id': webhook_id,
            }
        }
        url = reverse('webhook-detail', kwargs={'pk':webhook_id})
        self.client.credentials(HTTP_AUTHORIZATION=self.user1_auth_header)
        response = self.client.delete(url, data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Webhook.objects.count(), 0)

    def test_we_cannot_create_webhook_objects_without_authentication(self):
        """
        Ensure CREATE methods for Webhook objects are not allowed without authentication
        """
        data = {
                'data': {
                    'type': 'Webhook',
                    'attributes': {
                        'url': 'https://example.com/hook',
                        'comment': 'Webhook',
                    }
                }
            }
        url = reverse('webhook-list')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_we_cannot_put_patch_and_delete_webhook_objects_without_authentication(self):
        """
        Ensure PUT, PATCH and DELETE methods for Webhook objects are not allowed without authentication
        """
        data = {
                'data': {
                    'type': 'Webhook',
                    'id': 1,
                    'attributes': {
                        'url': 'https://example.com/hook',
                        'comment': 'Webhook',
                    }
                }
            }
        url = reverse('webhook-detail', kwargs={'pk':1})
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.delete(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_authenticated_user_cannot_put_patch_and_delete_webhook_objects_he_doesnt_own(self):
        """
        Ensure PUT, PATCH and DELETE methods for Webhook object are not allowed for authenticated user,
        who is not not an owner of this object
        """
        user2 = User.objects.create_user(
            username='testuser2', 
            password='12345',
        )
        user2_token = Token.objects.create(user=user2)
        auth_header2 = 'Token ' + user2_token.key
        data = {
                'data': {
                    'type': 'Webhook',
                    'id': 1,
                    'attributes': {
                        'url': 'https://example.com/hook',
                        'comment': 'Webhook',
                    }
                }
            }
        url = reverse('webhook-detail', kwargs={'pk':1})
        self.client.credentials(HTTP_AUTHORIZATION=auth_header2)
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.delete(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class WebhookCeleryTasksTests(SimpleTestCase):
    """
    Webhook Celery Tasks Tests
    """
    databases = '__all__'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.celery_worker = start_worker(app, perform_ping_check=False)
        cls.celery_worker.__enter__()    

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.celery_worker.__exit__(None, None, None)

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='testuser1', 
            password='12345',
        )
        self.user1_webhook = Webhook.objects.create(
            url='https://example.com/0abb8ad2-48db-47bf-9eef-c653ee36ff32-test',
            comment='User 1 Webhook',
            owner=self.user1,
        )

    @patch('webhooks.tasks.requests.post')
    def test_webhooks_on_project_creation(self,mock):
        """
        Ensure we send webhooks with correct payload on Project creation 
        """
        mock.return_value.ok = True

        pjct_name = 'Project Two'
        pjct_description = 'Some basic description'
        pjct_url = 'https://github.com/fedorkosilov/literate-parakeet'
        pjct_rating = Decimal('4.99')
        
        project = Project.objects.create(
            name= pjct_name,
            description= pjct_description,
            url=pjct_url,
            rating=pjct_rating,
            owner=self.user1,
        )

        mock_call_args, mock_call_kwargs = mock.call_args_list[0]
        webhook_payload = json.loads(mock_call_kwargs['data'])
        self.assertEqual(mock.call_count, 1)
        self.assertEqual(mock_call_kwargs['url'], self.user1_webhook.url)
        self.assertEqual(webhook_payload['data']['type'], 'Project')
        self.assertEqual(webhook_payload['data']['id'], project.id)
        self.assertEqual(webhook_payload['data']['attributes']['name'], project.name)
        self.assertEqual(webhook_payload['data']['attributes']['description'], project.description)
        self.assertEqual(webhook_payload['data']['attributes']['url'], project.url)
        self.assertEqual(webhook_payload['data']['attributes']['rating'], str(project.rating))
        self.assertEqual(webhook_payload['data']['attributes']['owner'], project.owner.username)