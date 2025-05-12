from django.db import models
from django.contrib.auth.models import User


class Problem(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    sample_input = models.TextField()
    sample_output = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Submissions(models.Model):
    LANGUAGES = (("C++", "C++"), ("C", "C"), ("Python3", "Python3"), ("Java", "Java"))
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    language = models.CharField(max_length=50)
    user_code = models.TextField()
    user_stdout = models.TextField(max_length=10000, default="")
    user_stderr = models.TextField(max_length=10000, default="")
    verdict = models.CharField(max_length=20, default="Wrong Answer")
    run_time = models.FloatField(null=True, default=0)
    language = models.CharField(
        max_length=10, choices=LANGUAGES, default="C++")
    submission_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s submission for {self.problem.title}"


class Testcase(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    input = models.TextField()
    output = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.problem.title}'s testcase"



class Leaderboard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s leaderboard entry"
