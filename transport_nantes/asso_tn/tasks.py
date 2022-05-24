import time

from celery import shared_task

@shared_task
def compute_sum_slowly(n):
    """Compute the sum_{i=0}^n slowly.
    """
    sum = 0
    for i in range(n):
        time.sleep(1)
        sum += i
    print(f"The sum is {sum}.")
