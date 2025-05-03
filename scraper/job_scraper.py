import requests

def scrape_jsearch(role, location="Remote", limit=5):
    url = "https://jsearch.p.rapidapi.com/search"

    query = f"{role} in {location}"
    print(f"🔍 Query: {query}")

    querystring = {
        "query": query,
        "page": "1",
        "num_pages": "1"
    }

    headers = {
        "X-RapidAPI-Key": "62a17b7d81mshb98bd0f2fc56ecbp105f44jsn28b3f6d4f54e",
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        print("🔗 JSearch Status Code:", response.status_code)

        if response.status_code != 200:
            print("❌ API Error:", response.text)
            return []

        data = response.json()
        print(f"📄 Raw job count in API response: {len(data.get('data', []))}")

    except Exception as e:
        print("❌ Error fetching from JSearch:", e)
        return []

    jobs = []
    for item in data.get("data", [])[:limit]:
        print(f"✅ Found job: {item.get('job_title')} at {item.get('employer_name')}")
        jobs.append({
            "title": item.get("job_title"),
            "company": item.get("employer_name"),
            "link": item.get("job_apply_link")
        })

    return jobs
