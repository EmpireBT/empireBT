from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect


from empirebt.webapp.forms import RegistrationForm


def register(request):
	if request.method == 'POST':
		form = RegistrationForm(request.POST)     
		if form.is_valid():
 			form.save()
			return HttpResponseRedirect('/login/')
	else:
		form = RegistrationForm()
	return render_to_response('registration/register.html', 
		{'form':form}, context_instance=RequestContext(request))


def dashboard(request):
	return render_to_response('dashboard.html', {}, context_instance=RequestContext(request))


    

