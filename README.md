# Here are your Instructions

# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file
MONGO_URL=mongodb://localhost:27017/mediconnect
SECRET_KEY=your-super-secret-key-change-in-production

# Run backend
uvicorn server:app --reload --host 0.0.0.0 --port 8001



# Navigate to frontend
cd frontend

# Install dependencies (use yarn, not npm!)
yarn install

# Create .env file
cat > .env << EOF
REACT_APP_BACKEND_URL=http://localhost:8001
EOF

# Run frontend
yarn start