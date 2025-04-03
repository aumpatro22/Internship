# Stock Market Gainers/Losers Tracking Agent

This application tracks the top gainers and losers in the stock market, stores the data in a SQLite database, and sends email notifications with daily summaries.

## Setup Instructions

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Update the email configuration in `stock_tracker_agent.py`:
   ```python
   EMAIL_CONFIG = {
       "smtp_server": "smtp.gmail.com",
       "smtp_port": 587,
       "sender_email": "your_email@gmail.com",
       "sender_password": "your_app_password",  # Use app password for Gmail
   }
   ```

3. Run the application:
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
