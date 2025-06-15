from spacy.matcher import Matcher
import pandas as pd
import re
import streamlit as st

from utils.logger.EventLogger import log_message

# ---{ Chunk job descriptions into labeled sections based on heading patterns }---
def data_chunking(jobs_data, nlp, section_map, log_base="logs/job_application_logs/logs_text/", echo=False):
    if st.session_state.get("applying_jobs_ext", False):
        log_message("📦 Starting data chunking process...", log_file=log_base, echo=echo)

        # ---{ Setup spaCy Matcher with section headings }---
        matcher = Matcher(nlp.vocab)
        for section, headings in section_map.items():

            if st.session_state.get("applying_jobs_ext", False) is False:
                return None  # Exit if applying_jobs flag is off:
            
            for heading in headings:
                if st.session_state.get("applying_jobs_ext", False) is False:
                    return None  # Exit if applying_jobs flag is off:
                
                pattern = [{"LOWER": token.lower()} for token in heading.split()]
                matcher.add(section, [pattern])
                
        log_message("🧠 Matcher initialized with provided section headings.", log_file=log_base, echo=echo)

        # ---{ Extract sections from a single job description }---
        def extract_sections(text):
            if not isinstance(text, str) or not text.strip():
                return {}

            doc = nlp(text)
            matches = matcher(doc)
            matches = sorted(matches, key=lambda x: x[1])  # Sort by position

            sections = {}
            for i, (match_id, start, end) in enumerate(matches):
                if st.session_state.get("applying_jobs_ext", False) is False:
                    return None  # Exit if applying_jobs flag is off:
                label = nlp.vocab.strings[match_id]
                start_char = doc[start].idx
                end_char = doc[matches[i + 1][1]].idx if i + 1 < len(matches) else len(text)

                # Skip if the section is empty or too short
                if end_char - start_char < 10:
                    continue

                section_text = text[start_char:end_char].strip()

                if label in sections:
                    sections[label] += "\n" + section_text
                else:
                    sections[label] = section_text

            return sections

        # ---{ Apply section extraction to each job description }---
        parsed_sections = jobs_data["Job Description"].fillna("").apply(extract_sections)
        log_message("🧾 Section parsing completed for all job descriptions.", log_file=log_base, echo=echo)

        # ---{ Normalize parsed data into a flat DataFrame }---
        parsed_df_reset = pd.json_normalize(parsed_sections).reset_index(drop=True)
        jobs_data_reset = jobs_data.reset_index(drop=True)

        # ---{ Combine parsed sections with original DataFrame }---
        final_df = pd.concat([jobs_data_reset, parsed_df_reset], axis=1)

        log_message("✔ Data chunking complete. Parsed sections added to the dataset.", log_file=log_base, echo=echo)

        return final_df
    else:
        # If applying_jobs flag is off, return the original DataFrame
        log_message("🛑 Applying jobs flag is off. Returning original DataFrame without chunking.", log_file=log_base, echo=echo)
        return None

# ---{ Clean job data by removing duplicates and filtering bad entries }---
def data_cleaning(jobs_data, job_settings, log_base="logs/job_application_logs/logs_text/", echo=False):
    if st.session_state.get("applying_jobs_ext", False):
        # ---{ Remove duplicate rows }---
        log_message(" Removing duplicate rows based on Job ID and Application Link...", log_file=log_base, echo=echo)
        before_dedup = len(jobs_data)
        jobs_data = jobs_data.drop_duplicates(subset=["Job ID", "Application Link"])
        after_dedup = len(jobs_data)
        log_message(f"🧹 Removed {before_dedup - after_dedup} duplicate rows based on Job ID and Application Link.", log_file=log_base, echo=echo)

        # ---{ Prepare filtering word lists }---
        bad_companies = [c.strip().lower() for c in job_settings.get("bad_words", "").split(",") if c.strip()]
        bad_phrases = [p.strip() for p in job_settings.get("job_desc_bad", "").split(",") if p.strip()]

        # ---{ Filter out jobs from blacklisted companies }---
        log_message("🔍 Filtering out jobs where you don't want you apply...", log_file=log_base, echo=echo)
        if bad_companies:
            before_filter = len(jobs_data)
            jobs_data = jobs_data[~jobs_data["Company Name"].astype(str).str.lower().isin(bad_companies)]
            after_filter = len(jobs_data)
            log_message(f"🚫 Removed {before_filter - after_filter} jobs from bad companies.", log_file=log_base, echo=echo)

        # ---{ Filter out jobs containing bad phrases in description }---
        log_message("🔍 Filtering out jobs with bad phrases in description...", log_file=log_base, echo=echo)
        if bad_phrases:
            pattern = '|'.join([re.escape(p) for p in bad_phrases])
            before_filter = len(jobs_data)
            jobs_data = jobs_data[~jobs_data["Job Description"].str.contains(pattern, case=False, na=False)]
            after_filter = len(jobs_data)
            log_message(f"📄 Removed {before_filter - after_filter} jobs with bad phrases in description.", log_file=log_base, echo=echo)

        return jobs_data
    else:       
        # If applying_jobs flag is off, return the original DataFrame
        log_message("🛑 Applying jobs flag is off. Returning original DataFrame without cleaning.", log_file=log_base, echo=echo)
        return None