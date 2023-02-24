# da-ayr-bag-receiver

## Manual Execution

* Copy a bag archive to a s3 location; e.g.:

    ```bash
    # Get an arbitrary example bag
    BAG_FILE='TDR-2022-D6WD.tar.gz'
   
    BAG_URL='https://github.com/nationalarchives/'\
    'da-ayr-design-documentation/blob/main/'\
    'sample-data/bagit/'"${BAG_FILE:?}"'?raw=true'
   
    curl \
      --location \
      --output "${BAG_FILE:?}" \
      "${BAG_URL:?}"
    
    # Upload to s3
    export AWS_PROFILE=''
    S3_BUCKET=''
    
    aws s3 cp "${BAG_FILE:?}" "s3://${S3_BUCKET:?}/tre-data/${BAG_FILE:?}"
    
    # List items in path tre-data:
    aws s3 ls "s3://${S3_BUCKET:?}/tre-data/"
    ```

    ```bash
    # To remove all items in path tre-data:
    export AWS_PROFILE=''
    aws s3 rm --recursive "s3://${S3_BUCKET:?}/tre-data/"
    ```

* Create mock TRE output event with pre-signed URL to fetch TRE bag file:

    ```bash
    export AWS_PROFILE=''
    S3_BUCKET=''
    BAG_FILE='TDR-2022-D6WD.tar.gz'
    S3_URL="s3://${S3_BUCKET:?}/tre-data/${BAG_FILE:?}"
  
    TRE_OUTPUT_EVENT="$(
      printf '{
        "dri-preingest-sip-available": {
          "bag-url": "%s"
        }
      }\n' \
        "$(aws s3 presign --expires-in 60 "${S3_URL:?}")"
    )"
    
    echo "${TRE_OUTPUT_EVENT:?}"
    ```

* Trigger the Lambda:

    ```bash
    # Running locally
    export AWS_PROFILE=''
    export AYR_TARGET_S3_BUCKET=''
  
    # Setup virtual environment
    python3 -m venv venv-test-lambda
    . ./venv-test-lambda/bin/activate
    pip install --require-virtualenv --requirement requirements-dev.txt

    # Run Lambda handler function locally
    PYTHONPATH='.' ./run_lambda_function.py --event "${TEST_EVENT:?}"
    ```

    ```bash
    # Running on AWS
    LAMBDA_AWS_NAME=''
    TRE_OUTPUT_EVENT=''  # see above example
  
    aws lambda invoke \
      --function-name "${LAMBDA_AWS_NAME:?}" \
      --cli-binary-format raw-in-base64-out \
      --payload "${TRE_OUTPUT_EVENT:?}" \
      "${LAMBDA_AWS_NAME:?}.out" \
      --log-type Tail \
      --query 'LogResult' \
      --output text \
    | base64 --decode
    ```
