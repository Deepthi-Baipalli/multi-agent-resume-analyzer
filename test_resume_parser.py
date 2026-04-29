# test_specific_resume.py - Test with your specific resume

import asyncio
import sys
import os
from dotenv import load_dotenv

# Add src to path for imports
sys.path.append('src')

from services.resume_parser import LLMResumeParser

load_dotenv()

async def test_sreecharan_resume():
    """Test the LLM resume parser with Sreecharan's resume"""
    
    print("🧪 TESTING WITH SREECHARAN'S RESUME")
    print("=" * 60)
    
    # Your resume path
    resume_path = r"D:\Hare_Krishna_JobAgent\sreecharan_resume_2.0_with photo.pdf"
    
    # Check if file exists
    if not os.path.exists(resume_path):
        print(f"❌ Resume file not found: {resume_path}")
        print("Please check the file path and try again.")
        return
    
    print(f"✅ Found resume file: {os.path.basename(resume_path)}")
    
    # Check API key
    if not os.getenv("GROQ_API_KEY"):
        print("❌ GROQ_API_KEY not found in .env file")
        return
    
    print("✅ GROQ_API_KEY found")
    
    # Initialize parser
    parser = LLMResumeParser()
    print("✅ Parser initialized")
    
    try:
        # Step 1: Extract text from PDF
        print(f"\n📄 STEP 1: Extracting text from PDF...")
        resume_text = parser.extract_text_from_file(resume_path)
        
        print(f"✅ Text extracted successfully")
        print(f"   Text length: {len(resume_text)} characters")
        print(f"   First 200 chars: {resume_text[:200]}...")
        
        # Step 2: Parse with LLM
        print(f"\n🤖 STEP 2: Parsing with LLM...")
        profile = await parser.parse_resume(resume_path)
        
        # Step 3: Display results
        print(f"\n📊 STEP 3: EXTRACTED PROFILE")
        print("=" * 40)
        
        print(f"👤 Personal Information:")
        print(f"   Name: {profile.get('name')}")
        print(f"   Email: {profile.get('email')}")
        print(f"   Phone: {profile.get('phone')}")
        print(f"   Location: {profile.get('location')}")
        
        print(f"\n💼 Professional Information:")
        print(f"   Current Title: {profile.get('current_title')}")
        print(f"   Years Experience: {profile.get('years_experience')}")
        print(f"   Education: {profile.get('education')}")
        
        print(f"\n🛠️ Technical Skills:")
        skills = profile.get('skills', [])
        for i, skill in enumerate(skills, 1):
            print(f"   {i}. {skill}")
        
        print(f"\n🎯 Suggested Job Roles:")
        roles = profile.get('desired_roles', [])
        for i, role in enumerate(roles, 1):
            print(f"   {i}. {role}")
        
        # Step 4: Test workflow integration
        print(f"\n🔄 STEP 4: Testing Workflow Integration")
        print("=" * 40)
        
        # Simulate job search inputs
        job_type = "Software Engineer"
        location = "Bangalore, Remote"
        
        print(f"Job Type Input: {job_type}")
        print(f"Location Input: {location}")
        
        # Create search filters (simulate the processor logic)
        search_filters = {
            "keywords": job_type.split(","),
            "locations": location.split(","),
            "experience_level": determine_experience_level(profile.get('years_experience', 0))
        }
        
        print(f"\n✅ Generated Search Filters:")
        print(f"   Keywords: {search_filters['keywords']}")
        print(f"   Locations: {search_filters['locations']}")
        print(f"   Experience Level: {search_filters['experience_level']}")
        
        # Create complete workflow input
        workflow_input = {
            "profile": profile,
            "search_filters": search_filters
        }
        
        print(f"\n🎯 READY FOR YOUR LANGGRAPH WORKFLOW!")
        print("✅ Profile extracted successfully")
        print("✅ Search filters created")
        print("✅ Workflow input ready")
        
        # Optional: Test with your actual workflow
        print(f"\n🚀 STEP 5: Testing with Your LangGraph (Optional)")
        print("=" * 40)
        
        try:
            from graph.complete_job_agent_graph import create_complete_job_agent_graph
            
            print("📝 Found your LangGraph workflow")
            print("🔄 Running complete job application workflow...")
            
            # Create and run your workflow
            job_agent = create_complete_job_agent_graph()
            result = await job_agent.ainvoke(workflow_input)
            
            print("✅ WORKFLOW COMPLETED!")
            print(f"   Job Found: {result.get('job', {}).get('title', 'Unknown')}")
            print(f"   Company: {result.get('job', {}).get('company', 'Unknown')}")
            print(f"   Fit Score: {result.get('score', {}).get('overall_score', 0):.1f}%")
            print(f"   Recommendation: {result.get('score', {}).get('recommendation', 'unknown').upper()}")
            print(f"   Application Status: {result.get('result', {}).get('status', 'unknown')}")
            print(f"   Tracking ID: {result.get('tracking', {}).get('application_id', 'N/A')}")
            
        except ImportError:
            print("ℹ️ LangGraph workflow not available - skipping workflow test")
        except Exception as e:
            print(f"⚠️ Workflow test failed: {str(e)}")
        
        return profile
        
    except Exception as e:
        print(f"❌ Resume parsing failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def determine_experience_level(years: int) -> str:
    """Determine experience level from years"""
    if years <= 1:
        return "entry"
    elif years <= 4:
        return "mid"
    elif years <= 8:
        return "senior"
    else:
        return "lead"

async def test_end_to_end_workflow():
    """Test the complete end-to-end workflow with simple inputs"""
    
    print(f"\n" + "=" * 60)
    print("🎯 END-TO-END WORKFLOW TEST")
    print("=" * 60)
    
    # Your inputs (simulating what a user would provide)
    resume_path = r"D:\Hare_Krishna_JobAgent\sreecharan_resume_2.0_with photo.pdf"
    job_type = "Python Developer, Software Engineer"
    location = "Bangalore, Mumbai, Remote"
    
    print(f"📄 Resume: {os.path.basename(resume_path)}")
    print(f"💼 Job Type: {job_type}")
    print(f"📍 Location: {location}")
    
    try:
        # Step 1: Parse resume
        parser = LLMResumeParser()
        profile = await parser.parse_resume(resume_path)
        
        # Step 2: Create search filters
        keywords = [k.strip() for k in job_type.split(',')]
        locations = [l.strip() for l in location.split(',')]
        experience_level = determine_experience_level(profile.get('years_experience', 0))
        
        search_filters = {
            "keywords": keywords,
            "locations": locations,
            "experience_level": experience_level
        }
        
        # Step 3: Create workflow input
        workflow_input = {
            "profile": profile,
            "search_filters": search_filters
        }
        
        print(f"\n🚀 Running your job application workflow...")
        
        # Step 4: Run your existing LangGraph workflow
        from graph.complete_job_agent_graph import create_complete_job_agent_graph
        job_agent = create_complete_job_agent_graph()
        result = await job_agent.ainvoke(workflow_input)
        
        # Step 5: Display results
        print(f"\n🎉 SUCCESS! Here's what happened:")
        print("=" * 40)
        
        job = result.get('job', {})
        score = result.get('score', {})
        materials = result.get('materials', {})
        tracking = result.get('tracking', {})
        
        print(f"👤 Candidate: {profile.get('name')}")
        print(f"💼 Job Found: {job.get('title')} at {job.get('company')}")
        print(f"📍 Location: {job.get('location')}")
        print(f"🎯 Fit Score: {score.get('overall_score', 0):.1f}%")
        print(f"💡 Recommendation: {score.get('recommendation', 'unknown').upper()}")
        print(f"📝 Materials: {'Generated' if materials else 'Not generated'}")
        print(f"📊 Tracking ID: {tracking.get('application_id', 'N/A')}")
        
        print(f"\n✅ SIMPLE INPUT → COMPLETE JOB APPLICATION WORKFLOW WORKS!")
        
    except Exception as e:
        print(f"❌ End-to-end test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_sreecharan_resume())
    
    # Uncomment to test complete workflow
    # asyncio.run(test_end_to_end_workflow())
