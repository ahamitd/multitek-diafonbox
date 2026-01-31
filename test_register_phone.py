import requests
import hashlib
import uuid
import urllib3
urllib3.disable_warnings()

email = "hamitdurmus@gmail.com"
password = "6404969.Ham"
password_hash = hashlib.md5(password.encode()).hexdigest()
phone_id = str(uuid.uuid4()).upper()

headers = {
    "Content-Type": "application/json",
    "Authorization": "Basic bXVsdGl0ZWs6TWx0LjM4Mzgh",
    "Accept": "*/*",
}

print("Step 1: Register phone_id via userAccountControl")
print(f"Email: {email}")
print(f"Phone ID: {phone_id}")
print()

# Step 1: Register via userAccountControl (even if it returns "0")
url1 = "https://cloud.multitek.com.tr:8096/multitek_service/root/userAccountControl"
payload1 = {
    "email": email,
    "password": password_hash,
    "phone_id": phone_id,
    "phone_info": "Home Assistant",
    "pushy_token": "",
    "push_kit_token": "",
    "language": "tr-TR"
}

response1 = requests.post(url1, json=payload1, headers=headers, verify=False)
print(f"userAccountControl Status: {response1.status_code}")
print(f"userAccountControl Response: '{response1.text}'")
print()

# Step 2: Now try getAccount with the SAME phone_id
print("Step 2: Try getAccount with registered phone_id")
url2 = "https://cloud.multitek.com.tr:8096/multitek_service/root/getAccount"
payload2 = {
    "email": email,
    "phone_id": phone_id,
    "language": "tr-TR"
}

response2 = requests.post(url2, json=payload2, headers=headers, verify=False)
print(f"getAccount Status: {response2.status_code}")
print(f"getAccount Response length: {len(response2.text)}")
print(f"getAccount Response: {response2.text[:500]}")

if response2.text and len(response2.text) > 10:
    try:
        import json
        data = response2.json()
        if "email" in data:
            print("\n✅ SUCCESS! Phone ID registered and working!")
        else:
            print("\n❌ Still not working")
    except:
        print("\n❌ Not JSON")
else:
    print("\n❌ Empty response")
