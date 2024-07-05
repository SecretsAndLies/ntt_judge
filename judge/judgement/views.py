from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages

from .models import Problem, Solution

from .forms import CodeForm
from time import sleep

def index(request):
    # todo: sort problems by requested, filter problems
    return render(request,"judgement/problems.html", {"problems":Problem.objects.all()})


def problem(request, problem_id):
    if request.method == "POST":
        form = CodeForm(request.POST)
        if form.is_valid():
            code_text = form.cleaned_data["code"]
            # todo: execute the code. If it suceeds, get their solution id, and show the stats page, otherwise return the failure page.
            if(execute_code(code_text)):
                return HttpResponse("SUCESS")
            else:
                messages.error(request, "Failed to compile")
                render(request, 
                       "judgement/problem.html", 
                       {"form": form,"problem":Problem.objects.get(id=problem_id)})
    else:
        form = CodeForm()

    return render(request, "judgement/problem.html", {"form": form,"problem":Problem.objects.get(id=problem_id)})

def solution(request,problem_id, solution_id):
    return HttpResponse("Nothing")

# Executes the code and populates the solutions object if it's a solution.
def execute_code(code):
    sleep(2)
    if(code=="a"):
        return True
    return False