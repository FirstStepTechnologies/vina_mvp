import requests
import sys

# Replace with your actual production URL
BASE_URL = "https://vina-backend.onrender.com"  
# Or whatever the user provides if known, defaulting to probable Render URL structure
# Since user hasn't provided IT yet, I'll make it an argument

def test_adaptation(base_url, email="demo@vina.ai", password="password123"):
    print(f"🔍 Testing Production API: {base_url}")
    
    # 1. Login to get token
    login_url = f"{base_url}/api/v1/auth/login"
    register_url = f"{base_url}/api/v1/auth/register"
    
    token = None
    
    # Try Login
    try:
        resp = requests.post(login_url, json={"email": email, "password": password})
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return
    
    if resp.status_code == 200:
        token = resp.json()["access_token"]
        print("✅ Login Successful")
    elif resp.status_code == 400 and "Incorrect email" in resp.text:
        print("⚠️ User not found. Attempting registration...")
        # Try Register
        reg_data = {
            "email": email,
            "password": password,
            "fullName": "Test User"
        }
        reg_resp = requests.post(register_url, json=reg_data)
        if reg_resp.status_code == 201:
             print("✅ Registration Successful. Logging in...")
             # Login again
             resp = requests.post(login_url, json={"email": email, "password": password})
             if resp.status_code == 200:
                 token = resp.json()["access_token"]
             else:
                 print(f"❌ Login after registration failed: {resp.text}")
                 return
        else:
             print(f"❌ Registration Failed: {reg_resp.status_code} - {reg_resp.text}")
             return
    else:
        print(f"❌ Login Failed: {resp.status_code} - {resp.text}")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Set Profile (Crucial for Hash Match)
    profile_url = f"{base_url}/api/v1/user/profile"
    profile_data = {
        "profession": "HR Manager",
        "industry": "Tech Company",
        "experienceLevel": "Beginner",
        "bio": "Test User Bio"
    }
    print(f"👤 Updating Profile to matches 'HR Manager'...")
    prof_resp = requests.patch(profile_url, headers=headers, json=profile_data)
    if prof_resp.status_code != 200:
        print(f"⚠️ Profile Update Failed: {prof_resp.status_code} - {prof_resp.text}")
        print("Continuing anyway, but cache lookup may fail...")
    else:
        print("✅ Profile Updated")

    # 3. Request Lesson with Adaptation
    # Targeting Lesson 1, Examples
    lesson_id = "c_llm_foundations:l01_what_llms_are"
    params = {
        "difficulty": 3,
        "adaptation": "examples" 
    }
    
    print(f"🚀 Requesting Lesson: {lesson_id} with params={params}")
    
    url = f"{base_url}/api/v1/lessons/{lesson_id}"
    resp = requests.get(url, headers=headers, params=params)
    
    if resp.status_code == 200:
        data = resp.json()
        print("\n📊 Response:")
        print(f"Title: {data.get('title')}")
        print(f"Video URL: {data.get('videoUrl')}")
        print(f"Cached: {data.get('cached')}")
        
        if not data.get('videoUrl'):
            print("\n❌ ISSUE DETECTED: Video URL is missing/null.")
        elif "cloudinary" not in data.get('videoUrl', ''):
            print(f"\n⚠️ WARNING: Video URL does not look like Cloudinary: {data.get('videoUrl')}")
        else:
            print("\n✅ SUCCESS: Cloudinary URL returned.")
            
    else:
        print(f"❌ Request Failed: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_prod_api.py <backend_url> [email] [password]")
        print("Example: python scripts/test_prod_api.py https://my-app.onrender.com")
        sys.exit(1)
        
    url = sys.argv[1]
    email = sys.argv[2] if len(sys.argv) > 2 else "demo@vina.ai"
    pwd = sys.argv[3] if len(sys.argv) > 3 else "password123"
    
    test_adaptation(url, email, pwd)
