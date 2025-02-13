from django.test import TestCase
from django.urls import reverse

class UserAuthTest(TestCase):
    def test_getAllUsers(self):
        # URL for the view
        url = reverse('GetAllUsers')  # Assuming you have named your URL pattern 'my_view'

        # Making a GET request to the view
        response = self.client.get(url)

        # Asserting that the response has a 200 status code
        self.assertEqual(response.status_code, 200)

        # Asserting that the response content is as expected
        self.assertContains(response, [])