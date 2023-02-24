#!/usr/bin/env bash
# Builds deployment zip file for Lambda. Must be run from this directory.

# Exit on error
set -e

DEPLOYMENT_ZIP="${1:-aws_lambda.zip}"
LAMBDA_FILE="${2:-lambda_function.py}"

printf 'Packaging Lambda "%s" into "%s"\n' "${LAMBDA_FILE:?}" "${DEPLOYMENT_ZIP:?}"

# Install location for Python packages to be bundled with deployment zip
PACKAGE_DIR=package

# Stop if package dir exists; prompt caller to remove it to proceed
if [ -d "${PACKAGE_DIR:?}" ]; then
    printf 'Unable to build; remove directory "%s" to proceed\n' "${PACKAGE_DIR:?}"
    exit 1
fi

# Install Python packages required for deployment into the (new) package dir
pip install --target "${PACKAGE_DIR:?}" --requirement requirements-deploy.txt

# Add packages to zip
cd "${PACKAGE_DIR:?}"
zip -r "../${DEPLOYMENT_ZIP:?}" .

# Add Lambda file to zip
cd ..
zip "${DEPLOYMENT_ZIP:?}" "${LAMBDA_FILE:?}"

printf 'Build complete; "%s" created:\n' "${DEPLOYMENT_ZIP:?}"
ls -ltrh "${DEPLOYMENT_ZIP:?}"
