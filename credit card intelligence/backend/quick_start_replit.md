# 🚀 Quick Start for Replit

## 1. Import Your Repository
- Go to [replit.com](https://replit.com)
- Click "Create Repl"
- Choose "Import from GitHub"
- Enter your repository URL

## 2. Set Environment Variables
In Replit, go to **Tools → Secrets** and add:

```
POSTGRES_SERVER=your-postgres-host
POSTGRES_PORT=5432
POSTGRES_DB=credit_intelligence
POSTGRES_USER=your-postgres-user
POSTGRES_PASSWORD=your-postgres-password
MONGODB_URL=mongodb+srv://priyaingle456:CLcRSTcllzOzrEpg@creditintelligence.hk0sndt.mongodb.net/
MONGODB_DB=credit_intelligence
SECRET_KEY=generate-a-strong-secret-key
LOG_LEVEL=INFO
```

## 3. Install Dependencies
In the Replit shell:
```bash
cd backend
pip install -r requirements.txt
```

## 4. Test Setup
```bash
python setup_replit.py
```

## 5. Run Your App
```bash
python run.py
```

## 6. Access Your API
- **Main API**: Your Replit URL
- **Docs**: Your Replit URL + `/docs`
- **Health**: Your Replit URL + `/health`

## 🔧 Database Options

### PostgreSQL (Required):
- **Neon**: [neon.tech](https://neon.tech) - Free 3GB
- **Supabase**: [supabase.com](https://supabase.com) - Free 500MB

### MongoDB:
✅ Already configured with Atlas

### Redis (Optional):
- **Redis Cloud**: [redis.com/try-free](https://redis.com/try-free/) - Free tier

## 🚨 Common Issues

1. **Port Issues**: Replit handles ports automatically
2. **Dependencies**: Use `pip install -r requirements.txt`
3. **Database**: Ensure external databases allow Replit connections
4. **Environment**: Check all variables are set in Secrets

## 📞 Need Help?
- Check the console for error messages
- Run `python setup_replit.py` to diagnose issues
- Verify database connectivity
- Check the full deployment guide in `REPLIT_DEPLOYMENT.md`

Your FastAPI backend will be live at your Replit URL! 🎉 