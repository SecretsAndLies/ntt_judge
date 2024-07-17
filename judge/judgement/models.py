from django.db import models

class Problem(models.Model):
    title = models.CharField(max_length=280)
    description = models.TextField(default="""Problem description.
                                   
Inputs
RAM[0] = 12
RAM[1] = 12
                                    
Outputs
RAM[2] = 12
""")
    rating = models.PositiveIntegerField() # 1=easy, 2==medium, 3==hard
    added = models.DateTimeField(auto_now_add=True)
    tst_file_text = models.TextField(default="""//NOTE: You may load this file as a .tst into your simulator to help debug your code.
load assembly.hack,
output-file assembly.out,
compare-to compare.cmp,
""")
    cmp_file_text = models.TextField()
    timeout_cycles = models.PositiveIntegerField(default=0, 
                                                 help_text ="""The max number of cycles you students have to run your entire test code. 0 is infinite (Python will time out the CPU Emulator after 30 seconds)."""
                                                 )
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