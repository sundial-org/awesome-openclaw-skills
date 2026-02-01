#!/usr/bin/env python3
"""
Flow - Streamlit UI

Web-based interface for the Flow Skill Orchestrator.
"""

import streamlit as st
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from flow import Flow
    from skill_registry import SkillRegistry
except ImportError:
    st.error("Could not import Flow modules. Make sure all files are in the same directory.")
    st.stop()

# Page config
st.set_page_config(
    page_title="Flow - Intelligent Skill Orchestrator",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .status-safe {
        color: #28a745;
        font-weight: 600;
    }
    .status-warning {
        color: #ffc107;
        font-weight: 600;
    }
    .status-danger {
        color: #dc3545;
        font-weight: 600;
    }
    .step-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'flow' not in st.session_state:
    st.session_state.flow = Flow()
if 'last_result' not in st.session_state:
    st.session_state.last_result = None

# Sidebar
st.sidebar.title("🔄 Flow")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["🏠 Build Flow", "📚 Skill Registry", "ℹ️ About"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
### Quick Stats
""")

try:
    skills = st.session_state.flow.list_available_skills()
    st.sidebar.metric("Skills in Registry", len(skills))
except:
    st.sidebar.metric("Skills in Registry", 0)

# Main content
if page == "🏠 Build Flow":
    st.markdown('<div class="main-header">🔄 Flow - Intelligent Skill Orchestrator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Compose natural language requests into secure, reusable workflows</div>', unsafe_allow_html=True)
    
    # Input section
    st.markdown("### What do you want to build?")
    user_request = st.text_area(
        "Describe your idea in natural language",
        placeholder="Example: Build a web scraper that extracts product prices and saves to CSV",
        height=100,
        help="Describe what you want to build. Flow will find existing skills, scan for security, and compose them into a unified workflow."
    )
    
    col1, col2, col3 = st.columns([1, 1, 4])
    
    with col1:
        build_button = st.button("🚀 Build Flow", type="primary", use_container_width=True)
    
    with col2:
        clear_button = st.button("🗑️ Clear", use_container_width=True)
    
    if clear_button:
        st.session_state.last_result = None
        st.rerun()
    
    if build_button and user_request:
        with st.spinner("Processing your request..."):
            # Create progress display
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Parsing
            status_text.text("[1/5] Parsing request...")
            progress_bar.progress(20)
            
            # Step 2: Searching
            status_text.text("[2/5] Searching skill registry...")
            progress_bar.progress(40)
            
            # Step 3: Scanning
            status_text.text("[3/5] Running security scans...")
            progress_bar.progress(60)
            
            # Step 4: Composing
            status_text.text("[4/5] Composing FLOW skill...")
            progress_bar.progress(80)
            
            # Step 5: Complete
            status_text.text("[5/5] Updating registry...")
            progress_bar.progress(100)
            
            # Process request
            result = st.session_state.flow.process(user_request)
            st.session_state.last_result = result
            
            progress_bar.empty()
            status_text.empty()
    
    # Display results
    if st.session_state.last_result:
        result = st.session_state.last_result
        
        st.markdown("---")
        st.markdown("### 📊 Flow Results")
        
        # Status overview
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if result.success:
                st.metric("Status", "✅ Success")
            else:
                st.metric("Status", "❌ Failed")
        
        with col2:
            security_color = {
                "PASSED": "status-safe",
                "WARNING": "status-warning",
                "FAILED": "status-danger",
                "ERROR": "status-danger"
            }.get(result.security_status, "")
            st.markdown(f'<div class="{security_color}" style="font-size: 0.875rem;">Security: {result.security_status}</div>', unsafe_allow_html=True)
        
        with col3:
            st.metric("Skills Used", len(result.skills_used))
        
        with col4:
            st.metric("Time", f"{result.execution_time:.2f}s")
        
        # Details
        if result.success:
            st.success(f"✨ Created FLOW: **{result.flow_name}**")
            
            if result.output_path:
                st.code(result.output_path, language="text")
            
            if result.skills_used:
                st.markdown("#### 🧩 Skills Composed")
                for skill in result.skills_used:
                    st.markdown(f"- {skill}")
        
        # Warnings
        if result.warnings:
            st.markdown("#### ⚠️ Warnings")
            for warning in result.warnings:
                st.warning(warning)
        
        # Errors
        if result.errors:
            st.markdown("#### ❌ Errors")
            for error in result.errors:
                st.error(error)

elif page == "📚 Skill Registry":
    st.markdown('<div class="main-header">📚 Skill Registry</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Browse and search available skills</div>', unsafe_allow_html=True)
    
    # Search and filter
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input("🔍 Search skills", placeholder="Search by name or capability...")
    
    with col2:
        sort_by = st.selectbox("Sort by", ["Reuse Score", "Name", "Capabilities"])
    
    # Get skills
    try:
        skills = st.session_state.flow.list_available_skills()
        
        # Filter by search
        if search_query:
            skills = [
                s for s in skills 
                if search_query.lower() in s['name'].lower() 
                or search_query.lower() in s.get('description', '').lower()
                or any(search_query.lower() in cap.lower() for cap in s.get('capabilities', []))
            ]
        
        # Sort
        if sort_by == "Name":
            skills.sort(key=lambda x: x['name'])
        elif sort_by == "Capabilities":
            skills.sort(key=lambda x: len(x.get('capabilities', [])), reverse=True)
        # Default is already sorted by reuse score
        
        st.markdown(f"### {len(skills)} Skills Found")
        
        if skills:
            for skill in skills:
                with st.expander(f"**{skill['name']}** - Score: {skill.get('reuse_score', 0)}"):
                    st.markdown(f"**Description:** {skill.get('description', 'No description')}")
                    
                    if skill.get('capabilities'):
                        st.markdown("**Capabilities:**")
                        caps = ", ".join(skill['capabilities'])
                        st.markdown(f"`{caps}`")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Reuse Score", skill.get('reuse_score', 0))
                    with col2:
                        st.metric("Usage Count", skill.get('usage_count', 0))
        else:
            st.info("No skills found. Skills will be registered as you build FLOWs.")
    
    except Exception as e:
        st.error(f"Error loading skills: {str(e)}")
        st.info("No skills found. Skills will be registered as you build FLOWs.")

elif page == "ℹ️ About":
    st.markdown('<div class="main-header">ℹ️ About Flow</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ## What is Flow?
    
    Flow is an **Intelligent Skill Orchestrator** that allows you to:
    
    - 🗣️ Express build ideas in **natural language**
    - 🔍 Find and **reuse existing skills** automatically
    - 🔒 **Security scan** all components before composition
    - 🔄 **Compose** multiple skills into unified workflows
    - 📊 Track skill usage for **intelligent reuse**
    
    ## How It Works
    
    1. **Parse Request** - NLP extracts intent, capabilities, and steps
    2. **Search Registry** - Finds existing skills matching requirements
    3. **Security Scan** - Checks all skills for malicious patterns
    4. **Compose** - Merges skills into single executable FLOW
    5. **Register** - Saves new FLOW for future reuse
    
    ## Security Features
    
    Flow includes comprehensive security scanning:
    
    - ✅ Code execution detection (eval, exec)
    - ✅ Data exfiltration pattern matching
    - ✅ Crypto mining indicator scanning
    - ✅ System modification attempt detection
    - ✅ AST-based code analysis
    - ✅ Obfuscation detection
    
    ## Architecture
    
    - `flow.py` - Main orchestrator
    - `natural_language_parser.py` - NLP for user intent
    - `skill_registry.py` - Reusable skill database
    - `skill_scanner_integration.py` - Security scanning
    - `skill_composer.py` - Compiles skills into FLOW
    
    ## Author
    
    Created by **@bvinci1-design**
    
    GitHub: [bvinci1-design/flow](https://github.com/bvinci1-design/flow)
    """)
    
    st.markdown("---")
    st.markdown("### 🚀 Quick Start")
    
    st.code("""
# CLI Mode
python flow.py "Build a web scraper that extracts prices"

# Interactive Mode
python flow.py

# Web UI (this interface)
streamlit run streamlit_ui.py
    """, language="bash")

st.sidebar.markdown("---")
st.sidebar.markdown("Made with ❤️ by @bvinci1-design")
st.sidebar.markdown("[GitHub](https://github.com/bvinci1-design/flow) | [ClawdHub](https://clawdhub.com)")
