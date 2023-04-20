from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Numeric

Base = declarative_base()

class Transactions(Base):
    __tablename__ = 'transactions'
    id = Column(String, primary_key=True)
    datetime = Column(DateTime)
    type = Column(String)
    currency_code = Column(String)
    amount = Column(Numeric)
    amount_usd = Column(Numeric)
    

    def __repr__(self):
        return "<Transactions(datetime='%s', type='%s', currency_code='%s', amount='%s', amount_usd='%s')>" % (
            self.datetime, self.type, self.currency_code, self.amount, self.amount_usd)