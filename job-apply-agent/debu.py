# debug_state_flow.py - Quick test to see what's happening
import asyncio
import sys
import os
from dotenv import load_dotenv

# Add src to path
sys.path.append('src')

from services.job_search_service import JobSearchService
from nodes.ingest_node import ingest_jobs_node
from nodes.parse_node import parse_requirements_node
from nodes.scoring_node import compute_fit_score_node

load_dotenv()

async def debug_individual_nodes():
    """Test each node individually to see where the problem is"""
    print("🔍 DEBUGGING INDIVIDUAL NODES")
    print("=" * 50)
    
    # Test input state
    initial_state = {
        "search_filters": {
            "keywords": ["python", "developer"],
            "locations": ["bangalore"],
            "experience_level": "mid"
        },
        "profile": {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1-555-0123",
            "location": "Bangalore, India",
            "skills": ["Python", "Django", "FastAPI", "PostgreSQL"],
            "years_experience": 5,
            "current_title": "Senior Software Engineer",
            "work_authorization": "Indian Citizen"
        }
    }
    
    print("📝 Initial State Keys:", list(initial_state.keys()))
    print("📝 Profile Skills:", initial_state['profile']['skills'])
    
    # Test Node 1: Ingest
    print("\n🔧 Testing Ingest Node...")
    try:
        ingest_result = await ingest_jobs_node(initial_state)
        print("✅ Ingest Result Keys:", list(ingest_result.keys()))
        
        if 'job' in ingest_result:
            job_data = ingest_result['job']
            print("📋 Job Data:")
            print(f"   Title: {job_data.get('title')}")
            print(f"   Company: {job_data.get('company')}")
            print(f"   Description Length: {len(job_data.get('description', ''))}")
        
        # Merge state for next node
        state_after_ingest = {**initial_state, **ingest_result}
        
    except Exception as e:
        print(f"❌ Ingest failed: {str(e)}")
        return
    
    # Test Node 2: Parse
    print("\n🔧 Testing Parse Node...")
    try:
        parse_result = await parse_requirements_node(state_after_ingest)
        print("✅ Parse Result Keys:", list(parse_result.keys()))
        
        if 'job' in parse_result:
            job_data = parse_result['job']
            parsed_req = job_data.get('parsed_requirements', {})
            print("📋 Parsed Requirements:")
            print(f"   Required Skills: {parsed_req.get('required_skills', [])}")
            print(f"   Years Experience: {parsed_req.get('years_experience')}")
        
        # Merge state for next node
        state_after_parse = {**state_after_ingest, **parse_result}
        
    except Exception as e:
        print(f"❌ Parse failed: {str(e)}")
        return
    
    # Test Node 3: Score
    print("\n🔧 Testing Scoring Node...")
    try:
        score_result = await compute_fit_score_node(state_after_parse)
        print("✅ Score Result Keys:", list(score_result.keys()))
        
        if 'score' in score_result:
            score_data = score_result['score']
            print("📊 Score Data:")
            print(f"   Overall Score: {score_data.get('overall_score')}")
            print(f"   Recommendation: {score_data.get('recommendation')}")
            print(f"   Components: {score_data.get('components', {})}")
        
    except Exception as e:
        print(f"❌ Scoring failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n✅ All individual nodes working!")

async def debug_job_search_service():
    """Test the job search service directly"""
    print("\n🔍 DEBUGGING JOB SEARCH SERVICE")
    print("=" * 50)
    
    search_service = JobSearchService()
    
    try:
        jobs = await search_service.search_jobs(
            keywords="python developer",
            location="bangalore",
            platform="naukri",
            limit=1
        )
        
        print(f"✅ Found {len(jobs)} jobs")
        
        if jobs:
            job = jobs[0]
            print("📋 Sample Job:")
            for key, value in job.items():
                if isinstance(value, str) and len(value) > 100:
                    print(f"   {key}: {value[:100]}...")
                else:
                    print(f"   {key}: {value}")
        
        return jobs
        
    except Exception as e:
        print(f"❌ Job search failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

async def test_llm_connection():
    """Test if LLM (Groq) is working"""
    print("\n🔍 DEBUGGING LLM CONNECTION")
    print("=" * 50)
    
    try:
        from groq import Groq
        
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # Simple test
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": "Return a JSON object with a single field 'status': 'working'"}
            ],
            temperature=0.1,
            max_tokens=100
        )
        
        print("✅ LLM Response:", response.choices[0].message.content)
        return True
        
    except Exception as e:
        print(f"❌ LLM test failed: {str(e)}")
        return False

async def main():
    """Run all debug tests"""
    print("🐛 JOB AGENT DEBUG SUITE")
    print("=" * 60)
    
    # Check environment
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        print(f"✅ GROQ_API_KEY found: {groq_key[:20]}...")
    else:
        print("❌ GROQ_API_KEY not found")
        return
    
    # Test 1: LLM Connection
    llm_working = await test_llm_connection()
    
    if not llm_working:
        print("❌ LLM not working - stopping debug")
        return
    
    # Test 2: Job Search Service
    jobs = await debug_job_search_service()
    
    # Test 3: Individual Nodes
    await debug_individual_nodes()
    
    print("\n" + "=" * 60)
    print("🎯 DEBUG SUMMARY")
    print("=" * 60)
    print(f"✅ LLM Connection: {'Working' if llm_working else 'Failed'}")
    print(f"✅ Job Search: {'Working' if jobs else 'Failed'}")
    print("✅ Individual Nodes: Check output above")

if __name__ == "__main__":
    asyncio.run(main())
