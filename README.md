# Stock Market Gainers/Losers Tracking Agent

This application tracks the top gainers and losers in the stock market, stores the data in a SQLite database, and sends email notifications with daily summaries.

## Setup Instructions

### Option 1: Standard Installation
1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

### Option 2: Alternative Installation Methods
If you encounter the "metadata-generation-failed" error, try one of these alternatives:

1. **Install packages individually:**
   ```
   pip install fastapi==0.95.2
   pip install uvicorn==0.21.1
   pip install sqlalchemy==1.4.48
   pip install pandas==1.5.3
   pip install requests==2.28.2
   pip install pydantic==1.10.8
   pip install python-multipart==0.0.6
   ```

2. **Use pip with no build isolation:**
   ```
   pip install --no-build-isolation -r requirements.txt
   ```

3. **Use an older pip version:**
   ```
   python -m pip install pip==21.3.1
   pip install -r requirements.txt
   ```

4. **Create and use a virtual environment:**
   ```
   # Windows
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   
   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Install with --no-cache-dir option:**
   ```
   pip install --no-cache-dir -r requirements.txt
   ```

### Configuration and Running

1. Update the email configuration in `stock_tracker_agent.py`:
   ```python
   EMAIL_CONFIG = {
       "smtp_server": "smtp.gmail.com",
       "smtp_port": 587,
       "sender_email": "your_email@gmail.com",
       "sender_password": "your_app_password",  # Use app password for Gmail
   }
   ```

2. Run the application:
   ```
   uvicorn stock_tracker_agent:app --reload
   ```

## API Endpoints

- **GET /** - Check if the API is running
- **POST /track-movers/** - Trigger the process to track stock movers (gainers/losers)
- **GET /gainers/** - Get the latest top gainers
- **GET /losers/** - Get the latest top losers

## Scheduling

For automatic daily tracking, you can set up a cron job or Windows Task Scheduler to hit the `/track-movers/` endpoint at a specific time each day.

Example cron job (Linux/Mac):
```
0 17 * * 1-5 curl -X POST http://localhost:8000/track-movers/
```

This will run the tracking process at 5:00 PM Monday through Friday.

## Troubleshooting

### Common pip Installation Issues

1. **Metadata Generation Failed**
   - This usually happens due to incompatible package versions or build issues
   - Try the alternative installation methods listed above

2. **Dependency Conflicts**
   - If you see conflicts between packages, install them one by one in the correct order
   - Start with lower-level packages like requests and sqlalchemy before installing fastapi

3. **Python Version Compatibility**
   - Make sure you're using Python 3.7-3.10 which has better compatibility with these packages
   - You can check your Python version with: `python --version`
