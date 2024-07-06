from django.db import models

class Problem(models.Model):
    title = models.CharField(max_length=280)
    description = models.TextField()
    rating = models.PositiveIntegerField() # 1=easy, 2==medium, 3==hard
    added = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title + " " + self.description

class Solution(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    cycles = models.PositiveIntegerField()
    rom = models.PositiveIntegerField()
    ram = models.PositiveIntegerField()
    added = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.problem.title} | cycles: {self.cycles} rom: {self.rom} ram: {self.ram}"

class Test(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    test_file_text = models.TextField() # this is run by the CPU Emulator
    test_description = models.TextField() # this is shown to the user
    title = models.CharField(max_length=280)
    def __str__(self):
        return f"{self.problem.title} {self.title}"
