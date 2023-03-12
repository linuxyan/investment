import math
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from functools import wraps

import numpy as np
import pandas as pd
from config import db_file
from sqlalchemy import Column, Float, Integer, String, create_engine, func
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker
from sqlalchemy.pool import StaticPool

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
    name = Column(String(50), nullable=False, doc="股票名称")
    year = Column(String(50), nullable=True, doc="R15年份")
    start_date = Column(String(50), nullable=True, doc="R15开始时间")
    end_date = Column(String(50), nullable=True, doc="R15结束时间")
    roe_mean = Column(String(50), nullable=True, doc="10年算数平均ROE")
    roe_min = Column(String(50), nullable=True, doc="10年最低ROE")
    debt_to_assets = Column(String(50), nullable=True, doc="资产负债率%")

    def to_json(self):
        dict_ = self.__dict__
        if "_sa_instance_state" in dict_:
            del dict_["_sa_instance_state"]
        return dict_


class DailyBasic(Base):
    __tablename__ = 'daily_basic'
    id = Column(Integer, primary_key=True)
    ts_code = Column(String(50), nullable=False, doc="TS代码")
    trade_date = Column(String(50), nullable=True, doc="交易日期")
    close = Column(String(50), nullable=True, doc="当日收盘价")
    pe_ttm = Column(Float(), nullable=True, doc="市盈率(TTM)")
    ps_ttm = Column(Float(), nullable=True, doc="市销率(TTM)")
    dv_ttm = Column(Float(), nullable=True, doc="股息率(TTM)%")
    total_share = Column(Float(), nullable=True, doc="总股本")
    total_mv = Column(Float(), nullable=True, doc="总市值")

    def to_json(self):
        dict_ = self.__dict__
        if "_sa_instance_state" in dict_:
            del dict_["_sa_instance_state"]
        return dict_


# 标准差计算
class StdevFunc:
    def __init__(self):
        self.M = 0.0
        self.S = 0.0
        self.k = 1

    def step(self, value):
        if value is None:
            return
        tM = self.M
        self.M += (value - tM) / self.k
        self.S += (value - tM) * (value - self.M)
        self.k += 1

    def finalize(self):
        if self.k < 3:
            return None
        return math.sqrt(self.S / (self.k - 2))


class DBManager:
    def __init__(self):
        self.engine = create_engine('sqlite://', poolclass=StaticPool, creator=self.__sqlite_engine_creator)
        # if not os.path.exists(db_file):
        #     Base.metadata.create_all(self.engine)
        Base.metadata.create_all(self.engine)

    def __sqlite_engine_creator(self):
        con = sqlite3.connect(db_file)
        con.create_aggregate("stdev", 1, StdevFunc)
        return con

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

    @class_dbsession
    def get_fina_indicator_debt_to_assets(self, session, ts_code_list, end_date):
        fina_indicator_debt_to_assets = (
            session.query(FinaIndicator)
            .filter(FinaIndicator.ts_code.in_(ts_code_list))
            .filter(FinaIndicator.end_date == end_date)
            .all()
        )
        if fina_indicator_debt_to_assets:
            fina_indicator_debt_to_assets = list(map(lambda x: x.to_json(), fina_indicator_debt_to_assets))
            fina_indicator_debt_to_assets = pd.DataFrame(
                fina_indicator_debt_to_assets,
                columns=[
                    'ts_code',
                    'ann_date',
                    'end_date',
                    'roe_waa',
                    'netprofit_yoy',
                    'debt_to_assets',
                    'netprofit_margin',
                    'grossprofit_margin',
                ],
            )
            return fina_indicator_debt_to_assets[['ts_code', 'debt_to_assets']]
        else:
            return None

    @class_dbsession
    def get_daily_basic_last(self, session, ts_code):
        daily_basic_last = (
            session.query(DailyBasic).filter_by(ts_code=ts_code).order_by(DailyBasic.trade_date.desc()).first()
        )

        if daily_basic_last:
            return daily_basic_last.to_json()
        else:
            return None

    @class_dbsession
    def count_r15(self, session, year):
        max_end_date = int(str(year) + '0101')
        min_end_date = int(str(int(year) - 7) + '1231')
        r15 = (
            session.query(
                FinaIndicator.ts_code,
                StockBasic.name,
                func.avg(FinaIndicator.roe_waa),
                func.min(FinaIndicator.roe_waa),
                func.count(FinaIndicator.roe_waa),
                func.stdev(FinaIndicator.netprofit_yoy),
            )
            .filter(
                FinaIndicator.ts_code == StockBasic.ts_code,
                FinaIndicator.end_date < max_end_date,
                FinaIndicator.end_date >= min_end_date,
            )
            .group_by(FinaIndicator.ts_code)
            .having(
                func.count(FinaIndicator.roe_waa) == 7,
                func.avg(FinaIndicator.roe_waa) >= 20,
                func.min(FinaIndicator.roe_waa) >= 15,
                func.stdev(FinaIndicator.netprofit_yoy) <= 60,
            )
            .all()
        )
        if r15:
            r15_pd = pd.DataFrame(r15, columns=['ts_code', 'name', 'roe_mean', 'roe_min', 'year', 'net_std'])
            r15_pd['roe_mean'] = np.round(r15_pd['roe_mean'], 2)
            return r15_pd
        else:
            None
        # select ts_code,avg(roe_waa) as roe_mean,min(roe_waa) as roe_min, count(roe_waa) as roe_count, stdev(netprofit_yoy) as netprofit_yoy_std from fina_indicator where end_date < 20190101 and end_date >= 20121231 GROUP BY ts_code HAVING roe_mean >= 20 and roe_min >= 15 and roe_count == 7 and netprofit_yoy_std <= 60;

    @class_dbsession
    def query_r15(self, session, year=None):
        if year:
            start_date = int(str(year) + '0501')
            end_date = int(str(year + 1) + '0430')
            r15 = session.query(R15).filter(R15.start_date >= start_date, R15.end_date <= end_date).all()
        else:
            r15 = session.query(R15).all()

        if r15:
            r15_list = list(map(lambda x: x.to_json(), r15))
            return pd.DataFrame(
                r15_list, columns=['ts_code', 'name', 'start_date', 'end_date', 'roe_mean', 'roe_min', 'debt_to_assets']
            )
        else:
            None

    @class_dbsession
    def drop_r15(self, session, year):
        start_date = int(str(year) + '0501')
        end_date = int(str(year + 1) + '0430')
        session.query(R15).filter(R15.start_date >= start_date, R15.end_date <= end_date).delete()
