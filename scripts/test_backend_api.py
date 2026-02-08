import asyncio
import aiohttp
import json
import uuid
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
OUTPUT_FILE = "reports/api_test_results.txt"
TEST_EMAIL = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
TEST_PASSWORD = "secure_password_123"

class APITester:
    def __init__(self):
        self.session = None
        self.token = None
        self.results = []
        self.course_map = []

    async def init(self):
        self.session = aiohttp.ClientSession()

    async def close(self):
        if self.session:
            await self.session.close()

    def log(self, message):
        print(message)
        self.results.append(message)

    async def request(self, method, endpoint, data=None, auth=True, expected_status=200):
        url = f"{BASE_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        if auth and self.token:
            headers["Authorization"] = self.token # Start with just token, check if prefix needed
            # Common convention is "Bearer <token>"
            headers["Authorization"] = f"Bearer {self.token}"

        start_time = datetime.now()
        try:
            async with self.session.request(method, url, json=data, headers=headers) as response:
                elapsed = (datetime.now() - start_time).total_seconds()
                status = response.status
                
                try:
                    resp_data = await response.json()
                except:
                    resp_data = await response.text()

                result_str = f"[{method}] {endpoint} - Status: {status} (Expected: {expected_status}) - {elapsed:.3f}s"
                
                if status == expected_status:
                    self.log(f"✅ PASS: {result_str}")
                    return True, resp_data
                else:
                    self.log(f"❌ FAIL: {result_str}")
                    self.log(f"   Response: {resp_data}")
                    return False, resp_data

        except Exception as e:
            self.log(f"❌ ERROR: [{method}] {endpoint} - Exception: {str(e)}")
            return False, None

    async def run_all_tests(self):
        await self.init()
        self.log(f"Starting API Tests at {datetime.now()}")
        self.log(f"Target: {BASE_URL}")
        self.log("-" * 60)

        # 1. Register with HR Manager persona for realistic video validation
        success, data = await self.request("POST", "/auth/register", {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "fullName": "Test HR Manager"
        }, auth=False, expected_status=201)
        
        if success and "access_token" in data:
            self.token = data["access_token"]
            self.log("   Got Access Token.")
            
            # 1.5. Set Profile to HR Manager
            await self.request("PATCH", "/user/profile", {
                "profession": "HR Manager",
                "industry": "Tech Company"
            })
            self.log("   Updated profile to 'HR Manager'.")
        else:
            self.log("⚠️ CRITICAL: Registration failed. Aborting auth-dependent tests.")
            await self.close()
            return

        # 2. Login (Verify credentials work)
        success, data = await self.request("POST", "/auth/login", {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }, auth=False)

        # 3. Get Profile (Auto-created)
        success, profile = await self.request("GET", "/user/profile")
        if success:
            self.log(f"   User ID: {profile.get('user_id')}")
            self.log(f"   Profession: {profile.get('profile', {}).get('profession')}")

        # 4. Update Profile
        await self.request("PATCH", "/user/profile", {
            "dailyGoalMinutes": 45,
            "resolution": "API Testing Master"
        })

        # Verify Update
        success, profile = await self.request("GET", "/user/profile")
        if success:
             res = profile.get("profile", {}).get("resolution")
             if res == "API Testing Master":
                 self.log("   ✅ Update persisted correctly.")
             else:
                 self.log(f"   ❌ Update failed persistence. Got: {res}")

        # 5. Get Progress (Initial)
        await self.request("GET", "/user/progress")

        # 6. Sync Progress
        await self.request("POST", "/user/progress/sync", {
            "minutes_added": 15,
            "diamonds_earned": 10
        })

        # 7. Get Course Map
        success, map_data = await self.request("GET", "/course/map")
        if success and isinstance(map_data, list) and len(map_data) > 0:
            self.course_map = map_data
            self.log(f"   Retrieved {len(map_data)} lessons.")
            first_lesson = map_data[0]
            first_id = first_lesson.get("lessonId")
        
            # 8. Check Video URLs for lessons 1 to 3 (with different difficulty levels)
            self.log("   Checking video availability for Lessons 1-3 (Persona-specific)...")
            test_cases = [
                ("l01_what_llms_are", 1), # Lesson 1, Beginner (d1)
                ("l02_tokens_context", 3), # Lesson 2, Intermediate (d3)
                ("l03_prompting_basics", 5) # Lesson 3, Advanced (d5)
            ]
            
            videos_found = 0
            for lid, diff in test_cases:
                success, lesson_detail = await self.request("GET", f"/lessons/{lid}?difficulty={diff}")
                if success and lesson_detail.get("videoUrl"):
                    videos_found += 1
                    self.log(f"   ✅ Lesson {lid} (D{diff}): {lesson_detail.get('videoUrl')}")
                else:
                    self.log(f"   ❌ Lesson {lid} (D{diff}) - Video not found")
            
            self.log(f"   ✅ Found working videos for {videos_found}/{len(test_cases)} target lessons.")

            # 9. Complete First Lesson
            if first_id:
                await self.request("POST", f"/user/progress/lesson/{first_id}/complete")
        
        # 10. Pre-Assessment
        await self.request("GET", "/assessment/pre-quiz")

        # 11. Submit Assessment
        await self.request("POST", "/assessment/submit", {
            "answers": [
                {"questionId": "aq_001", "selected": "A"}, # Correct
                {"questionId": "aq_002", "selected": "C"}  # Correct
            ]
        })

        # 12. Reset Pathway
        await self.request("POST", "/user/profile/reset-pathway")

        self.log("-" * 60)
        self.log("Tests Completed.")
        await self.close()
        
        # Save to file
        with open(OUTPUT_FILE, "w") as f:
            f.write("\n".join(self.results))
        print(f"\nReport saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    tester = APITester()
    try:
        asyncio.run(tester.run_all_tests())
    except Exception as e:
        print(f"Fatal Error: {e}")
        print("Ensure the backend server is running on http://localhost:8000")
