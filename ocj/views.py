import sys
import requests
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from .forms import *
from django.http import JsonResponse, HttpResponseForbidden
from .models import *
from django.views.decorators.csrf import csrf_exempt
import subprocess
import docker
from datetime import datetime
from time import time
import os
from django.conf import settings
def index(request):
    return render(request,"index.html")

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = LoginForm()
        return render(request, 'login.html', {'form': form})



def signup_view(request):
    if request.method == 'POST':
        form = signupform(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = signupform()
    return render(request, 'signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')
from django.http import HttpResponseForbidden


# @csrf_exempt
def problems_view(request):
    problems = Problem.objects.all()
    context = {'problems': problems}
    return render(request, 'problems.html', context)

@csrf_exempt
def problem_detail(request, pk):
    try:
        problem = Problem.objects.get(pk=pk)
    except Problem.DoesNotExist:
        return JsonResponse({'error': 'Problem does not exist'}, status=404)

    if request.method == 'GET':
        problem = Problem.objects.filter(id=pk)
        testcaselist = Testcase.objects.filter(problem_id=pk)
        testcase = testcaselist[0]

        return render(request, 'probView.html', {'problem': problem[0],'testcase':testcase})

def execute(request,pk):
    problem = Problem.objects.filter(id=pk)
    if request.method == 'POST':
        code_part = request.POST['user_code']
        input_part = request.POST['input_area']
        y = input_part
        input_part = input_part.replace("\n", " ").split()
        def input():
            a = input_part[0]
            del input_part[0]
            # return input_part
            return a
        try:
            orig_stdout = sys.stdout
            sys.stdout = open('file.txt', 'w')
            exec(code_part)
            sys.stdout.close()
            sys.stdout = orig_stdout
            output = open('file.txt', 'r').read()
        except Exception as e:
            sys.stdout.close()
            sys.stdout = orig_stdout
            output = e
        # print(output)
    res = render(request, 'probView.html', {"user_code": code_part, "input": y, "output": output,"problem":problem[0]})
    return res

def leaderboard_view(request):
    return render(request,'leaderboard.html')
def submission(request):
    submissions = Submissions.objects.filter(user=request.user)
    sorted_submissions = sorted(submissions, key=lambda x: x.submission_time, reverse=True)

    context = {'submissions': sorted_submissions}
    return render(request, 'submission.html', context)

@csrf_exempt
def submission_detail(request, pk):
    try:
        submission = Submissions.objects.get(pk=pk)
    except Submissions.DoesNotExist:
        return JsonResponse({'error': 'Submission does not exist'}, status=404)

    if request.method == 'GET':
        submission = Submissions.objects.filter(id=pk)


        # testcaselist = Testcase.objects.filter(problem_id=pk)
        # testcase = testcaselist[0]
        context = {'submission': submission[0]}
        return render(request, 'submissionView.html', context)


def verdictPage(request, problem_id):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'run':
            return execute(request,problem_id)
        # setting docker-client
        
        docker_client = docker.from_env()
        Running = "running"

        problem = Problem.objects.get(id=problem_id)
        testcaselist=Testcase.objects.filter(problem_id=problem_id)
        testcase=testcaselist[0]

        testcase.output = testcase.output.replace('\r\n', '\n').strip()
        score=100

        # setting verdict to wrong by default
        verdict = "Wrong Answer"
        res = ""
        run_time = 0

        # extract data from form
        form = CodeForm(request.POST)
        user_code = ''
        if form.is_valid():
            user_code = form.cleaned_data.get('user_code')
            user_code = user_code.replace('\r\n', '\n').strip()

        language = request.POST['language']
        submission = Submissions(user=request.user, problem=problem, submission_time=datetime.now(),
                                language=language, user_code=user_code)
        submission.save()

        filename = str(submission.id)

        # if user code is in C++
        if language == "C++":
            extension = ".cpp"
            cont_name = "oj-cpp"
            compile = f"g++ -o {filename} {filename}.cpp"
            clean = f"{filename} {filename}.cpp"
            docker_img = "gcc:11.2.0"
            exe = f"./{filename}"

        elif language == "C":
            extension = ".c"
            cont_name = "oj-c"
            compile = f"gcc -o {filename} {filename}.c"
            clean = f"{filename} {filename}.c"
            docker_img = "gcc:11.2.0"
            exe = f"./{filename}"

        elif language == "Python3":
            extension = ".py"
            cont_name = "oj-py3"
            compile = "python3"
            clean = f"{filename}.py"
            docker_img = "python"
            exe = f"python {filename}.py"

        elif language == "Java":
            filename = "Main"
            extension = ".java"
            cont_name = "oj-java"
            compile = f"javac {filename}.java"
            clean = f"{filename}.java {filename}.class"
            docker_img = "openjdk"
            exe = f"java {filename}"

        file = filename + extension
        filepath = settings.FILES_DIR + "/" + file
        code = open(filepath, "w")
        code.write(user_code)
        code.close()

        # checking if the docker container is running or not
        try:

            container = docker_client.containers.get(cont_name)
            container_state = container.attrs['State']
            container_is_running = (container_state['Status'] == Running)
            print("docker",container_is_running)
            if not container_is_running:
                subprocess.run(f"docker start {cont_name}", shell=True)
        except docker.errors.NotFound:
            subprocess.run(f"docker run -dt --name {cont_name} {docker_img}", shell=True)

        # copy/paste the .cpp file in docker container
        subprocess.run(f"docker cp {filepath} {cont_name}:/{file}", shell=True)

        # compiling the code
        cmp = subprocess.run(f"docker exec {cont_name} {compile}", capture_output=True, shell=True)

        if cmp.returncode != 0:
            verdict = "Compilation Error"
            subprocess.run(f"docker exec {cont_name} rm {file}", shell=True)
            user_stderr = cmp.stderr.decode('utf-8')
            submission.user_stderr = user_stderr

        else:
            # running the code on given input and taking the output in a variable in bytes
            for testcase_i in testcaselist:
                # copy/paste the .cpp file in docker container
                subprocess.run(f"docker cp {filepath} {cont_name}:/{file}", shell=True)
                # compiling the code
                cmp = subprocess.run(f"docker exec {cont_name} {compile}", capture_output=True, shell=True)

                start = time()
                try:
                    command = ["docker", "exec", cont_name, "sh", "-c", f'echo "{testcase_i.input}" | {exe}']
                    res = subprocess.run(command, capture_output=True, timeout=2000)
                    run_time = time() - start
                    subprocess.run(f"docker exec {cont_name} rm {clean}", shell=True)

                except subprocess.TimeoutExpired:
                    run_time = time() - start
                    verdict = "Time Limit Exceeded"
                    subprocess.run(f"docker container kill {cont_name}", shell=True)
                    subprocess.run(f"docker start {cont_name}", shell=True)
                    subprocess.run(f"docker exec {cont_name} rm {clean}", shell=True)
                    break
                if verdict != "Time Limit Exceeded" and res.returncode != 0:
                    verdict = "Runtime Error"
                    break
                if verdict == "Accepted" or verdict == "Wrong Answer":
                    user_stdout= res.stdout.decode('utf-8')
                    submission.user_stdout = user_stdout

                    if str(user_stdout) == str(testcase_i.output):
                        verdict = "Accepted"
                        print("result:", user_stdout, testcase_i.output,verdict)
                    else:
                        verdict = "Wrong Answer"
                        print("result:", user_stdout, testcase_i.output, verdict)
                        break

            print(verdict)

        # leaderboard
        # user = User.objects.get(username=request.user)
        # previous_verdict = Submissions.objects.filter(user=user.id, problem=problem, verdict="Accepted")
        # if len(previous_verdict) == 0 and verdict == "Accepted":
            # user.total_score += score
            # user.total_solve_count += 1
            # if problem.difficulty == "Easy":
            #     user.easy_solve_count += 1
            # elif problem.difficulty == "Medium":
            #     user.medium_solve_count += 1
            # else:
            #     user.tough_solve_count += 1
            # user.save()
        submission.verdict = verdict
        submission.run_time = run_time
        submission.save()
        os.remove(filepath)
        context = {'verdict': verdict}
        return render(request, 'verdict.html', context)