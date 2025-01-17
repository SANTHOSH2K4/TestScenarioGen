from django.db import models

class User(models.Model):
    uid = models.AutoField(primary_key=True)  # Auto-incrementing integer for user ID
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Conversation(models.Model):
    uid = models.ForeignKey(User, on_delete=models.CASCADE, to_field='uid')  # Reference to User table
    cid = models.AutoField(primary_key=True)  # Auto-incrementing integer for conversation ID
    config = models.TextField(default="{'application_type': {'description': 'Type of application', 'options': {'web app': False, 'mobile app': True, 'api': False}}, 'test_design_techniques': {'description': 'Test Design Techniques', 'test_methodologies': {'boundary_value_analysis': True, 'equivalence_partitioning': True, 'state_transition_testing': True, 'decision_table_testing': True}}, 'testing_coverage': {'description': 'Required testing coverage', 'test_coverage_needed': {'functional_testing': True, 'nonfunctional_testing': True}, 'test_coverage_options': {'functional_testing': {'description': 'Functional testing coverage options', 'individual_field_testing': True}, 'nonfunctional_testing': {'description': 'Non-functional testing coverage options', 'performance_testing': True, 'security_testing': False, 'compatibility_testing': True, 'network_based_testing': True, 'interruption_testing': True}}}}")
    datetime = models.DateTimeField(auto_now_add=True)
    conversation_name = models.CharField(max_length=255, default="conversation name")  # New field for conversation name

    def __str__(self):
        return f"Conversation {self.cid} for User {self.uid}"

import os
from django.utils.text import slugify
from django.core.files.storage import default_storage
from cryptography.fernet import Fernet
import re
import hashlib


def encrypt_string(plain_text):
    key = load_key()  # Ensure the key is generated and saved beforehand
    fernet = Fernet(key)
    encrypted = fernet.encrypt(plain_text.encode())
    return encrypted.decode()

def load_key():
    with open("secret.key", "rb") as key_file:
        key = key_file.read()
    return key

def hash_string(input_string):
    return hashlib.sha256(input_string.encode()).hexdigest()

# Custom upload function
def custom_upload_to(instance, filename):
    # Define the directory where the files will be stored
    uid=instance.cid.cid
    uid=str(uid)
    if (uid):
        print("uid iruku")
    else:
        print("uid illa")
        uid='-0'
    encrypted_uid=encrypt_string(uid)
    hashed_uid = hash_string(encrypted_uid)
    print(encrypted_uid)
    upload_dir = f'uploads/{hashed_uid}/convo/'

    # Get the file extension
    file_extension = filename.split('.')[-1]
    base_filename = filename.rsplit('.', 1)[0]  # Remove the extension to get the base name
    
    # Slugify the base filename to avoid special characters
    base_filename = slugify(base_filename)

    # Check if the file already exists in the directory, and if so, increment the number
    counter = 1
    new_filename = f"{base_filename}.{file_extension}"

    while default_storage.exists(os.path.join(upload_dir, new_filename)):
        # If file exists, increment the counter and check again
        new_filename = f"{base_filename}_{counter}.{file_extension}"
        counter += 1
    return os.path.join(upload_dir, new_filename)


    # Return the path where the file will be stored
    

class Chat(models.Model):
    cid = models.ForeignKey(Conversation, on_delete=models.CASCADE, to_field='cid')
    input_string = models.TextField()
    input_file = models.FileField(upload_to=custom_upload_to, blank=True, null=True)  # Use custom_upload_to
    output_string = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat in Conversation {self.cid}"

    def get_input_file_url(self):
        """
        Retrieves the URL of the uploaded input file.
        Uses Django's storage system to get the file URL.
        """
        return self.input_file.url if self.input_file else None