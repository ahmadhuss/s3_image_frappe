import random
import string
import re
import os
import datetime
import mimetypes

import frappe

import magic
import boto3

from botocore.client import Config


@frappe.whitelist()
def img_upload_to_s3(doc, method):
    try:
        if doc.attached_to_doctype and doc.attached_to_field and doc.attached_to_name:
            doctype_name = doc.attached_to_doctype
            field_name = doc.attached_to_field
            doc_id = doc.attached_to_name
        else:
            print(f"\n\n No attachment found for file {doc.name}. \n\n")

        # Get the File_Url
        path = doc.file_url
        site_path = frappe.utils.get_site_path()

        # If path is None then exit the function
        if not path:
            return  # exit from the function

        if not doc.is_private:
            file_path = site_path + "/public" + path
        else:
            file_path = site_path + path

        mime_type = magic.from_file(file_path, mime=True)
        content_type = mime_type
        extension = mimetypes.guess_extension(mime_type)
        image_mime_pattern = re.compile(r"^image/")

        # Exit if file content type not matches the image MIME type
        if not image_mime_pattern.match(content_type):
            return  # exit from the function

        # S3 Upload
        # Boto3 Settngs:
        setting = frappe.get_single("S3 Image Upload")
        # Boto3 Object:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=setting.aws_key,
            aws_secret_access_key=setting.aws_secret,
            region_name=setting.region_name,
            config=Config(signature_version="s3v4")
        )

        # Create object name:
        original_filename = doc.file_name
        today = datetime.datetime.now()
        year = today.strftime("%Y")
        month = today.strftime("%m")
        day = today.strftime("%d")

        file_name = original_filename.replace(" ", "_")
        file_name = strip_special_chars(file_name)
        key = "".join(
            random.choice(
                string.ascii_uppercase + string.digits) for _ in range(8)
        )

        object_name = f"{setting.folder_name}/{year}/{month}/{day}/{key}_{file_name}"

        # Upload file
        s3_client.upload_file(
            file_path,  # Read the file from the original path
            setting.bucket_name,
            object_name,
            ExtraArgs={
                "ContentType": content_type,
                "Metadata": {
                    "ContentType": content_type,

                }
            }
        )

        # File URL Set Manually:
        # e.g. https://s3.amazonaws.com/a.imgpass.com/images/2024/09/18/6FJ44AHR_3d426add.jpg
        file_url = f"{setting.s3_bucket_base_url}/{object_name}"
        # Remove file physically from the OS
        os.remove(file_path)
        # DB Update
        frappe.db.sql("""UPDATE `tabFile` SET file_url=%s, folder=%s,
                    old_parent=%s, content_hash=%s WHERE name=%s""", (
            file_url, "Home/Attachments", "Home/Attachments", object_name, doc.name))

        doc.file_url = file_url
        frappe.db.commit()
    except Exception as err:
        frappe.log_error(err)


def strip_special_chars(file_name):
    regex = re.compile("[^0-9a-zA-Z._-]")
    file_name = regex.sub("", file_name)
    return file_name
