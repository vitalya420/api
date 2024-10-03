
# API


### Authorization flow

#### Requesting an OTP code 
To request an OTP (One-Time Password) code, the payload must contain the phone number in international format. Please note that there is an SMS cooldown period between sending messages, and there is a limit on the number of messages that can be sent (see possible errors below).

Example of request
```shell
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/auth' \
  -H 'accept: application/json' \
  -H 'X-Business-ID: MY-BUSINESS-ID' \
  -H 'Content-Type: application/json' \
  -d '{
  "phone": "+11234567890"
}'
```

On success the response will be 200.

```json
{
  "success": true,
  "message": "OTP sent successfully."
}
```
Possible errors:
- Bad Request (400) if phone number is invalid
- Service Unavailable (503) if sending to many sms.

```json
{
  "description": "Bad Request",
  "status": 400,
  "message": "Invalid phone number"
}
```

```json
{
  "description": "Service Unavailable",
  "status": 503,
  "message": "Too many SMS"
}
```

#### Completing authorization
Having an OTP code you can complete authorization and access and refresh tokens.

**Warning: issued token will be work for business from headers.** 

Example of request
```shell
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/auth/confirm' \
  -H 'accept: application/json' \
  -H 'X-Business-ID: MY-BUSINESS-ID' \
  -H 'Content-Type: application/json' \
  -d '{
  "phone": "+380956405967",
  "otp": "674057"
}'
```

On success the response will be 200.

```json
{
  "access_token": "<access token>",
  "refresh_token": "<refresh token>"
}
```

Possible errors:
- Bad Request (400) if OTP code is expired or user did not requested OTP code.

```json
{
  "description":"Bad Request",
  "status":400,
  "message":"OTP code is expired"
}
```
