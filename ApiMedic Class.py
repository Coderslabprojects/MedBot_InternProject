import requests
import hmac
import base64
import json

class DiagnosisClient:
    
    # Constructor to initialize the DiagnosisClient object with necessary attributes
    def __init__(self, username, password, authServiceUrl, language, healthServiceUrl):
        self._language = language  # Language for communication with the service
        self._healthServiceUrl = healthServiceUrl  # Base URL of the health service API
        # Load the authentication token using the provided credentials
        self._token = self._loadToken(username, password, authServiceUrl)

    # Private method to generate and load the authentication token
    def _loadToken(self, username, password, url):
        # Generate HMAC hash using the password and service URL
        rawHashString = hmac.new(bytes(password, encoding='utf-8'), url.encode('utf-8')).digest()
        # Encode the hash to Base64 to create the computed hash string
        computedHashString = base64.b64encode(rawHashString).decode()
        # Combine the username and computed hash string to form the bearer credentials
        bearer_credentials = username + ':' + computedHashString
        # Create the headers for the POST request with the Authorization token
        postHeaders = {
            'Authorization': f'Bearer {bearer_credentials}'
        }
        # Send a POST request to the authentication service URL to obtain the token
        responsePost = requests.post(url, headers=postHeaders)
        # Parse the JSON response to extract the token data
        data = json.loads(responsePost.text)
        return data  # Return the token data

    # Private method to make requests to the health service API
    def _loadFromWebService(self, action):
        # Add the token, format, and language as query parameters
        extraArgs = "token=" + self._token["Token"] + "&format=json&language=" + self._language
        # Append the query parameters to the action URL
        if "?" not in action:
            action += "?" + extraArgs
        else:
            action += "&" + extraArgs
        # Combine the base health service URL with the action URL
        url = self._healthServiceUrl + "/" + action
        # Send a GET request to the constructed URL
        response = requests.get(url)
        # Parse the JSON response to extract the data
        data = json.loads(response.text)
        return data  # Return the data from the web service

    # Public method to load all available medical issues
    def loadIssues(self):
        return self._loadFromWebService("issues")

    # Public method to load detailed information about a specific issue
    def loadIssueInfo(self, issueId):
        issueId = str(issueId)  # Convert issue ID to a string
        action = f"issues/{issueId}/info"  # Construct the action URL
        return self._loadFromWebService(action)  # Request and return the issue info

    # Public method to load all available symptoms
    def loadSymptoms(self):
        return self._loadFromWebService("symptoms")

    # Public method to load a diagnosis based on selected symptoms, gender, and year of birth
    def loadDiagnosis(self, selectedSymptoms, gender, yearOfBirth):
        # Serialize the selected symptoms to a JSON-formatted string
        serializedSymptoms = json.dumps(selectedSymptoms)
        # Construct the action URL with the necessary query parameters
        action = f"diagnosis?symptoms={serializedSymptoms}&gender={gender}&year_of_birth={yearOfBirth}"
        return self._loadFromWebService(action)  # Request and return the diagnosis

