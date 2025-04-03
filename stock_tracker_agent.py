import os
import requests
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Initialize FastAPI
app = FastAPI(title="Stock Gainers/Losers Tracker")

# Database setup
DATABASE_URL = "sqlite:///./stock_tracker.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class StockMovement(Base):
    __tablename__ = "stock_movements"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    company_name = Column(String)
    price = Column(Float)
    change = Column(Float)
    percent_change = Column(Float)
    movement_type = Column(String)  # "gainer" or "loser"
    timestamp = Column(DateTime, default=datetime.now)

# Create database tables
Base.metadata.create_all(bind=engine)

# Email configuration - update with your email settings
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your_email@gmail.com",
    "sender_password": "your_app_password",  # Use app password for Gmail
}

# Models for API requests/responses
class StockData(BaseModel):
    symbol: str
    company_name: str
    price: float
    change: float
    percent_change: float

class StockMovementResponse(BaseModel):
    id: int
    symbol: str
    company_name: str
    price: float
    change: float
    percent_change: float
    movement_type: str
    timestamp: datetime

def fetch_top_movers(api_key="3TCWPX9NPQVDUS90"):
    """
    Fetch top gainers and losers from Alpha Vantage or similar API
    
    Note: Alpha Vantage doesn't have a direct endpoint for top gainers/losers,
    so this is a simplified example. In a real application, you might:
    1. Use a different API that provides this data directly
    2. Calculate it from a universe of stocks you're tracking
    """
    # This is a sample function - you'll need to adapt it based on your API source
    gainers = []
    losers = []
    
    try:
        # For demonstration, we'll track a few major stocks
        symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
        
        for symbol in symbols:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                quote = data.get("Global Quote", {})
                
                if quote:
                    stock_data = {
                        "symbol": symbol,
                        "company_name": f"{symbol} Inc.",  # Ideally get actual names
                        "price": float(quote.get("05. price", 0)),
                        "change": float(quote.get("09. change", 0)),
                        "percent_change": float(quote.get("10. change percent", "0%").strip("%"))
                    }
                    
                    # Categorize as gainer or loser
                    if stock_data["change"] > 0:
                        gainers.append(stock_data)
                    else:
                        losers.append(stock_data)
            
        # Sort gainers by percent change (descending)
        gainers = sorted(gainers, key=lambda x: x["percent_change"], reverse=True)
        # Sort losers by percent change (ascending)
        losers = sorted(losers, key=lambda x: x["percent_change"])
        
        return {"gainers": gainers, "losers": losers}
    
    except Exception as e:
        print(f"Error fetching stock data: {e}")
        return {"gainers": [], "losers": []}

def save_to_database(data):
    """Save gainers and losers to database"""
    db = SessionLocal()
    try:
        # Save gainers
        for gainer in data["gainers"]:
            stock = StockMovement(
                symbol=gainer["symbol"],
                company_name=gainer["company_name"],
                price=gainer["price"],
                change=gainer["change"],
                percent_change=gainer["percent_change"],
                movement_type="gainer"
            )
            db.add(stock)
        
        # Save losers
        for loser in data["losers"]:
            stock = StockMovement(
                symbol=loser["symbol"],
                company_name=loser["company_name"],
                price=loser["price"],
                change=loser["change"],
                percent_change=loser["percent_change"],
                movement_type="loser"
            )
            db.add(stock)
            
        db.commit()
    finally:
        db.close()

def send_email_notification(data):
    """Send email with summary of top gainers and losers"""
    subject = f"Stock Market Movers - {datetime.now().strftime('%Y-%m-%d')}"
    
    # Create email body
    body = "<html><body>"
    body += f"<h2>Stock Market Summary for {datetime.now().strftime('%Y-%m-%d')}</h2>"
    
    # Add gainers table
    body += "<h3>Top Gainers</h3>"
    body += "<table border='1'><tr><th>Symbol</th><th>Company</th><th>Price</th><th>Change</th><th>% Change</th></tr>"
    for gainer in data["gainers"]:
        body += f"<tr><td>{gainer['symbol']}</td><td>{gainer['company_name']}</td>"
        body += f"<td>${gainer['price']:.2f}</td><td>${gainer['change']:.2f}</td>"
        body += f"<td>{gainer['percent_change']:.2f}%</td></tr>"
    body += "</table>"
    
    # Add losers table
    body += "<h3>Top Losers</h3>"
    body += "<table border='1'><tr><th>Symbol</th><th>Company</th><th>Price</th><th>Change</th><th>% Change</th></tr>"
    for loser in data["losers"]:
        body += f"<tr><td>{loser['symbol']}</td><td>{loser['company_name']}</td>"
        body += f"<td>${loser['price']:.2f}</td><td>${loser['change']:.2f}</td>"
        body += f"<td>{loser['percent_change']:.2f}%</td></tr>"
    body += "</table>"
    
    body += "</body></html>"
    
    # Set up email
    msg = MIMEMultipart()
    msg['From'] = EMAIL_CONFIG["sender_email"]
    msg['To'] = EMAIL_CONFIG["sender_email"]  # Send to yourself or configure recipients
    msg['Subject'] = subject
    
    # Attach HTML body
    msg.attach(MIMEText(body, 'html'))
    
    try:
        # Connect to SMTP server and send email
        server = smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"])
        server.starttls()
        server.login(EMAIL_CONFIG["sender_email"], EMAIL_CONFIG["sender_password"])
        server.send_message(msg)
        server.quit()
        print("Email notification sent successfully")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def process_stock_movers(api_key="3TCWPX9NPQVDUS90"):
    """Main function to process stock movers"""
    # Fetch data
    data = fetch_top_movers(api_key)
    
    # Save to database
    save_to_database(data)
    
    # Send email notification
    send_email_notification(data)
    
    return data

# API Endpoints
@app.get("/")
def root():
    return {"message": "Stock Gainers/Losers Tracking API"}

@app.post("/track-movers/")
async def track_movers(background_tasks: BackgroundTasks, api_key: str = "3TCWPX9NPQVDUS90"):
    """Endpoint to trigger tracking of stock movers"""
    background_tasks.add_task(process_stock_movers, api_key)
    return {"message": "Stock tracking process started in background"}

@app.get("/gainers/", response_model=List[StockMovementResponse])
def get_gainers(limit: int = 10):
    """Get the latest top gainers"""
    db = SessionLocal()
    try:
        gainers = db.query(StockMovement).filter(
            StockMovement.movement_type == "gainer"
        ).order_by(StockMovement.timestamp.desc()).limit(limit).all()
        return gainers
    finally:
        db.close()

@app.get("/losers/", response_model=List[StockMovementResponse])
def get_losers(limit: int = 10):
    """Get the latest top losers"""
    db = SessionLocal()
    try:
        losers = db.query(StockMovement).filter(
            StockMovement.movement_type == "loser"
        ).order_by(StockMovement.timestamp.desc()).limit(limit).all()
        return losers
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
