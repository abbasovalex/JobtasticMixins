JobtasticMixins
===============

## Package includes:

#### AVGTimeRedis class
The class that helps automate calculate an avarage time
for different kind tasks and saves result into Redis DB


## Install
Install from Github

```pip install git+https://github.com/abbasovalex/JobtasticMixins```


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
