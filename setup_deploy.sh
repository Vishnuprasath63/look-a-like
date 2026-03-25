#!/bin/bash
# Deployment setup script for Railway/Render

echo "🚀 Setting up StarMatch AI for deployment..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Seed database with placeholders (faster than downloads)
echo "🎭 Seeding celebrity database with placeholders..."
python manage.py seed_celebrities --use-placeholders

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Deployment setup complete!"
echo "🎉 Your app is ready to deploy!"
echo ""
echo "Next steps:"
echo "1. Set environment variables in your deployment platform"
echo "2. Push to GitHub and connect to Railway/Render"
echo "3. Create a superuser: python manage.py createsuperuser"