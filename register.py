import os
import json
from cryptography.fernet import Fernet

# Create a Fernet key for encryption 
# fernet_key = Fernet.generate_key()
# print(fernet_key)
fernet_key = os.environ['FERNET_KEY'].encode()
# Store the Fernet key as a secret in your GitHub repository

# Define a function to store email addresses and course preferences
def store_preferences(email, course_preferences):
    # Load the Fernet key from the environment variable
    fernet_key = os.environ['FERNET_KEY'].encode()
    cipher_suite = Fernet(fernet_key)

    # Create a JSON payload with the email address and course preferences
    payload = {'email': email, 'course_preferences': course_preferences}

    # Encrypt the payload using Fernet
    encrypted_payload = cipher_suite.encrypt(json.dumps(payload).encode())

    # Store the encrypted payload in a JSON file
    with open('preferences.json', 'a') as f:
        f.write(encrypted_payload.decode() + '\n')

# Define a function to retrieve email addresses and course preferences
def retrieve_preferences():
    # Load the Fernet key from the environment variable
    fernet_key = os.environ['FERNET_KEY'].encode()
    cipher_suite = Fernet(fernet_key)

    # Load the encrypted payload from the JSON file
    with open('preferences.json', 'r') as f:
        encrypted_payloads = [line.strip() for line in f.readlines()]

    # Decrypt the payloads using Fernet
    preferences = []
    for encrypted_payload in encrypted_payloads:
        decrypted_payload = cipher_suite.decrypt(encrypted_payload.encode())
        preferences.append(json.loads(decrypted_payload.decode()))

    return preferences

if __name__ == '__main__':
    register_email = os.environ['REGISTER_EMAIL']
    course_name = os.environ['REGISTER_COURSE']
    course_list = [course.strip() for course in course_name.replace(' ', '').split(',')]
    store_preferences(register_email, course_list) # 存到 JSON 檔
