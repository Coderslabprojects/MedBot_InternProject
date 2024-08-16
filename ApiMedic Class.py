import requests
import hmac
import base64
import json

class DiagnosisClient:
    
    def __init__(self, username, password, auth_service_url, language, health_service_url):
        self._language = language
        self._health_service_url = health_service_url
        self._token = self._load_token(username, password, auth_service_url)

    def _load_token(self, username, password, url):
        # Generate HMAC hash using password and URL
        raw_hash = hmac.new(password.encode('utf-8'), url.encode('utf-8')).digest()
        computed_hash = base64.b64encode(raw_hash).decode()
        bearer_credentials = f'{username}:{computed_hash}'
        headers = {'Authorization': f'Bearer {bearer_credentials}'}

        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error loading token: {e}")
            return None

    def _load_from_web_service(self, action):
        if not self._token:
            print("Error: No token available.")
            return None

        extra_args = f"token={self._token['Token']}&format=json&language={self._language}"
        action = f"{action}?{extra_args}" if "?" not in action else f"{action}&{extra_args}"
        url = f"{self._health_service_url}/{action}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error loading from web service: {e}")
            return None       

    def load_issues(self):
        return self._load_from_web_service("issues")

    def load_issue_info(self, issue_id):
        action = f"issues/{issue_id}/info"
        return self._load_from_web_service(action)

    def load_symptoms(self):
        return self._load_from_web_service("symptoms")

    def load_diagnosis(self, selected_symptoms, gender, year_of_birth):
        serialized_symptoms = json.dumps(selected_symptoms)
        action = f"diagnosis?symptoms={serialized_symptoms}&gender={gender}&year_of_birth={year_of_birth}"
        return self._load_from_web_service(action)
