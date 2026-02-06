import requests
from hashlib import blake2b

# Fetch the data from the API
response = requests.get("https://api.close.com/buildwithus/")
data = response.json()

traits = data["traits"]
key = data["key"]

# Compute BLAKE2b hash for each trait
hashes = []
for trait in traits:
    key_bytes = key.encode('utf-8')
    trait_bytes = trait.encode('utf-8')
    hash_digest = blake2b(trait_bytes, key=key_bytes).hexdigest().lower()
    hashes.append(hash_digest)

# Post the array back to the API
post_response = requests.post("https://api.close.com/buildwithus/", json=hashes)

# Extract and print the Verification ID
verification_id = post_response.text.strip().split(":")[-1].strip()
print("Verification ID:", verification_id)