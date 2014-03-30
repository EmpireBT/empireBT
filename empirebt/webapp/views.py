from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
import empirebt.main.models as models
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

@login_required(login_url = '/login/')
def dashboard(request):
	empire = request.user.empire
	commanders = models.UserCustom.objects.all()
	misterritorios = models.Territory.objects.filter(empire = empire).all()
	territorios = models.Territory.objects.all()
	otrosterritorios = models.Territory.objects.exclude(empire = empire)
	return render_to_response('dashboard.html', { "empire": empire.name, "commanders": commanders, "misterr": misterritorios, "otrosterr": otrosterritorios, "todosterr": territorios}, context_instance=RequestContext(request))

@login_required(login_url = '/login/')
def battle(request):
	#empire = request.user.empire
	return render_to_response('game.html', { "battle_id": 1}, context_instance=RequestContext(request))


