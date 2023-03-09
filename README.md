# da-ayr-lambdas

Lambda code for the Access Your Records service

## Pipeline workflow

This is a GitHub workflow that automates the process of zipping AWS Lambda functions and uploading them to an S3 bucket.

The workflow is triggered when there is a push to the "dev" branch. The "permissions" section specifies the permissions required for the workflow to execute successfully.

The "zip-lambda-function" job runs on an "ubuntu-latest" environment and consists of several steps, each of which performs a specific task:

1. "Checkout" step checks out the code from the repository.
2. "Zip" steps zip the Lambda functions and rename them accordingly.
3. "Login in to Non Prod Account" step uses AWS Actions to configure the AWS credentials and access the Non-Prod account.
4. "Move Lambda zip file to /old folder" step moves the previously uploaded zip files to a folder called "/old" with a timestamp.
5. "Upload" steps upload the newly created zip files to the S3 bucket.

The "env" section provides environment variables to the steps. In this workflow, the environment variable "AWS_BUCKET_NAME" is used to specify the name of the S3 bucket. Additionally, the "timestamp" variable is used to add a timestamp to the names of the files that are moved to the "/old" folder.

The workflow uses the "aws-cli" to upload and move the files. The "aws s3 cp" command is used to upload files to the S3 bucket, and the "aws s3 mv" command is used to move files from the root directory to the "/old" folder.

Overall, this workflow automates the tedious process of zipping Lambda functions and uploading them to S3, saving time and reducing the likelihood of errors.