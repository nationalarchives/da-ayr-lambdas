# da-ayr-bag-receiver

## Manual Execution

### Copy a bag archive to a s3 location

For example:

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
aws s3 ls "s3://${S3_BUCKET:?}/tre-data/" --recursive
```

```bash
# To remove all items in path tre-data:
export AWS_PROFILE=''
aws s3 rm --recursive "s3://${S3_BUCKET:?}/tre-data/"
```

### Run Test

Set `AWS_PROFILE`:

```bash
export AWS_PROFILE=''
```

Set input/output bucket:

```bash
export AYR_TARGET_S3_BUCKET=''
```

Set input name:

```bash
# For example:
export S3_KEY=tre-data/TDR-2022-D6WD.tar.gz
```

Run test:

```bash
python3 -m unittest test_lambda_function.TestLambdaAYRBagReceiver
```
