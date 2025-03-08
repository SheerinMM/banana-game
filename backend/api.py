import requests

def fetch_question():
    url = "http://marcconrad.com/uob/banana/api.php"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Failed to fetch question"}
    except Exception as e:
        return {"error": str(e)}
