import streamlit as st

# ----{ Skip Conditions }----
def get_skip_conditions(cols: list):
    cols_ = st.columns(cols)
    cols_[0].markdown("**:no_entry: Skip filters**")
    cols_[1].text_area(label=":x: Company 'About' bad keywords", placeholder="(Comma-Separated): e.g: Crossover, ACCENTURE", key="bad_words")
    cols_[1].text_area(label=":white_check_mark: Good exceptions", placeholder="(Comma-Separated): e.g:, If any good words in their 'About Company' or Leave blank if not applicable", key="good_words")
    cols_[1].text_area(label=":x: Job description bad keywords", placeholder="(Comma-Separated): e.g: polygraph, US Citizenship, Security Clearance, etc. Leave blank if not applicable", key="job_desc_bad")

# ----{ Security & Education Filters }----
def get_security_and_education_filters(cols: list):
    cols_ = st.columns(cols)
    cols_[0].markdown("**:closed_lock_with_key: Security & Education**")
    cols_[1].checkbox(label="Do you have Security Clearance?", value=False, key="security_clearance")
    cols_[2].checkbox(label="Do you have a Master's Degree?", value=True, key="has_masters")
    cols_[3].number_input(label="Years of Experience", min_value=0, step=1, value=3, key="current_experience")


# ----{ Main Job Settings Aggregator }----
def get_ext_job_settings():
    cols_base = [3, 8]
    cols_quad = [3, 3, 3, 2]
    get_skip_conditions(cols_base)
    get_security_and_education_filters(cols_quad)
    
    return ["bad_words", "good_words", "job_desc_bad", 
            "security_clearance", "has_masters", "current_experience"]