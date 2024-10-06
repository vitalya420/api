
# Loyalty Program API

## Overview
The Loyalty Program API is designed to enhance customer engagement and retention by allowing clients to earn and spend bonuses through a seamless rewards system. With features such as "Buy 6 Coffees, Get 1 Free," the API incentivizes repeat purchases, encouraging customers to return to participating businesses.

In addition to managing loyalty rewards, the API enables businesses to create and maintain a dynamic list of available menu items. This functionality allows users to browse and select from a variety of offerings directly within the app, enhancing their overall experience and making it easier to discover new products.

Moreover, the API provides businesses with the tools to communicate effectively with their customers. Through the app, businesses can share important news, promotions, and special offers, ensuring that users are always informed about the latest updates and opportunities to earn bonuses.

## Base Routes:
- `/api/auth/` - This endpoint is used for user authorization. It supports two realms of access:
  - **Mobile Realm:** Users can authenticate as business clients using the mobile app (realm set to 'mobile').
  - **Web Realm:** Users can also authenticate through the web interface designed for managing the loyalty program (realm set to 'web').
- `/api/mobile/` - This endpoint provides the API functionalities specifically tailored for the mobile application. It allows business clients to access features related to earning and spending bonuses, viewing available menu items, and receiving updates on promotions and news.
- `/api/web/` - This endpoint is dedicated to managers and administrators. It offers API functionalities for managing the loyalty program, including creating and updating promotions, managing user accounts, and overseeing the overall operation of the loyalty system.

**Warning:** Please note that tokens issued for the "mobile" realm will not be valid for the "web" realm, and vice versa. Users must authenticate separately for each realm to ensure proper access to the respective functionalities.

### Authorization flow

#### Requesting an OTP code 
To request an OTP (One-Time Password) code, the payload must contain the phone number in international format. Please note that there is an SMS cooldown period between sending messages, and there is a limit on the number of messages that can be sent (see possible errors below).

Example of request
```shell
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/auth' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "phone": "+1555555555"
}'
```

On success the response will be 200.

```json
{
  "success": true,
  "message": "OTP sent successfully."
}
```
**Possible errors:**
- Bad Request (400) if phone number is invalid

```json
{
  "description": "Bad Request",
  "status": 400,
  "message": "Invalid phone number"
}
```
- Service Unavailable (503) if sending to many sms.
```json
{
  "description": "Service Unavailable",
  "status": 503,
  "message": "Too many SMS"
}
```

#### Completing authorization
Having an OTP code you can complete authorization and access and refresh tokens.


Example of request to authorize in mobile realm.
```shell
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/auth/confirm' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "phone": "+1555555555",
  "otp": "105933",
  "realm": "web",
  "business": null
}'
```

Example of request to authorize in web realm.
```shell
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/auth/confirm' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "phone": "+1555555555",
  "otp": "105933",
  "realm": "mobile",
  "business": "BUSINESSCODE"
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
