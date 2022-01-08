# Recipe Book API

## Generate API Client
### 1. Update the OpenAPI spec
```
$ python manage.py generateschema --file openapi-schema.yaml
```

### 2. Regenerate the API SDK
```
$ cd recipe-book-sdk/src
$ npx @openapitools/openapi-generator-cli generate -i https://raw.githubusercontent.com/steven-mercatante/recipe-book-api/main/openapi-schema.yaml -g typescript-axios
```

### 3. Publish the new API SDK version
```
# From recipe-book-sdk project
# Bump the version number in package.json
# Commit all changes & push to origin
$ npm publish
```