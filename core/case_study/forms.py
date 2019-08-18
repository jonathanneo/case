from django.forms import ModelForm
from django import forms
from .models import Question, CaseStudy, MedicalHistory, Medication #,TagRelationships


# populate patient particulars and description
class CaseStudyForm(ModelForm):
    class Meta:
        model = CaseStudy
        fields = ['height', 'weight', 'scr', 'age_type', 'age', 'sex','description', 'answer_1', 'answer_2', 'answer_3', 'answer_4']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'answer_1': forms.Textarea(attrs={'rows': 4}),
            'answer_2': forms.Textarea(attrs={'rows': 4}),
            'answer_3': forms.Textarea(attrs={'rows': 4}),
            'answer_4': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super(CaseStudyForm, self).__init__(*args, **kwargs)

        # you can iterate all fields here
        for fname, f in self.fields.items():
            f.widget.attrs['class'] = 'form-control'

# select existing question
class CaseStudyQuestionForm(ModelForm):
    class Meta:
        model = Question
        fields = ['body']

# populate patient medical history
class MedicalHistoryForm(ModelForm):
    class Meta:
        model = MedicalHistory
        fields = ['body']

# populate patient medication
class MedicationForm(ModelForm):
    class Meta:
        model = Medication
        fields = ['name']

# # select tags for case study
# class CaseTagForm(ModelForm):
#     class Meta: 
#         model = TagRelationships
#         fields = ['tag']