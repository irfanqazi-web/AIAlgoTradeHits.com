"""
MarketingAI - Multi-User Social Media Content Creation Platform
Backend API with Flask, BigQuery, and Firebase Auth
"""

import os
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from google.cloud import bigquery
from google.oauth2 import service_account
import jwt

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Register AI Blueprint for new AI endpoints (Gemini 2.5, Imagen 4, Veo 3, Lyria 2, Agentic AI)
try:
    from ai_routes import ai_bp
    app.register_blueprint(ai_bp)
    AI_BLUEPRINT_AVAILABLE = True
    print('AI Blueprint registered successfully at /api/ai/*')
except ImportError as e:
    AI_BLUEPRINT_AVAILABLE = False
    print(f'Warning: AI Blueprint not available: {e}')

# Configuration
PROJECT_ID = os.environ.get('PROJECT_ID', 'aialgotradehits')
DATASET_ID = 'marketingai_data'
SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(32))
TOKEN_EXPIRY_HOURS = 24

# Initialize BigQuery client
try:
    client = bigquery.Client(project=PROJECT_ID)
except Exception as e:
    print(f"BigQuery client initialization error: {e}")
    client = None


def get_password_hash(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_token(user_id, email, role='user'):
    """Generate JWT token"""
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    """Decorator for protected routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token missing'}), 401

        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401

        request.user = payload
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Decorator for admin-only routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token missing'}), 401

        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401

        if payload.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        request.user = payload
        return f(*args, **kwargs)
    return decorated


# ==================== AUTH ROUTES ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.json
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        name = data.get('name', '')
        company = data.get('company', '')

        if not email or not password or not name:
            return jsonify({'error': 'Email, password, and name are required'}), 400

        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400

        # Check if user exists
        check_query = f"""
            SELECT email FROM `{PROJECT_ID}.{DATASET_ID}.users`
            WHERE email = @email
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("email", "STRING", email)]
        )
        results = list(client.query(check_query, job_config=job_config).result())

        if results:
            return jsonify({'error': 'Email already registered'}), 400

        # Create user
        user_id = secrets.token_hex(16)
        password_hash = get_password_hash(password)
        created_at = datetime.utcnow().isoformat()

        insert_query = f"""
            INSERT INTO `{PROJECT_ID}.{DATASET_ID}.users`
            (user_id, email, password_hash, name, company, role, created_at, last_login, is_active)
            VALUES (@user_id, @email, @password_hash, @name, @company, 'user', @created_at, @created_at, TRUE)
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                bigquery.ScalarQueryParameter("email", "STRING", email),
                bigquery.ScalarQueryParameter("password_hash", "STRING", password_hash),
                bigquery.ScalarQueryParameter("name", "STRING", name),
                bigquery.ScalarQueryParameter("company", "STRING", company),
                bigquery.ScalarQueryParameter("created_at", "STRING", created_at),
            ]
        )
        client.query(insert_query, job_config=job_config).result()

        token = generate_token(user_id, email, 'user')

        return jsonify({
            'message': 'Registration successful',
            'token': token,
            'user': {
                'user_id': user_id,
                'email': email,
                'name': name,
                'company': company,
                'role': 'user'
            }
        }), 201

    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.json
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')

        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400

        password_hash = get_password_hash(password)

        query = f"""
            SELECT user_id, email, name, company, role, is_active
            FROM `{PROJECT_ID}.{DATASET_ID}.users`
            WHERE email = @email AND password_hash = @password_hash
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("email", "STRING", email),
                bigquery.ScalarQueryParameter("password_hash", "STRING", password_hash),
            ]
        )
        results = list(client.query(query, job_config=job_config).result())

        if not results:
            return jsonify({'error': 'Invalid email or password'}), 401

        user = results[0]

        if not user.is_active:
            return jsonify({'error': 'Account is disabled'}), 403

        # Update last login
        update_query = f"""
            UPDATE `{PROJECT_ID}.{DATASET_ID}.users`
            SET last_login = @now
            WHERE user_id = @user_id
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("now", "STRING", datetime.utcnow().isoformat()),
                bigquery.ScalarQueryParameter("user_id", "STRING", user.user_id),
            ]
        )
        client.query(update_query, job_config=job_config).result()

        token = generate_token(user.user_id, user.email, user.role)

        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'user_id': user.user_id,
                'email': user.email,
                'name': user.name,
                'company': user.company,
                'role': user.role
            }
        })

    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user():
    """Get current user info"""
    try:
        query = f"""
            SELECT user_id, email, name, company, role, created_at, last_login
            FROM `{PROJECT_ID}.{DATASET_ID}.users`
            WHERE user_id = @user_id
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("user_id", "STRING", request.user['user_id']),
            ]
        )
        results = list(client.query(query, job_config=job_config).result())

        if not results:
            return jsonify({'error': 'User not found'}), 404

        user = results[0]
        return jsonify({
            'user_id': user.user_id,
            'email': user.email,
            'name': user.name,
            'company': user.company,
            'role': user.role,
            'created_at': str(user.created_at),
            'last_login': str(user.last_login)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== BRANDS ROUTES ====================

@app.route('/api/brands', methods=['GET'])
@token_required
def get_brands():
    """Get user's brands"""
    try:
        query = f"""
            SELECT brand_id, name, description, primary_color, secondary_color,
                   accent_color, text_color, logo_url, theme, created_at
            FROM `{PROJECT_ID}.{DATASET_ID}.brands`
            WHERE user_id = @user_id
            ORDER BY created_at DESC
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("user_id", "STRING", request.user['user_id']),
            ]
        )
        results = list(client.query(query, job_config=job_config).result())

        brands = []
        for row in results:
            brands.append({
                'brand_id': row.brand_id,
                'name': row.name,
                'description': row.description,
                'primary_color': row.primary_color,
                'secondary_color': row.secondary_color,
                'accent_color': row.accent_color,
                'text_color': row.text_color,
                'logo_url': row.logo_url,
                'theme': row.theme,
                'created_at': str(row.created_at)
            })

        return jsonify({'brands': brands})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/brands', methods=['POST'])
@token_required
def create_brand():
    """Create a new brand"""
    try:
        data = request.json
        brand_id = secrets.token_hex(8)

        insert_query = f"""
            INSERT INTO `{PROJECT_ID}.{DATASET_ID}.brands`
            (brand_id, user_id, name, description, primary_color, secondary_color,
             accent_color, text_color, logo_url, theme, created_at, updated_at)
            VALUES (@brand_id, @user_id, @name, @description, @primary_color,
                    @secondary_color, @accent_color, @text_color, @logo_url, @theme, @now, @now)
        """
        now = datetime.utcnow().isoformat()
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("brand_id", "STRING", brand_id),
                bigquery.ScalarQueryParameter("user_id", "STRING", request.user['user_id']),
                bigquery.ScalarQueryParameter("name", "STRING", data.get('name', '')),
                bigquery.ScalarQueryParameter("description", "STRING", data.get('description', '')),
                bigquery.ScalarQueryParameter("primary_color", "STRING", data.get('primary_color', '#667eea')),
                bigquery.ScalarQueryParameter("secondary_color", "STRING", data.get('secondary_color', '#764ba2')),
                bigquery.ScalarQueryParameter("accent_color", "STRING", data.get('accent_color', '#f5576c')),
                bigquery.ScalarQueryParameter("text_color", "STRING", data.get('text_color', '#2c3e50')),
                bigquery.ScalarQueryParameter("logo_url", "STRING", data.get('logo_url', '')),
                bigquery.ScalarQueryParameter("theme", "STRING", data.get('theme', 'modern')),
                bigquery.ScalarQueryParameter("now", "STRING", now),
            ]
        )
        client.query(insert_query, job_config=job_config).result()

        return jsonify({
            'message': 'Brand created successfully',
            'brand_id': brand_id
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/brands/<brand_id>', methods=['PUT'])
@token_required
def update_brand(brand_id):
    """Update a brand"""
    try:
        data = request.json

        update_query = f"""
            UPDATE `{PROJECT_ID}.{DATASET_ID}.brands`
            SET name = @name, description = @description, primary_color = @primary_color,
                secondary_color = @secondary_color, accent_color = @accent_color,
                text_color = @text_color, logo_url = @logo_url, theme = @theme, updated_at = @now
            WHERE brand_id = @brand_id AND user_id = @user_id
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("brand_id", "STRING", brand_id),
                bigquery.ScalarQueryParameter("user_id", "STRING", request.user['user_id']),
                bigquery.ScalarQueryParameter("name", "STRING", data.get('name', '')),
                bigquery.ScalarQueryParameter("description", "STRING", data.get('description', '')),
                bigquery.ScalarQueryParameter("primary_color", "STRING", data.get('primary_color', '')),
                bigquery.ScalarQueryParameter("secondary_color", "STRING", data.get('secondary_color', '')),
                bigquery.ScalarQueryParameter("accent_color", "STRING", data.get('accent_color', '')),
                bigquery.ScalarQueryParameter("text_color", "STRING", data.get('text_color', '')),
                bigquery.ScalarQueryParameter("logo_url", "STRING", data.get('logo_url', '')),
                bigquery.ScalarQueryParameter("theme", "STRING", data.get('theme', '')),
                bigquery.ScalarQueryParameter("now", "STRING", datetime.utcnow().isoformat()),
            ]
        )
        client.query(update_query, job_config=job_config).result()

        return jsonify({'message': 'Brand updated successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/brands/<brand_id>', methods=['DELETE'])
@token_required
def delete_brand(brand_id):
    """Delete a brand"""
    try:
        delete_query = f"""
            DELETE FROM `{PROJECT_ID}.{DATASET_ID}.brands`
            WHERE brand_id = @brand_id AND user_id = @user_id
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("brand_id", "STRING", brand_id),
                bigquery.ScalarQueryParameter("user_id", "STRING", request.user['user_id']),
            ]
        )
        client.query(delete_query, job_config=job_config).result()

        return jsonify({'message': 'Brand deleted successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== CONTENT ROUTES ====================

@app.route('/api/content', methods=['GET'])
@token_required
def get_content():
    """Get user's content"""
    try:
        brand_id = request.args.get('brand_id')
        platform = request.args.get('platform')
        status = request.args.get('status')
        limit = int(request.args.get('limit', 50))

        query = f"""
            SELECT content_id, brand_id, platform, content_type, title, body,
                   color_scheme, font_style, slide_count, scheduled_date, status,
                   created_at, updated_at
            FROM `{PROJECT_ID}.{DATASET_ID}.content`
            WHERE user_id = @user_id
        """

        params = [bigquery.ScalarQueryParameter("user_id", "STRING", request.user['user_id'])]

        if brand_id:
            query += " AND brand_id = @brand_id"
            params.append(bigquery.ScalarQueryParameter("brand_id", "STRING", brand_id))

        if platform:
            query += " AND platform = @platform"
            params.append(bigquery.ScalarQueryParameter("platform", "STRING", platform))

        if status:
            query += " AND status = @status"
            params.append(bigquery.ScalarQueryParameter("status", "STRING", status))

        query += f" ORDER BY created_at DESC LIMIT {limit}"

        job_config = bigquery.QueryJobConfig(query_parameters=params)
        results = list(client.query(query, job_config=job_config).result())

        content_list = []
        for row in results:
            content_list.append({
                'content_id': row.content_id,
                'brand_id': row.brand_id,
                'platform': row.platform,
                'content_type': row.content_type,
                'title': row.title,
                'body': row.body,
                'color_scheme': row.color_scheme,
                'font_style': row.font_style,
                'slide_count': row.slide_count,
                'scheduled_date': str(row.scheduled_date) if row.scheduled_date else None,
                'status': row.status,
                'created_at': str(row.created_at),
                'updated_at': str(row.updated_at)
            })

        return jsonify({'content': content_list})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/content', methods=['POST'])
@token_required
def create_content():
    """Create new content"""
    try:
        data = request.json
        content_id = secrets.token_hex(8)
        now = datetime.utcnow().isoformat()

        insert_query = f"""
            INSERT INTO `{PROJECT_ID}.{DATASET_ID}.content`
            (content_id, user_id, brand_id, platform, content_type, title, body,
             color_scheme, font_style, slide_count, scheduled_date, status, created_at, updated_at)
            VALUES (@content_id, @user_id, @brand_id, @platform, @content_type, @title, @body,
                    @color_scheme, @font_style, @slide_count, @scheduled_date, @status, @now, @now)
        """

        scheduled_date = data.get('scheduled_date')

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("content_id", "STRING", content_id),
                bigquery.ScalarQueryParameter("user_id", "STRING", request.user['user_id']),
                bigquery.ScalarQueryParameter("brand_id", "STRING", data.get('brand_id', '')),
                bigquery.ScalarQueryParameter("platform", "STRING", data.get('platform', '')),
                bigquery.ScalarQueryParameter("content_type", "STRING", data.get('content_type', '')),
                bigquery.ScalarQueryParameter("title", "STRING", data.get('title', '')),
                bigquery.ScalarQueryParameter("body", "STRING", data.get('body', '')),
                bigquery.ScalarQueryParameter("color_scheme", "STRING", data.get('color_scheme', '')),
                bigquery.ScalarQueryParameter("font_style", "STRING", data.get('font_style', '')),
                bigquery.ScalarQueryParameter("slide_count", "INT64", int(data.get('slide_count', 1))),
                bigquery.ScalarQueryParameter("scheduled_date", "STRING", scheduled_date),
                bigquery.ScalarQueryParameter("status", "STRING", data.get('status', 'draft')),
                bigquery.ScalarQueryParameter("now", "STRING", now),
            ]
        )
        client.query(insert_query, job_config=job_config).result()

        return jsonify({
            'message': 'Content created successfully',
            'content_id': content_id
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/content/<content_id>', methods=['PUT'])
@token_required
def update_content(content_id):
    """Update content"""
    try:
        data = request.json
        now = datetime.utcnow().isoformat()

        update_query = f"""
            UPDATE `{PROJECT_ID}.{DATASET_ID}.content`
            SET brand_id = @brand_id, platform = @platform, content_type = @content_type,
                title = @title, body = @body, color_scheme = @color_scheme,
                font_style = @font_style, slide_count = @slide_count,
                scheduled_date = @scheduled_date, status = @status, updated_at = @now
            WHERE content_id = @content_id AND user_id = @user_id
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("content_id", "STRING", content_id),
                bigquery.ScalarQueryParameter("user_id", "STRING", request.user['user_id']),
                bigquery.ScalarQueryParameter("brand_id", "STRING", data.get('brand_id', '')),
                bigquery.ScalarQueryParameter("platform", "STRING", data.get('platform', '')),
                bigquery.ScalarQueryParameter("content_type", "STRING", data.get('content_type', '')),
                bigquery.ScalarQueryParameter("title", "STRING", data.get('title', '')),
                bigquery.ScalarQueryParameter("body", "STRING", data.get('body', '')),
                bigquery.ScalarQueryParameter("color_scheme", "STRING", data.get('color_scheme', '')),
                bigquery.ScalarQueryParameter("font_style", "STRING", data.get('font_style', '')),
                bigquery.ScalarQueryParameter("slide_count", "INT64", int(data.get('slide_count', 1))),
                bigquery.ScalarQueryParameter("scheduled_date", "STRING", data.get('scheduled_date')),
                bigquery.ScalarQueryParameter("status", "STRING", data.get('status', 'draft')),
                bigquery.ScalarQueryParameter("now", "STRING", now),
            ]
        )
        client.query(update_query, job_config=job_config).result()

        return jsonify({'message': 'Content updated successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/content/<content_id>', methods=['DELETE'])
@token_required
def delete_content(content_id):
    """Delete content"""
    try:
        delete_query = f"""
            DELETE FROM `{PROJECT_ID}.{DATASET_ID}.content`
            WHERE content_id = @content_id AND user_id = @user_id
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("content_id", "STRING", content_id),
                bigquery.ScalarQueryParameter("user_id", "STRING", request.user['user_id']),
            ]
        )
        client.query(delete_query, job_config=job_config).result()

        return jsonify({'message': 'Content deleted successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== CALENDAR ROUTES ====================

@app.route('/api/calendar', methods=['GET'])
@token_required
def get_calendar():
    """Get calendar entries for a date range"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        brand_id = request.args.get('brand_id')

        query = f"""
            SELECT content_id, brand_id, platform, title, scheduled_date, status
            FROM `{PROJECT_ID}.{DATASET_ID}.content`
            WHERE user_id = @user_id
              AND scheduled_date IS NOT NULL
              AND scheduled_date >= @start_date
              AND scheduled_date <= @end_date
        """

        params = [
            bigquery.ScalarQueryParameter("user_id", "STRING", request.user['user_id']),
            bigquery.ScalarQueryParameter("start_date", "STRING", start_date),
            bigquery.ScalarQueryParameter("end_date", "STRING", end_date),
        ]

        if brand_id:
            query += " AND brand_id = @brand_id"
            params.append(bigquery.ScalarQueryParameter("brand_id", "STRING", brand_id))

        query += " ORDER BY scheduled_date ASC"

        job_config = bigquery.QueryJobConfig(query_parameters=params)
        results = list(client.query(query, job_config=job_config).result())

        entries = []
        for row in results:
            entries.append({
                'content_id': row.content_id,
                'brand_id': row.brand_id,
                'platform': row.platform,
                'title': row.title,
                'scheduled_date': str(row.scheduled_date),
                'status': row.status
            })

        return jsonify({'calendar': entries})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== TEMPLATES ROUTES ====================

@app.route('/api/templates', methods=['GET'])
def get_templates():
    """Get available templates (public)"""
    templates = [
        {
            'id': 'gradient-bold',
            'name': 'Gradient Bold',
            'category': 'Educational Carousels',
            'slides': 5,
            'style': 'stats-focus',
            'preview_colors': ['#667eea', '#764ba2']
        },
        {
            'id': 'minimal-clean',
            'name': 'Minimal Clean',
            'category': 'Educational Carousels',
            'slides': 10,
            'style': 'text-heavy',
            'preview_colors': ['#ffffff', '#f8f9fa']
        },
        {
            'id': 'colorful-fun',
            'name': 'Colorful Fun',
            'category': 'Educational Carousels',
            'slides': 7,
            'style': 'visual-first',
            'preview_colors': ['#f093fb', '#f5576c']
        },
        {
            'id': 'dark-mode',
            'name': 'Dark Mode',
            'category': 'Educational Carousels',
            'slides': 8,
            'style': 'tech',
            'preview_colors': ['#2c3e50', '#1a1a2e']
        },
        {
            'id': 'nature-quotes',
            'name': 'Nature Quotes',
            'category': 'Quote & Inspiration',
            'slides': 1,
            'style': 'quote',
            'preview_colors': ['#11998e', '#38ef7d']
        },
        {
            'id': 'minimal-quote',
            'name': 'Minimal Quote',
            'category': 'Quote & Inspiration',
            'slides': 1,
            'style': 'typography',
            'preview_colors': ['#ffffff', '#f8f9fa']
        },
        {
            'id': 'bold-statement',
            'name': 'Bold Statement',
            'category': 'Quote & Inspiration',
            'slides': 1,
            'style': 'impact',
            'preview_colors': ['#ee0979', '#ff6a00']
        },
        {
            'id': 'numbered-list',
            'name': 'Numbered List',
            'category': 'Tips & Lists',
            'slides': 10,
            'style': 'step-by-step',
            'preview_colors': ['#ffeaa7', '#fdcb6e']
        },
        {
            'id': 'checklist',
            'name': 'Checklist Style',
            'category': 'Tips & Lists',
            'slides': 5,
            'style': 'actionable',
            'preview_colors': ['#a8edea', '#fed6e3']
        },
        {
            'id': 'comparison',
            'name': 'Comparison',
            'category': 'Tips & Lists',
            'slides': 3,
            'style': 'before-after',
            'preview_colors': ['#dfe6e9', '#b2bec3']
        }
    ]
    return jsonify({'templates': templates})


# ==================== PLATFORM SPECS ROUTES ====================

@app.route('/api/platforms', methods=['GET'])
def get_platforms():
    """Get platform specifications (public)"""
    platforms = {
        'instagram': {
            'name': 'Instagram',
            'icon': '📸',
            'specs': {
                'feed_square': {'width': 1080, 'height': 1080, 'ratio': '1:1'},
                'feed_portrait': {'width': 1080, 'height': 1350, 'ratio': '4:5'},
                'feed_landscape': {'width': 1080, 'height': 566, 'ratio': '1.91:1'},
                'stories': {'width': 1080, 'height': 1920, 'ratio': '9:16'},
                'reels': {'width': 1080, 'height': 1920, 'ratio': '9:16'}
            },
            'best_practices': [
                'Post 1-2 times daily',
                'Use 5-10 hashtags',
                'Engage within first hour',
                'Save rate is key metric'
            ]
        },
        'facebook': {
            'name': 'Facebook',
            'icon': '📘',
            'specs': {
                'link_post': {'width': 1200, 'height': 630, 'ratio': '1.91:1'},
                'image_post': {'width': 1200, 'height': 1200, 'ratio': '1:1'},
                'stories': {'width': 1080, 'height': 1920, 'ratio': '9:16'}
            },
            'best_practices': [
                'Post 1-2 times daily',
                'Video performs best',
                'Ask questions in posts',
                'Go live regularly'
            ]
        },
        'youtube': {
            'name': 'YouTube',
            'icon': '▶️',
            'specs': {
                'video': {'width': 1920, 'height': 1080, 'ratio': '16:9'},
                'thumbnail': {'width': 1280, 'height': 720, 'ratio': '16:9'},
                'shorts': {'width': 1080, 'height': 1920, 'ratio': '9:16'}
            },
            'best_practices': [
                'Hook in first 5 seconds',
                'Consistent upload schedule',
                'Optimize titles & descriptions',
                'Create playlists'
            ]
        },
        'tiktok': {
            'name': 'TikTok',
            'icon': '🎵',
            'specs': {
                'video': {'width': 1080, 'height': 1920, 'ratio': '9:16'},
                'cover': {'width': 1080, 'height': 1920, 'ratio': '9:16'}
            },
            'best_practices': [
                'Post 1-4 times daily',
                'Use trending sounds',
                'Hook in first 3 seconds',
                'Use 3-5 hashtags max'
            ]
        }
    }
    return jsonify({'platforms': platforms})


# ==================== ADMIN ROUTES ====================

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def admin_get_users():
    """Admin: Get all users"""
    try:
        query = f"""
            SELECT user_id, email, name, company, role, created_at, last_login, is_active
            FROM `{PROJECT_ID}.{DATASET_ID}.users`
            ORDER BY created_at DESC
        """
        results = list(client.query(query).result())

        users = []
        for row in results:
            users.append({
                'user_id': row.user_id,
                'email': row.email,
                'name': row.name,
                'company': row.company,
                'role': row.role,
                'created_at': str(row.created_at),
                'last_login': str(row.last_login),
                'is_active': row.is_active
            })

        return jsonify({'users': users})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/stats', methods=['GET'])
@admin_required
def admin_get_stats():
    """Admin: Get platform statistics"""
    try:
        stats = {}

        # User count
        user_query = f"SELECT COUNT(*) as count FROM `{PROJECT_ID}.{DATASET_ID}.users`"
        stats['total_users'] = list(client.query(user_query).result())[0].count

        # Brand count
        brand_query = f"SELECT COUNT(*) as count FROM `{PROJECT_ID}.{DATASET_ID}.brands`"
        stats['total_brands'] = list(client.query(brand_query).result())[0].count

        # Content count
        content_query = f"SELECT COUNT(*) as count FROM `{PROJECT_ID}.{DATASET_ID}.content`"
        stats['total_content'] = list(client.query(content_query).result())[0].count

        return jsonify({'stats': stats})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== STATIC FILES ====================

@app.route('/')
def serve_frontend():
    """Serve the frontend application"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')


# ==================== AI SERVICES ====================

# Import AI services
try:
    from ai_services import gemini_service, imagen_service, veo_service, campaign_agent
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("Warning: AI services not available. Install dependencies.")


@app.route('/api/ai/generate-copy', methods=['POST'])
@token_required
def generate_marketing_copy():
    """Generate marketing copy using Gemini"""
    if not AI_AVAILABLE:
        return jsonify({'error': 'AI services not available'}), 503

    try:
        data = request.json
        import asyncio

        result = asyncio.run(gemini_service.generate_marketing_copy(
            product_description=data.get('description', ''),
            platform=data.get('platform', 'instagram'),
            tone=data.get('tone', 'professional'),
            target_audience=data.get('audience', 'general'),
            max_length=data.get('max_length', 500)
        ))

        return jsonify({
            'success': True,
            'content': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/generate-carousel', methods=['POST'])
@token_required
def generate_carousel():
    """Generate carousel post content"""
    if not AI_AVAILABLE:
        return jsonify({'error': 'AI services not available'}), 503

    try:
        data = request.json
        import asyncio

        result = asyncio.run(gemini_service.generate_carousel_content(
            topic=data.get('topic', ''),
            num_slides=data.get('slides', 5),
            style=data.get('style', 'educational')
        ))

        return jsonify({
            'success': True,
            'slides': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/generate-image', methods=['POST'])
@token_required
def generate_image():
    """Generate image using Imagen"""
    if not AI_AVAILABLE:
        return jsonify({'error': 'AI services not available'}), 503

    try:
        data = request.json
        import asyncio

        result = asyncio.run(imagen_service.generate_image(
            prompt=data.get('prompt', ''),
            aspect_ratio=data.get('aspect_ratio', '1:1'),
            style=data.get('style', 'photorealistic'),
            num_images=data.get('count', 1)
        ))

        return jsonify({
            'success': True,
            'images': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/generate-social-graphic', methods=['POST'])
@token_required
def generate_social_graphic():
    """Generate branded social media graphics"""
    if not AI_AVAILABLE:
        return jsonify({'error': 'AI services not available'}), 503

    try:
        data = request.json
        import asyncio

        result = asyncio.run(imagen_service.generate_social_graphics(
            brand_colors={
                'primary': data.get('primary_color', '#667eea'),
                'secondary': data.get('secondary_color', '#764ba2')
            },
            text_content=data.get('text', ''),
            platform=data.get('platform', 'instagram_feed'),
            template_style=data.get('style', 'modern')
        ))

        return jsonify({
            'success': True,
            'graphic': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/generate-video', methods=['POST'])
@token_required
def generate_video():
    """Generate video using Veo"""
    if not AI_AVAILABLE:
        return jsonify({'error': 'AI services not available'}), 503

    try:
        data = request.json
        import asyncio

        result = asyncio.run(veo_service.generate_video(
            prompt=data.get('prompt', ''),
            duration_seconds=data.get('duration', 5),
            aspect_ratio=data.get('aspect_ratio', '16:9'),
            style=data.get('style', 'cinematic')
        ))

        return jsonify({
            'success': True,
            'video': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/image-to-video', methods=['POST'])
@token_required
def image_to_video():
    """Animate image to video using Veo"""
    if not AI_AVAILABLE:
        return jsonify({'error': 'AI services not available'}), 503

    try:
        data = request.json
        import asyncio

        result = asyncio.run(veo_service.image_to_video(
            image_url=data.get('image_url', ''),
            motion_prompt=data.get('motion', 'subtle movement'),
            duration_seconds=data.get('duration', 5)
        ))

        return jsonify({
            'success': True,
            'video': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== CAMPAIGN AGENT ====================

@app.route('/api/campaigns', methods=['POST'])
@token_required
def create_campaign():
    """Create automated marketing campaign"""
    if not AI_AVAILABLE:
        return jsonify({'error': 'AI services not available'}), 503

    try:
        data = request.json
        import asyncio

        result = asyncio.run(campaign_agent.create_campaign(
            brand_id=data.get('brand_id', ''),
            user_id=request.user['user_id'],
            campaign_config={
                'goals': data.get('goals', 'brand awareness'),
                'duration_days': data.get('duration_days', 7),
                'platforms': data.get('platforms', ['instagram']),
                'posts_per_day': data.get('posts_per_day', 1)
            }
        ))

        return jsonify({
            'success': True,
            'campaign': result
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/campaigns/<campaign_id>/optimize', methods=['POST'])
@token_required
def optimize_campaign(campaign_id):
    """Optimize campaign based on performance"""
    if not AI_AVAILABLE:
        return jsonify({'error': 'AI services not available'}), 503

    try:
        data = request.json
        import asyncio

        result = asyncio.run(campaign_agent.optimize_campaign(
            campaign_id=campaign_id,
            performance_data=data.get('performance', {})
        ))

        return jsonify({
            'success': True,
            'optimization': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/auto-respond', methods=['POST'])
@token_required
def auto_respond():
    """Generate automated response to comment"""
    if not AI_AVAILABLE:
        return jsonify({'error': 'AI services not available'}), 503

    try:
        data = request.json
        import asyncio

        response = asyncio.run(campaign_agent.auto_respond(
            comment_data={'text': data.get('comment', '')},
            brand_voice=data.get('brand_voice', 'friendly and professional')
        ))

        return jsonify({
            'success': True,
            'response': response
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/analyze-performance', methods=['POST'])
@token_required
def analyze_performance():
    """Analyze content performance"""
    if not AI_AVAILABLE:
        return jsonify({'error': 'AI services not available'}), 503

    try:
        data = request.json
        import asyncio

        result = asyncio.run(gemini_service.analyze_content_performance(
            content_data=data.get('content', []),
            platform=data.get('platform', 'instagram')
        ))

        return jsonify({
            'success': True,
            'analysis': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/generate-strategy', methods=['POST'])
@token_required
def generate_strategy():
    """Generate complete marketing strategy"""
    if not AI_AVAILABLE:
        return jsonify({'error': 'AI services not available'}), 503

    try:
        data = request.json
        import asyncio

        result = asyncio.run(gemini_service.generate_campaign_strategy(
            brand_info=data.get('brand', {}),
            goals=data.get('goals', 'increase engagement'),
            duration_days=data.get('duration_days', 30),
            platforms=data.get('platforms', ['instagram', 'facebook'])
        ))

        return jsonify({
            'success': True,
            'strategy': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== AI STATUS ====================

@app.route('/api/ai/status', methods=['GET'])
def ai_status():
    """Check AI services status"""
    return jsonify({
        'ai_available': AI_AVAILABLE,
        'services': {
            'gemini': AI_AVAILABLE,
            'imagen': AI_AVAILABLE,
            'veo': AI_AVAILABLE,
            'campaign_agent': AI_AVAILABLE
        },
        'models': {
            'gemini_model': 'gemini-2.0-flash-exp',
            'imagen_model': 'imagen-3.0-generate-001',
            'veo_model': 'veo-001 (coming soon)'
        }
    })


# ==================== HEALTH CHECK ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'MarketingAI API',
        'version': '2.0.0',
        'ai_enabled': AI_AVAILABLE
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
