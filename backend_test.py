import requests
import sys
import json
from datetime import datetime

class INWOGameAPITester:
    def __init__(self, base_url="https://game-cards-whatsapp.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.participant_id = None
        self.session_id = None
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root API", "GET", "", 200)

    def test_get_cards(self):
        """Test getting all INWO cards"""
        success, response = self.run_test("Get All Cards", "GET", "cards", 200)
        if success and 'cards' in response:
            cards = response['cards']
            print(f"   Found {len(cards)} cards")
            if len(cards) > 0:
                print(f"   Sample card: {cards[0]['name']}")
        return success

    def test_get_prizes(self):
        """Test getting all prizes"""
        success, response = self.run_test("Get All Prizes", "GET", "prizes", 200)
        if success and 'prizes' in response:
            prizes = response['prizes']
            print(f"   Found {len(prizes)} prizes")
            if len(prizes) > 0:
                print(f"   Sample prize: {prizes[0]['name']}")
        return success

    def test_register_participant(self):
        """Test participant registration"""
        timestamp = datetime.now().strftime('%H%M%S')
        participant_data = {
            "name": f"Test User {timestamp}",
            "email": f"test{timestamp}@example.com",
            "whatsapp": f"11999{timestamp}"
        }
        
        success, response = self.run_test(
            "Register Participant", 
            "POST", 
            "participants", 
            200, 
            data=participant_data
        )
        
        if success and 'participant' in response:
            self.participant_id = response['participant']['id']
            print(f"   Participant ID: {self.participant_id}")
            print(f"   Is new: {response.get('is_new', False)}")
        
        return success

    def test_get_participant(self):
        """Test getting participant by ID"""
        if not self.participant_id:
            print("❌ No participant ID available")
            return False
            
        return self.run_test(
            "Get Participant", 
            "GET", 
            f"participants/{self.participant_id}", 
            200
        )[0]

    def test_start_game(self):
        """Test starting a game session"""
        if not self.participant_id:
            print("❌ No participant ID available")
            return False
            
        success, response = self.run_test(
            "Start Game", 
            "POST", 
            "game/start", 
            200,
            params={"participant_id": self.participant_id}
        )
        
        if success:
            self.session_id = response.get('session_id')
            print(f"   Session ID: {self.session_id}")
            print(f"   Total questions: {response.get('total_questions')}")
            print(f"   First question: {response.get('question', {}).get('question', 'N/A')[:50]}...")
        
        return success

    def test_submit_answer(self):
        """Test submitting an answer"""
        if not self.session_id:
            print("❌ No session ID available")
            return False
            
        # Get the current session to find the first question
        session_success, session_data = self.run_test(
            "Get Session", 
            "GET", 
            f"game/session/{self.session_id}", 
            200
        )
        
        if not session_success or not session_data.get('questions'):
            print("❌ Could not get session data")
            return False
            
        first_question = session_data['questions'][0]
        question_id = first_question['id']
        correct_answer = first_question['correct']
        
        success, response = self.run_test(
            "Submit Answer", 
            "POST", 
            "game/answer", 
            200,
            params={
                "session_id": self.session_id,
                "question_id": question_id,
                "answer": correct_answer
            }
        )
        
        if success:
            print(f"   Is correct: {response.get('is_correct')}")
            print(f"   Points earned: {response.get('points_earned')}")
            print(f"   Total score: {response.get('total_score')}")
        
        return success

    def test_get_leaderboard(self):
        """Test getting leaderboard"""
        return self.run_test("Get Leaderboard", "GET", "leaderboard", 200, params={"limit": 5})[0]

    def test_get_stats(self):
        """Test getting game statistics"""
        success, response = self.run_test("Get Stats", "GET", "stats", 200)
        if success:
            print(f"   Total participants: {response.get('total_participants')}")
            print(f"   Total games: {response.get('total_games')}")
            print(f"   Completed games: {response.get('completed_games')}")
        return success

    def test_duplicate_registration(self):
        """Test registering with same email/whatsapp"""
        if not self.participant_id:
            print("❌ No participant ID available")
            return False
            
        # Try to register with same email
        participant_data = {
            "name": "Duplicate Test User",
            "email": f"test{datetime.now().strftime('%H%M%S')}@example.com",  # Use same email pattern
            "whatsapp": f"11999{datetime.now().strftime('%H%M%S')}"  # Use same whatsapp pattern
        }
        
        # First, get the original participant data
        success, orig_response = self.run_test(
            "Get Original Participant", 
            "GET", 
            f"participants/{self.participant_id}", 
            200
        )
        
        if not success:
            return False
            
        # Now try to register with the same email
        participant_data['email'] = orig_response['email']
        
        success, response = self.run_test(
            "Duplicate Registration", 
            "POST", 
            "participants", 
            200, 
            data=participant_data
        )
        
        if success:
            print(f"   Is new: {response.get('is_new')} (should be False)")
            return response.get('is_new') == False
        
        return success

def main():
    print("🎮 INWO Game API Testing Suite")
    print("=" * 50)
    
    tester = INWOGameAPITester()
    
    # Test sequence
    tests = [
        ("Root API", tester.test_root_endpoint),
        ("Get Cards", tester.test_get_cards),
        ("Get Prizes", tester.test_get_prizes),
        ("Register Participant", tester.test_register_participant),
        ("Get Participant", tester.test_get_participant),
        ("Start Game", tester.test_start_game),
        ("Submit Answer", tester.test_submit_answer),
        ("Get Leaderboard", tester.test_get_leaderboard),
        ("Get Stats", tester.test_get_stats),
        ("Duplicate Registration", tester.test_duplicate_registration),
    ]
    
    print(f"\n🚀 Running {len(tests)} test categories...")
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            test_func()
        except Exception as e:
            print(f"❌ Test {test_name} failed with exception: {str(e)}")
    
    # Print final results
    print(f"\n{'='*50}")
    print(f"📊 Final Results:")
    print(f"   Tests run: {tester.tests_run}")
    print(f"   Tests passed: {tester.tests_passed}")
    print(f"   Success rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())