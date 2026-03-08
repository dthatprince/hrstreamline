import streamlit as st
from langchain_helper_postgresql import get_few_shot_postgresql_chain
from style_loader import load_css
import os
import json
import time
from datetime import datetime

# ─────────────────────────────────────────────
#  Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="HR Streamline · AI Query",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  Load stylesheet
# ─────────────────────────────────────────────
load_css("styles.css")


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────
@st.cache_resource
def initialize_chain():
    try:
        return get_few_shot_postgresql_chain()
    except Exception as e:
        st.error(f"Failed to initialize database chain: {str(e)}")
        return None


@st.cache_data(ttl=300)
def get_database_stats():
    try:
        stats = {"last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")}
        return stats
    except:
        return None


def load_query_history():
    if "query_history" not in st.session_state:
        st.session_state.query_history = []


def export_history():
    if st.session_state.get("query_history"):
        return json.dumps(
            {"exported_at": datetime.now().isoformat(),
             "queries": st.session_state.query_history},
            indent=2,
        )
    return None


# ─────────────────────────────────────────────
#  Sidebar
# ─────────────────────────────────────────────
CATEGORIES = {
    "Employee Queries": {
        "icon": "◈",
        "questions": [
            "How many employees do we have?",
            "How many male and female employees do we have?",
            "Which employees are in the Engineering department?",
            "Show me all active employees",
        ],
    },
    "Leave Management": {
        "icon": "◇",
        "questions": [
            "Who has pending leave requests?",
            "Which employee has an annual leave request starting soon?",
            "What's the average leave balance by gender?",
            "Show me employees with low leave balance",
        ],
    },
    "Attendance": {
        "icon": "◉",
        "questions": [
            "Show me all employees that clocked in today",
            "Who hasn't clocked in yet?",
            "What's the average clock-in time?",
        ],
    },
    "Analytics": {
        "icon": "△",
        "questions": [
            "What's the department distribution?",
            "Show me leave trends by month",
            "Which department has the most employees?",
        ],
    },
}


def render_sidebar():
    with st.sidebar:
        # Brand
        st.markdown("""
        <div style="padding: 0.5rem 0 1.2rem 0; border-bottom: 1px solid #1e1e2e; margin-bottom: 1.2rem;">
            <div style="font-size:0.65rem; font-weight:600; letter-spacing:0.14em; text-transform:uppercase; color:#3b82f6; margin-bottom:0.25rem;">HR Streamline</div>
            <div style="font-size:0.75rem; color:#475569;">AI Query Interface</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<span class="section-label">Sample Queries</span>', unsafe_allow_html=True)

        for cat_name, cat_data in CATEGORIES.items():
            with st.expander(f"{cat_data['icon']}  {cat_name}"):
                for i, q in enumerate(cat_data["questions"]):
                    if st.button(q, key=f"ex_{cat_name}_{i}"):
                        st.session_state.user_question = q
                        st.rerun()

        st.divider()

        # DB status
        st.markdown('<span class="section-label">Database</span>', unsafe_allow_html=True)
        stats = get_database_stats()
        if stats:
            st.markdown(f"""
            <div style="background:#0d0d14; border:1px solid #1e1e2e; border-radius:6px; padding:0.75rem 1rem;">
                <div style="display:flex; align-items:center; margin-bottom:0.4rem;">
                    <span class="status-dot"></span>
                    <span style="font-size:0.72rem; color:#4ade80; font-weight:500;">Connected</span>
                </div>
                <div style="font-family:'IBM Plex Mono',monospace; font-size:0.65rem; color:#374151;">
                    PostgreSQL · {stats['last_updated']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        # History controls
        if st.session_state.get("query_history"):
            total = len(st.session_state.query_history)
            st.markdown(f'<span class="section-label">History · {total} queries</span>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Clear", key="clear_hist"):
                    st.session_state.query_history = []
                    st.rerun()
            with col2:
                history_json = export_history()
                if history_json:
                    st.download_button(
                        "Export",
                        history_json,
                        file_name=f"queries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        key="export_hist",
                    )

        # Powered-by footer
        st.markdown("""
        <div style="position:absolute; bottom:1.5rem; left:1rem; right:1rem;">
            <div style="font-size:0.62rem; color:#1e293b; text-align:center; letter-spacing:0.06em;">
                POWERED BY GEMINI AI · LANGCHAIN
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────
def main():
    load_query_history()
    render_sidebar()

    # ── Page header ──
    st.markdown("""
    <div class="page-header">
        <div class="page-header-left">
            <div class="page-header-icon">⬡</div>
            <div>
                <p class="page-header-title">HR Query Assistant</p>
                <p class="page-header-subtitle">Natural language interface to your HR database</p>
            </div>
        </div>
        <span class="page-header-badge">● Live</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Query input ──
    st.markdown('<span class="section-label">Natural Language Query</span>', unsafe_allow_html=True)

    if "user_question" not in st.session_state:
        st.session_state.user_question = ""

    user_question = st.text_area(
        "Enter your query:",
        value=st.session_state.user_question,
        placeholder="e.g.  Show me all employees in Engineering with their leave balances",
        height=110,
        label_visibility="collapsed",
    )

    if user_question != st.session_state.user_question:
        st.session_state.user_question = user_question

    # ── Action row ──
    c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
    with c1:
        run_query = st.button("⬡  Execute Query", type="primary", use_container_width=True)
    with c2:
        if st.button("Clear", use_container_width=True):
            st.session_state.user_question = ""
            st.rerun()
    with c3:
        if st.button("Suggest", use_container_width=True):
            hints = [
                "Try: employee counts by department",
                "Try: leave balance trends",
                "Try: today's attendance summary",
            ]
            st.info(hints[len(st.session_state.query_history) % len(hints)])
    with c4:
        if st.button("Random", use_container_width=True):
            import random
            all_q = [q for c in CATEGORIES.values() for q in c["questions"]]
            st.session_state.user_question = random.choice(all_q)
            st.rerun()

    # ── Execution ──
    if run_query and user_question.strip():
        if not os.environ.get("GOOGLE_API_KEY"):
            st.markdown("""
            <div class="error-card">
                <div class="error-card-title">Configuration Error</div>
                <div class="error-card-body">GOOGLE_API_KEY environment variable is not set.
                Please configure it before running queries.</div>
            </div>
            """, unsafe_allow_html=True)
            return

        progress_bar = st.progress(0)
        status = st.empty()

        try:
            status.markdown('<span style="font-size:0.78rem; color:#64748b;">Initializing connection…</span>', unsafe_allow_html=True)
            progress_bar.progress(15)

            chain = initialize_chain()
            if not chain:
                st.error("Failed to initialize database connection.")
                return

            status.markdown('<span style="font-size:0.78rem; color:#64748b;">Translating to SQL…</span>', unsafe_allow_html=True)
            progress_bar.progress(45)

            start = time.time()
            result = chain.invoke({"query": user_question})
            elapsed = round(time.time() - start, 2)

            if isinstance(result, dict):
                answer = result.get("result", result.get("answer", str(result)))
            else:
                answer = str(result)

            status.markdown('<span style="font-size:0.78rem; color:#4ade80;">Query completed</span>', unsafe_allow_html=True)
            progress_bar.progress(100)
            time.sleep(0.4)
            progress_bar.empty()
            status.empty()

            # ── Result card ──
            st.markdown(f"""
            <div class="result-card">
                <div class="result-card-header">
                    <span class="result-card-tag">Query Result</span>
                </div>
                <div class="result-card-body">{answer}</div>
            </div>
            """, unsafe_allow_html=True)

            # ── Metrics row ──
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Execution Time", f"{elapsed}s")
            with m2:
                st.metric("Query Length", f"{len(user_question)} chars")
            with m3:
                st.metric("Response Size", f"{len(answer)} chars")

            # ── Feedback ──
            st.markdown('<span class="section-label" style="margin-top:1rem; display:block;">Feedback</span>', unsafe_allow_html=True)
            st.markdown("""
            <div class="fb-btn-row">
                <button class="fb-btn" title="This was helpful">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none"
                        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M7 10v12"/>
                        <path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2a3.13 3.13 0 0 1 3 3.88Z"/>
                    </svg>
                    Helpful
                </button>
                <button class="fb-btn" title="This needs improvement">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none"
                        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M17 14V2"/>
                        <path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22a3.13 3.13 0 0 1-3-3.88Z"/>
                    </svg>
                    Needs Improvement
                </button>
            </div>
            """, unsafe_allow_html=True)

            # ── Save to history ──
            st.session_state.query_history.append({
                "timestamp": datetime.now().isoformat(),
                "question": user_question,
                "answer": answer,
                "processing_time": elapsed,
            })

        except Exception as e:
            progress_bar.empty()
            status.empty()
            st.markdown(f"""
            <div class="error-card">
                <div class="error-card-title">Execution Error</div>
                <div class="error-card-body">{str(e)}</div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("Diagnostic Details"):
                st.code(str(e), language="text")
                st.markdown("""
**Checklist**
1. Verify database is reachable and credentials are correct
2. Confirm `GOOGLE_API_KEY` is exported in your environment
3. Rephrase the question using simpler terms
4. Use one of the example queries from the sidebar
5. Restart the Streamlit server and try again
                """)

    elif run_query:
        st.warning("Please enter a question before executing.")

    # ── Query History ──
    if st.session_state.query_history:
        st.markdown("---")

        total = len(st.session_state.query_history)
        avg_t = sum(q.get("processing_time", 0) for q in st.session_state.query_history) / total

        st.markdown('<span class="section-label">Recent History</span>', unsafe_allow_html=True)

        hm1, hm2 = st.columns(2)
        with hm1:
            st.metric("Total Queries", total)
        with hm2:
            st.metric("Avg Execution Time", f"{avg_t:.2f}s")

        with st.expander(f"Query Log  ·  {min(10, total)} most recent", expanded=False):
            for i, entry in enumerate(reversed(st.session_state.query_history[-10:])):
                idx = total - i
                ts = entry.get("timestamp", "")[:19].replace("T", " ")
                pt = entry.get("processing_time", 0)
                st.markdown(f"""
                <div class="history-item">
                    <div class="history-q"><span>#{idx}</span>  {entry['question']}</div>
                    <div class="history-a">{entry['answer']}</div>
                    <div class="history-meta">
                        <span class="history-meta-item">⏱ {pt}s</span>
                        <span class="history-meta-item">🕐 {ts}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Tips footer ──
    st.markdown("---")
    st.markdown('<span class="section-label">Usage Tips</span>', unsafe_allow_html=True)
    st.markdown("""
    <div class="tips-grid">
        <div class="tip-card">
            <div class="tip-title">Be Specific</div>
            <div class="tip-body">Instead of "show employees", try "show all active employees with their department and leave balance".</div>
        </div>
        <div class="tip-card">
            <div class="tip-title">Natural Language</div>
            <div class="tip-body">Ask as you would a colleague — the AI handles SQL translation automatically.</div>
        </div>
        <div class="tip-card">
            <div class="tip-title">Rephrase if Needed</div>
            <div class="tip-body">If a result seems off, try rewording or use the Suggest button for query ideas.</div>
        </div>
        <div class="tip-card">
            <div class="tip-title">Use Examples</div>
            <div class="tip-body">Browse the sidebar for curated queries organized by category to get started quickly.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; padding:2rem 0 0.5rem; font-size:0.65rem; color:#1e293b; letter-spacing:0.1em;">
        HR STREAMLINE · AI QUERY INTERFACE · BUILT WITH GEMINI &amp; LANGCHAIN
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()