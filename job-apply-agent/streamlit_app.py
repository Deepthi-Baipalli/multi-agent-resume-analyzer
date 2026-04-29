# streamlit_app.py - Complete Job Apply-Assist Agent Web App

import streamlit as st
import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
import json
import base64
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append('src')

# Check required environment variables
def check_environment():
    """Check if required API keys are set"""
    required_vars = {
        'GROQ_API_KEY': 'Groq API key for LLM processing',
        'ADZUNA_API_KEY': 'Adzuna API key for job search',
        'ADZUNA_APP_ID': 'Adzuna App ID for job search'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"**{var}**: {description}")
    
    return missing_vars

# Import your existing modules
from services.resume_parser import LLMResumeParser
from graph.complete_job_agent_graph import create_complete_job_agent_graph

# Set page config
st.set_page_config(
    page_title="🚀 Job Apply-Assist Agent",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'processed_profile' not in st.session_state:
    st.session_state.processed_profile = None
if 'job_results' not in st.session_state:
    st.session_state.job_results = None
if 'materials_generated' not in st.session_state:
    st.session_state.materials_generated = False

def save_uploaded_file(uploaded_file):
    """Save uploaded file temporarily"""
    temp_dir = Path("temp_uploads")
    temp_dir.mkdir(exist_ok=True)
    
    file_path = temp_dir / uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return str(file_path)

def create_download_link(content, filename, link_text):
    """Create download link for text content"""
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:text/plain;base64,{b64}" download="{filename}">{link_text}</a>'
    return href

async def process_resume(resume_file):
    """Process uploaded resume"""
    try:
        # Save uploaded file
        file_path = save_uploaded_file(resume_file)
        
        # Parse resume
        parser = LLMResumeParser()
        profile = await parser.parse_resume(file_path)
        
        # Clean up temp file
        os.remove(file_path)
        
        return profile, None
    except Exception as e:
        return None, str(e)

async def run_job_pipeline(profile, locations, job_keywords=None):
    """Run the complete job application pipeline"""
    try:
        # Auto-detect keywords if not provided
        if not job_keywords:
            job_keywords = auto_detect_keywords(profile)
        
        # Create search filters
        search_filters = {
            "keywords": job_keywords,
            "locations": locations,
            "experience_level": detect_experience_level(profile.get('years_experience', 0))
        }
        
        # Create workflow input
        workflow_input = {
            "profile": profile,
            "search_filters": search_filters
        }
        
        # Run complete pipeline
        job_agent = create_complete_job_agent_graph()
        result = await job_agent.ainvoke(workflow_input)
        
        return result, None
        
    except Exception as e:
        return None, str(e)

def auto_detect_keywords(profile):
    """Auto-detect job keywords from comprehensive profile"""
    current_title = profile.get('current_title', '').lower()
    skills = [skill.lower() for skill in profile.get('skills', [])]
    specializations = [spec.lower() for spec in profile.get('specializations', [])]
    projects = profile.get('projects', [])
    
    # Enhanced keyword detection using all profile data
    if any(word in current_title for word in ['data scientist', 'data science']):
        return ['Data Scientist', 'Machine Learning Engineer', 'Data Analyst']
    
    elif any(spec in specializations for spec in ['machine learning', 'ai', 'data science']):
        return ['Data Scientist', 'ML Engineer', 'AI Engineer']
    
    elif any(word in current_title for word in ['software engineer', 'developer']):
        if any(skill in skills for skill in ['python', 'java', 'javascript']):
            return ['Software Engineer', 'Backend Developer', 'Full Stack Developer']
        else:
            return ['Software Engineer', 'Software Developer']
    
    elif any(word in current_title for word in ['analyst', 'business']):
        return ['Business Analyst', 'Data Analyst', 'Financial Analyst']
    
    elif any(word in current_title for word in ['product', 'manager']):
        return ['Product Manager', 'Project Manager']
    
    # Check skills and projects for more specific roles
    elif any(skill in skills for skill in ['pytorch', 'tensorflow', 'machine learning']):
        return ['Data Scientist', 'ML Engineer', 'AI Engineer']
    
    elif any(skill in skills for skill in ['python', 'fastapi', 'flask']):
        return ['Python Developer', 'Backend Engineer', 'Data Scientist']
    
    elif any(skill in skills for skill in ['java', 'spring']):
        return ['Java Developer', 'Backend Engineer', 'Software Engineer']
    
    elif any(skill in skills for skill in ['react', 'javascript', 'node']):
        return ['Frontend Developer', 'Full Stack Developer', 'JavaScript Developer']
    
    # Check project titles for domain expertise
    project_text = ' '.join([p.get('title', '') + ' ' + p.get('description', '') for p in projects]).lower()
    if any(term in project_text for term in ['computer vision', 'image', 'opencv']):
        return ['Computer Vision Engineer', 'ML Engineer', 'AI Engineer']
    
    elif any(term in project_text for term in ['nlp', 'text', 'language']):
        return ['NLP Engineer', 'ML Engineer', 'Data Scientist']
    
    elif any(term in project_text for term in ['genai', 'llm', 'generative']):
        return ['GenAI Engineer', 'ML Engineer', 'AI Engineer']
    
    else:
        # Fallback: use current title or default
        return [profile.get('current_title', 'Software Engineer')]

def detect_experience_level(years):
    """Detect experience level"""
    if years == 0:
        return "entry"  # Fresh graduate
    elif years <= 2:
        return "entry"
    elif years <= 5:
        return "mid"
    else:
        return "senior"

def main():
    # Check environment variables first
    missing_vars = check_environment()
    
    if missing_vars:
        st.error("🚨 **Missing Required API Keys**")
        st.markdown("Please set the following environment variables:")
        for var in missing_vars:
            st.markdown(f"- {var}")
        
        st.markdown("""
        **How to fix:**
        1. Create a `.env` file in your project root
        2. Add these lines to the `.env` file:
        ```
        GROQ_API_KEY=your_groq_api_key_here
        ADZUNA_API_KEY=your_adzuna_api_key_here
        ADZUNA_APP_ID=your_adzuna_app_id_here
        ```
        3. Restart the Streamlit app
        """)
        
        st.info("💡 **Need API keys?**\n- Get Groq API key from: https://console.groq.com/\n- Get Adzuna API key from: https://developer.adzuna.com/")
        return
    
    # Header
    st.markdown('<h1 class="main-header">🚀 Job Apply-Assist Agent</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Upload Resume + Select Location → Get Complete Application Materials</p>', unsafe_allow_html=True)
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("📋 Application Input")
        
        # File upload
        st.subheader("1. Upload Resume")
        uploaded_file = st.file_uploader(
            "Upload your resume (PDF/DOCX)",
            type=['pdf', 'docx'],
            help="Upload your latest resume in PDF or DOCX format"
        )
        
        # Location selection
        st.subheader("2. Select Locations")
        indian_cities = [
            "Bangalore", "Mumbai", "Delhi", "Hyderabad", "Chennai", 
            "Pune", "Kolkata", "Ahmedabad", "Gurugram", "Noida", "Remote"
        ]
        
        selected_locations = st.multiselect(
            "Choose preferred job locations",
            indian_cities,
            default=["Bangalore"],
            help="Select one or more cities where you want to work"
        )
        
        # Optional: Custom job keywords
        st.subheader("3. Job Keywords (Optional)")
        custom_keywords = st.text_input(
            "Specific job types (comma-separated)",
            placeholder="e.g., Data Scientist, ML Engineer",
            help="Leave empty for auto-detection from resume"
        )
        
        # Process button
        process_button = st.button(
            "🚀 Find Jobs & Generate Materials",
            type="primary",
            use_container_width=True
        )
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📄 Resume Analysis")
        
        if uploaded_file is not None:
            st.success(f"✅ Resume uploaded: {uploaded_file.name}")
            
            # Process resume when uploaded
            if st.session_state.processed_profile is None:
                with st.spinner("🔄 Parsing resume..."):
                    profile, error = asyncio.run(process_resume(uploaded_file))
                    
                    if profile:
                        st.session_state.processed_profile = profile
                        st.rerun()
                    else:
                        st.error(f"❌ Resume parsing failed: {error}")
            
            # Display parsed profile
            if st.session_state.processed_profile:
                profile = st.session_state.processed_profile
                
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.write("**✅ Profile Extracted Successfully**")
                st.write(f"**Name:** {profile.get('name', 'N/A')}")
                st.write(f"**Current Title:** {profile.get('current_title', 'N/A')}")
                st.write(f"**Experience:** {profile.get('years_experience', 0)} years")
                st.write(f"**Location:** {profile.get('location', 'N/A')}")
                st.write(f"**Education:** {profile.get('education', 'N/A')}")
                
                # Technical Skills
                skills = profile.get('skills', [])
                programming_langs = profile.get('programming_languages', [])
                if programming_langs:
                    st.write(f"**Programming:** {', '.join(programming_langs[:4])}")
                if skills:
                    st.write(f"**Key Skills:** {', '.join(skills[:6])}")
                
                # Projects
                projects = profile.get('projects', [])
                if projects:
                    st.write(f"**Projects:** {len(projects)} projects detected")
                    with st.expander("📋 View Projects"):
                        for i, project in enumerate(projects[:3], 1):
                            st.write(f"**{i}. {project.get('title', 'Project')}**")
                            if project.get('description'):
                                st.write(f"   {project['description'][:100]}...")
                            if project.get('technologies'):
                                techs = project['technologies'][:4]
                                st.write(f"   *Tech:* {', '.join(techs)}")
                            if project.get('achievements'):
                                st.write(f"   *Impact:* {project['achievements'][:80]}...")
                
                # Achievements
                achievements = profile.get('achievements', [])
                if achievements:
                    st.write(f"**Achievements:** {len(achievements)} recognitions")
                    with st.expander("🏆 View Achievements"):
                        for achievement in achievements[:5]:
                            st.write(f"• {achievement}")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Auto-detected keywords
                auto_keywords = auto_detect_keywords(profile)
                st.info(f"🎯 **Auto-detected job types:** {', '.join(auto_keywords)}")
        
        else:
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.write("📁 **Please upload your resume to get started**")
            st.write("Supported formats: PDF, DOCX")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.header("🎯 Job Search Settings")
        
        if selected_locations:
            st.success(f"📍 **Selected Locations:** {', '.join(selected_locations)}")
        else:
            st.warning("⚠️ Please select at least one location")
        
        if custom_keywords:
            keywords_list = [k.strip() for k in custom_keywords.split(',')]
            st.info(f"🔍 **Custom Keywords:** {', '.join(keywords_list)}")
        
        # Experience level display
        if st.session_state.processed_profile:
            years = st.session_state.processed_profile.get('years_experience', 0)
            level = detect_experience_level(years)
            st.info(f"📊 **Experience Level:** {level.title()} ({years} years)")
    
    # Process job search
    if process_button:
        if not uploaded_file:
            st.error("❌ Please upload a resume first")
        elif not selected_locations:
            st.error("❌ Please select at least one location")
        elif not st.session_state.processed_profile:
            st.error("❌ Resume not processed yet. Please wait for parsing to complete.")
        else:
            # Prepare keywords
            if custom_keywords:
                job_keywords = [k.strip() for k in custom_keywords.split(',')]
            else:
                job_keywords = None
            
            # Run pipeline
            with st.spinner("🔄 Running complete job search pipeline..."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Update progress
                status_text.text("🔍 Searching for jobs...")
                progress_bar.progress(20)
                
                result, error = asyncio.run(run_job_pipeline(
                    st.session_state.processed_profile,
                    selected_locations,
                    job_keywords
                ))
                
                progress_bar.progress(60)
                status_text.text("📊 Analyzing job fit...")
                
                if result:
                    st.session_state.job_results = result
                    st.session_state.materials_generated = True
                    progress_bar.progress(100)
                    status_text.text("✅ Complete! Results ready.")
                    st.rerun()
                else:
                    st.error(f"❌ Pipeline failed: {error}")
                    progress_bar.empty()
                    status_text.empty()
    
    # Display results
    if st.session_state.job_results:
        st.header("🎉 Results")
        
        result = st.session_state.job_results
        job = result.get('job', {})
        score = result.get('score', {})
        materials = result.get('materials', {})
        
        # Job details
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.subheader("🏢 Selected Job")
            st.write(f"**Title:** {job.get('title', 'N/A')}")
            st.write(f"**Company:** {job.get('company', 'N/A')}")
            st.write(f"**Location:** {job.get('location', 'N/A')}")
            st.write(f"**Source:** {job.get('source', 'N/A').title()}")
            
            if job.get('url'):
                st.markdown(f"[🔗 Apply Here]({job.get('url')})")
        
        with col2:
            st.subheader("📊 Fit Analysis")
            fit_score = score.get('overall_score', 0)
            
            # Color-coded score
            if fit_score >= 70:
                st.success(f"**{fit_score:.1f}%**")
            elif fit_score >= 40:
                st.warning(f"**{fit_score:.1f}%**")
            else:
                st.error(f"**{fit_score:.1f}%**")
            
            recommendation = score.get('recommendation', 'review').upper()
            st.write(f"**Recommendation:** {recommendation}")
        
        with col3:
            st.subheader("📈 Score Breakdown")
            components = score.get('components', {})
            for component, value in components.items():
                if component != 'penalties':
                    st.write(f"**{component.replace('_', ' ').title()}:** {value:.1f}")
        
        # Materials section
        st.header("📝 Generated Materials")
        
        tab1, tab2, tab3 = st.tabs(["📄 Cover Letter", "📋 Resume Bullets", "❓ Q&A Answers"])
        
        with tab1:
            cover_letter = materials.get('cover_letter', '')
            if cover_letter:
                st.subheader("Your Personalized Cover Letter")
                st.text_area("Cover Letter", cover_letter, height=300, disabled=True)
                
                # Download button
                st.markdown(
                    create_download_link(
                        cover_letter,
                        f"cover_letter_{job.get('company', 'job')}_{datetime.now().strftime('%Y%m%d')}.txt",
                        "💾 Download Cover Letter"
                    ),
                    unsafe_allow_html=True
                )
            else:
                st.warning("No cover letter generated")
        
        with tab2:
            resume_bullets = materials.get('resume_bullets', [])
            if resume_bullets:
                st.subheader("Tailored Resume Bullets")
                for i, bullet in enumerate(resume_bullets, 1):
                    st.write(f"**{i}.** {bullet}")
                
                # Download button
                bullets_text = "\n".join([f"• {bullet}" for bullet in resume_bullets])
                st.markdown(
                    create_download_link(
                        bullets_text,
                        f"resume_bullets_{job.get('company', 'job')}_{datetime.now().strftime('%Y%m%d')}.txt",
                        "💾 Download Resume Bullets"
                    ),
                    unsafe_allow_html=True
                )
            else:
                st.warning("No resume bullets generated")
        
        with tab3:
            qa_answers = materials.get('qa_answers', {})
            if qa_answers:
                st.subheader("Application Q&A Answers")
                for question, answer in qa_answers.items():
                    st.write(f"**Q: {question.replace('_', ' ').title()}**")
                    st.write(f"A: {answer}")
                    st.write("---")
                
                # Download button
                qa_text = "\n\n".join([
                    f"Q: {q.replace('_', ' ').title()}\nA: {a}" 
                    for q, a in qa_answers.items()
                ])
                st.markdown(
                    create_download_link(
                        qa_text,
                        f"qa_answers_{job.get('company', 'job')}_{datetime.now().strftime('%Y%m%d')}.txt",
                        "💾 Download Q&A Answers"
                    ),
                    unsafe_allow_html=True
                )
            else:
                st.warning("No Q&A answers generated")
        
        # Next steps
        st.header("🚀 Next Steps")
        st.markdown("""
        <div class="info-box">
        <h4>How to Apply:</h4>
        <ol>
            <li><strong>Review</strong> your generated materials above</li>
            <li><strong>Download</strong> the cover letter and other materials</li>
            <li><strong>Click</strong> the "Apply Here" link to go to the job posting</li>
            <li><strong>Copy-paste</strong> your materials into the application form</li>
            <li><strong>Submit</strong> your application</li>
        </ol>
        <p><strong>💡 Tip:</strong> Customize the materials further if needed before submitting!</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #666;">🚀 Job Apply-Assist Agent - Powered by AI | Built with Streamlit</p>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
