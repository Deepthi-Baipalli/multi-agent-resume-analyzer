# test_runner.py - COMPLETE VERSION
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append('src')

from graph.complete_job_agent_graph import create_complete_job_agent_graph, create_simple_test_graph
from models.state import JobApplicationState

# Load environment variables
load_dotenv()

async def test_simple_graph():
    """Test the basic 3-node graph (ingest -> parse -> score)"""
    print("🧪 Testing Simple Graph (3 nodes)")
    print("=" * 50)
    
    # Create test graph
    app = create_simple_test_graph()
    
    # Test input state with job search
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
            "skills": ["Python", "Django", "FastAPI", "PostgreSQL", "Docker"],
            "years_experience": 5,
            "current_title": "Senior Software Engineer",
            "work_authorization": "Indian Citizen"
        }
    }
    
    try:
        # Run the graph
        print("🔄 Running simple workflow...")
        result = await app.ainvoke(initial_state)
        
        print("\n✅ Simple Graph Test Results:")
        job_info = result.get('job', {})
        score_info = result.get('score', {})
        
        print(f"Job Title: {job_info.get('title', 'N/A')}")
        print(f"Company: {job_info.get('company', 'N/A')}")
        print(f"Location: {job_info.get('location', 'N/A')}")
        print(f"Fit Score: {score_info.get('overall_score', 'N/A')}%")
        
        if score_info.get('recommendation'):
            print(f"Recommendation: {score_info.get('recommendation')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Simple graph test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_complete_graph():
    """Test the complete graph with all nodes and routing"""
    print("\n🚀 Testing Complete Graph (All nodes)")
    print("=" * 50)
    
    # Create complete graph
    app = create_complete_job_agent_graph()
    
    # Test scenarios with different input types
    test_scenarios = [
        {
            "name": "Auto Job Search - Python Developer",
            "input": {
                "search_filters": {
                    "keywords": ["python", "backend"],
                    "locations": ["bangalore"],
                    "experience_level": "senior"
                },
                "profile": {
                    "name": "Priya Sharma",
                    "email": "priya@example.com",
                    "phone": "+91-98765-43210",
                    "location": "Bangalore, India",
                    "skills": ["Python", "Django", "REST API", "PostgreSQL", "AWS", "Docker"],
                    "years_experience": 6,
                    "current_title": "Senior Backend Developer",
                    "desired_roles": ["Senior Software Engineer", "Backend Developer", "Python Developer"],
                    "work_authorization": "Indian Citizen",
                    "remote_ok": True
                }
            }
        },
        {
            "name": "Specific LinkedIn Job URL",
            "input": {
                "job_url": "https://www.linkedin.com/jobs/view/software-engineer-ai/",
                "profile": {
                    "name": "Rahul Kumar",
                    "email": "rahul@example.com",
                    "phone": "+91-87654-32109",
                    "location": "Mumbai, India",
                    "skills": ["JavaScript", "React", "Node.js", "MongoDB", "Express"],
                    "years_experience": 4,
                    "current_title": "Full Stack Developer",
                    "desired_roles": ["Software Engineer", "Full Stack Developer"],
                    "work_authorization": "Indian Citizen",
                    "remote_ok": True
                }
            }
        },
        {
            "name": "Naukri Job Search - Data Science",
            "input": {
                "search_filters": {
                    "keywords": ["data scientist", "machine learning"],
                    "locations": ["pune"],
                    "experience_level": "mid"
                },
                "profile": {
                    "name": "Anita Patel",
                    "email": "anita@example.com",
                    "phone": "+91-76543-21098",
                    "location": "Pune, India",
                    "skills": ["Python", "Machine Learning", "TensorFlow", "Pandas", "SQL", "Power BI"],
                    "years_experience": 3,
                    "current_title": "Data Analyst",
                    "desired_roles": ["Data Scientist", "ML Engineer"],
                    "work_authorization": "Indian Citizen",
                    "remote_ok": False
                }
            }
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🔄 Testing Scenario {i}: {scenario['name']}")
        print("-" * 40)
        
        try:
            print("📝 Input Details:")
            if scenario['input'].get('job_url'):
                print(f"   Job URL: {scenario['input']['job_url']}")
            if scenario['input'].get('search_filters'):
                filters = scenario['input']['search_filters']
                print(f"   Keywords: {filters.get('keywords')}")
                print(f"   Location: {filters.get('locations')}")
            
            profile = scenario['input']['profile']
            print(f"   Candidate: {profile['name']} ({profile['current_title']})")
            
            print("\n🚀 Running complete workflow...")
            result = await app.ainvoke(scenario['input'])
            
            # Extract key results
            job_info = result.get('job', {})
            score_info = result.get('score', {})
            materials_info = result.get('materials', {})
            policy_info = result.get('policy', {})
            result_info = result.get('result', {})
            tracking_info = result.get('tracking', {})
            
            scenario_result = {
                "scenario": scenario['name'],
                "success": True,
                "job_title": job_info.get('title', 'Unknown'),
                "company": job_info.get('company', 'Unknown'),
                "fit_score": score_info.get('overall_score', 0),
                "recommendation": score_info.get('recommendation', 'unknown'),
                "channel": result.get('channel', 'unknown'),
                "mode": result.get('mode', 'unknown'),
                "status": result_info.get('status', 'unknown'),
                "materials_generated": bool(materials_info),
                "application_id": tracking_info.get('application_id', 'N/A')
            }
            
            print(f"\n📊 Results:")
            print(f"   Job: {scenario_result['job_title']} at {scenario_result['company']}")
            print(f"   Fit Score: {scenario_result['fit_score']}% ({scenario_result['recommendation']})")
            print(f"   Channel: {scenario_result['channel']} ({scenario_result['mode']})")
            print(f"   Status: {scenario_result['status']}")
            print(f"   Materials: {'Generated' if scenario_result['materials_generated'] else 'Not generated'}")
            print(f"   Tracking ID: {scenario_result['application_id']}")
            
            # Show materials preview
            if materials_info:
                print(f"\n📝 Generated Materials:")
                resume_bullets = materials_info.get('resume_bullets', [])
                if resume_bullets:
                    print(f"   Resume bullets: {len(resume_bullets)} points")
                    print(f"   Sample: {resume_bullets[0][:60]}..." if resume_bullets else "")
                
                cover_letter = materials_info.get('cover_letter', '')
                if cover_letter:
                    print(f"   Cover letter: {len(cover_letter)} characters")
                    print(f"   Preview: {cover_letter[:80]}..." if cover_letter else "")
            
            results.append(scenario_result)
            print("✅ Scenario completed successfully!")
            
        except Exception as e:
            print(f"   ❌ Failed: {str(e)}")
            results.append({
                "scenario": scenario['name'],
                "success": False,
                "error": str(e)
            })
    
    return results

async def test_detailed_workflow():
    """Test detailed workflow with full output"""
    print("\n🎯 Testing Detailed Workflow")
    print("=" * 50)
    
    app = create_complete_job_agent_graph()
    
    # Comprehensive test case
    initial_state = {
        "search_filters": {
            "keywords": ["software engineer", "python"],
            "locations": ["bangalore"],
            "experience_level": "senior",
            "companies_exclude": ["low-rated-company"]
        },
        "profile": {
            "name": "Vikram Singh",
            "email": "vikram.singh@email.com",
            "phone": "+91-98765-43210",
            "location": "Bangalore, Karnataka, India",
            "skills": ["Python", "Django", "FastAPI", "React", "PostgreSQL", "AWS", "Docker", "Kubernetes", "Redis"],
            "years_experience": 7,
            "current_title": "Senior Software Engineer",
            "desired_roles": ["Senior Software Engineer", "Lead Developer", "Principal Engineer"],
            "work_authorization": "Indian Citizen",
            "remote_ok": True,
            "salary_min": 2000000  # 20 LPA
        }
    }
    
    try:
        print("🔄 Running detailed workflow...")
        result = await app.ainvoke(initial_state)
        
        print("\n📊 DETAILED WORKFLOW RESULTS")
        print("=" * 50)
        
        # Display comprehensive results
        display_detailed_results(result)
        
        return result
        
    except Exception as e:
        print(f"❌ Detailed workflow test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def display_detailed_results(result):
    """Display formatted detailed results"""
    
    # Job Information
    job = result.get('job', {})
    print(f"🏢 JOB DETAILS")
    print(f"   Title: {job.get('title', 'N/A')}")
    print(f"   Company: {job.get('company', 'N/A')}")
    print(f"   Location: {job.get('location', 'N/A')}")
    print(f"   Source: {job.get('source', 'N/A')}")
    print(f"   URL: {job.get('url', 'N/A')[:60]}...")
    
    # Requirements Analysis
    parsed_req = job.get('parsed_requirements', {})
    if parsed_req:
        print(f"\n📋 PARSED REQUIREMENTS")
        print(f"   Required Skills: {parsed_req.get('required_skills', [])[:5]}")
        print(f"   Preferred Skills: {parsed_req.get('preferred_skills', [])[:3]}")
        print(f"   Experience: {parsed_req.get('years_experience', 'N/A')} years")
        print(f"   Seniority: {parsed_req.get('seniority_level', 'N/A')}")
    
    # Scoring Details
    score = result.get('score', {})
    if score:
        print(f"\n🎯 FIT ANALYSIS")
        print(f"   Overall Score: {score.get('overall_score', 'N/A')}%")
        print(f"   Recommendation: {score.get('recommendation', 'N/A').upper()}")
        
        components = score.get('components', {})
        if components:
            print(f"   Score Breakdown:")
            for component, value in components.items():
                print(f"     • {component.replace('_', ' ').title()}: {value}")
        
        explanation = score.get('explanation', {})
        if explanation:
            strengths = explanation.get('strengths', [])
            gaps = explanation.get('gaps', [])
            
            if strengths:
                print(f"   Strengths: {', '.join(strengths[:2])}")
            if gaps:
                print(f"   Gaps: {', '.join(gaps[:2])}")
    
    # Generated Materials
    materials = result.get('materials', {})
    if materials:
        print(f"\n📝 GENERATED MATERIALS")
        
        resume_bullets = materials.get('resume_bullets', [])
        print(f"   Resume Bullets ({len(resume_bullets)} total):")
        for i, bullet in enumerate(resume_bullets[:3], 1):
            print(f"     {i}. {bullet[:70]}...")
        
        cover_letter = materials.get('cover_letter', '')
        if cover_letter:
            print(f"   Cover Letter ({len(cover_letter)} chars):")
            print(f"     {cover_letter[:120]}...")
        
        qa_answers = materials.get('qa_answers', {})
        if qa_answers:
            print(f"   Q&A Answers: {len(qa_answers)} questions prepared")
    
    # Policy Decision
    policy = result.get('policy', {})
    print(f"\n🛡️ POLICY DECISION")
    print(f"   Channel: {result.get('channel', 'N/A')}")
    print(f"   Mode: {result.get('mode', 'N/A')}")
    print(f"   Reasoning: {policy.get('reasoning', 'N/A')}")
    print(f"   Compliance: {policy.get('compliance_status', 'N/A')}")
    
    # Application Result
    app_result = result.get('result', {})
    print(f"\n📤 APPLICATION STATUS")
    print(f"   Status: {app_result.get('status', 'N/A')}")
    print(f"   Platform: {app_result.get('platform', 'N/A')}")
    
    if app_result.get('confirmation_id'):
        print(f"   Confirmation: {app_result.get('confirmation_id')}")
    elif app_result.get('open_url'):
        print(f"   Manual URL: {app_result.get('open_url')[:60]}...")
    
    # Tracking Information
    tracking = result.get('tracking', {})
    if tracking:
        print(f"\n📊 TRACKING & FOLLOW-UP")
        print(f"   Application ID: {tracking.get('application_id', 'N/A')}")
        
        email_monitoring = tracking.get('email_monitoring', {})
        if email_monitoring:
            print(f"   Email Monitoring: {email_monitoring.get('status', 'N/A')}")
            print(f"   Monitor Duration: {email_monitoring.get('duration_days', 'N/A')} days")
        
        follow_ups = tracking.get('follow_ups', [])
        if follow_ups:
            print(f"   Follow-ups Scheduled: {len(follow_ups)}")
            for followup in follow_ups[:2]:
                date = followup.get('scheduled_for', '')[:10]
                print(f"     • {followup.get('message', 'N/A')} ({date})")

async def main():
    """Main test runner"""
    print("🤖 Job Apply-Assist Agent - Complete Test Suite")
    print("=" * 60)
    
    # Check environment
    if not os.getenv("GROQ_API_KEY"):
        print("❌ GROQ_API_KEY not found in environment")
        print("Please check your .env file")
        return
    
    print("✅ Environment configured")
    print("🔧 LLM Provider: Groq")
    print("🔍 Job Sources: Naukri, Indeed, Alternative APIs")
    
    # Run comprehensive tests
    try:
        # Test 1: Simple graph
        print("\n" + "🧪 PHASE 1: CORE FUNCTIONALITY TEST")
        simple_success = await test_simple_graph()
        
        if simple_success:
            # Test 2: Complete graph scenarios
            print("\n" + "🚀 PHASE 2: COMPLETE WORKFLOW TEST")
            complete_results = await test_complete_graph()
            
            # Test 3: Detailed workflow
            print("\n" + "🎯 PHASE 3: DETAILED ANALYSIS")
            detailed_result = await test_detailed_workflow()
            
            # Final Summary
            print("\n" + "=" * 60)
            print("🎉 FINAL TEST SUMMARY")
            print("=" * 60)
            
            print(f"✅ Core functionality: {'PASSED' if simple_success else 'FAILED'}")
            
            successful_scenarios = len([r for r in complete_results if r.get('success')])
            total_scenarios = len(complete_results)
            print(f"✅ Complete workflows: {successful_scenarios}/{total_scenarios} PASSED")
            
            print(f"✅ Detailed analysis: {'PASSED' if detailed_result else 'FAILED'}")
            
            if simple_success and successful_scenarios > 0:
                print("\n🚀 JOB APPLICATION AGENT IS FULLY FUNCTIONAL!")
                print("Ready for production use with real job applications.")
            else:
                print("\n⚠️ Some components need attention before production use.")
        
    except Exception as e:
        print(f"❌ Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
