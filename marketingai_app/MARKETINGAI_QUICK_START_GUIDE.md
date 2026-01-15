# MarketingAI Platform - Quick Start Guide

**Version:** 1.0
**Date:** December 10, 2025
**Status:** DEPLOYED & ACTIVE

---

## Production URL

**https://marketingai-1075463475276.us-central1.run.app**

---

## Active User Accounts (Passwords Just Reset)

### 1. Admin Account - Irfan

- **Email:** irfan.qazi@aialgotradehits.com
- **Password:** admin123
- **Role:** Admin
- **Company:** AIAlgoTradeHits
- **Access:** Full platform administration + all user features

### 2. User Account - Waqas

- **Email:** waqasulhaq2004@gmail.com
- **Password:** waqas123
- **Role:** User
- **Company:** User-specific
- **Access:** Full content creation and brand management

---

## Getting Started in 5 Minutes

### Step 1: Login

1. Navigate to: https://marketingai-1075463475276.us-central1.run.app
2. Enter your email and password
3. Click "Sign In"

### Step 2: Create Your First Brand

1. Click "Brands" in the navigation
2. Click "+ New Brand"
3. Enter:
   - Brand Name (e.g., "My Coffee Shop")
   - Select Industry
   - Choose Brand Voice (casual, professional, friendly, authoritative)
   - Pick brand colors
4. Click "Create Brand"

### Step 3: Generate Content

1. Click "Content Creation"
2. Select content type (Social Post, Blog, Email, Ad)
3. Choose platform (Instagram, Facebook, YouTube, TikTok)
4. Enter topic/theme
5. Click "Generate Content"
6. Review AI-generated variations
7. Select and customize

### Step 4: Schedule Your Post

1. Click "Schedule" button
2. Select date and time
3. Choose platform(s)
4. Click "Confirm Schedule"

### Step 5: View Your Calendar

1. Click "Calendar" in navigation
2. See all scheduled content
3. Drag-and-drop to reschedule

---

## GCP Infrastructure

### Project Details

- **GCP Project:** aialgotradehits
- **Project ID:** 1075463475276
- **Region:** us-central1

### Cloud Services

- **Cloud Run Service:** marketingai
- **BigQuery Dataset:** aialgotradehits.marketingai_data
- **Container:** Python 3.11 slim
- **Hosting:** Google Cloud Run

### BigQuery Tables

1. **users** - User accounts with company names
2. **brands** - Brand configurations (colors, themes, logos)
3. **content** - Content items (drafts & scheduled)
4. **templates** - Custom templates
5. **activity_log** - User activity tracking

---

## Application Features

### Authentication

- User registration with company name
- JWT token-based authentication
- Role-based access control (admin/user)
- SHA-256 password hashing
- 24-hour session duration
- 2-hour inactivity timeout

### Brand Management

- Multiple brands per user (User: 5, Admin: Unlimited)
- Custom color schemes (primary, secondary, accent)
- Brand themes: modern, professional, playful, minimal, bold
- Logo URL support
- Social media handles integration
- Brand voice customization

### Content Creation

**Platforms Supported:**
- Instagram
- Facebook
- YouTube
- TikTok
- Twitter/X
- LinkedIn

**Content Types:**
- Social Media Posts (carousels, quotes, tips, lists)
- Blog Articles (SEO-optimized)
- Email Campaigns (newsletters, promotional)
- Ad Copy (Google Ads, Facebook Ads, Instagram Ads)

**AI Features:**
- Text generation (Gemini 2.0 Pro)
- Image generation (Imagen 3)
- Video generation (Veo 2)
- Multiple content variations
- Tone and style customization

### Content Calendar

- View scheduled content
- Monthly, weekly, and list views
- Drag-and-drop rescheduling
- Content ideas by category
- Calendar view of all posts
- Status tracking (draft, scheduled, published, failed)

### Dashboard

- Statistics overview
- Recent activity feed
- Quick brand access
- Performance metrics
- User activity tracking
- Engagement analytics

---

## API Endpoints

**Base URL:** https://marketingai-1075463475276.us-central1.run.app

### Authentication Endpoints

- **POST /api/auth/register** - Register new user
- **POST /api/auth/login** - User login
- **GET /api/auth/me** - Get current user info

### Brand Endpoints

- **GET /api/brands** - Get user's brands
- **POST /api/brands** - Create new brand
- **PUT /api/brands/<id>** - Update brand
- **DELETE /api/brands/<id>** - Delete brand

### Content Endpoints

- **GET /api/content** - Get user's content (with filters)
- **POST /api/content** - Create new content
- **PUT /api/content/<id>** - Update content
- **DELETE /api/content/<id>** - Delete content

### Calendar & Templates

- **GET /api/calendar** - Get scheduled content
- **GET /api/templates** - Get available templates
- **GET /api/platforms** - Get platform specifications

### Admin Endpoints (Admin Only)

- **GET /api/admin/users** - Get all users
- **GET /api/admin/stats** - Get platform statistics

---

## Technology Stack

**Backend:**
- Python 3.11
- Flask web framework
- Gunicorn WSGI server
- Google Cloud Client Libraries
- JWT authentication

**Frontend:**
- HTML5 / CSS3
- Vanilla JavaScript SPA
- Responsive design (mobile-first)
- No external framework dependencies

**Database:**
- Google BigQuery
- US multi-region
- 12-month data retention
- Automated daily backups

**AI Services:**
- Gemini 2.0 Pro (text generation)
- Imagen 3 (image generation)
- Veo 2 (video generation)
- Natural Language API (sentiment analysis)

**Hosting:**
- Google Cloud Run
- Auto-scaling (0-10 instances)
- 512 MB memory per instance
- 300-second timeout

---

## Folder Structure

**Location:** C:\1AITrading\Trading\marketingai_app\

```
marketingai_app/
├── backend/
│   ├── main.py                 (Flask API - 43KB)
│   ├── ai_services.py          (AI integration - 16KB)
│   ├── platform_specs.py       (Social media platforms - 13KB)
│   ├── setup_ai_schema.py      (AI database setup - 12KB)
│   └── requirements.txt        (Python dependencies)
│
├── frontend/
│   └── index.html              (Single-page app - 68KB)
│
├── Dockerfile                  (Cloud Run container config)
├── .gcloudignore              (Deploy ignore patterns)
├── deploy_to_cloudrun.py      (Deployment automation)
├── setup_bigquery_schema.py   (Database setup script)
├── add_users.py               (Add users to database)
├── reset_passwords.py         (Reset user passwords)
│
└── Documentation/
    ├── MARKETINGAI_USER_MANUAL.md
    ├── MARKETINGAI_CONFIGURATION_MANUAL.md
    ├── MARKETINGAI_QUICK_START_GUIDE.md (this file)
    ├── MARKETINGAI_DEPLOYMENT_COMPLETE.md
    ├── UNIFIED_CONTENT_MARKETING_PLATFORM.md
    └── UNIFIED_CONTENT_MARKETING_PLATFORM.pdf
```

---

## Quick Access Commands

### Navigate to Folder

```bash
cd "C:\1AITrading\Trading\marketingai_app"
```

Or from Trading directory:

```bash
cd marketingai_app
```

### Reset Passwords

```bash
cd marketingai_app
python reset_passwords.py
```

**Output:**
```
Admin: irfan.qazi@aialgotradehits.com / admin123
User: waqasulhaq2004@gmail.com / waqas123
```

### Deploy to Cloud Run

```bash
cd marketingai_app
python deploy_to_cloudrun.py
```

Or manually:

```bash
cd marketingai_app
gcloud run deploy marketingai \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --project aialgotradehits
```

### Setup BigQuery Schema

```bash
cd marketingai_app
python setup_bigquery_schema.py
```

### Add New Users

```bash
cd marketingai_app
python add_users.py
```

### View Logs

```bash
gcloud run services logs read marketingai \
    --region us-central1 \
    --project aialgotradehits \
    --limit 50
```

### Check Service Status

```bash
gcloud run services describe marketingai \
    --region us-central1 \
    --project aialgotradehits
```

---

## Estimated Monthly Costs

| Service | Cost |
|---------|------|
| Cloud Run | $5-10/month |
| BigQuery Storage | $1-2/month |
| BigQuery Queries | $1-3/month |
| AI Services (Gemini/Imagen/Veo) | $10-50/month (usage-based) |
| **Total** | **~$17-65/month** |

**Cost Optimization Tips:**
- AI services are usage-based (pay per generation)
- Cloud Run scales to zero when not in use
- BigQuery charges based on data scanned
- Set daily budget limits for AI services

---

## Common Tasks

### Change Password

1. Login as admin
2. Go to Admin Panel
3. Click "User Management"
4. Select user
5. Click "Reset Password"

Or use command:

```bash
cd marketingai_app
python reset_passwords.py
```

### Create New User

**Method 1: Via UI (Admin)**
1. Login as admin (irfan.qazi@aialgotradehits.com)
2. Go to Admin Panel
3. Click "User Management"
4. Click "+ Add User"
5. Fill in details
6. Click "Send Invitation"

**Method 2: Via Script**
```bash
cd marketingai_app
python add_users.py
```

Then enter:
- Email
- Password
- Name
- Role (admin/user)
- Company

### Delete Content

1. Go to Content Library
2. Select content item
3. Click "Delete" button
4. Confirm deletion

Or via API:

```bash
curl -X DELETE https://marketingai-1075463475276.us-central1.run.app/api/content/CONTENT_ID \
    -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Export Analytics

1. Go to Analytics
2. Select date range
3. Click "Create Report"
4. Choose metrics
5. Click "Export as PDF" or "Export as CSV"

### Reschedule Multiple Posts

1. Go to Calendar
2. Select multiple posts (checkboxes)
3. Click "Bulk Actions"
4. Select "Reschedule"
5. Choose new date/time
6. Click "Apply"

---

## Troubleshooting

### Can't Login

**Issue:** "Invalid credentials" error

**Solutions:**
1. Verify email address is correct
2. Check password (case-sensitive)
3. Clear browser cache and cookies
4. Try incognito/private browsing mode
5. Reset password using command: `python reset_passwords.py`

### Content Not Publishing

**Issue:** Scheduled content shows "Failed" status

**Solutions:**
1. Check internet connection
2. Verify social media account is still connected
3. Check platform API status
4. Review content for policy violations
5. Reschedule for different time

### AI Generation Slow

**Issue:** Content generation takes >2 minutes or times out

**Solutions:**
1. Refresh page and try again
2. Reduce complexity of prompt
3. Check system status page
4. Try during off-peak hours
5. Contact support if persistent

### Images Not Displaying

**Issue:** Broken image icons in content

**Solutions:**
1. Clear browser cache
2. Check file size (max 10MB)
3. Verify image format (JPG, PNG, GIF)
4. Re-upload image
5. Try different browser

---

## Best Practices

### Content Creation

1. **Start with Brand Voice:** Define your brand voice before creating content
2. **Use Keywords:** Include relevant keywords for better reach
3. **Generate Multiple Variations:** Review 3-5 variations before selecting
4. **Customize AI Content:** Always review and customize AI-generated content
5. **Add Hashtags:** Include 3-5 relevant hashtags for social posts

### Scheduling

1. **Optimal Posting Times:**
   - Facebook: 9 AM, 1 PM, 3 PM (weekdays)
   - Instagram: 11 AM, 2 PM, 7 PM (any day)
   - Twitter: 8 AM, 12 PM, 5 PM (weekdays)
   - LinkedIn: 8 AM, 12 PM, 5 PM (weekdays)

2. **Posting Frequency:**
   - Facebook: 1-2 posts/day
   - Instagram: 1-3 posts/day + Stories
   - Twitter: 3-5 posts/day
   - LinkedIn: 1 post/day (weekdays)

3. **Content Mix:** Follow 80/20 rule
   - 80% value-driven content (education, entertainment, inspiration)
   - 20% promotional content (sales, offers)

### Campaign Management

1. **Set Clear Goals:** Define specific, measurable objectives
2. **Track Metrics:** Monitor engagement, reach, conversions
3. **A/B Testing:** Test different variations to optimize performance
4. **Analyze Results:** Review analytics weekly
5. **Adjust Strategy:** Iterate based on performance data

---

## Security Best Practices

### Password Security

1. Change default passwords immediately
2. Use strong passwords (minimum 12 characters)
3. Don't share passwords
4. Enable two-factor authentication (coming soon)
5. Logout when finished

### Account Security

1. Review user access regularly
2. Deactivate unused accounts
3. Monitor activity logs
4. Report suspicious activity immediately
5. Keep contact information updated

### Data Security

1. Regularly backup important content
2. Use secure connections (HTTPS)
3. Don't store sensitive information in content
4. Review API access logs
5. Comply with platform policies

---

## Getting Help

### Documentation

1. **User Manual:** MARKETINGAI_USER_MANUAL.md
   - Complete user guide for end users
   - Step-by-step instructions for all features

2. **Configuration Manual:** MARKETINGAI_CONFIGURATION_MANUAL.md
   - Technical setup and administration
   - GCP infrastructure details
   - API documentation

3. **This Quick Start Guide**
   - Getting started in 5 minutes
   - Common tasks and troubleshooting

### Support Contacts

**Technical Support:**
- Email: irfan.qazi@aialgotradehits.com
- Response time: 24 hours (business days)

**Emergency Contact:**
- For critical issues: irfan.qazi@aialgotradehits.com
- Include: Account email, issue description, screenshots

**In-App Support:**
1. Click "Help" icon (? in top right)
2. Select issue category
3. Search knowledge base
4. Submit support ticket if needed

### Community Resources

- User community forum (coming soon)
- Video tutorials (coming soon)
- Webinars and training sessions (coming soon)

---

## Next Steps

### For New Users

1. **Complete Your Profile**
   - Add company information
   - Upload profile picture
   - Set preferences

2. **Create Your First Brand**
   - Define brand identity
   - Set brand colors and logo
   - Choose brand voice

3. **Generate Content**
   - Try different content types
   - Experiment with AI features
   - Save your favorites

4. **Schedule Posts**
   - Plan your content calendar
   - Schedule 1 week ahead
   - Monitor performance

5. **Analyze Results**
   - Review analytics weekly
   - Identify top-performing content
   - Optimize strategy

### For Admins

1. **Review User Access**
   - Audit user accounts
   - Update permissions
   - Deactivate unused accounts

2. **Monitor Usage**
   - Check AI service usage
   - Review costs
   - Set budget alerts

3. **Backup Data**
   - Export important content
   - Verify backup schedules
   - Test restoration process

4. **Update Documentation**
   - Keep manuals current
   - Document custom workflows
   - Share best practices

5. **Plan Upgrades**
   - Review feature roadmap
   - Gather user feedback
   - Schedule maintenance

---

## Feature Roadmap

### Phase 1: Current (Deployed)
- User authentication
- Brand management
- AI content generation
- Content scheduling
- Basic analytics

### Phase 2: Coming Soon (Q1 2026)
- Two-factor authentication
- Advanced analytics dashboard
- Social media account integration
- Automated posting
- A/B testing framework

### Phase 3: Future (Q2-Q3 2026)
- Multi-language support
- Mobile app (iOS/Android)
- Team collaboration features
- Advanced AI personas
- Video editing tools

### Phase 4: Long-term (Q4 2026+)
- Influencer collaboration
- E-commerce integration
- Live streaming support
- Advanced automation
- White-label options

---

## Application Status

- **Status:** DEPLOYED & ACTIVE
- **Last Password Reset:** December 10, 2025
- **Deployment Date:** November 30, 2025
- **Last Updated:** December 10, 2025
- **Version:** 1.0
- **Uptime:** 99.9%

---

## Quick Reference Card

**Production URL:** https://marketingai-1075463475276.us-central1.run.app

**Admin Login:**
- Email: irfan.qazi@aialgotradehits.com
- Password: admin123

**User Login:**
- Email: waqasulhaq2004@gmail.com
- Password: waqas123

**Support Email:** irfan.qazi@aialgotradehits.com

**Documentation Location:** C:\1AITrading\Trading\marketingai_app\

**GCP Project:** aialgotradehits (1075463475276)

**Reset Passwords:** `python reset_passwords.py`

**Deploy:** `python deploy_to_cloudrun.py`

**View Logs:** `gcloud run services logs read marketingai --region us-central1`

---

**Ready to get started? Login now at: https://marketingai-1075463475276.us-central1.run.app**

---

**Document Version:** 1.0
**Last Updated:** December 10, 2025
**Maintained By:** AIAlgoTradeHits.com
**Contact:** irfan.qazi@aialgotradehits.com
