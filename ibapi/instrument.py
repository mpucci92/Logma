from apscheduler.schedulers.background import BlockingScheduler

from zmodel import Model

from datetime import datetime
from threading import Thread
import time

class Instrument(Thread):
    
    def __init__(self, ticker, time_period, short_num_periods, num_periods, log_trim, manager, storage, 
                 n_times_per_second):
        
        ## Book keeping
        self.ticker = ticker
        self.time_period = time_period
        self.short_num_periods = short_num_periods
        self.num_periods = num_periods
        self.log_trim = log_trim
        
        ## Evaluation granularity
        self.n_times_per_second = n_times_per_second
        self.n_micros = int(1e6 / n_times_per_second)
        
        ## Get ML Model
        self.model = Model(ticker = ticker, short_period = short_num_periods, long_period = num_periods,
                           log_trim = log_trim)
        
        ## Storage object for historical data
        self.storage = storage
        
        ## Manager to execute trades
        self.manager = manager
        
    def scanner_job(self):
    
        ## Update the storage object
        self.storage.on_period()

        ## Evaluate the current candle for a signal
        signal, features, direction, price = self.model.is_trade(list(self.storage.data))

        ## Start a trade if we have a signal
        if signal and self.ticker not in self.manager.trades:

            ## Initiate the trade via the order manager
            self.manager.on_signal(direction = direction, quantity = 20000, symbol = self.ticker, price = price)

            ## Pause the scanner job
            #self.blocker.pause('scanner_job')

            ## Resume the manager job
            self.blocker.resume('manager_job')
            
    def manager_job(self):
    
        ## Check that the position hasnt been closed / not filled
        if self.ticker in self.manager.trades:

            self.manager.trades[self.ticker].on_period()

        ## Trade has been removed aka closed or not filled
        else:

            # Pause the current job
            self.blocker.pause('manager_job')

            # Resume the scanner job
            #self.blocker.resume('scanner_job')
            
    def microsecond_job(self, job_func, params):
        
        micros = datetime.now().microsecond
        
        while int(micros / self.n_micros) < self.n_times_per_second - 1:
            
            job_func(*params)
            
            micros = datetime.now().microsecond
            time.sleep(1.0 / self.n_times_per_second)
    
    def run(self):
        
        ## Scheduler to run
        job_defaults = {
            'coalesce': True,
            'max_instances': 1
        }
        self.blocker = BlockingScheduler(job_defaults = job_defaults)
        self.blocker.add_job(self.microsecond_job, 'cron', second='*', id='manager_job', next_run_time=None, args=(self.manager_job, ()))
        self.blocker.add_job(self.scanner_job, 'cron', minute='*', id='scanner_job')
        
        self.blocker.start()