# -*- coding: utf-8 -*-
import redis
try:
    import simplejson as json
except:
    import json
from time import time
from datetime import timedelta
from celery.utils.log import get_task_logger
from celery.signals import task_postrun
from celery.task.control import inspect
from jobtastic.states import PROGRESS
from django.conf import settings

logger = get_task_logger(__name__)


class AVGTimeRedis(object):
    """
    Calculating average time of executing task

    For any task would be created own key. By the key
    can be get average time the task
    """

    # initial value for cases when
    # DB still hasn't value and user not set
    # initial value for own type task
    default_avg_time = 30

    @classmethod
    def delay_or_eager(cls, *args, **kw):
        t_start = int(time())
        t_estimated = t_start + timedelta(seconds=cls.estimated_waiting()).seconds

        celery_task_key = 'celery_%s' % cls.name
        instance = super(AVGTimeRedis, cls).delay_or_eager(*args, **kw)
        try:
            r = redis.from_url(settings.BROKER_URL)
            fields = {
                '%s_time_start' % instance.task_id: t_start,
                '%s_time_estimated' % instance.task_id: t_estimated,
            }
            r.hmset(celery_task_key, fields)
        except Exception as e:
            logger.debug(e)
            logger.debug('Redis doesn\'t work 1')
        return instance

    @classmethod
    def delay_or_fail(cls, *args, **kw):
        # logger from here would be log to django.log
        return super(AVGTimeRedis, cls).delay_or_fail(*args, **kw)

    @task_postrun.connect
    def stop_executing_time(task_id, task, args, kwargs, retval, state, **kw):
        try:
            r = redis.from_url(settings.BROKER_URL)
            celery_task_key = 'celery_%s' % task.__class__.name
            t_start = r.hget(celery_task_key, '%s_time_start' % task_id)
            t_task = int(time()) - int(t_start)
            new_t_avg = None
            t_avg = r.hget(celery_task_key, 'avg_time')
            if t_avg:
                new_t_avg = abs((int(t_avg) + t_task) / 2)
            r.hset(celery_task_key, 'avg_time', new_t_avg or t_task)
            r.hdel(celery_task_key,
                   '%s_time_start' % task_id,
                   '%s_time_estimated' % task_id)
        except Exception as e:
            logger.debug(e)
            logger.debug('Redis doesn\'t work 2')

    @classmethod
    def celery_avg_time_task(cls):
        """ Return seconds or None """
        try:
            r = redis.from_url(settings.BROKER_URL)
            celery_task_key = 'celery_%s' % cls.name
            return abs(int(r.hget(celery_task_key, 'avg_time')))
        except Exception as e:
            logger.debug(e)
            logger.debug('Redis doesn\'t work 3')
            return None

    @classmethod
    def estimated_waiting(cls):
        """
            calculate how much remain
            time before task would be executed
        """
        tasks_reserved = inspect().reserved()
        count_workers = len(tasks_reserved.keys())
        count_tasks_reserved = sum(len(v) for k,v in tasks_reserved.items()) or 1
        avg_time = cls.celery_avg_time_task() or cls.default_avg_time
        if count_tasks_reserved == 1:
            return avg_time * count_tasks_reserved
        else:
            return avg_time * count_tasks_reserved / count_workers

    def update_progress(self, finish=None):
        """ Function was rewritten from original """
        if self.request.id:
            if finish:
                self.update_state(None, PROGRESS, {
                    'progress_percent': 100,
                    'time_remaining': 0,
                })
            else:
                try:
                    r = redis.from_url(settings.BROKER_URL)
                    celery_task_key = 'celery_%s' % self.__class__.name
                    t_start, t_estimated = r.hmget(celery_task_key,
                                                   ['%s_time_start' % self.request.id,
                                                    '%s_time_estimated' % self.request.id])
                    t_start, t_estimated = int(t_start), int(t_estimated)
                    cur_time = int(time())
                    total_time = t_estimated - t_start
                    part_time = cur_time - t_start
                    if total_time:
                        progress_percent = 100 * part_time / total_time
                        time_remaining = t_estimated - cur_time
                    else:
                        progress_percent = 100
                        time_remaining = 0

                    self.update_state(None, PROGRESS, {
                        'progress_percent': progress_percent,
                        'time_remaining': time_remaining,
                    })
                except Exception as e:
                    logger.debug(e)
                    logger.debug('Redis doesn\'t work 4')
