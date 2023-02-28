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

Set `AWS_PROFILE`:

```bash
export AWS_PROFILE=''
```

Specify `S3_BUCKET`:

```bash
export S3_BUCKET=''
```

Run test:

```bash
python3 -m unittest test_lambda_function.TestLambdaAYRBagUnpacker
```
