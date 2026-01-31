import requests
import hashlib
import uuid
import urllib3
urllib3.disable_warnings()

email = "hamitdurmus@gmail.com"
password = "6404969.Ham"
password_hash = hashlib.md5(password.encode()).hexdigest()
phone_id = str(uuid.uuid4()).upper()

url = "https://cloud.multitek.com.tr:8096/multitek_service/root/getAccount"

headers = {
    "Content-Type": "application/json",
    "Authorization": "Basic bXVsdGl0ZWs6TWx0LjM4Mzgh",
    "Accept": "*/*",
}

print(f"Testing getAccount with NEW UUID and PASSWORD...")
print(f"Email: {email}")
print(f"Phone ID: {phone_id}")
print(f"Password hash: {password_hash}")
print()

# Test WITH password
payload = {
    "email": email,
    "password": password_hash,
    "phone_id": phone_id,
    "language": "tr-TR"
}

response = requests.post(url, json=payload, headers=headers, verify=False)
print(f"Status: {response.status_code}")
print(f"Response length: {len(response.text)}")
print(f"Response: {response.text[:500]}")

if response.text and len(response.text) > 10:
    try:
        import json
        data = response.json()
        if "email" in data:
            print("\n✅ SUCCESS! Email found in response")
            print(f"User: {data.get('user_name')} {data.get('user_surname')}")
            print(f"SIP: {data.get('sip')}")
        else:
            print("\n❌ Email NOT in response")
    except:
        print("\n❌ Not valid JSON")
else:
    print("\n❌ Empty or very short response")
