# Lambda da-ayr-bag-role-assigner

## To Build Deployment Zip

```base
cd ..
./package_lambda.sh \
  da-ayr-bag-role-assigner \
  lambda_function.py
```

## AWS Deployment Requirements

* Parameter Store:
  * Add parameter with JSON mapping config; for example:

    ```json
    [
      {"bag_department": "Testing A", "ayr_role": "department_a_role"},
      {"bag_department": "Testing B", "ayr_role": "department_b_role"},
      {"bag_department": "Testing C", "ayr_role": "department_c_role"}
    ]
    ```

    * Specify new parameter name in env var `AYR_ROLE_MAP_PARAM_STORE_KEY`
      (see next section)
* Lambda:
    * Configuration -> Environment variables:
        * `AYR_ROLE_MAP_PARAM_STORE_KEY`
            * Specifies the AWS Parameter Store parameter name that holds the JSON
              config that maps Bag department names to AYR role names
    * Configuration -> Permissions:
      * Need to assign Parameter Store access and decrypt permission; e.g.:
      
      ```json
      {
          "Version": "2012-10-17",
          "Statement": [
              {
                  "Sid": "GetParameter",
                  "Effect": "Allow",
                  "Action": "ssm:GetParameter",
                  "Resource": "arn:aws:ssm:---:---:parameter/ayr-key-path-here"
              },
              {
                  "Sid": "DecryptKey",
                  "Effect": "Allow",
                  "Action": "kms:Decrypt",
                  "Resource": "arn:aws:ssm:---:---:parameter/ayr-key-path-here"
              }
          ]
      }
      ```

## Run Test

For local testing env var `AYR_ROLE_MAP` can be used; for AWS deployment, use
env var `AYR_ROLE_MAP_PARAM_STORE_KEY` instead.

```bash
export AYR_ROLE_MAP='[{"bag_department": "Testing A", "ayr_role": "department_a_role"}]'
```

Set `AWS_PROFILE` to locally test getting OpenSearch password from Parameter
Store (using environment variable `AYR_ROLE_MAP_PARAM_STORE_KEY`):

```bash
export AWS_PROFILE=''
export AYR_ROLE_MAP_PARAM_STORE_KEY=''
```

Run test:

```bash
python3 -m unittest test_lambda_function.TestLambdaAYRBagRoleAssigner
```
