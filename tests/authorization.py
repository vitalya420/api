import unittest

from sanic_testing.testing import SanicASGITestClient

from app import app
from app.services import otp_service


class TestAuthorization(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = SanicASGITestClient(app)
        self.phone = "+15556667878"

    async def test_send_otp(self):
        _, response = await self.client.post('/api/v1/auth', json={"phone": self.phone})
        print(response)

    async def test_confirm_otp(self):
        result = await otp_service.get_unexpired_otp(self.phone)
        print(result)
