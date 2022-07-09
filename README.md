## Notes
* When testing with curl you may need to enable the option to follow redirects (-L) because S3 may initially respond with 307 redirect on requests to newly created buckets.
* Though it is possible to recognize and catalog multiple celebrities in a single image, for simplicity of this demo we assume that images will only contain a single person.
* Since this is a demo and we don't expect a high volume of requests, billing on the DynamoDB has been set to Pay Per Request to save costs.
