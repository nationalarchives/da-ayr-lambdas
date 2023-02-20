# da-ayr-rest-api

* [Deploying](#deploying)
    * [Create Deployment Package](#create-deployment-package)
* [Running](#running)
    * [Access Private API Gateway Via SSH Tunnel](#access-private-api-gateway-via-ssh-tunnel)
    * [Keycloak Authentication](#keycloak-authentication)
        * [Access Keycloak Directly](#access-keycloak-directly)
        * [Access Keycloak Via SSH Tunnel](#access-keycloak-via-ssh-tunnel)

* [Deploying](#deploying)
    * [Create Deployment Package](#create-deployment-package)
* [Running](#running)
    * [Access Private API Gateway Via SSH Tunnel](#access-private-api-gateway-via-ssh-tunnel)
* [Keycloak Operations](#keycloak-operations)
    * [Keycloak Authentication](#keycloak-authentication)
        * [Access Keycloak Directly](#access-keycloak-directly)
        * [Access Keycloak Via SSH Tunnel](#access-keycloak-via-ssh-tunnel)
    * [Keycloak Token Validation](#keycloak-token-validation)

# Deploying

## Create Deployment Package

Run the following from the Lambda function directory:

```bash
# If present, remove old version of package dir
rm -rf ./package

# Create deployment package zip file
./build.sh
```

# Running

## Access Private API Gateway Via SSH Tunnel

Open tunnel; i.e. `localhost:22443` -> Jump Host -> Private API Gateway:

```bash
JUMP_HOST='?'
JUMP_HOST_USER='?'
API_GATEWAY_HOST='?.execute-api.?.amazonaws.com'

ssh -N \
  "${JUMP_HOST_USER}"@"${JUMP_HOST}" \
  -L localhost:22443:${API_GATEWAY_HOST}:443
```

Hit endpoint via local tunnel (--resolve for SSL certificate hostname match):

```bash
API_GATEWAY_HOST='?.execute-api.?.amazonaws.com'

# --resolve to make hostname resolve to local IP address (127.0.0.1):
curl --request POST \
  --resolve "${API_GATEWAY_HOST}:22443:127.0.0.1" \
  "https://${API_GATEWAY_HOST}:22443/test"
```

# Keycloak Operations

## Keycloak Authentication

### Access Keycloak Directly

```bash
KEYCLOAK_HOST=''
KEYCLOAK_REALM=''
CLIENT_ID=''
CLIENT_SECRET=''
USER_NAME=''
USER_PASSWORD=''

if token="$(
  curl --request POST \
    --fail-with-body \
    --silent \
    --show-error \
    --data "client_id=${CLIENT_ID:?}" \
    --data "client_secret=${CLIENT_SECRET:?}" \
    --data "username=${USER_NAME:?}" \
    --data "password=${USER_PASSWORD:?}" \
    --data 'grant_type=password' \
    "https://${KEYCLOAK_HOST:?}/realms/${KEYCLOAK_REALM:?}/protocol/openid-connect/token"
)"; then
  printf 'token:\n%s\n' "${token}"
  if access_token="$(
    echo -n "${token:?}" \
    | python3 -c 'import json,sys;print(json.load(sys.stdin)["access_token"])'
  )"; then
    printf 'access_token:\n%s\n' "${access_token}"
  else
    printf 'ERROR: %s\n' "${$?}"
  fi
else
  printf 'ERROR: %s\n' "${$?}"
fi
```

### Access Keycloak Via SSH Tunnel

Open tunnel; i.e. `localhost:22444` -> Jump Host -> Keycloak:

```bash
JUMP_HOST=''
JUMP_HOST_USER=''
KEYCLOAK_HOST=''

ssh -N \
  "${JUMP_HOST_USER}"@"${JUMP_HOST}" \
  -L localhost:22444:${KEYCLOAK_HOST}:443
```

Hit endpoint via local tunnel (--resolve for SSL certificate hostname match):

```bash
KEYCLOAK_HOST=''

# --resolve to make hostname resolve to local IP address (127.0.0.1):
curl --request POST \
  --resolve "${KEYCLOAK_HOST:?}:22444:127.0.0.1" \
  --fail-with-body \
  --silent \
  --show-error \
  --data "client_id=${CLIENT_ID:?}" \
  --data "client_secret=${CLIENT_SECRET:?}" \
  --data "username=${USER_NAME:?}" \
  --data "password=${USER_PASSWORD:?}" \
  --data 'grant_type=password' \
  "https://${KEYCLOAK_HOST:?}:22444/realms/${KEYCLOAK_REALM:?}/protocol/openid-connect/token"
```

## Keycloak Token Validation

To check value in var `access_token`:

```bash
KEYCLOAK_HOST=''
KEYCLOAK_REALM=''
CLIENT_ID=''
CLIENT_SECRET=''

curl --request POST \
  --fail-with-body \
  --silent \
  --show-error \
  --data "client_id=${CLIENT_ID:?}" \
  --data "client_secret=${CLIENT_SECRET:?}" \
  --data "token=${access_token:?}" \
  "https://${KEYCLOAK_HOST:?}/realms/${KEYCLOAK_REALM:?}/protocol/openid-connect/token/introspect" \
| python3 -m json.tool
```

> See section [Keycloak Authentication](#keycloak-authentication) above to get
> an access token

* Validation endpoint can be verified with:

    ```bash
    KEYCLOAK_HOST=''
    KEYCLOAK_REALM=''
    
    curl \
        "https://${KEYCLOAK_HOST:?}/realms/${KEYCLOAK_REALM:?}/.well-known/openid-configuration" \
        | python3 -m json.tool
    ```
  