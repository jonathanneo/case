from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone

from .forms import CaseStudyForm, CaseStudyTagForm, MedicalHistoryForm, MedicationForm, OtherForm  # , CaseTagForm
from .models import Tag, TagRelationship, CaseStudy, MedicalHistory, Medication, Attempt, Comment, Other


@login_required
def start_new_case(request):
    case = CaseStudy.objects.create(created_by=request.user)
    return HttpResponseRedirect(
        reverse("cases:create-new-case", kwargs={"case_study_id": case.id}))


@login_required
def create_new_case(request, case_study_id):
    # returns object (case_study), and boolean specifying whether an object was created
    case_study, created = CaseStudy.objects.get_or_create(pk=case_study_id)
    # case has been submitted or pending review so it cannot be accessed again 
    if (case_study.is_submitted or case_study.is_draft==False):
        return HttpResponseNotFound()
        # return HttpResponseRedirect(reverse('cases:view-case', args=[case_study.id]))
    relevant_tags = TagRelationship.objects.filter(case_study=case_study)  # return Tags for that case_study
    all_tags = Tag.objects.all()
    medical_histories = MedicalHistory.objects.filter(case_study=case_study)
    medications = Medication.objects.filter(case_study=case_study)
    others = Other.objects.filter(case_study=case_study)
    # Check if the choice was in years format, if yes, integer division by 12.
    if case_study.age:
        if case_study.age_type == 'Y':
            case_study.age = case_study.age // 12
    if request.method == "POST":
        # Fixes mutable error
        request.POST = request.POST.copy()
        print(request.POST)
        # obtain forms with fields populated from POST request
        case_study_form = CaseStudyForm(request.POST, instance=case_study)
        # -- Medical history -- 
        medical_histories = list(MedicalHistory.objects.filter(case_study=case_study).values_list("body",flat=True))
        medical_history_list = request.POST.getlist("medical-history-list")
        # Create new ones 
        for medical_history in medical_history_list:
            if medical_history not in medical_histories:
                MedicalHistory.objects.create(body=medical_history, case_study=case_study)
        medical_histories = list(MedicalHistory.objects.filter(case_study=case_study).values_list("body",flat=True))
        # Delete ones that are removed 
        for medical_history in medical_histories:
            if medical_history not in medical_history_list:
                MedicalHistory.objects.filter(body=medical_history, case_study=case_study).delete()
        # Obtain updated list of medical histories
        medical_histories = MedicalHistory.objects.filter(case_study=case_study)

        # -- Medication -- 
        medications = list(Medication.objects.filter(case_study=case_study).values_list("name",flat=True))
        medication_list = request.POST.getlist("medication-list")
        # Create new ones 
        for medication in medication_list:
            if medication not in medications:
                Medication.objects.create(name=medication, case_study=case_study)
        medications = list(Medication.objects.filter(case_study=case_study).values_list("name",flat=True))
        # Delete ones that are removed 
        for medication in medications:
            if medication not in medication_list:
                Medication.objects.filter(name=medication, case_study=case_study).delete()
        # Obtain updated list of medical histories
        medications = Medication.objects.filter(case_study=case_study)

        # -- Other -- 
        others = list(Other.objects.filter(case_study=case_study).values_list("other_body",flat=True))
        other_list = request.POST.getlist("other-list")
        # Create new ones 
        for other in other_list:
            if other not in others:
                Other.objects.create(other_body=other, case_study=case_study)
        others = list(Other.objects.filter(case_study=case_study).values_list("other_body",flat=True))
        # Delete ones that are removed 
        for other in others:
            if other not in other_list:
                Other.objects.filter(other_body=other, case_study=case_study).delete()
        # Obtain updated list of medical histories
        others = Other.objects.filter(case_study=case_study)

        # -- Tag -- 
        relevant_tags = TagRelationship.objects.filter(case_study=case_study)
        tag_list = request.POST.getlist("tag-list")
        # Create new ones 
        for tag in tag_list:
            tag_object = get_object_or_404(Tag, pk=tag) 
            if TagRelationship.objects.filter(tag=tag_object, case_study=case_study).exists() == False:
                TagRelationship.objects.create(tag=tag_object, case_study=case_study)
        relevant_tag_ids = TagRelationship.objects.filter(case_study=case_study).values_list("tag",flat=True)
        relevant_tags = []
        for relevant_tag in relevant_tag_ids:
            relevant_tags.append(relevant_tag)

        if request.POST["submission_type"] == "save":

            # Checking for the type on submission, if years, store the value as months
            if request.POST['age_type'] == 'Y' and request.POST['age'] != '':
                request.POST['age'] = int(request.POST['age']) * 12
            if case_study_form.is_valid():
                case_study_form.save()
                # When page is re rendered, the value from the database is taken, so if years, render the correct value
                if request.POST['age_type'] == 'Y' and request.POST['age'] != '':
                    request.POST['age'] = int(request.POST['age']) // 12
                case_study_form = CaseStudyForm(request.POST, instance=case_study)
                messages.success(request, 'Case Study saved!')
                return render(request, "create_new_case.html",
                              {
                                  "case_study_form": case_study_form,
                                  "relevant_tags": relevant_tags,
                                  "all_tags": all_tags, 
                                  "medical_histories": medical_histories,
                                  "medications": medications,
                                  "others": others,
                                  "case_study":case_study,
                              })
        elif request.POST["submission_type"] == "submit":
            if request.POST['age_type'] == 'Y':
                request.POST['age'] = int(request.POST['age']) * 12
            if case_study_form.is_valid():
                print("it is valid!!!!!")
                case_study_form.is_submitted = False 
                case_study_form = case_study_form.save(commit = False)
                case_study_form.is_draft = False 
                case_study_form.save()
                messages.success(request, 'Case study submitted for review!')
                return HttpResponseRedirect(reverse('cases:view-case', args=[case_study.id]))
            else:
                if request.POST['age_type'] == 'Y':
                    request.POST['age'] = int(request.POST['age']) // 12
                case_study_form = CaseStudyForm(request.POST, instance=case_study)
                return render(request, "create_new_case.html",
                              {
                                  "case_study_form": case_study_form,
                                  "relevant_tags": relevant_tags,
                                  "all_tags": all_tags, 
                                  "medical_histories": medical_histories,
                                  "medications": medications,
                                  "others": others,
                                  "case_study":case_study,
                              })
        else:
            return render(request, "create_new_case.html",
                          {
                              "case_study_form": case_study_form,
                              "relevant_tags": relevant_tags,
                              "all_tags": all_tags, 
                              "medical_histories": medical_histories,
                              "medications": medications,
                              "others": others,
                              "case_study":case_study,
                          })
    else:
        case_study_form = CaseStudyForm(instance=case_study)
    return render(request, "create_new_case.html",
                  {
                      "case_study_form": case_study_form,
                      "relevant_tags": relevant_tags,
                      "all_tags": all_tags, 
                      "medical_histories": medical_histories,
                      "medications": medications,
                      "others": others,
                      "case_study":case_study,
                  })

@login_required
def view_case(request, case_study_id):
    case_study = get_object_or_404(CaseStudy, pk=case_study_id)
    mhx = MedicalHistory.objects.filter(case_study=case_study)
    medications = Medication.objects.filter(case_study=case_study)
    others = Other.objects.filter(case_study=case_study)
    tags = TagRelationship.objects.filter(case_study=case_study)
    total_average = case_study.get_average_score()
    user_average = case_study.get_average_score(user=request.user)
    user_attempts = Attempt.objects.filter(case_study=case_study, user=request.user).count()
    total_attempts = Attempt.objects.filter(case_study=case_study).count()
    comments = Comment.objects.filter(case_study=case_study_id, is_deleted=False).order_by("-comment_date")
    c = {
        "attempts": {
            "total_average": total_average,
            "total_attempts": total_attempts,
            "user_average": user_average,
            "user_attempts": user_attempts
        },
        "case": case_study,
        "mhx": mhx,
        "medications": medications,
        "others" : others, 
        "tags": tags,
        "comments": comments
    }
    return render(request, "view_case.html", c)

@login_required
def validate_answer(request, case_study_id):
    case = get_object_or_404(CaseStudy, pk=case_study_id)
    choice = request.GET.get('choice', None)
    success = False
    # Get message
    if choice == case.answer:
        success = True
    message = "<strong>Correct Answer: " + case.answer + "</strong><br><em>" + case.get_answer_from_character(
        case.answer) + "</em><br>You answered incorrectly. Your answer was <strong>" + choice + "</strong>, " + case.get_answer_from_character(
        choice)
    if success:
        message = "<strong>Correct Answer: " + case.answer + "</strong><br><em>" + case.get_answer_from_character(
            case.answer) + "</em><br>You answered correctly."
    # Get attempts information
    Attempt.objects.create(user_answer=choice, case_study=case, user=request.user, attempt_date=timezone.now())
    total_average = case.get_average_score()
    user_average = case.get_average_score(user=request.user)
    user_attempts = Attempt.objects.filter(case_study=case, user=request.user).count()
    total_attempts = Attempt.objects.filter(case_study=case).count()
    # Get comments
    comments = Comment.objects.filter(case_study=case_study_id)
    comments_json = serializers.serialize('json', comments)
    data = {
        'attempts': {
            'total_average': total_average,
            'total_attempts': total_attempts,
            'user_average': user_average,
            'user_attempts': user_attempts
        },
        'success': success,
        'answer_message': message,
        'feedback': case.feedback,
        'comments': comments_json
    }
    return JsonResponse(data)

@login_required
def submit_comment(request, case_study_id):
    case = get_object_or_404(CaseStudy, pk=case_study_id)
    body = request.GET.get('body', None)
    is_anon = request.GET.get('is_anon', None).capitalize()
    # Create comment 
    if request.user.is_tutor: 
        comment = Comment.objects.create(comment=body, case_study=case, user=request.user, is_anon=False,
                                        comment_date=timezone.now())
    else: 
        comment = Comment.objects.create(comment=body, case_study=case, user=request.user, is_anon=is_anon,
                                        comment_date=timezone.now())
    data = {
        'comment': {
            'body': body,
            'date': timezone.now(),
            'is_anon': comment.is_anon == 'True'
        },
        'user': {
            'name': request.user.get_full_name(),
            'is_staff': request.user.is_staff,
            'is_tutor': request.user.is_tutor
        }
    }
    return JsonResponse(data)
