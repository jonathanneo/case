from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from accounts.models import User
from case_study.models import CaseStudy
from core.decorators import staff_required
import copy
import json

schema_user = {
    "endpoint": "/caseadmin/users/",
    "fields": [
        {
            "title": "First Name",
            "key": "first_name",
            "widget": {
                "template": "w-text.html",
                "maxchars": 40,
            },
            "write": True,
        },
        {
            "title": "Last Name",
            "key": "last_name",
            "widget": {
                "template": "w-text.html",
                "maxchars": 60,
            },
            "write": True,
        },
        {
            "title": "Email",
            "key": "email",
            "widget": {
                "template": "w-email.html",
                "maxchars": 250,
            },
            "write": True,
        },
        {
            "title": "University",
            "key": "university",
            "widget": {
                "template": "w-text.html",
                "maxchars": 150,
            },
            "write": True,
        },
        {
            "title": "Degree Start",
            "key": "degree_commencement_year",
            "widget": {
                "template": "w-number.html",
            },
            "write": True,
        },
        {
            "title": "Is Staff",
            "key": "is_staff",
            "widget": {
                "template": "w-checkbox.html",
                "maxchars": 40,
            },
            "write": True,
        },
    ]
}

schema_case = {
    "endpoint": "/caseadmin/cases/",
    "fields": [],
}

schema_comment = {
    "endpoint": "/caseadmin/comments/",
    "fields": [],
}

schema_tag = {
    "endpoint": "/caseadmin/tags/",
    "fields": [],
}


def populate_data(schema, model):
    records = model.objects.all()
    data = {
        "endpoint": schema["endpoint"],
        "entities": [],
    }
    # for all records in the db
    for r in records:
        row_data = []  # this rows data
        # add each field to the data
        for f in schema["fields"]:
            d = copy.deepcopy(f)
            d["value"] = vars(r)[d["key"]]
            d["entity"] = r.id
            row_data.append(d)
        data["entities"].append(row_data)
    return data


def user_PUT(request, user_id):
    # get all the updates the user has requested
    updates = json.loads(request.body)
    # only apply updates to fields that are writable in the schema
    usr = get_object_or_404(User, pk=user_id)  # get the user
    for field in schema_user["fields"]:
        key = field["key"]
        default_val = getattr(usr, key, None)  # default to what the user already had, then to None
        new_val = updates.get(key, default_val)
        setattr(usr, key, new_val)
    usr.save()  # save the user to the db
    return JsonResponse({
        "success": True,
    })


def user_DELETE(request, user_id):
    User.objects.filter(pk=user_id).delete()
    return JsonResponse({
        "success": True,
    })


@staff_required
def api_admin_user(request, user_id):
    if request.method == "PUT":
        return user_PUT(request, user_id)
    elif request.method == "DELETE":
        return user_DELETE(request, user_id)
    else:
        return JsonResponse({
            "success": False,
            "message": "Unsupported HTTP method: " + request.method
        })


@staff_required
def view_admin_user(request):
    # get returns a template with all the users in a table
    data = populate_data(schema_user, User)
    c = {
        "title": "User Admin",
        "model_name": "User",
        "data": data,
    }
    return render(request, "case-admin.html", c)


@staff_required
def view_admin_case(request):
    data = populate_data(schema_case, User)
    c = {
        "title": "Case Study Admin",
        "model_name": "Case Study",
        "data": data
    }
    return render(request, "case-admin.html", c)


@staff_required
def view_admin_comment(request):
    data = populate_data(schema_comment, User)
    c = {
        "title": "Comment Admin",
        "model_name": "Comment",
        "data": data
    }
    return render(request, "case-admin.html", c)


@staff_required
def view_admin_tag(request):
    data = populate_data(schema_tag, User)
    c = {
        "title": "Tag Admin",
        "model_name": "Tag",
        "data": data
    }
    return render(request, "case-admin.html", c)


@staff_required
def view_default(request):
    return render(request, "case-admin-landing.html")