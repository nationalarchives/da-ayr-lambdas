# OpenSearch Config

Example OpenSearch index and data configuration files showing one way a Bag
can be represented in OpenSearch.

The following sections describe how to load and query the data:

* [Loading OpenSearch configuration](#loading-opensearch-configuration)
  * [Environment setup](#environment-setup)
    * [Identify OpenSearch host and credentials](#identify-opensearch-host-and-credentials)
    * [Verify access](#verify-access)
  * [Add index to OpenSearch](#add-index-to-opensearch)
    * [Put index](#put-index)
    * [View index definition](#view-index-definition)
  * [Add data record to OpenSearch](#add-data-record-to-opensearch)
* [Viewing OpenSearch records](#viewing-opensearch-records)
  * [Listing indices](#listing-indices)
  * [Listing records](#listing-records)
    * [Without query](#without-query)
    * [With query](#with-query)

# Loading OpenSearch configuration

| File                                                       | Description                                                    |
|------------------------------------------------------------|----------------------------------------------------------------|
| [opensearch_bag_example.json](opensearch_bag_example.json) | Shows one way a bag can be represented as an OpenSearch record |
| [bag_index.json](bag_index.json)                           | An OpenSearch index file for the above example                 |

## Environment setup

### Identify OpenSearch host and credentials

```bash
OPENSEARCH_USER=''
OPENSEARCH_PASSWORD=''
OPENSEARCH_CREDENTIALS="${OPENSEARCH_USER}:${OPENSEARCH_PASSWORD}"
OPENSEARCH_HOST=''
OPENSEARCH_PORT=''
OPENSEARCH_URL="https://${OPENSEARCH_HOST:?}:${OPENSEARCH_PORT:?}"
OPENSEARCH_INDEX='bag-example'
```

### Verify access

Print OpenSearch "about" page:

```bash
curl \
  --request GET "${OPENSEARCH_URL:?}" \
  --user "${OPENSEARCH_CREDENTIALS:?}"
```

## Add index to OpenSearch

### Put index

```bash
curl \
  --header "Content-Type: application/json" \
  --request PUT "${OPENSEARCH_URL:?}/${OPENSEARCH_INDEX:?}" \
  --user "${OPENSEARCH_CREDENTIALS:?}" \
  --data-binary '@bag_index.json'
```


### View index definition

```bash
curl \
  --request GET "${OPENSEARCH_URL:?}/${OPENSEARCH_INDEX:?}" \
  --user "${OPENSEARCH_CREDENTIALS:?}"
```

## Add data record to OpenSearch

To load a sample record:

```bash
OPENSEARCH_RECORD_ID='1'

curl \
  --header "Content-Type: application/json" \
  --request PUT "${OPENSEARCH_URL:?}/${OPENSEARCH_INDEX:?}/_doc/${OPENSEARCH_RECORD_ID:?}" \
  --user "${OPENSEARCH_CREDENTIALS:?}" \
  --data-binary '@opensearch_bag_example.json'
```

# Viewing OpenSearch records

## Listing indices

```bash
curl \
  --request GET "${OPENSEARCH_URL:?}/_cat/indices" \
  --user "${OPENSEARCH_CREDENTIALS:?}"
```

## Listing records

### Without query

```bash
curl \
  --request GET "${OPENSEARCH_URL:?}/${OPENSEARCH_INDEX:?}/_search" \
  --user "${OPENSEARCH_CREDENTIALS:?}"
```

### With query

```bash
# Define the OpenSearch query to run
OPENSEARCH_QUERY='{
  "query": {
    "match_phrase": {
      "bag_data.bag-info.txt.Source-Organization": "Testing A"
    }
  }
}'

# Show matching records
curl \
  --header 'Content-Type: application/json' \
  --request GET "${OPENSEARCH_URL:?}/${OPENSEARCH_INDEX:?}/_search" \
  --user "${OPENSEARCH_CREDENTIALS:?}" \
  --data "${OPENSEARCH_QUERY:?}"

# Count matching records
curl \
  --header 'Content-Type: application/json' \
  --request GET "${OPENSEARCH_URL:?}/${OPENSEARCH_INDEX:?}/_count" \
  --user "${OPENSEARCH_CREDENTIALS:?}" \
  --data "${OPENSEARCH_QUERY:?}"
```
