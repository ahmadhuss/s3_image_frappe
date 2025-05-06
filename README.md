# Frappe S3 Image Handler/Uploader

The following Frappe app automatically uploads all Frappe images to an AWS S3 bucket.

## Installation
```sh
# Clone and install the app in Frappe Bench
cd ~/frappe-bench
bench get-app https://github.com/your-repo/s3_image_fappe.git
bench --site your-site install-app s3_image_fappe
bench restart
```
## Set AWS S3 Credentials and Ready to Upload Images

![AWS Attachment](/attachment.jpg)

**Note:** 

Ensure that the bucket policy permits public access to images.

```js
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::test/*"
        }
    ]
}
```



## License
MIT (see [license.txt](./license.txt)
)
