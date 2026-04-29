# adzuna_diagnostic.py - Diagnose and fix Adzuna search issues

import asyncio
import sys
import os
from dotenv import load_dotenv

# Add src to path for imports
sys.path.append('src')

load_dotenv()

async def diagnose_adzuna_api():
    """Comprehensive Adzuna API diagnosis"""
    
    print("🔬 ADZUNA API COMPREHENSIVE DIAGNOSIS")
    print("=" * 60)
    
    # Check credentials
    api_key = os.getenv("ADZUNA_API_KEY")
    app_id = os.getenv("ADZUNA_APP_ID")
    
    if not api_key or not app_id:
        print("❌ Missing API credentials")
        return
    
    print(f"✅ API Key: {api_key[:10]}...{api_key[-4:]}")
    print(f"✅ App ID: {app_id}")
    
    try:
        # Test 1: Basic API connectivity
        print(f"\n🔍 TEST 1: Basic API connectivity")
        await test_basic_connectivity(api_key, app_id)
        
        # Test 2: No location filter (broad search)
        print(f"\n🔍 TEST 2: Broad search (no location)")
        await test_broad_search(api_key, app_id)
        
        # Test 3: Different countries
        print(f"\n🔍 TEST 3: Different countries")
        await test_different_countries(api_key, app_id)
        
        # Test 4: Simple keywords
        print(f"\n🔍 TEST 4: Simple keywords")
        await test_simple_keywords(api_key, app_id)
        
        # Test 5: Raw API response
        print(f"\n🔍 TEST 5: Raw API response analysis")
        await test_raw_api_response(api_key, app_id)
        
    except Exception as e:
        print(f"❌ Diagnosis failed: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_basic_connectivity(api_key, app_id):
    """Test basic API connectivity"""
    
    import httpx
    
    try:
        url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
        params = {
            "app_id": app_id,
            "app_key": api_key,
            "what": "software",
            "results_per_page": 5
        }
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, params=params)
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                total_results = data.get("count", 0)
                results = data.get("results", [])
                
                print(f"   ✅ API Working! Total jobs available: {total_results}")
                print(f"   ✅ Retrieved: {len(results)} job samples")
                
                if results:
                    sample_job = results[0]
                    print(f"   Sample job: {sample_job.get('title', 'N/A')}")
                    print(f"   Company: {sample_job.get('company', {}).get('display_name', 'N/A')}")
                    print(f"   Location: {sample_job.get('location', {}).get('display_name', 'N/A')}")
                
                return True
            else:
                print(f"   ❌ API Error: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
                
    except Exception as e:
        print(f"   ❌ Connection failed: {str(e)}")
        return False

async def test_broad_search(api_key, app_id):
    """Test broad search without location filter"""
    
    import httpx
    
    keywords_to_test = ["software", "python", "data", "engineer", "developer"]
    
    for keyword in keywords_to_test:
        try:
            url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
            params = {
                "app_id": app_id,
                "app_key": api_key,
                "what": keyword,
                "results_per_page": 10
            }
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    total_results = data.get("count", 0)
                    results = data.get("results", [])
                    
                    print(f"   '{keyword}': {total_results} total jobs, {len(results)} returned")
                    
                    # Show locations found
                    if results:
                        locations = set()
                        for job in results[:5]:
                            loc = job.get('location', {}).get('display_name', 'Unknown')
                            locations.add(loc)
                        print(f"      Sample locations: {', '.join(list(locations)[:3])}")
                else:
                    print(f"   '{keyword}': API error {response.status_code}")
                    
        except Exception as e:
            print(f"   '{keyword}': Failed - {str(e)}")

async def test_different_countries(api_key, app_id):
    """Test different country codes"""
    
    import httpx
    
    countries = ["in", "us", "gb", "au", "ca"]
    
    for country in countries:
        try:
            url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
            params = {
                "app_id": app_id,
                "app_key": api_key,
                "what": "software",
                "results_per_page": 5
            }
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    total_results = data.get("count", 0)
                    print(f"   {country.upper()}: {total_results} jobs available")
                else:
                    print(f"   {country.upper()}: API error {response.status_code}")
                    
        except Exception as e:
            print(f"   {country.upper()}: Failed - {str(e)}")

async def test_simple_keywords(api_key, app_id):
    """Test very simple keywords"""
    
    import httpx
    
    simple_keywords = ["python", "java", "manager", "analyst", "engineer"]
    
    for keyword in simple_keywords:
        try:
            url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
            params = {
                "app_id": app_id,
                "app_key": api_key,
                "what": keyword,
                "results_per_page": 5
            }
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    total_results = data.get("count", 0)
                    
                    print(f"   '{keyword}': {len(results)} jobs returned (of {total_results} total)")
                    
                    # Check if any are in Bangalore
                    bangalore_jobs = 0
                    for job in results:
                        location = job.get('location', {}).get('display_name', '').lower()
                        if 'bangalore' in location or 'bengaluru' in location:
                            bangalore_jobs += 1
                    
                    if bangalore_jobs > 0:
                        print(f"      🎯 {bangalore_jobs} jobs found in Bangalore area!")
                
        except Exception as e:
            print(f"   '{keyword}': Failed - {str(e)}")

async def test_raw_api_response(api_key, app_id):
    """Analyze raw API response structure"""
    
    import httpx
    import json
    
    try:
        url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
        params = {
            "app_id": app_id,
            "app_key": api_key,
            "what": "python",
            "results_per_page": 3
        }
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"   ✅ Raw API Response Analysis:")
                print(f"   Response keys: {list(data.keys())}")
                print(f"   Total count: {data.get('count', 0)}")
                print(f"   Results returned: {len(data.get('results', []))}")
                
                results = data.get("results", [])
                if results:
                    sample_job = results[0]
                    print(f"\n   📋 Sample Job Structure:")
                    print(f"   Job keys: {list(sample_job.keys())}")
                    
                    # Show location structure
                    location = sample_job.get('location', {})
                    print(f"   Location keys: {list(location.keys()) if location else 'None'}")
                    
                    # Show company structure  
                    company = sample_job.get('company', {})
                    print(f"   Company keys: {list(company.keys()) if company else 'None'}")
                    
                    print(f"\n   📄 Sample Job Data:")
                    print(f"   Title: {sample_job.get('title', 'N/A')}")
                    print(f"   Company: {company.get('display_name', 'N/A') if company else 'N/A'}")
                    print(f"   Location: {location.get('display_name', 'N/A') if location else 'N/A'}")
                    print(f"   URL: {sample_job.get('redirect_url', 'N/A')}")
                    print(f"   Description length: {len(sample_job.get('description', ''))}")
                
                # Save full response for analysis
                with open('adzuna_sample_response.json', 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"\n   💾 Full response saved to 'adzuna_sample_response.json'")
                
            else:
                print(f"   ❌ API Error: {response.status_code}")
                print(f"   Error response: {response.text}")
                
    except Exception as e:
        print(f"   ❌ Analysis failed: {str(e)}")

async def test_location_search_fix(api_key, app_id):
    """Test potential fixes for location search"""
    
    import httpx
    
    print(f"\n🔧 TESTING LOCATION SEARCH FIXES")
    print("=" * 50)
    
    # Strategy 1: Search without location, then filter results
    print(f"Strategy 1: Broad search + post-filter")
    
    try:
        url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
        params = {
            "app_id": app_id,
            "app_key": api_key,
            "what": "python developer",
            "results_per_page": 50  # Get more results to filter
        }
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                # Filter for Bangalore jobs
                bangalore_jobs = []
                for job in results:
                    location = job.get('location', {}).get('display_name', '').lower()
                    if any(city in location for city in ['bangalore', 'bengaluru', 'karnataka']):
                        bangalore_jobs.append(job)
                
                print(f"   ✅ Found {len(bangalore_jobs)} Bangalore jobs out of {len(results)} total")
                
                if bangalore_jobs:
                    print(f"   🎯 Bangalore jobs found:")
                    for i, job in enumerate(bangalore_jobs[:3], 1):
                        title = job.get('title', 'N/A')
                        company = job.get('company', {}).get('display_name', 'N/A')
                        location = job.get('location', {}).get('display_name', 'N/A')
                        print(f"      {i}. {title} at {company} ({location})")
                
                return bangalore_jobs
            
    except Exception as e:
        print(f"   ❌ Strategy 1 failed: {str(e)}")
    
    return []

async def main():
    """Main diagnostic function"""
    
    await diagnose_adzuna_api()
    
    # Test potential fix
    api_key = os.getenv("ADZUNA_API_KEY")
    app_id = os.getenv("ADZUNA_APP_ID")
    
    bangalore_jobs = await test_location_search_fix(api_key, app_id)
    
    if bangalore_jobs:
        print(f"\n🎉 SOLUTION FOUND!")
        print("=" * 30)
        print("✅ Use broad search + post-filtering for Bangalore jobs")
        print(f"✅ Found {len(bangalore_jobs)} real Bangalore opportunities")
    else:
        print(f"\n🤔 INVESTIGATION NEEDED")
        print("=" * 30)
        print("• Check adzuna_sample_response.json for API structure")
        print("• Verify Adzuna India job coverage")
        print("• Consider alternative APIs")

if __name__ == "__main__":
    asyncio.run(main())
