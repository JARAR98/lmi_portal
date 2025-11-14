# WiFi Portal - Vercel Deployment Guide

## Overview
This guide walks through deploying the WiFi Portal application to Vercel with MongoDB for data persistence.

## Architecture Changes for Vercel

### Key Differences from Docker
| Aspect | Docker | Vercel |
|--------|--------|--------|
| **Runtime** | Gunicorn + Flask | Serverless Functions |
| **Storage** | File-based JSON | Cloud Database (MongoDB) |
| **Scaling** | Manual | Automatic |
| **Cost** | Always running | Pay per request |
| **Session** | In-process | Requires configuration |

## Prerequisites

1. **Vercel Account**
   - Sign up at https://vercel.com
   - Link your GitHub account

2. **MongoDB Atlas Account** (Free tier available)
   - Create at https://www.mongodb.com/cloud/atlas
   - Create a free cluster
   - Get connection string

3. **GitHub Repository**
   - Push code to GitHub
   - Example: `https://github.com/yourusername/wifi-portal`

## Step 1: Set Up MongoDB Atlas

### 1.1 Create MongoDB Cluster
```bash
# Go to MongoDB Atlas
1. Create a new project: "WiFi Portal"
2. Create a Cluster (Free tier M0)
3. Choose AWS, region closest to you
4. Wait 5-10 minutes for cluster creation
```

### 1.2 Create Database User
```
1. Network Access → Add IP Address
   - Click "Allow Access from Anywhere" (0.0.0.0/0) for testing
   - Production: Restrict to Vercel IPs
   
2. Database Access → Add Database User
   - Username: wifi_portal_user
   - Password: Generate secure password
   - Save password securely
```

### 1.3 Get Connection String
```
1. Clusters → Connect → Connect your application
2. Select Python 3.6+
3. Copy connection string
4. Replace:
   - <username> with your database user
   - <password> with your password
   - Example:
     mongodb+srv://wifi_portal_user:YOUR_PASSWORD@cluster.mongodb.net/wifi_portal?retryWrites=true&w=majority
```

## Step 2: Deploy to Vercel

### 2.1 Clone/Update Your Repository
```bash
cd ~/GitHub/wifi-portal
git add .
git commit -m "Add Vercel configuration"
git push origin main
```

### 2.2 Deploy Using Vercel Dashboard

**Option A: Web Dashboard**
```
1. Go to https://vercel.com/import
2. Select "Other" → Input GitHub repository URL
3. Project name: wifi-portal
4. Root Directory: ./lmi_portal
5. Framework: Other (since Flask is handled by vercel.json)
```

**Option B: Vercel CLI**
```bash
# Install Vercel CLI
npm i -g vercel

# Or using npx (no install needed)
npx vercel

# Follow the prompts:
# - Link to GitHub account
# - Select the wifi-portal repository
# - Deploy
```

### 2.3 Configure Environment Variables

After deployment starts in Vercel Dashboard:

```
1. Go to Project Settings → Environment Variables
2. Add these variables:
   
   Name: MONGODB_URI
   Value: mongodb+srv://wifi_portal_user:PASSWORD@cluster.mongodb.net/wifi_portal?retryWrites=true&w=majority
   
   Name: FLASK_SECRET_KEY
   Value: [Generate strong random string - minimum 32 characters]
   
   Name: ADMIN_USERNAME
   Value: admin
   
   Name: ADMIN_PASSWORD
   Value: [Your secure admin password]
   
   Name: FLASK_ENV
   Value: production

3. Click "Save"
```

### 2.4 Redeploy with Environment Variables
```
1. Go to Deployments
2. Select the latest deployment
3. Click "Redeploy"
4. This redeploy will use the environment variables
```

## Step 3: Verify Deployment

### 3.1 Test Public Routes
```bash
# Replace YOUR_DEPLOYMENT_URL with your Vercel URL
curl https://YOUR_DEPLOYMENT_URL/
curl https://YOUR_DEPLOYMENT_URL/terms
curl https://YOUR_DEPLOYMENT_URL/privacy

# Should all return HTML content
```

### 3.2 Test Registration
```bash
curl -X POST https://YOUR_DEPLOYMENT_URL/api/auth \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "fullName=Test User&purpose=business&terms=on"

# Should redirect to /success
```

### 3.3 Test Admin Dashboard
```bash
# 1. Navigate to: https://YOUR_DEPLOYMENT_URL/admin/login
# 2. Enter credentials:
#    Username: admin
#    Password: [Your admin password]
# 3. Check if user list displays
```

### 3.4 Verify Data in MongoDB
```bash
1. Go to MongoDB Atlas
2. Collections → wifi_portal → users
3. Should see your test registrations
```

## Step 4: Configure Custom Domain (Optional)

### 4.1 Add Domain to Vercel
```
1. Project Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions
```

## Troubleshooting

### Issue: MongoDB Connection Error
```
Error: Could not connect to MongoDB

Solution:
1. Check connection string is correct in Environment Variables
2. Verify IP whitelist in MongoDB Atlas (should include 0.0.0.0/0 or Vercel IPs)
3. Check username/password are correct
4. Redeploy after fixing
```

### Issue: Admin Login Not Working
```
Error: Invalid credentials after login

Solution:
1. Check ADMIN_USERNAME and ADMIN_PASSWORD in Environment Variables
2. Verify no extra spaces or line breaks
3. Redeploy
```

### Issue: Session Lost After Admin Login
```
Error: Redirects back to login after successful admin login

Solution:
This is a known issue with Vercel's serverless functions and session management.
Working on solution: Use JWT tokens instead of sessions.
Current workaround: Session data stored in MongoDB instead of in-process memory.
```

### Issue: 502 Bad Gateway
```
Error: 502 Bad Gateway when accessing app

Solution:
1. Check Vercel Functions logs
2. Look for Python import errors
3. Verify all required files are in /api folder
4. Check environment variables are set
```

## Performance Optimization

### 1. Cold Starts
- Vercel functions may take 1-2 seconds on first request
- Consider upgrading to Pro plan for faster cold starts

### 2. Database Connection Pooling
- MongoDB Atlas free tier has connection limits
- Consider using MongoDB connection pooling

### 3. Caching
```
# Add caching headers for static assets
# This is handled by Vercel automatically
```

## Production Checklist

- [ ] MongoDB Atlas cluster configured and secured
- [ ] Connection string added to Vercel environment variables
- [ ] Admin credentials changed from defaults
- [ ] FLASK_SECRET_KEY is strong and random
- [ ] All environment variables are set
- [ ] Application tested at production URL
- [ ] Admin dashboard verified working
- [ ] User registration tested end-to-end
- [ ] Database backups configured in MongoDB Atlas
- [ ] Custom domain configured (if desired)
- [ ] Monitoring set up (optional: Sentry, DataDog)

## Next Steps

1. **Monitoring**
   - Set up error tracking with Sentry
   - Monitor function execution time
   - Track user registrations

2. **Analytics**
   - Track user patterns
   - Monitor peak usage times
   - Analyze business vs guest ratio

3. **Enhancements**
   - Add email notifications for registrations
   - Implement user deregistration
   - Add data export functionality

## Rollback

If something goes wrong:

```
1. Go to Vercel Dashboard → Deployments
2. Find the previous working deployment
3. Click the three dots → Promote to Production
4. Your app will revert to the previous version
```

## Support

For issues:
- Vercel Documentation: https://vercel.com/docs
- MongoDB Support: https://docs.mongodb.com
- Flask Documentation: https://flask.palletsprojects.com

---

**Last Updated:** 2024
**Status:** Ready for Deployment
