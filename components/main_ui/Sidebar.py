import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ---{ Application Selector }---
def select_application(disabled=False):
    app_descriptions = {
        "PDF Summarizer": "Summarize legal or research-oriented PDF documents.",
        "LinkedIn Jobs Apply": "Automatically apply to LinkedIn job postings (non-Easy Apply only).",
        "Data Analyst": "Analyze and clean data from uploaded CSV or Excel files."
    }
    
    with st.sidebar:
        st.subheader(body="Select an Application:", divider=True)
        st.selectbox(
            label="Select an Application:",
            options=list(app_descriptions.keys()),
            key="app_selector",
            disabled=disabled,
            label_visibility="collapsed"
        )
        st.caption(app_descriptions[st.session_state.app_selector])

        #---{ Visualize usage history }---
        if "usage_history" in st.session_state:
            get_api(usage_history=st.session_state.usage_history)

# ---{ Together AI API Key Entry }---
def get_api(usage_history: int):
    # Get last 7 days (including today)
    today = datetime.today()
    last_7_days = [(today - timedelta(days=i)).date() for i in range(6, -1, -1)]

    # Extract usage or fill 0 if missing
    daily_usage = []
    date_labels = []
    for date in last_7_days:
        date_str = date.isoformat()
        usage = usage_history.get(date_str, 0)
        daily_usage.append(usage)
        date_labels.append(date.strftime('%a %d'))

    # Total usage across the week
    total_usage = sum(usage_history.values())
    date_labels.append("Total")
    daily_usage.append(total_usage)
    
    with st.sidebar:
        #----{ Display total API usage }----
        if total_usage in range(950,1000):
            st.toast(":warning: You are close to the API usage limit of 1000 requests.")
        
        # If usage exceeds 1000, show API key input
        elif total_usage > 1000:
            st.subheader("🔑 Together AI API key")
            st.text_input(label="You have exhausted usage", key="user_api_key", type="password")
        else:
            #----{ Display daily usage history }----
            st.subheader("🔍 API Usage History")
            fig = go.Figure()
            fig.add_trace(go.Bar(x=date_labels, y=daily_usage, name='Daily Usage', marker_color='blue'))

            #----{ Add cut-off line at 1000 requests }----
            fig.add_shape(type="line", x0=-0.5, x1=len(date_labels) - 0.5, y0=1000, y1=1000, 
                          line=dict(color="red", width=2, dash="dash"))
            
            y_max = max(1000 if total_usage >= 400 else 0, max(daily_usage) + 50)

            if y_max > 300: y_max = 1000
            fig.update_layout( title="API Usage History (Cut-off: 1000 requests)", 
                              xaxis_title="Date", yaxis_title="Usage Count", 
                              yaxis=dict(range=[0, y_max]),
                              height=300, showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
            
            st.plotly_chart(fig, use_container_width=True)