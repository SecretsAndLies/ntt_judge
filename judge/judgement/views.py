import random
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages

from .models import Problem, Solution
from scipy.stats import rankdata

from .forms import CodeForm
from time import sleep

import inflect


def index(request):
    # todo: sort problems by requested, filter problems
    return render(request,"judgement/problems.html", {"problems":Problem.objects.all()})


def problem(request, problem_id):
    if request.method == "POST":
        form = CodeForm(request.POST)
        if form.is_valid():
            code_text = form.cleaned_data["code"]
            if(execute_code(code_text)):
                # execute the code and get the solution id (hard coded as 1)
                return solution(request, problem_id,)
            else:
                # todo: eventually this will be an error message given from the CPU Emulator.
                messages.error(request, "Failed to compile")
                render(request, 
                       "judgement/problem.html", 
                       {"form": form,"problem":Problem.objects.get(id=problem_id)})
    else:
        form = CodeForm()

    return render(request, "judgement/problem.html", {"form": form,"problem":Problem.objects.get(id=problem_id)})

def calculate_percentile(rank, total):
    return (rank / total) * 100

def solution(request, problem_id):  
    problem = Problem.objects.get(id=problem_id)
    solutions = Solution.objects.filter(problem=problem)
    # todo actually calculate these.
    rom = random.randint(1,100)
    ram = random.randint(1,100)
    cycles = random.randint(1,1000)

    user_solution = Solution(problem=problem,cycles=cycles,rom=rom,ram=ram)
    user_solution.save()

    rom_values = [solution.rom for solution in solutions]
    ram_values = [solution.ram for solution in solutions]
    cycles_values = [solution.cycles for solution in solutions]

    rom_ranks = rankdata(rom_values, method='min')
    ram_ranks = rankdata(ram_values, method='min')
    cycles_ranks = rankdata(cycles_values, method='min')

    user_rom_rank = rom_ranks[-1]
    user_ram_rank = ram_ranks[-1]
    user_cycles_rank = cycles_ranks[-1]

    total_solutions = len(solutions)

    user_rom_percentile = calculate_percentile(user_rom_rank, total_solutions)
    user_ram_percentile = calculate_percentile(user_ram_rank, total_solutions)
    user_cycles_percentile = calculate_percentile(user_cycles_rank, total_solutions)

    # Prettier number formats. Used to change 1 into 1st, and 99 into 99th etc.
    p = inflect.engine() 

    # (percentiles, ranks, histogram)
    context = {
        'problem': problem,
        'solutions': solutions,
        'user_solution': user_solution,
        'rom_rank': user_rom_rank,
        'cycle_rank': user_cycles_rank,
        'ram_rank': user_ram_rank,
        'out_of_rank': total_solutions,
        'ram_percentile': p.ordinal(round(user_ram_percentile)),
        'rom_percentile': p.ordinal(round(user_rom_percentile)),
        'cycle_percentile': p.ordinal(round(user_cycles_percentile)),
        'tests_passed': 11,  # todo change
        'tests_total': 11,  # todo change
    }

    return render(request,"judgement/solved.html", context)

# Executes the code and populates the solutions object if it's a solution.
def execute_code(code):
    # if the code doesn't solve, we need to know how many of the test cases it passed.
    # sleep(1)
    if(code=="a"):
        return True
    return False