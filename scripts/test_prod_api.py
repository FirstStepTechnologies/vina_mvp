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
        "experience": "Beginner", 
        "experience_level": "Beginner", # Covering both bases
        "bio": "Test User Bio"
    }
    print(f"👤 Updating Profile to matches 'HR Manager'...")
    prof_resp = requests.patch(profile_url, headers=headers, json=profile_data)
    if prof_resp.status_code != 200:
        print(f"⚠️ Profile Update Failed: {prof_resp.status_code} - {prof_resp.text}")
        print("Continuing anyway, but cache lookup may fail...")
    else:
        print("✅ Profile Updated")

    # Verify Profile State
    get_prof_resp = requests.get(profile_url, headers=headers)
    if get_prof_resp.status_code == 200:
        p_data = get_prof_resp.json().get("profile", {})
        print(f"🧐 Current Profile on Server:")
        print(f"   Profession: {p_data.get('profession')}")
        print(f"   Industry: {p_data.get('industry')}")
        print(f"   Level: {p_data.get('experienceLevel')}")
        print(f"   Daily Goal: {p_data.get('dailyGoalMinutes')}")
    else:
        print(f"⚠️ Could not verify profile: {get_prof_resp.status_code}")

    # 3. Test Adaptation Variations
    lesson_id = "c_llm_foundations:l01_what_llms_are"
    for adapt_type in ["examples", "more_examples"]:
        print(f"\n🚀 Testing Adaptation: '{adapt_type}'")
        params = {
            "difficulty": 3,
            "adaptation": adapt_type 
        }
        
        url = f"{base_url}/api/v1/lessons/{lesson_id}"
        resp = requests.get(url, headers=headers, params=params)
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"📊 Response for {adapt_type}:")
            v_url = data.get('videoUrl')
            print(f"   Video URL: {v_url}")
            print(f"   Cached: {data.get('cached')}")
            
            if v_url and "cloudinary" in v_url:
                print(f"   ✅ SUCCESS for {adapt_type}")
            else:
                print(f"   ❌ FAILURE for {adapt_type} (Got default/null)")
        else:
            print(f"❌ Request Failed: {resp.status_code}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_prod_api.py <backend_url> [email] [password]")
        print("Example: python scripts/test_prod_api.py https://my-app.onrender.com")
        sys.exit(1)
        
    url = sys.argv[1]
    email = sys.argv[2] if len(sys.argv) > 2 else "demo@vina.ai"
    pwd = sys.argv[3] if len(sys.argv) > 3 else "password123"
    
    test_adaptation(url, email, pwd)
