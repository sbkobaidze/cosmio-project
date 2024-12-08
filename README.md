# Python Flask Application

## Description

This is a Flask-based Python application with JWT authentication, WebSocket support, and AWS DynamoDB integration.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- AWS account with DynamoDB access
- DynamoDB table named 'users' (with 'email' as partition key)

### AWS DynamoDB Setup

1. Create a DynamoDB table:

   - Table name: `users`
   - Partition key: `email` (String)
   - Region: [your-aws-region]

2. Ensure your AWS credentials have permissions to:
   - Read/Write to DynamoDB table
   - Scan table
   - Query table

### Application Setup

1. Clone this repository:

```bash
git clone [your-repository-url]
cd [repository-name]
```

2. Create a virtual environment (recommended):

```bash
python -m venv venv
```

3. Activate the virtual environment:

- On Windows:

```bash
venv\Scripts\activate
```

- On macOS/Linux:

```bash
source venv/bin/activate
```

4. Install required packages:

```bash
pip install -r requirements.txt
```

## Dependencies

```
Flask==3.0.0
Flask-JWT-Extended==4.6.0
Werkzeug==3.0.1
PyJWT==2.8.0
python-dotenv==1.0.0
boto3==1.0.0
Flask-CORS==4.0.0
flask-socketio==5.3.6
pydantic==2.5.2
pydantic[email]
```

## AWS Configuration

Your application needs proper AWS credentials to access DynamoDB. Set these up using one of the following methods:

AWS credentials file (`~/.aws/credentials`):

```
[default]
aws_access_key_id = your-access-key
aws_secret_access_key = your-secret-key
region = your-region
```

## Usage

To run the application:

```bash
python app.py
```

## DynamoDB Table Structure

The application expects a DynamoDB table with the following structure:

```python
users_table = resource('dynamodb').Table('users')
# Table schema:
# - email (String) - Partition Key
# [Add any additional fields your table uses]
```

## Project Structure

```
.
├── app.py              # Main application file
├── requirements.txt    # Package dependencies
├── .env               # Environment variables (not in git)
├── README.md          # This file
└── venv/              # Virtual environment (not in git)
```

## Common Issues

1. **CORS Error**: If you encounter CORS issues, verify your CORS configuration matches your frontend URL:

```python
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173"], "supports_credentials": True}})
```

2. **DynamoDB Connection Issues**:
   - Verify AWS credentials are correctly set
   - Check if the table name matches exactly ('users')
   - Ensure the table exists in the specified AWS region

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

[Your chosen license]
