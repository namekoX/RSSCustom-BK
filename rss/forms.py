from .models import Entry, LoginUser
from django import forms

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['no','url','user_id','site_name','inclede_category','inclede_subject','max_count','limit_day','version','inclede_creater','create_at','update_at']

class LoginUserForm(forms.ModelForm):
    class Meta:
        model = LoginUser
        fields = ['user_id','site_id','password','create_at','update_at']
