# Create your views here.
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
import empirebt.main.models as models
import json
from django.views.decorators.csrf import ensure_csrf_cookie
@ensure_csrf_cookie

def auth_general(req):
	if "token" not in req.GET or "user_id" not in req.GET:
		return jsonfy({'valid': False})
	res = models.UserCustom.objects.filter(id = req.GET["user_id"], websocket_token = req.GET["token"]).exists()
	return jsonfy({'valid': res})

def empire_auth(req):
	if "token" not in req.GET or "user_id" not in req.GET or "empire_id" not in req.GET:
		return jsonfy({'valid': False})
	res = models.UserCustom.objects.filter(id = req.GET["user_id"], websocket_token = req.GET["token"], emperorEmpire = req.GET["empire_id"]).exists()
	user = models.UserCustom.objects.get(id = req.GET["user_id"])
	return jsonfy({'valid': res, 'username' : user.username})


def oneonone_auth(req):
	if "token" not in req.GET or "user_id" not in req.GET:
		return jsonfy({'valid': False})
	res = models.UserCustom.objects.filter(id = req.GET["user_id"], websocket_token = req.GET["token"]).exists()
	user = models.UserCustom.objects.get(id = req.GET["user_id"])
	return jsonfy({'valid': res, 'username' : user.username})

def battle_auth(req):
	if "token" not in req.GET or "user_id" not in req.GET or "battle_id" not in req.GET:
		return jsonfy({'valid': False})

	try:
		user = models.UserCustom.objects.filter(
			websocket_token = req.GET["token"]
		).get(id = req.GET["user_id"])
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
		user.chat_oneonone_connected = True if req.GET["presence"] == "true" else False
		user.save()
		return jsonfy({'valid': True})
	except ObjectDoesNotExist, e:
		return jsonfy({'valid': False, 'exception': True})

def connected_empire(req):
	if "user_id" not in req.GET or "presence" not in req.GET or "empire_id" not in req.GET:
		return jsonfy({'ok': False})
	try:
		user = models.UserCustom.objects.filter(empire = req.GET["empire_id"]).get(id = req.GET["user_id"])
		
		user.chat_empire_connected = req.GET["presence"] == "true"
		return jsonfy({'ok': True})
	except ObjectDoesNotExist, e:
		return jsonfy({'ok': False, 'exception': True})

def list_oneonone(req):
	cons = models.UserCustom.objects.filter(chat_oneonone_connected = True).values('id', 'username')
	return jsonfy({'list': list(cons)})

@login_required(login_url = '/login/')
def list_empire(req):

	if "empire_id" not in req.GET:
		return jsonfy({'ok': False})
	user = req.user
	#print dir(user.empire)
	#return jsonfy({})
	if user.empire.id != int(req.GET['empire_id']):
		return jsonfy({'valid': False})
	#return jsonfy({})
	cons = models.UserCustom.objects.filter(chat_empire_connected = True, empire = req.GET["empire_id"]).values('id', 'username')
	return jsonfy({'ok': True, 'list': list(cons)})

def battle_info(req):
	if "battle_id" not in req.GET:
		return jsonfy({'ok': False, 'missing_params': True})
	try:
		battle = models.Battle.objects.get(id=req.GET['battle_id'])
		#territory = models.Territory.objects.get(id = battle.territory.id)
		return jsonfy({'ok': True, 'attacker': battle.attacker.id, 'defender': battle.defender.id, 'sp_attacker': battle.sp_attacker, 'sp_defender': battle.sp_defender, 'conf_attacker': json.loads(battle.conf_attacker), 'conf_defender': json.loads(battle.conf_defender), 'battlefield': json.loads(battle.territory.battlefield)})
		#return jsonfy({'swag':True})
	except ObjectDoesNotExist, e:
		return jsonfy({'ok': False, 'exception': True})

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

@login_required(login_url = '/login/')
def lock_summary(req):
	user = req.UserCustom

@login_required(login_url = '/login/')
def summary_lock(req):
	if "empire_id" not in req.POST or "lock" not in req.POST:
		return jsonfy({'ok': False, 'missing_params': True})
	try:
		user = req.user
		empire = models.Empire.objects.get(id = req.POST['empire_id'])
		if empire.summary_locked == None or empire.summary_locked == user or empire.summary_locked.rank > user.rank:
			empire.summary_locked = user if req.POST['lock'] == "true" else None
		else:
			return jsonfy({'ok': False, 'forbbiden': True})
		empire.save()
		return jsonfy({'ok': True})
	except ObjectDoesNotExist, e:
		return jsonfy({'ok': False, 'exception': True})

@login_required(login_url = '/login/')
def change_summary(req):
	if "empire_id" not in req.POST or "summary" not in req.POST:
		return jsonfy({'ok': False, 'missing': True})
	try:
		user = req.user
		empire = models.Empire.objects.get(id = req.POST['empire_id'])
		if empire.summary_locked == None or empire.summary_locked == user or empire.summary_locked.rank >= user.rank:
			empire.summary_locked = user
			empire.summary = req.POST['summary']
		else:
			return jsonfy({'ok': False, 'forbbiden': True})
		empire.save()
		return jsonfy({'ok': True})
	except ObjectDoesNotExist, e:
		return jsonfy({'ok': False, 'exception': True})

@login_required(login_url = '/login/')
def decisions_lock(req):
	if "empire_id" not in req.POST or "lock" not in req.POST:
		return jsonfy({'ok': False, 'missing_params': True})
	try:
		user = req.user
		empire = models.Empire.objects.get(id = req.POST['empire_id'])
		if empire.decision_locked == None or empire.decision_locked == user or empire.decision_locked.rank > user.rank:
			empire.decision_locked = user if req.POST['lock'] == "true" else None
		else:
			return jsonfy({'ok': False})
		empire.save()
		return jsonfy({'ok': True})
	except ObjectDoesNotExist, e:
		return jsonfy({'ok': False, 'exception': True})

@login_required(login_url = '/login/')
def add_attack(req):
	if "empire_id" not in req.POST or "commander_id" not in req.POST or "territory_id" not in req.POST:
		return jsonfy({'ok': False, 'missing_params': True})
	try:
		user = req.user
		if user.empire.id != int(req.POST['empire_id']):
			return jsonfy({'valid': False, 'not_in_empire': True})
		empire = models.Empire.objects.get(id = req.POST['empire_id'])
		if empire.decision_locked == None or empire.decision_locked == user or empire.decision_locked.rank > user.rank:
			empire.decision_locked = user
			empire.save()
			com = models.UserCustom.objects.get(id=req.POST['commander_id'])
			territory = models.Territory.objects.get(id = req.POST['territory_id'])
			decision = models.DecisionAttack(empire = empire, territory = territory, commander = com)
			decision.save()
			return jsonfy({'ok': True, 'decision_attack_id': decision.id})
		else:
			return jsonfy({'ok': False, 'forbbiden': True})
	except ObjectDoesNotExist, e:
		return jsonfy({'ok': False, 'exception': True})

@login_required(login_url = '/login/')
def remove_attack(req):
	if "decision_attack_id" not in req.POST:
		return jsonfy({'ok': False, 'missing_params': True})
	try:
		user = req.user
		decision = models.DecisionAttack.objects.get(id=req.POST['decision_attack_id'])
		empire = models.Empire.objects.get(id = decision.empire.id)
		if empire.decision_locked == None or empire.decision_locked == user or empire.decision_locked.rank > user.rank:
			empire.decision_locked = user
			empire.save()
			decision.delete()
			return jsonfy({'ok': True})
		else:
			return jsonfy({'ok': False, 'forbbiden': True})

	except ObjectDoesNotExist, e:
		return jsonfy({'ok': False, 'exception': True})

@login_required(login_url = '/login/')
def add_defend(req):
	if "empire_id" not in req.POST or "commander_id" not in req.POST or "territory_id" not in req.POST:
		return jsonfy({'ok': False, 'missing_params': True})
	try:
		user = req.user
		if user.empire.id != int(req.POST['empire_id']):
			return jsonfy({'ok': False, 'not_in_empire': True})
		empire = models.Empire.objects.get(id = req.POST['empire_id'])
		if empire.decision_locked == None or empire.decision_locked == user or empire.decision_locked.rank > user.rank:
			empire.decision_locked = user
			empire.save()
			com = models.UserCustom.objects.get(id=req.POST['commander_id'])
			territory = models.Territory.objects.get(id = req.POST['territory_id'])
			decision = models.DecisionDefend(empire = empire, territory = territory, commander = com)
			decision.save()
			return jsonfy({'ok': True, 'decision_defend_id': decision.id})
		else:
			return jsonfy({'ok': False, 'forbbiden': True})
	except ObjectDoesNotExist, e:
		return jsonfy({'ok': False, 'exception': True})

@login_required(login_url = '/login/')
def remove_defend(req):
	if "decision_defend_id" not in req.POST:
		return jsonfy({'ok': False, 'missing_params': True})
	try:
		user = req.user
		decision = models.DecisionDefend.objects.get(id=req.POST['decision_defend_id'])
		empire = models.Empire.objects.get(id = decision.empire.id)
		if empire.decision_locked == None or empire.decision_locked == user or empire.decision_locked.rank > user.rank:
			empire.decision_locked = user
			empire.save()
			decision.delete()
			return jsonfy({'ok': True})
		else:
			return jsonfy({'ok': False, 'forbbiden': True})
	except ObjectDoesNotExist, e:
		return jsonfy({'ok': False})

@login_required(login_url = '/login/')
def attack_decision_eval(req):
	if "type" not in req.POST or "decision_attack_id" not in req.POST or "description" not in req.POST:
		return jsonfy({'ok': False, 'missing_params': True})
	try:
		user = req.user
		decision = models.DecisionAttack.objects.get(id=req.POST['decision_attack_id'])
		empire = models.Empire.objects.get(id = decision.empire.id)
		if empire.decision_locked == None or empire.decision_locked == user or empire.decision_locked.rank > user.rank:
			empire.decision_locked = user
			empire.save()
			attack_eval = models.DecisionEvaluationAttack(type_enum = req.POST['type'], description = req.POST['description'], decision_attack = decision)
			attack_eval.save()
			return jsonfy({'ok': True, 'decision_attack_evaluation_id': attack_eval.id})
		else:
			return jsonfy({'ok': False, 'forbbiden': True})
	except ObjectDoesNotExist, e:
		return jsonfy({'ok': False, 'exception': True})

@login_required(login_url = '/login/')
def defend_decision_eval(req):
	if "type" not in req.POST or "decision_defend_id" not in req.POST or "description" not in req.POST:
		return jsonfy({'ok': False, 'missing_params': True})
	try:
		user = req.user
		decision = models.DecisionDefend.objects.get(id=req.POST['decision_defend_id'])
		empire = models.Empire.objects.get(id = decision.empire.id)
		if empire.decision_locked == None or empire.decision_locked == user or empire.decision_locked.rank > user.rank:
			empire.decision_locked = user
			empire.save()
			defend_eval = models.DecisionEvaluationDefend(type_enum = req.POST['type'], description = req.POST['description'], decision_defend = decision)
			defend_eval.save()
			return jsonfy({'ok': True, 'decision_defend_evaluation_id': defend_eval.id})
		else:
			return jsonfy({'ok': False, 'forbbiden': True})
	except ObjectDoesNotExist, e:
		return jsonfy({'ok': False, 'exception': True})

@login_required(login_url = '/login/')
def defend_decision_final(req):
	if "decision_defend_id" not in req.POST:
		return jsonfy({'ok': False, 'missing_params': True})
	try:
		user = req.user
		decision = models.DecisionDefend.objects.get(id=req.POST['decision_defend_id'])
		empire = models.Empire.objects.get(id = decision.empire.id)
		if empire.decision_locked == None or empire.decision_locked == user or empire.decision_locked.rank > user.rank:
			empire.decision_locked = user
			empire.save()
			decision.final = True
			decision.save()
			return jsonfy({'ok': True})
		else:
			return jsonfy({'ok': False, 'forbbiden': True})
	except ObjectDoesNotExist, e:
		return jsonfy({'ok': False, 'exception': True})

def falsify(req):
	battle = models.Battle.objects.get(id = 1)
	battle.battle_manager_started = False
	battle.save()
	return jsonfy({'ok': True})

def jsonfy(obj):
	return HttpResponse(json.dumps(obj))