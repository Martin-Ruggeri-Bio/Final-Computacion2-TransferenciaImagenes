from celery import Celery

app = Celery('tasks', broker='redis://localhost:6379/0')
app.conf.update(result_backend='redis://localhost:6380/0')


@app.task
def add(x, y):
    return x + y

@app.task
def mul(x, y):
    return x * y

def run_tasks(x, y):
    add_task = add.apply_async((x, y))
    mul_task = mul.apply_async((x, y))
    return add_task.get() + mul_task.get()

result = run_tasks(5, 5)
print(result.get())