import json
import aws_lambda

event = {
    'body': json.dumps(
        {
            'a': 42,
            'opensearch_index': 'bag_flat',
            'Source-Organization': 'Testing A'
        }
    )
}

result = aws_lambda.lambda_handler(event, None)
print(f'### result {"#" * 80}\n{result}')
