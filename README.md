JobtasticMixins
===============

## Package includes:

#### AVGTimeRedis class
The class that helps automate calculate an avarage time
for different kind tasks and saves result into Redis DB


## Install
Install from Github

```pip install https://github.com/abbasovalex/JobtasticMixins/archive/master.zip```


## Usage

1. You must will add the mixin class as first argument
2. You should set ```default_avg_time``` in the seconds 
3. You must use ```self.update_progress()``` without arguments

```python
class YourTask(AVGTimeRedis, JobtasticTask):
    default_avg_time = 60 # 1 minute
    
    ...
    
    def calculate_result(self, ..., **kwargs):
        ...
```

```default_avg_time``` used when task still never calculated
It will be encompass arithmetical mean after task was executed.
Forecast accuracy depends from count executed tasks 


### Example with AVGTimeRedis class

The class that helps automate calculate an avarage time for different kind
tasks and saves result into Redis DB

Let's take a look at the example task using with JobtasticMixins and
AVGTimeRedis class:

``` python
from time import sleep
from jobtastic import JobtasticTask
from jobtasticmixins import AVGTimeRedis


class LotsOfDivisionTask(AVGTimeRedis, JobtasticTask):
    """
    Division is hard. Make Celery do it a bunch.
    """
    significant_kwargs = [
        ('numerators', str),
        ('denominators', str),
    ]
    herd_avoidance_timeout = 60
    cache_duration = 0
    # optional variable was added. by default is 30 seconds   
    default_avg_time = 90

    def calculate_result(self, numerators, denominators, **kwargs):
        results = []
        for count, divisors in enumerate(zip(numerators, denominators)):
            numerator, denominator = divisors
            results.append(numerator / denominator)
            # it will be auto calculated
            self.update_progress()
            sleep(0.1)

        # set finish=True for avoid trouble
        self.update_progress(finish=True)
        return results

```

Under the hood:

1. AVGTimeRedis gets settings.BROKER_URL and connects to Redis 
2. It counts the tasks and the workers and uses to calculating 

More details you can see into [source](https://github.com/abbasovalex/JobtasticMixins/blob/master/jobtasticmixins/mixins.py)
