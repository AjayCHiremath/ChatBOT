import streamlit as st

# ----{ Search Terms Input }----
def get_search_terms_input(cols: list):
    cols_search = st.columns(cols)
    cols_search[0].markdown("**:mag: Enter your job search keywords**")
    cols_search[1].text_area(
        label="Search Terms",
        placeholder="e.g., Software Engineer, Python Developer, QA Tester, etc. (Comma Seperated)",
        label_visibility="collapsed",
        key="search_terms"
    )

# ----{ Search Location Input }----
def get_search_location_input(cols: list):
    cols_location = st.columns(cols)
    cols_location[0].markdown("**:round_pushpin: Enter a location**")
    cols_location[1].text_area(
        label="Search Location",
        placeholder='e.g., "", "India", "United States", "Chicago, IL", "90001, Los Angeles, CA". (Only one)',
        label_visibility="collapsed",
        key="search_location"
    )

# ----{ Switch & Randomization Settings }----
def get_switch_and_random_settings(cols: list):
    cols_settings = st.columns(cols)
    cols_settings[0].markdown("**:repeat: Number of applications per search before switching**")
    cols_settings[1].number_input(
        label="Jobs per search term",
        min_value=7, max_value=100, value=50,
        key="switch_number"
    )
    cols_settings[2].markdown("**:twisted_rightwards_arrows: Randomize the order of search terms?**")
    cols_settings[3].checkbox("Randomize", value=False, key="randomize")

# ----{ Sort By Filter }----
def get_sort_by_filter(cols: list):
    cols_ = st.columns(cols)
    cols_[0].markdown("**:card_index_dividers: Sort job results by**")
    cols_[1].selectbox(label="Sort By", options=["", "Most recent", "Most relevant"], index=1, key="sort_by")

# ----{ Date Posted Filter }----
def get_date_posted_filter(cols: list):
    cols_ = st.columns(cols)
    cols_[0].markdown("**:calendar: Date job was posted**")
    cols_[1].selectbox(label="Date Posted", options=["", "Any time", "Past month", "Past week", "Past 24 hours"], 
                                     index=3, key="date_posted")

# ----{ Salary Filter }----
def get_salary_filter(cols: list):
    cols_ = st.columns(cols)
    cols_[0].markdown("**:moneybag: Minimum salary filter**")
    cols_[1].slider(label="Salary", value=0, min_value=0, max_value=100000, step=10000, key="salary")

# ----{ Experience Level Filter }----
def get_experience_level_filter(cols: list):
    cols_ = st.columns(cols)
    cols_[0].markdown("**:mortar_board: Select experience levels**")
    cols_[1].multiselect(label="Experience Level", options=["Internship", "Entry level", "Associate", "Mid-Senior level", 
                                                    "Director", "Executive"], key="experience_level")

# ----{ Job Type Filter }----
def get_job_type_filter(cols: list):
    cols_ = st.columns(cols)
    cols_[0].markdown("**:briefcase: Select job types**")
    cols_[1].multiselect(label="Job Type", options=["Full-time", "Part-time", "Contract", 
                                                               "Temporary", "Volunteer", "Internship", "Other"],
                                                               key="job_type")

# ----{ Work Environment Filter }----
def get_workplace_type_filter(cols: list):
    cols_ = st.columns(cols)
    cols_[0].markdown("**:office: Select work environment**")
    cols_[1].multiselect(label="Work Environment", options=["On-site", "Remote", "Hybrid"],
                                          key="workplace_type")

# ----{ Company Preferences }----
def get_preferred_companies_input(cols: list):
    cols_ = st.columns(cols)
    cols_[0].markdown("**:department_store: Preferred Companies**")
    cols_[1].text_area(label=":building_construction: Companies", placeholder="(Pipe | Seperated): e.g., Google| Meta| Microsoft", key="preferred_companies")

# ----{ Additional Dynamic Filters }----
def get_dynamic_filters(cols: list):
    cols_ = st.columns(cols)
    cols_[0].markdown("**:file_folder: Additional Dynamic Filters**")
    cols_[1].text_area(label=":cityscape: City Locations", placeholder="(Comma Seperated): e.g., Bangalore, London. Leave blank if not applicable or fill based on country selected.", key="location")
    cols_[1].text_area(label=":factory: Industries", placeholder="(Pipe | Seperated): e.g., IT Services| Financail| Retail. Leave blank if not applicable.", key="industry")
    cols_[1].text_area(label=":bar_chart: Job Functions", placeholder="(Pipe | Seperated): e.g., Finance| Marketing| PM. Leave blank if not applicable.", key="job_function")
    cols_[1].text_area(label=":busts_in_silhouette: Job Titles", placeholder="(Comma Seperated): e.g., Software Engineer, Nurse. Leave blank if not applicable.", key="job_titles")
    cols_[1].text_area(label=":gift: Benefits", placeholder="(Comma Seperated): e.g., Medical, Vision, Dental, Pension. Leave blank if not applicable.", key="benefits")
    cols_[1].text_area(label=":handshake: Commitments", placeholder="(Comma Seperated): e.g., DEI, Sustainability. Leave blank if not applicable.", key="commitments")

# ----{ Application Preferences }----
def get_application_preferences(cols: list):
    cols_ = st.columns(cols)
    cols_[0].markdown("**:interrobang: Application Preferences**")
    cols_[1].checkbox(label="Under 10 Applicants", value=False, key="under_10")
    cols_[2].checkbox(label="In Your Network", value=False, key="in_network")
    cols_[3].checkbox(label="Fair Chance Employer", value=False, key="fair_chance")


# ----{ Main Job Settings Aggregator }----
def get_job_settings():
    cols_base = [3, 8]
    cols_quad = [3, 3, 3, 2]
    get_search_terms_input(cols_base)
    get_search_location_input(cols_base)
    get_switch_and_random_settings(cols_quad)
    get_sort_by_filter(cols_base)
    get_date_posted_filter(cols_base)
    get_salary_filter(cols_base)
    get_experience_level_filter(cols_base)
    get_job_type_filter(cols_base)
    get_workplace_type_filter(cols_base)
    get_preferred_companies_input(cols_base)
    get_dynamic_filters(cols_base)
    get_application_preferences(cols_quad)

    return [
        "search_terms", "search_location", "switch_number", "randomize", "sort_by", 
        "date_posted", "salary", "experience_level", "job_type", "workplace_type", 
        "preferred_companies", "location", "industry", "job_function", "job_titles", 
        "benefits", "commitments", "under_10", "in_network", "fair_chance"
    ]