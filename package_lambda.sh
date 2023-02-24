#!/usr/bin/env bash
# Builds deployment zip file for Lambda Python file in a subdirectory.
# Arguments:
# 1. Lambda subdirectory name
# 2. Name of Lambda Python file(s)

# Exit on error
set -e

printf 'Usage: lambda_dir lambda_python_filename...\n'

if [ "$#" -lt 2 ]; then
  exit 1
fi

LAMBDA_DIR="${1:?}"
LAMBDA_FILES=("${@:2}")
# DEPLOYMENT_ZIP='aws_lambda.zip'
DEPLOYMENT_ZIP=("${@:3}")
REQUIREMENTS_FILE='requirements-deploy.txt'

cd "${LAMBDA_DIR:?}"

# Install location for Python packages to be bundled with deployment zip
PACKAGE_DIR=package

# Stop if package dir or output zip exists; prompt caller to remove
if [ -f "${DEPLOYMENT_ZIP:?}" ]; then
    printf 'Unable to build; remove "%s" to proceed\n' "${DEPLOYMENT_ZIP:?}"
    exit 1
fi

if [ -d "${PACKAGE_DIR:?}" ]; then
    printf 'Unable to build; remove directory "%s" to proceed\n' "${PACKAGE_DIR:?}"
    exit 2
fi

if [ -f "${REQUIREMENTS_FILE:?}" ]; then
  # Install Python packages required for deployment into the (new) package dir
  printf 'Running pip install to "%s" dir\n' "${PACKAGE_DIR}"
  pip install --target "${PACKAGE_DIR:?}" --requirement "${REQUIREMENTS_FILE:?}"

  # Add packages to zip
  cd "${PACKAGE_DIR:?}"
  zip --recurse-paths "../${DEPLOYMENT_ZIP:?}" .
  cd ..
else
  printf 'No requirements file ("%s") to process\n' "${REQUIREMENTS_FILE}"
fi

# Add Lambda file(s) to zip
for lambda_file in "${LAMBDA_FILES[@]}"; do
  printf 'Adding "%s" to "%s"\n' "${lambda_file:?}" "${DEPLOYMENT_ZIP:?}"
  zip "${DEPLOYMENT_ZIP:?}" "${lambda_file:?}"
done

printf 'Deployment package:\n'
ls -ltrh "${DEPLOYMENT_ZIP:?}"
printf 'Deployment package content:\n'
unzip -l "${DEPLOYMENT_ZIP:?}"

printf 'Build complete; "%s" created in "%s":\n' "${DEPLOYMENT_ZIP:?}" "${PWD:?}"
