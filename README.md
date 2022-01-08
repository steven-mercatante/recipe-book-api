# Recipe Book API

## Generate API Client
### 1. Update the OpenAPI spec
```
$ python manage.py generateschema --file openapi-schema.yaml
```

### 2. Regenerate the API SDK
```
$ npx @openapitools/openapi-generator-cli generate -i https://raw.githubusercontent.com/steven-mercatante/recipe-book-api/main/openapi-schema.yaml -g typescript-axios
```

### 3. Publish the new API SDK version
```
$ cd recipe-book-sdk
$ npm publish
```