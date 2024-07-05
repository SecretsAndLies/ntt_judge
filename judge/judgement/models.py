from django.db import models

class Problem(models.Model):
    title = models.CharField(max_length=280)
    description = models.CharField(max_length=100000)
    rating = models.PositiveIntegerField # 1=easy, 2==medium, 3==hard
    test_file = models.FileField # a txt file which contains keypresses, cycles to run, and output?
    def __str__(self):
        return self.title + " " + self.description

class Solution(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    cycles = models.PositiveIntegerField
    rom = models.PositiveIntegerField
    ram = models.PositiveIntegerField