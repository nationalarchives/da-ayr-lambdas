# Lambda da-ayr-bag-unpacker

## To Build Deployment Zip

```base
cd ..
./package_lambda.sh \
  da-ayr-bag-indexer \
  lambda_function.py \
  s3_bag_reader.py
```

## Run Test

Set `S3_BUCKET` to bucket holding unpacked test files:

```bash
export S3_BUCKET=''
```

Set `AWS_PROFILE`:

```bash
export AWS_PROFILE=''
```

Run test:

```bash
python3 -m unittest test_lambda_function.TestLambdaAYRBagIndexer
```
