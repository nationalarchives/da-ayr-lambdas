# Lambda da-ayr-bag-unpacker

## To Build Deployment Zip

```base
cd ..
./package_lambda.sh \
  da-ayr-bag-unpacker \
  lambda_function.py \
  tar_lib.py
```

## To Run Locally

* Create an input event; for example:

    ```bash
    export AWS_PROFILE=''
    S3_BUCKET=''
    BAG_FILE='TDR-2022-D6WD.tar.gz'
    BAG_OUTPUT_S3_PATH="ayr-in/${BAG_FILE:?}"
  
    TEST_EVENT="$(
    printf '{
      "s3_bucket": "%s",
      "bag_name": "%s",
      "bag_output_s3_path": "%s"
    }\n' \
      "${S3_BUCKET:?}" \
      "${BAG_FILE:?}" \
      "${BAG_OUTPUT_S3_PATH:?}" \
    )" && echo "${TEST_EVENT:?}"
    ```

* Trigger the Lambda:

    ```bash
    # Running locally
    export AWS_PROFILE=''
  
    # Setup virtual environment
    python3 -m venv venv-test-lambda
    . ./venv-test-lambda/bin/activate
    pip install --require-virtualenv --requirement requirements-dev.txt
  
    # Run Lambda handler function locally
    PYTHONPATH='.' ./run_lambda_function.py --event "${TEST_EVENT:?}"
    ```
