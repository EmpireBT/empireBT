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
	res = models.UserCustom.objects.filter(id = req.GET["user_id"], websocket_token = req.GET["token"], emperorEmpire = req.GET["empire_id"]).exists()
	return jsonfy({'valid': res})

def oneonone_auth(req):
	if "token" not in req.GET or "user_id" not in req.GET:
		return jsonfy({'valid': False})
	res = models.UserCustom.objects.filter(id = req.GET["user_id"], websocket_token = req.GET["token"]).exists()
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
		user.chat_oneonone_connected = True if req.GET["presence"] == "True" else False
		user.save()
		return jsonfy({'valid': user.chat_oneonone_connected})
	except ObjectDoesNotExist, e:
		return jsonfy({'valid': False})

def connected_empire(req):
	if "user_id" not in req.GET or "presence" not in req.GET or "empire_id" not in req.GET:
		return jsonfy({'valid': False})
	try:
		user = models.UserCustom.objects.filter(empire = req.GET["empire_id"]).get(id = req.GET["user_id"])
		#return jsonfy({'user': list(user)})
		user.chat_empire_connected = req.GET["presence"] == "True"
		user.save()
		return jsonfy({'valid': user.chat_empire_connected})
	except ObjectDoesNotExist, e:
		return jsonfy({'valid': False, 'exception': True})

def list_oneonone(req):
	cons = models.UserCustom.objects.filter(chat_oneonone_connected = True).values('id', 'username')
	return jsonfy({'list': list(cons)})

def list_empire(req):
	if "empire_id" not in req.GET:
		return jsonfy({'valid': False})
	cons = models.UserCustom.objects.filter(chat_empire_connected = True, empire = req.GET["empire_id"]).values('id', 'username')
	return jsonfy({'values': True, 'list': list(cons)})

def battle_info(req):
	if "battle_id" not in req.GET:
		return jsonfy({'ok': False})
	try:
		battle = models.Battle.objects.filter(id = req.GET["battle_id"]).get()
		territory = models.Territory.objects.get(id = battle.territory.id)
		return jsonfy({'ok': True, 
			'attacker': battle.attacker.username, 
			'defender': battle.defender.username,
			'sp_attacker': battle.sp_attacker,
			'sp_defender': battle.sp_defender,
			'conf_attacker': json.loads(battle.conf_attacker),
			'conf_defender': json.loads(battle.conf_defender),
			'battlefield': json.loads(territory.battlefield)})
	except ObjectDoesNotExist, e:
		return jsonfy({'ok': False})
def battle_result(req):
	if "battle_id" not in req.POST:
		return jsonfy({'ok': False})
	try:
		battle = models.Battle.objects.get(id=req.POST['battle_id'])
		winner = models.UserCustom.objects.get(id=req.POST['winner'])
		battle.winner = winner
		battle.sp_conceded = int(req.POST['sp_conceded'])
		battle.sp_casualties_attacker = int(req.POST['sp_casualties_attacker'])
		battle.sp_casualties_defender = int(req.POST['sp_casualties_defender'])
		battle.end_type = int(req.POST['end_type'])
		battle.save()
		return jsonfy({'ok': True})
	except ObjectDoesNotExist, e:
		return jsonfy({'ok': False})
	
def jsonfy(obj):
	return HttpResponse(json.dumps(obj))