# Create your views here.
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
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
		print user
		
		user.chat_empire_connected = req.GET["presence"] == "true"
		print user.username, user.chat_empire_connected
		print req.GET['presence']
		print user.save()
		print user.chat_empire_connected
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

@login_required(login_url = '/login/')
def lock_summary(req):
	user = req.UserCustom

@login_required(login_url = '/login/')
def summary_lock(req):
	if "empire_id" not in req.POST or "lock" not in req.POST:
		return jsonfy({'ok': False})
	try:
		user = req.user
		empire = models.Empire.objects.get(id = req.POST['empire_id'])
		if empire.summary_lock == None or empire.summary_lock.rank > user.rank:
			empire.summary_lock = user if req.POST['lock'] == "true" else None
		else:
			return jsonfy({'ok': False})
		empire.save()
		return jsonfy({'ok': True})
	except ObjectDoesNotExist, e:
		return jsonfy({'ok': False})

@login_required(login_url = '/login/')
def change_summary(req):
	if "empire_id" not in req.POST or "summary" not in req.POST:
		return jsonfy({'ok': False})
	try:
		user = req.user
		empire = models.Empire.objects.get(id = req.POST['empire_id'])
		if empire.summary_lock == None or empire.summary_lock.rank >= user.rank:
			empire.summary_lock = user
			empire.summary = req.POST['summary']
		else:
			return jsonfy({'ok': False})
		empire.save()
		return jsonfy({'ok': True})
	except ObjectDoesNotExist, e:
		return jsonfy({'ok': False})

@login_required(login_url = '/login/')
def decisions_lock(req):
	if "empire_id" not in req.POST or "lock" not in req.POST:
		return jsonfy({'ok': False})
	try:
		user = req.user
		empire = models.Empire.objects.get(id = req.POST['empire_id'])
		if empire.decision_locked == None or empire.decision_locked.rank > user.rank:
			empire.decision_locked = user if req.POST['lock'] == "true" else None
		else:
			return jsonfy({'ok': False})
		empire.save()
		return jsonfy({'ok': True})
	except ObjectDoesNotExist, e:
		return jsonfy({'ok': False})

@login_required(login_url = '/login/')
def add_attack(req):
	if "empire_id" not in req.POST or "commander_id" not in req.POST or "territory_id" not in req.POST:
		return jsonfy({'ok': False})
	try:
		user = req.user
		if user.empire.id != int(req.POST['empire_id']):
			return jsonfy({'valid': False})
		empire = models.Empire.objects.get(id = req.POST['empire_id'])
		if empire.decision_locked == None or empire.decision_locked.rank > user.rank:
			empire.decision_locked = user
			empire.save()
			territory = models.Territory.objects.get(id = req.POST['territory_id'])
			decision = models.Decision(empire = empire, territory = territory)
			decision.save()
			dattack = models.DecisionAttack(Decision=decision)
			dattack.save()
			return jsonfy({'ok': True, 'decision_attack_id': dattack.id})
		else:
			return jsonfy({'ok': False})
	except ObjectDoesNotExist, e:
		return jsonfy({'ok': False})

@login_required(login_url = '/login/')
def remove_attack(req):
	if "decision_attack_id" not in req.POST:
		return jsonfy({'ok': False})
	try:
		user = req.user
		decision = models.Decision.objects.get(id=req.POST['decision_attack_id'])
		empire = models.Empire.objects.get(id = decision.empire)
		if empire.decision_locked == None or empire.decision_locked.rank > user.rank:
			empire.decision_locked = user
			empire.save()
			models.DecisionAttack.objects.filter(Decision = decision).delete()
			decision.delete()
			return jsonfy({'ok': True})
		else:
			return jsonfy({'ok': False})

	except ObjectDoesNotExist, e:
		return jsonfy({'ok': False})

@login_required(login_url = '/login/')
def add_defend(req):
	if "empire_id" not in req.POST or "commander_id" not in req.POST or "territory_id" not in req.POST:
		return jsonfy({'ok': False, 'decision_defend_id': ''})
	try:
		user = req.user
		if user.empire.id != int(req.POST['empire_id']):
			return jsonfy({'ok': False, 'decision_defend_id': ''})
		empire = models.Empire.objects.get(id = req.POST['empire_id'])
		if empire.decision_locked == None or empire.decision_locked.rank > user.rank:
			empire.decision_locked = user
			empire.save()
			territory = models.Territory.objects.get(id = req.POST['territory_id'])
			decision = models.Decision(empire = empire, territory = territory)
			decision.save()
			ddefend = models.DecisionDefend(Decision=decision)
			ddefend.save()
			return jsonfy({'ok': True, 'decision_defend_id': ddefend.id})
		else:
			return jsonfy({'ok': False})
	except ObjectDoesNotExist, e:
		return jsonfy({'ok': False, 'decision_defend_id': ''})

@login_required(login_url = '/login/')
def remove_defend(req):
	if "decision_defend_id" not in req.POST:
		return jsonfy({'ok': False})
	try:
		user = req.user
		decision = models.Decision.objects.get(id=req.POST['decision_defend_id'])
		empire = models.Empire.objects.get(id = decision.empire)
		if empire.decision_locked == None or empire.decision_locked.rank > user.rank:
			empire.decision_locked = user
			empire.save()
			models.DecisionDefend.objects.filter(Decision = decision).delete()
			decision.delete()
			return jsonfy({'ok': True})
		else:
			return jsonfy({'ok': False})
	except ObjectDoesNotExist, e:
		return jsonfy({'ok': False})

@login_required(login_url = '/login/')
def attack_decision_eval(req):
	if "type" not in req.POST or "decision_attack_id" not in req.POST or "description" not in req.POST:
		return jsonfy({'ok': False})
	try:
		user = req.user
		dattack = models.DecisionAttack.objects.get(id=req.POST['decision_attack_id'])
		empire = models.Empire.objects.get(id = dattack.empire)
		if empire.decision_locked == None or empire.decision_locked.rank > user.rank:
			empire.decision_locked = user
			empire.save()
			deval = models.DecisionEvaluation(type_enum = req.POST['type'], description = req.POST['description'])
			deval.save()
			deval_attack = models.DecisionEvaluationAttack(DecisionEval = deval)
			deval_attack.save()
			return jsonfy({'ok': True, 'decision_attack_evaluation_id': deval_attack.id})
		else:
			return jsonfy({'ok': False})
	except ObjectDoesNotExist, e:
		return jsonfy({'ok': False})

@login_required(login_url = '/login/')
def defend_decision_eval(req):
	if "type" not in req.POST or "decision_defend_id" not in req.POST or "description" not in req.POST:
		return jsonfy({'ok': False})
	try:
		user = req.user
		ddefend = models.DecisionDefend.objects.get(id=req.POST['decision_defend_id'])
		empire = models.Empire.objects.get(id = ddefend.empire)
		if empire.decision_locked == None or empire.decision_locked.rank > user.rank:
			empire.decision_locked = user
			empire.save()
			deval = models.DecisionEvaluation(type_enum = req.POST['type'], description = req.POST['description'])
			deval.save()
			deval_defend = models.DecisionEvaluationDefend(DecisionEval = deval)
			deval_defend.save()
			return jsonfy({'ok': True, 'decision_defend_evaluation_id': deval_defend.id})
		else:
			return jsonfy({'ok': False})
	except ObjectDoesNotExist, e:
		return jsonfy({'ok': False})

@login_required(login_url = '/login/')
def defend_decision_final(req):
	if "decision_defend_id" not in req.POST:
		return jsonfy({'ok': False})
	try:
		user = req.user
		ddefend = models.DecisionDefend.objects.get(id=req.POST['decision_defend_id'])
		empire = models.Empire.objects.get(id = ddefend.empire)
		if empire.decision_locked == None or empire.decision_locked.rank > user.rank:
			empire.decision_locked = user
			empire.save()
			ddefend.final = True
			ddefend.save()
			return jsonfy({'ok': True})
		else:
			return jsonfy({'ok': False})
	except ObjectDoesNotExist, e:
		return jsonfy({'ok': False})
def falsify(req):
	battle = models.Battle.objects.get(id = 1)
	battle.battle_manager_started = False
	battle.save()
	return jsonfy({'ok': True})

def jsonfy(obj):
	return HttpResponse(json.dumps(obj))