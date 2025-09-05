import json
import os
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

SUBJECTS_FILE = 'subjects.json'
BASE_URL = "https://dynamicpapers.com/wp-content/uploads/2015/09/"

# Helper functions to manage the JSON data
def load_subjects():
    if not os.path.exists(SUBJECTS_FILE):
        return {}
    with open(SUBJECTS_FILE, 'r') as f:
        return json.load(f)

def save_subjects(subjects):
    with open(SUBJECTS_FILE, 'w') as f:
        json.dump(subjects, f, indent=2)

def generate_urls(subject_code, start_year, end_year, papers_dict, variants, sessions, types):
    years = list(range(int(start_year), int(end_year) + 1))
    results = {}

    for year in sorted(years, reverse=True):
        year_str = str(year)
        results[year_str] = {}
        year_short = year_str[2:]
        
        for session_code in ['w', 's', 'm']:
            if session_code not in sessions: continue
            if year == datetime.now().year and session_code == 'w' and datetime.now().month < 10: continue

            session_map = {'w': "Oct/Nov", 's': "May/June", 'm': "Feb/March"}
            session_name = f"{session_map[session_code]} {year}"
            
            # Pass more data to the template for ER/GT links
            results[year_str][session_name] = {
                'code': session_code,
                'short_code': f"{session_code}{year_short}", # e.g., s25
                'papers': {}
            }

            # Loop through the papers dictionary (with descriptions)
            for paper_num, paper_desc in papers_dict.items():
                paper_key = f"Paper {paper_num}: {paper_desc}"
                paper_data = results[year_str][session_name]['papers'][paper_key] = {'qp': [], 'ms': []}

                for variant_num in variants:
                    if session_code == 'm' and variant_num != '2': continue
                    paper_variant = f"{paper_num}{variant_num}"

                    if 'qp' in types:
                        filename = f"{subject_code}_{session_code}{year_short}_qp_{paper_variant}.pdf"
                        paper_data['qp'].append(f"{BASE_URL}{filename}")
                    
                    if 'ms' in types:
                        filename = f"{subject_code}_{session_code}{year_short}_ms_{paper_variant}.pdf"
                        paper_data['ms'].append(f"{BASE_URL}{filename}")
    return results

@app.route('/', methods=['GET', 'POST'])
def index():
    subjects = load_subjects()
    if request.method == 'POST':
        year_range = request.form.get('year_range', '2020-2025').split('-')
        start_year, end_year = year_range[0], year_range[1]
        variants = ['1', '2', '3'] if request.form.get('variants_all') else request.form.getlist('variants')
        sessions = ['w', 's', 'm'] if request.form.get('sessions_all') else request.form.getlist('sessions')
        
        all_results = {}
        for code, data in subjects.items():
            all_results[code] = {
                "name": data["name"],
                "subject_code": code,
                "base_url": BASE_URL,
                "links": generate_urls(code, start_year, end_year, data["papers"], variants, sessions, ['qp', 'ms'])
            }
        return render_template('index.html', results=all_results, submitted=True, subjects=subjects)

    return render_template('index.html', results=None, submitted=False, subjects=subjects)

@app.route('/add_subject', methods=['POST'])
def add_subject():
    subjects = load_subjects()
    
    code = request.form['code']
    name = request.form['name']
    papers_str = request.form['papers']
    
    # Parse the papers string (e.g., "1:Pure 1, 4:Mechanics") into a dictionary
    papers_dict = {}
    for part in papers_str.split(','):
        if ':' in part:
            num, desc = part.split(':', 1)
            papers_dict[num.strip()] = desc.strip()
            
    if code and name and papers_dict:
        subjects[code] = {"name": name, "papers": papers_dict}
        save_subjects(subjects)
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)