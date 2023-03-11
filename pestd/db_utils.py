import os
from contextlib import contextmanager
from datetime import datetime
from functools import wraps

import pandas as pd
from config import db_file
from sqlalchemy import Column, Float, Integer, String, create_engine, func
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

Base = declarative_base()


class StockBasic(Base):
    __tablename__ = 'stock_basic'
    ts_code = Column(String(50), primary_key=True, doc="TS代码")
    name = Column(String(50), nullable=False, doc="股票名称")
    area = Column(String(50), nullable=True, doc="地域")
    industry = Column(String(50), nullable=True, doc="所属行业")
    list_date = Column(String(50), nullable=True, doc="上市日期")


# 财务指标数据
class FinaIndicator(Base):
    __tablename__ = 'fina_indicator'
    id = Column(Integer, primary_key=True)
    ts_code = Column(String(50), nullable=False, doc="TS代码")
    ann_date = Column(String(50), nullable=True, doc="公告日期")
    end_date = Column(String(50), nullable=True, doc="报告期")
    roe_waa = Column(Float(), nullable=True, doc="加权平均净资产收益率")
    netprofit_yoy = Column(Float(), nullable=True, doc="归属母公司股东的净利润同比增长率(%)")
    debt_to_assets = Column(Float(), nullable=True, doc="资产负债率")
    netprofit_margin = Column(Float(), nullable=True, doc="销售净利率")
    grossprofit_margin = Column(Float(), nullable=True, doc="销售毛利率")

    def to_json(self):
        dict_ = self.__dict__
        if "_sa_instance_state" in dict_:
            del dict_["_sa_instance_state"]
        return dict_


class R15(Base):
    __tablename__ = 'r15'
    id = Column(Integer, primary_key=True)
    ts_code = Column(String(50), nullable=False, doc="TS代码")
    start_date = Column(String(50), nullable=True, doc="R15开始时间")
    end_date = Column(String(50), nullable=True, doc="R15结束时间")
    roe_mean = Column(String(50), nullable=True, doc="10年算数平均ROE")
    roe_min = Column(String(50), nullable=True, doc="10年最低ROE")


class DBManager:
    def __init__(self):
        self.engine = create_engine('sqlite:///' + db_file)
        if not os.path.exists(db_file):
            Base.metadata.create_all(self.engine)

    @contextmanager
    def db_session(self):
        session = scoped_session(sessionmaker(bind=self.engine, expire_on_commit=False))()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            if session:
                session.close()

    def class_dbsession(func):
        def wrapper(*args, **kwargs):
            cls, new_args = args[0], args[1:]
            with cls.db_session() as session:
                return func(cls, session, *new_args, **kwargs)

        return wrapper

    @class_dbsession
    def get_stock_basic(self, session, list_date_start=19900101, list_date_end=int(datetime.now().strftime('%Y%m%d'))):
        stock_basics = (
            session.query(StockBasic)
            .filter(StockBasic.list_date >= int(list_date_start), StockBasic.list_date <= int(list_date_end))
            .all()
        )
        if stock_basics:
            return pd.DataFrame.from_records(
                [
                    {
                        'ts_code': stock_basic.ts_code,
                        'name': stock_basic.name,
                        'area': stock_basic.area,
                        'industry': stock_basic.industry,
                        'list_date': stock_basic.list_date,
                    }
                    for stock_basic in stock_basics
                ]
            )
        else:
            return pd.DataFrame()

    @class_dbsession
    def get_fina_indicator_last(self, session, ts_code):
        fina_indicator_last = (
            session.query(FinaIndicator).filter_by(ts_code=ts_code).order_by(FinaIndicator.end_date.desc()).first()
        )

        if fina_indicator_last:
            return fina_indicator_last.to_json()
        else:
            return None

    # @class_dbsession
    # def add_user(self, session, name, age):
    #     user = User(name=name, age=age)
    #     session.add(user)

    # @class_dbsession
    # def delete_user(self, session, user_id):
    #     user = session.query(User).filter_by(id=user_id).first()
    #     if user:
    #         session.delete(user)

    # @class_dbsession
    # def update_user(self, session, user_id, name, age):
    #     user = session.query(User).filter_by(id=user_id).first()
    #     if user:
    #         user.name = name
    #         user.age = age

    # @class_dbsession
    # def get_user(self, session, user_id):
    #     user = session.query(User).filter_by(id=user_id).first()
    #     if user:
    #         return pd.DataFrame.from_records([{'id': user.id, 'name': user.name, 'age': user.age}])
    #     else:
    #         return pd.DataFrame()

    # @class_dbsession
    # def get_all_users(self, session):
    #     users = session.query(User).all()
    #     df = pd.DataFrame.from_records([{'id': user.id, 'name': user.name, 'age': user.age} for user in users])
    #     return df
