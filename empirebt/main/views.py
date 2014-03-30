# Create your views here.
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
import empirebt.main.models as models
import json

def auth_general(req):
	if "token" not in req.GET or "user_id" not in req.GET:
		return jsonfy({'valid': False})
	res = models.UserCustom.objects.filter(id = req.GET["user_id"], websocket_token = req.GET["token"]).exists()
	return jsonfy({'valid': res})

def empire_auth(req):
	if "token" not in req.GET or "user_id" not in req.GET or "empire_id" not in req.GET:
		return jsonfy({'valid': False})
	res = models.UserCustom.objects.filter(id = req.GET["user_id"], websocket_token = req.GET["token"], commander = req.GET["empire_id"]).exists()
	return jsonfy({'valid': res})

def oneonone_auth(req):
	if "token" not in req.GET or "user_id" not in req.GET:
		return jsonfy({'valid': False})
	res = models.UserCustom.objects.filter(id = req.GET["user_id"], websocket_token = req.GET["token"])
	return jsonfy({'valid': res})

def battle_auth(req):
	if "token" not in req.GET or "user_id" not in req.GET or "battle_id" not in req.GET:
		return jsonfy({'valid': False})

	try:
		user = models.UserCustom.objects.filter(
			websocket_token = reg.GET["token"]
		).get(id = reg.GET["user_id"])
		#models.Battle.objects.filter(id = req.GET["battle_id"], attacker__name = 'Pancho').get()
		battle = models.Battle.objects.get(id = req.GET["battle_id"])
		valid = battle.attacker.id == user.id or battle.defender.id == user.id
		bms = battle.battle_manager_started
		battle.battle_manager_started = True
		battle.save()
		return jsonfy({'valid': valid, 'battle_manager_started': bms})

	except ObjectDoesNotExist, e:
		return jsonfy({'valid': False})

def connected_oneonone(req):
	if "user_id" not in req.GET or "presence" not in req.GET:
		return jsonfy({'valid': False})
	try:
		user = models.UserCustom.objects.get(id = req.GET["user_id"])
		user.chat_oneonone_connected = req.GET["presence"]
		user.save()
		return jsonfy({'valid': user.chat_oneonone_connected})
	except Exception, e:
		return jsonfy({'valid': False})
def connected_empire(req):
	if "user_id" not in req.GET or "presence" not in req.GET or "empire_id" not in req.GET:
		return jsonfy({'valid': False})
def list_oneonone(req):

	pass
def list_empire(req):

	pass

def jsonfy(obj):
	return HttpResponse(json.dumps(obj))
