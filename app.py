from flask import Flask, request
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
import logging as logger


app = Flask(__name__)

# Load env vars
load_dotenv()

# Grab secrets from environment variables
DATABASE_URL = os.environ.get('DATABASE_URL')
PRICING_SERVICE_URL = os.environ.get('PRICING_SERVICE_URL')
NOTIFICATION_SERVICE_URL = os.environ.get('NOTIFICATION_SERVICE_URL')

# Setup DB connection
engine = create_engine(DATABASE_URL)

# Setup db session
Session = sessionmaker(bind=engine)
session = Session()

@app.route('/')
def base_route():
    return 'Base Transaction Route'

# Service to save transactions that are input by user
# Must include type, currency code, and amount in json format
# Currency code must be BTC or ETH
@app.route('/store_transaction/', methods=['POST'])
def store_transaction():

    # Grab the json that was posted
    posted_json = request.json

    # Hard coded to USD for demonstration purposes
    quote_currency_code = 'USD'

    try:
        # Pull the usd value of the currency code passed in to be stored as amount_usd
        response = requests.get(PRICING_SERVICE_URL + posted_json['currency_code'] + '/'  + quote_currency_code).json()
    except requests.exceptions.RequestException as e:  
        # If there is an error, return the error message
        return logger.error(e)

    # Create new transaction object
    new_transaction = Transactions(
        id=str(uuid.uuid4()),
        datetime=datetime.now(),
        type=posted_json['type'],
        currency_code=posted_json['currency_code'],
        amount=Decimal(posted_json['amount']),
        amount_usd=Decimal(posted_json['amount']) * Decimal(response['close_price']) # Calc amount usd based off of close price of /price/ endpoint
    )
  
    # Add transaction to db
    session.add(new_transaction)
    # Commit transaction to db
    session.commit()

    # Set notification message body
    message_body = {
        'type': 'transaction',
        'message': 'New transaction added to db',
        'body': {
            'id': new_transaction.id,
            'datetime': new_transaction.datetime.strftime("%m-%d-%Y %H:%M:%S"),
            'type': new_transaction.type,
            'currency_code': new_transaction.currency_code,
            'amount': str(new_transaction.amount),
            'amount_usd': str(new_transaction.amount_usd)
        }
    }

    try:
        # Send notification to thrall service
        response = requests.post(NOTIFICATION_SERVICE_URL, json=message_body)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        # If there is an error, return the error message
        return logger.error(e)

    # Return if transactions successfully saved
    return 'Transaction successfully saved and notification sent to queue.'


if __name__ == '__main__':
    # Force to run on specific ports set in env vars
    app.run(host=os.environ.get('HTTP_HOST'),
        port=int(os.environ.get('HTTP_PORT')))