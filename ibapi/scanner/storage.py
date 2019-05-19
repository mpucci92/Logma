from collections import deque
from datetime import datetime, timedelta

fmt = '%Y-%m-%d %H:%M:00'

class Storage(object):
    
    def __init__(self, symbol, num_periods, time_period):
        
        self.data = deque([], maxlen=num_periods)
        self.num_periods = num_periods
        self.time_period = time_period
        
        self.fmt = '%Y-%m-%d %H:%M:00'
        
        self.current_candle_time = self.candle_time()
        self.current_candle = None
        
    def candle_time(self):
        
        dt = datetime.now()
        dt -= timedelta(minutes = dt.minute % self.time_period)
        return dt.strftime(self.fmt)
    
    def update(self, bar):
        
        if self.current_candle_time == bar.date:
            self.current_candle = (bar.date, bar.open, bar.high, bar.low, bar.close)
            
    def on_period(self):
        
        self.append(self.current_candle)
        self.current_candle_time = self.candle_time()
        
    def append(self, bar):

        self.data.append((bar.date, bar.open, bar.high, bar.low, bar.close))
    
    def is_initialized(self):
        
        return len(self.data) == self.num_periods