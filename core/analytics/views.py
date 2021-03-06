from django.shortcuts import render, get_object_or_404
import csv
from django.http import HttpResponse, JsonResponse
from case_study.models import Question, \
    Tag, CaseStudy, TagRelationship, \
    MedicalHistory, Medication, Other, Attempt, \
    Comment, CommentReport
from accounts.models import User
from .forms import TagForm
from core.decorators import staff_required


def export_queryset_csv(qs, filename):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    csvw = csv.writer(response)
    header_done = False
    for e in qs:
        if not header_done:
            field_names = []
            for f in e._meta.fields:
                if f.name != "password":
                    field_names.append(f.name)
            csvw.writerow(field_names)
            header_done = True
        row_data = []
        for f in e._meta.fields:
            if f.name != "password":
                d = vars(e).get(f.attname, "")
                if d is None:
                    d = ""
                d = str(d).rstrip()
                row_data.append(d)
        csvw.writerow(row_data)
    return response


@staff_required
def view_landing(request):
    c = {"form": TagForm }
    return render(request, "analytics-landing.html", c)


@staff_required
def tag_performance(request):
    tag_id = request.GET.get('tag_id', None)
    tag = get_object_or_404(Tag, pk=tag_id)
    data = tag.get_average_score()
    if data:
        return JsonResponse({
            "success": True,
            "data": data
        })
    return JsonResponse({
        "success": False,
        "message": "Failed to fetch tag performance"
    })



@staff_required
def view_question(request):
    return export_queryset_csv(Question.objects.all(), "uwacase_questions.csv")


@staff_required
def view_tag(request):
    return export_queryset_csv(Tag.objects.all(), "uwacase_tags.csv")


@staff_required
def view_medicalhistory(request):
    return export_queryset_csv(MedicalHistory.objects.all(), "uwacase_medicalhistories.csv")


@staff_required
def view_comment(request):
    return export_queryset_csv(Comment.objects.all(), "uwacase_comments.csv")


@staff_required
def view_casestudy(request):
    return export_queryset_csv(CaseStudy.objects.all(), "uwacase_casestudies.csv")


@staff_required
def view_medication(request):
    return export_queryset_csv(Medication.objects.all(), "uwacase_medications.csv")


@staff_required
def view_tagrelationship(request):
    return export_queryset_csv(TagRelationship.objects.all(), "uwacase_tagrelationships.csv")


@staff_required
def view_other(request):
    return export_queryset_csv(Other.objects.all(), "uwacase_others.csv")


@staff_required
def view_commentreport(request):
    return export_queryset_csv(CommentReport.objects.all(), "uwacase_commentreports.csv")


@staff_required
def view_attempt(request):
    return export_queryset_csv(Attempt.objects.all(), "uwacase_attempts.csv")


@staff_required
def view_user(request):
    return export_queryset_csv(User.objects.all(), "uwacase_users.csv")

