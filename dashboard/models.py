from django.db import models

class Employee(models.Model):
    employee_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    attendance = models.FloatField()         # percentage
    performance_rating = models.FloatField() # score out of 10
    experience = models.IntegerField()       # years
    salary = models.FloatField()
    project_completion_rate = models.FloatField()

    def __str__(self):
        return self.name