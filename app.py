from flask import Flask
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Transactions
import os
from datetime import datetime
from dotenv import load_dotenv
import uuid
import requests
from decimal import Decimal


app = Flask(__name__)

# Load env vars
load_dotenv()

# Grab secrets from environment variables
DATABASE_URL = os.environ.get('DATABASE_URL')
PRICING_SERVICE_BASE_URL = os.environ.get('PRICING_SERVICE_BASE_URL')

# Setup DB connection
engine = create_engine(DATABASE_URL)

# Setup db session
Session = sessionmaker(bind=engine)
session = Session()

@app.route('/')
def base_route():
    return 'Base Transaction Route'

# Service to save transactions that are input by user (type, currency_code, amount)
# Currency code must be BTC or ETH
@app.route('/store_transaction/<type>/<currency_code>/<amount>')
def store_transaction(type, currency_code, amount):

    # Hard coded to USD for demonstration purposes
    quote_currency_code = 'USD'

    # Pull the usd value of the currency code passed in to be stored as amount_usd
    response = requests.get(PRICING_SERVICE_BASE_URL + currency_code + '/'  + quote_currency_code).json()
    
    print (response)
    print (response['close_price'])

    # Create new transaction object
    new_transaction = Transactions(
        id=str(uuid.uuid4()),
        datetime=datetime.now(),
        type=type,
        currency_code=currency_code,
        amount=Decimal(amount),
        amount_usd=Decimal(amount) * Decimal(response['close_price']) # Calc amount usd based off of close price of /price/ endpoint
    )
  
    # Add transaction to db
    session.add(new_transaction)
    # Commit transaction to db
    session.commit()

    # Return if transactions successfully saved
    return 'Transaction successfully saved'


if __name__ == '__main__':
    # Force to run on specific ports set in env vars
    app.run(host=os.environ.get('HTTP_HOST'),
        port=int(os.environ.get('HTTP_PORT')))