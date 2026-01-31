import requests
import hashlib
import urllib3
urllib3.disable_warnings()

email = "hamitdurmus@gmail.com"
password = "6404969.Ham"
password_hash = hashlib.md5(password.encode()).hexdigest()

# Proxyman loglarınızdan bilinen phone_id
known_phone_id = "32A8C6BB-F20D-4658-8595-8144098A922C"

url = "https://cloud.multitek.com.tr:8096/multitek_service/root/getAccount"

headers = {
    "Content-Type": "application/json",
    "Authorization": "Basic bXVsdGl0ZWs6TWx0LjM4Mzgh",
    "Accept": "*/*",
}

print("Testing with known phone_id from Proxyman logs...")
print(f"Email: {email}")
print(f"Phone ID: {known_phone_id}")
print()

payload = {
    "email": email,
    "phone_id": known_phone_id,
    "language": "tr-TR"
}

response = requests.post(url, json=payload, headers=headers, verify=False)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:1000]}")

if response.text and len(response.text) > 10:
    try:
        import json
        data = response.json()
        print("\n✅ SUCCESS with known phone_id!")
        print(f"User: {data.get('user_name')} {data.get('user_surname')}")
        print(f"SIP: {data.get('sip')}")
        
        # Check if there are multiple phone_ids registered
        phone_list = data.get('phone_list', [])
        print(f"\nRegistered phones: {len(phone_list)}")
        for phone in phone_list:
            print(f"  - {phone.get('phone_id')} ({phone.get('info')})")
    except Exception as e:
        print(f"\n❌ Error: {e}")
else:
    print("\n❌ Empty response even with known phone_id!")
