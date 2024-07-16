from django.db import models

class Problem(models.Model):
    title = models.CharField(max_length=280)
    description = models.TextField()
    rating = models.PositiveIntegerField() # 1=easy, 2==medium, 3==hard
    added = models.DateTimeField(auto_now_add=True)
    tst_file_text = models.TextField(default="""//NOTE: The load, output-file and compare-to shouldn't be changed. They are provided here for offline simulator use.
load assembly.hack,
output-file assembly.out,
compare-to compare.cmp,
""")
    cmp_file_text = models.TextField()
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