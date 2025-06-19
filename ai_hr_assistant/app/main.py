import streamlit as st
from langchain_helper_sqlite import get_few_shot_sqlite_chain
import os
import json
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="HR Database Query Assistant",
    page_icon="🗃️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .query-box {
        background-color: #000000;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        margin: 1rem 0;
    }
    
    .result-box {
        background-color: #000000;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
    
    .error-box {
        background-color: #ffeaa7;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #fdcb6e;
        margin: 1rem 0;
    }
    
    .sidebar .stButton > button {
        width: 100%;
        margin-bottom: 0.5rem;
    }
    
    .metric-container {
        background-color: #f1f3f4;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize chain with caching
@st.cache_resource
def initialize_chain():
    """Initialize the SQL chain with caching to avoid reloading on every interaction"""
    try:
        return get_few_shot_sqlite_chain()
    except Exception as e:
        st.error(f"Failed to initialize database chain: {str(e)}")
        return None

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_database_stats():
    """Get basic database statistics"""
    try:
        chain = initialize_chain()
        if not chain:
            return None
            
        stats = {}
        # You could add specific queries here to get database stats
        # For now, we'll return a placeholder
        stats['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return stats
    except:
        return None

def save_query_history():
    """Save query history to local storage (session-based)"""
    if 'query_history' in st.session_state:
        # In a production app, you might want to save this to a file or database
        pass

def load_query_history():
    """Load query history from storage"""
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []

def export_history():
    """Export query history as JSON"""
    if 'query_history' in st.session_state and st.session_state.query_history:
        history_data = {
            'exported_at': datetime.now().isoformat(),
            'queries': st.session_state.query_history
        }
        return json.dumps(history_data, indent=2)
    return None

# Main app
def main():
    # Load query history
    load_query_history()
    
    # Header with custom styling
    st.markdown("""
    <div class="main-header">
        <h1>🗃️ HR Streamline AI Assistant</h1>
        <p>Ask questions about your HR database in natural language!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar with enhanced features
    with st.sidebar:
        st.header("📝 Example Questions")
        
        # Categories of questions
        categories = {
            "👥 Employee Queries": [
                "How many employees do we have?",
                "How many male and female employees do we have?",
                "Which employees are in the Engineering department?",
                "Show me all active employees",
            ],
            "🏖️ Leave Management": [
                "Who has pending leave requests?",
                "Which employee has an annual leave request starting soon?",
                "What's the average leave balance by gender?",
                "Show me employees with low leave balance",
            ],
            "⏰ Attendance": [
                "Show me all employees that clocked in today",
                "Who hasn't clocked in yet?",
                "What's the average clock-in time?",
            ],
            "📊 Analytics": [
                "What's the department distribution?",
                "Show me leave trends by month",
                "Which department has the most employees?",
            ]
        }
        
        for category, questions in categories.items():
            with st.expander(category):
                for i, question in enumerate(questions):
                    if st.button(question, key=f"example_{category}_{i}"):
                        st.session_state.user_question = question
                        st.rerun()
        
        st.divider()
        
        # Database stats
        st.header("📈 Database Info")
        stats = get_database_stats()
        if stats:
            st.info(f"Last updated: {stats.get('last_updated', 'Unknown')}")
        
        # Query history management
        if st.session_state.query_history:
            st.header("📜 History")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear History"):
                    st.session_state.query_history = []
                    st.rerun()
            
            with col2:
                history_json = export_history()
                if history_json:
                    st.download_button(
                        "💾 Export",
                        history_json,
                        file_name=f"query_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
    
    # Initialize session state
    if 'user_question' not in st.session_state:
        st.session_state.user_question = ""
    
    # Main input area with enhanced layout
    st.subheader("💬 Ask Your Question")
    
    user_question = st.text_area(
        "Enter your question:",
        value=st.session_state.user_question,
        placeholder="e.g., How many employees are in each department? Show me their names and positions.",
        help="Ask any question about your HR database in plain English. You can ask about employees, departments, leave requests, attendance, or any other HR-related data.",
        height=100
    )
    
    # Update session state
    if user_question != st.session_state.user_question:
        st.session_state.user_question = user_question
    
    # Action buttons
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        run_query = st.button("🚀 Run Query", type="primary", use_container_width=True)
    
    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.user_question = ""
            st.rerun()
    
    with col3:
        # Quick suggestions
        if st.button("💡 Suggest", use_container_width=True):
            suggestions = [
                "Try asking about employee counts, leave balances, or department information",
                "You can ask for specific employee details or comparative statistics",
                "Ask about trends, averages, or filtering by specific criteria"
            ]
            st.info("💡 " + suggestions[len(st.session_state.query_history) % len(suggestions)])
    
    with col4:
        # Random example
        if st.button("🎲 Random", use_container_width=True):
            import random
            all_examples = []
            for questions in categories.values():
                all_examples.extend(questions)
            if all_examples:
                st.session_state.user_question = random.choice(all_examples)
                st.rerun()
    
    # Query execution with enhanced feedback
    if run_query and user_question.strip():
        
        # API key check
        if not os.environ.get("GOOGLE_API_KEY"):
            st.error("⚠️ Google API key not found. Please set the GOOGLE_API_KEY environment variable.")
            st.info("💡 You can get a Google API key from the Google Cloud Console")
            return
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Initialize chain
            status_text.text("🔄 Initializing database connection...")
            progress_bar.progress(20)
            
            chain = initialize_chain()
            if not chain:
                st.error("❌ Failed to initialize database connection.")
                return
            
            # Step 2: Process query
            status_text.text("🧠 Processing your question...")
            progress_bar.progress(50)
            
            start_time = time.time()
            
            # Run the query using the new invoke method
            result = chain.invoke({"query": user_question})
            
            # Handle different response types
            if isinstance(result, dict):
                answer = result.get('result', result.get('answer', str(result)))
            else:
                answer = str(result)
            
            end_time = time.time()
            processing_time = round(end_time - start_time, 2)
            
            # Step 3: Display results
            status_text.text("✅ Query completed!")
            progress_bar.progress(100)
            
            # Clear progress indicators
            time.sleep(0.5)
            progress_bar.empty()
            status_text.empty()
            
            # Display results with custom styling
            st.markdown("### 📊 Results:")
            st.markdown(f"""
            <div class="result-box">
                <strong>Answer:</strong><br>
                {answer}
            </div>
            """, unsafe_allow_html=True)
            
            # Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("⚡ Processing Time", f"{processing_time}s")
            with col2:
                st.metric("📝 Query Length", f"{len(user_question)} chars")
            with col3:
                st.metric("📊 Response Length", f"{len(answer)} chars")
            
            # Add to history
            st.session_state.query_history.append({
                'timestamp': datetime.now().isoformat(),
                'question': user_question,
                'answer': answer,
                'processing_time': processing_time
            })
            
            # Feedback section
            st.markdown("### 💬 Was this helpful?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("👍 Yes, helpful"):
                    st.success("Thank you for your feedback!")
            with col2:
                if st.button("👎 Could be better"):
                    st.info("We'll work on improving our responses!")
                    
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            
            st.markdown(f"""
            <div class="error-box">
                <strong>❌ Error occurred:</strong><br>
                {str(e)}
            </div>
            """, unsafe_allow_html=True)
            
            # Enhanced error diagnostics
            with st.expander("🔍 Diagnostic Information"):
                st.code(str(e))
                st.markdown("**Troubleshooting Steps:**")
                st.markdown("1. 🔍 Check if your database file exists and is accessible")
                st.markdown("2. 🔑 Verify your Google API key is set correctly")
                st.markdown("3. 📝 Try rephrasing your question or using simpler terms")
                st.markdown("4. 🔄 Refresh the page and try again")
                st.markdown("5. 💡 Use one of the example questions from the sidebar")
                
    elif run_query and not user_question.strip():
        st.warning("⚠️ Please enter a question before running the query.")
    
    # Enhanced Query History Section
    if st.session_state.query_history:
        st.markdown("---")
        st.subheader("📜 Recent Query History")
        
        # Show statistics
        total_queries = len(st.session_state.query_history)
        avg_processing_time = sum(q.get('processing_time', 0) for q in st.session_state.query_history) / total_queries
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Queries", total_queries)
        with col2:
            st.metric("Avg Processing Time", f"{avg_processing_time:.2f}s")
        
        # Display recent queries
        with st.expander(f"View History ({min(10, total_queries)} most recent)", expanded=False):
            for i, entry in enumerate(reversed(st.session_state.query_history[-10:])):
                timestamp = entry.get('timestamp', 'Unknown time')
                processing_time = entry.get('processing_time', 0)
                
                st.markdown(f"""
                <div class="query-box">
                    <strong>Q{total_queries-i}:</strong> {entry['question']}<br>
                    <strong>A:</strong> {entry['answer']}<br>
                    <small>🕐 {timestamp} | ⚡ {processing_time}s</small>
                </div>
                """, unsafe_allow_html=True)
    
    # Footer with tips and information
    st.markdown("---")
    st.markdown("""
    ### 💡 Tips for Better Results:
    - **Be specific**: Instead of "show employees", try "show all active employees with their departments"
    - **Use natural language**: Ask questions as you would to a human
    - **Try different phrasings**: If one question doesn't work, rephrase it
    - **Use examples**: Check the sidebar for sample questions
    
    ### 🔧 Technical Info:
    - Powered by Google's Gemini AI and LangChain
    - Uses semantic similarity for intelligent query understanding
    - Supports complex SQL operations through natural language
    """)

if __name__ == "__main__":
    main()