import empirebt.main.models as models

user = models.UserCustom()
user.username = 'hectoragr'
user.set_password('gohe1106')
user.email = 'hector.agr@gmail.com'
user.supply_points = 100
user.rank = 'Emperor'
user.save()
emp = models.Empire(emperor = user, name = 'hectoragrland', moral = 5, summary = 'Lorem ipsum')
user2 = models.UserCustom()
user2.username = 'quero'
user2.set_password('quero')
user2.email = 'quero.logos@gmail.com'
user2.supply_points = 100
user2.rank = 'Emperor'
user2.save()
emp2 = models.Empire(emperor = user2, name = 'queroland', moral = 5, summary = 'Lorem ipsum')
ter = models.Territory(name = 'Territorio 1', empire = emp, commander = user, battlefield = 'abcdefghijklmnopqrstuvwxyz0123456789', supply_points = 100)
battle = models.Battle(attacker = user, defender = user2, sp_attacker = 100, sp_defender = 90, conf_attacker = 'abcdefghijklmnopqrstuvwxyz0123456789', conf_defender = 'abcdefghijklmnopqrstuvwxyz0123456789', territory = ter, attacker_empire = emp, defender_empire = emp2)