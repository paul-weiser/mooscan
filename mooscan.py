#!/usr/bin/env python3

import requests
import json
from colorama import Fore, Back, Style
from prettytable import PrettyTable
from datetime import datetime

# Please change these values
moodleServer = "www.yourmoodle.com"
wstoken = "YOUR-WSTOKEN"
userid = "YOUR-USERID"

def scrape():

    todos = [];

    coursesRequest = requests.get("https://" + moodleServer + "/webservice/rest/server.php?moodlewsrestformat=json&wsfunction=core_enrol_get_users_courses&wstoken=" + wstoken + "&userid=" + userid)
    courses = coursesRequest.json();

    quizzesRequest = requests.get("https://" + moodleServer + "/webservice/rest/server.php?moodlewsrestformat=json&wsfunction=mod_quiz_get_quizzes_by_courses&wstoken=" + wstoken)
    quizzes = quizzesRequest.json()["quizzes"]
    for quiz in quizzes:
        closingDate = datetime.fromtimestamp(quiz["timeclose"])
        if closingDate > datetime.now():
            quizAttemptsRequest = requests.get('https://' + moodleServer + '/webservice/rest/server.php?moodlewsrestformat=json&wsfunction=mod_quiz_get_user_attempts&wstoken=' + wstoken + '&quizid=' + str(quiz["id"]))
            quizAttempts = quizAttemptsRequest.json()["attempts"]
            
            submitted = False

            if len(quizAttempts) > 0:
                for attempt in quizAttempts:
                    if attempt["state"] == "finished":
                        submitted = True
                        break

            courseName = "ERROR"
            for course in courses:
                if course["id"] == quiz["course"]:
                    courseName = course["shortname"]
                    break

            todos.append([courseName, "Quiz", quiz["name"], closingDate, submitted, -1, submitted]);

    workshopsRequest = requests.get("https://" + moodleServer + "/webservice/rest/server.php?moodlewsrestformat=json&wsfunction=mod_workshop_get_workshops_by_courses&wstoken=" + wstoken)
    workshops = workshopsRequest.json()["workshops"]
    for workshop in workshops:
        submissionEnd = datetime.fromtimestamp(workshop["submissionend"])
        assessmentEnd = datetime.fromtimestamp(workshop["assessmentend"])

        submissionPhaseEnded = submissionEnd < datetime.now();

        currentEnd = assessmentEnd if submissionPhaseEnded else submissionEnd

        if assessmentEnd > datetime.now():
            workshopDetailsRequest = requests.get('https://' + moodleServer + '/webservice/rest/server.php?moodlewsrestformat=json&wsfunction=tool_mobile_call_external_functions&wstoken=' + wstoken + '&requests[0][function]=mod_workshop_get_submissions&requests[0][arguments]={"workshopid":"' + str(workshop["id"]) + '","userid":"0","groupid":"0"}&requests[1][function]=mod_workshop_get_reviewer_assessments&requests[1][arguments]={"workshopid":"' + str(workshop["id"]) + '"}')
            workshopDetails = workshopDetailsRequest.json()["responses"]
            submissions = json.loads(workshopDetails[0]["data"])

            submitted = True if submissions["totalcount"] > 0 else False

            assessed = True

            if submissionPhaseEnded:
                assesments = json.loads(workshopDetails[1]["data"])
                assessmentsRequest = requests.get('https://' + moodleServer + '/webservice/rest/server.php?moodlewsrestformat=json&wsfunction=mod_workshop_get_reviewer_assessments&wstoken=' + wstoken + '&workshopid='+ str(workshop["id"]))
                assessments = assessmentsRequest.json()["assessments"]

                for assessment in assessments:
                    if assessment["grade"] == None:
                        assessed = False;
                        break

            finished = assessed if submissionPhaseEnded else submitted

            courseName = "ERROR"
            for course in courses:
                if course["id"] == workshop["course"]:
                    courseName = course["shortname"]
                    break

            todos.append([courseName, "Workshop", workshop["name"], currentEnd, submitted, assessed, finished]);

    assignmentsRequest = requests.get("https://" + moodleServer + "/webservice/rest/server.php?moodlewsrestformat=json&wsfunction=mod_assign_get_assignments&wstoken=" + wstoken)
    assignmentCourses = assignmentsRequest.json()["courses"]
    for course in assignmentCourses:
        assignments = course["assignments"]
        for assignment in assignments:
            dueDate = datetime.fromtimestamp(assignment["duedate"])
            if dueDate > datetime.now():
                assignmentSubmissionRequest = requests.get("https://" + moodleServer + "/webservice/rest/server.php?moodlewsrestformat=json&wsfunction=mod_assign_get_submission_status&wstoken=" + wstoken + "&assignid=" + str(assignment["id"]));
                assignmentSubmission = assignmentSubmissionRequest.json()["lastattempt"];
                assignmentSubmitted = False;
                if("submission" in assignmentSubmission and assignmentSubmission["submission"]["status"] == "submitted"):
                    assignmentSubmitted = True;
                todos.append([course["shortname"], "Assignment", assignment["name"], dueDate, assignmentSubmitted, -1, assignmentSubmitted]);

    output(todos);

def output(todos):
    x = PrettyTable()
    x.field_names = ["Course", "Type", "Name", "Time Left", "Submitted", "Assessed"]
    for todo in todos:
        timeLeft = todo[3] - datetime.now()
        submittedCharacter = '\u2713' if todo[4] else '\u2715'
        assesedCharacter = Fore.BLACK + "-" if todo[5] < 0 else ('\u2713' if todo[5] else '\u2715')
        lineColor = Fore.GREEN if todo[6] else Fore.YELLOW
        x.add_row([lineColor + todo[0] + Fore.RESET, lineColor + todo[1] + Fore.RESET, lineColor + todo[2] + Fore.RESET, lineColor + td_format(timeLeft) + Fore.RESET, lineColor + submittedCharacter + Fore.RESET, lineColor + assesedCharacter + Fore.RESET])
    print(x);

def td_format(td_object):
    seconds = int(td_object.total_seconds())
    periods = [
        ('year',        60*60*24*365),
        ('month',       60*60*24*30),
        ('day',         60*60*24),
        ('hr',        60*60),
        ('min',      60),
        ('sec',      1)
    ]

    strings=[]
    for period_name, period_seconds in periods:
        if seconds > period_seconds:
            period_value , seconds = divmod(seconds, period_seconds)
            has_s = 's' if period_value > 1 else ''
            strings.append("%s %s%s" % (period_value, period_name, has_s))

    return ", ".join(strings)

if __name__ == "__main__":
    scrape()