# Lambda da-ayr-bag-to-opensearch

## To Build Deployment Zip

```base
cd ..
./package_lambda.sh \
  da-ayr-bag-to-opensearch \
  lambda_function.py
```

## Run Test

For local testing env var `OPENSEARCH_USER_PASSWORD` can be used; for AWS
deployment, use env var `OPENSEARCH_USER_PASSWORD_PARAM_STORE_KEY` instead.

```bash
export OPENSEARCH_HOST_URL='https://localhost:22448'
export OPENSEARCH_USER='admin'
export OPENSEARCH_USER_PASSWORD=''
export OPENSEARCH_INDEX='example-test-index-1'
```

The following environment variable can be set to test against a remote
OpenSearch instance via a local `ssh` tunnel:

```bash
export DO_NOT_VERIFY_SSL='TRUE'
```

Set `AWS_PROFILE` to locally test getting OpenSearch password from Parameter
Store (using environment variable `OPENSEARCH_USER_PASSWORD_PARAM_STORE_KEY`):

```bash
export AWS_PROFILE=''
export OPENSEARCH_USER_PASSWORD_PARAM_STORE_KEY=''
```

Run test:

```bash
python3 -m unittest test_lambda_function.TestLambdaAYRBagToOpenSearch
```
