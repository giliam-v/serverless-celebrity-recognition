# Serverless celebrity recognition API
Deploy a serverless API in the AWS cloud that performs celebrity recognition on uploaded images.

## Architecture
The serverless API is provisioned by CloudFormation template using Serverless Application Model (SAM) and consists of the following elements:
* An S3 bucket for storing uploaded images.
* An API Gateway with endpoints for uploading, listing and describing catalogued images.
* A DynamoDB table which holds metadata about uploaded images.
* Several Lambda functions that perform the backend interaction between API Gateway, S3, DynamoDB and Rekognition service.

![Architecture](diagram.png?raw=true)


## Deployment
#### Using SAM CLI
```
$ sam deploy --stack-name <StackName> --s3-bucket <StagingBucketName> --parameter-overrides S3BucketName=<ImageUploadBucketName> --capabilities CAPABILITY_IAM
```
#### Using AWS CLI
```
$ aws cloudformation package --template-file template.yaml --s3-bucket <StagingBucketName> --output-template-file packaged.yaml

$ aws cloudformation deploy --template-file packaged.yaml --stack-name <StackName> --parameter-overrides S3BucketName=<ImageUploadBucketName> --capabilities CAPABILITY_IAM
```

## Example
### 1. Generate pre-signed URL and upload images
After the stack is created, note the API Gateway stage address from the stack outputs. In this example we will pretend the address is `https://abcd1234.execute-api.eu-west-1.amazonaws.com/Prod`

To get an upload pre-signed URL simply append **`/get-presigned-url`** endpoint path with **`?filename=<string>`** query string parameter to specify the file name:

```shell
$ curl https://abcd1234.execute-api.eu-west-1.amazonaws.com/Prod/get-presigned-url?filename=image_01.jpg

{"URL": "https://example-image-upload-api-bucket.s3.amazonaws.com/image_01.jpg?....long..string...."}
```

Now we can perform a PUT request to the pre-signed URL returned from previous step:
```shell
$ curl -I -L --upload-file sample_images/image_01.jpg "https://example-image-upload-api-bucket.s3.amazonaws.com/image_01.jpg?....long..string...."

HTTP/1.1 100 Continue

HTTP/1.1 200 OK
........
........
```

### 2. List all image files
To list metadata of all uploaded images we can perform GET request to the **`/images`** endpoint:

```shell
$ curl "https://abcd1234.execute-api.eu-west-1.amazonaws.com/Prod/images"

{
  "Items": [
    {
      "filename": {
        "S": "image_07.jpg"
      },
      "date": {
        "S": "2022-07-10T12:25:47.951Z"
      },
      "bucket": {
        "S": "example-image-upload-api-bucket"
      },
      "celebrities": {
        "SS": [
          "Anna Torv",
          "Blair Brown",
          "Jasika Nicole",
          "John Noble",
          "Joshua Jackson",
          "Lance Reddick",
          "Seth Gabel"
        ]
      }
    },
    ....
    ....
```

The **/images** endpoint path allows the following query string parameters:

| Query String | Function |
|--------------|----------|
|datetime=ascending\|descending | Sorts the images based on upload date
|limit=[int] | Limits number of results returned. Can be used to force pagination.

If results are paginated, a NextPage URL will be provided which automatically includes a pagination token for loading the next entries:

```shell
$ curl "https://abcd1234.execute-api.eu-west-1.amazonaws.com/Prod/images?datetime=descending&limit=1"
{
  "Items": [
    {
      "filename": {
        "S": "image_01.jpg"
      },
      "date": {
        "S": "2022-07-11T19:46:41.010Z"
      },
      "bucket": {
        "S": "example-image-upload-api-bucket"
      },
      "celebrities": {
        "SS": [
          "Anna Torv"
        ]
      }
    }
  ],
  "NextPage": "https://abcd1234.execute-api.eu-west-1.amazonaws.com/Prod/images?datetime=descending&limit=1&token=eyJmaWxlbmFtZSI6IHsiUyI6ICJpbWFnZV8wMS5qcGcifSwgImRhdGUiOiB7IlMiOiAiMjAyMi0wNy0xMVQxOTo0Njo0MS4wMTBaIn0sICJidWNrZXQiOiB7IlMiOiAidGVzdC1pbWFnZS11cGxvYWQtYXBpLWJ1Y2tldCJ9fQ=="
```

### 3. Describe single image
To get the metadata of a sinlge image file we perform a GET request to **`/images/{filename}`** where {filename} is the name of the image file:
```shell
$ curl "https://abcd1234.execute-api.eu-west-1.amazonaws.com/Prod/images/image_04.jpg"

{
  "filename": {
    "S": "image_04.jpg"
  },
  "date": {
    "S": "2022-07-10T17:03:07.377Z"
  },
  "bucket": {
    "S": "example-image-upload-api-bucket"
  },
  "celebrities": {
    "SS": [
      "Joshua Jackson"
    ]
  }
}
```


## Notes
* When uploading images to pre-signed URL, you may need to allow following redirects (-L option in curl) because S3 may initially respond with 307 redirect on requests to newly created buckets.
* When cleaning up, make sure to first empty the S3 image upload bucket, otherwise the CloudFormation stack may fail to delete the bucket during stack termination.
