# da-ayr-rest-api

## Create Deployment Package

Run the following from the Lambda function directory:

```bash
# If present, remove old version of package dir
rm -rf ./package

# Create deployment package zip file
./build.sh
```
