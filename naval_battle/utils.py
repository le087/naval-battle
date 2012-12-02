# -*- coding: utf-8 -*-

import datetime
from models import Fields, Users, Games
from utils2 import get_around_cells

#------------------------------------------------------------
# get database section
#------------------------------------------------------------
def get_fields():
    """return fields from database
    """
    return Fields.objects()

def get_wait_users():
    """return list of users who are waiting game
    """
    users_wait = Users.objects(status=0)
    for user in users_wait:
        try:
            field = Fields.objects.get(id=user.field_battle.id)
        except:
            field = Fields()
            field.save()
        try:
            game = Games.objects.get(id=user.game.id)
            game.fields = [field]
            game.save()
        except:
            game = Games(fields=[field])
            game.save()
        user.field_battle = field
        user.game = game
        user.save()
    return users_wait


def get_begin_games():
    """return list begin games
    
    the structure of dictionary is:
    { 'id_game':['user1', 'user2'],
      'id_game':['user1', 'user2']}
    """
    games_begin = Games.objects(status=1)
    users = Users.objects(game__in=games_begin)
    games = {}
    for user in users:
        game = user.game
        id_game = str(game.id)
        if games.has_key(id_game):
            games[id_game].append(user.user_name)
        else:
            games[id_game] = [user.user_name]
    return games


def get_user_id(session_id):
    """return user with id
    
    Arguments:
    - `session_id`: session_id
    """
    try:
        user = Users.objects.get(session=session_id)
        return str(user.id)
    except:
        return None

def get_user_status(session_id):
    """return user status
    
    Arguments:
    - `session_id`:
    """
    try:
        user = Users.objects.get(session=session_id)
        return user.status
    except:
        return 7

def get_field_dictionary(session_id):
    """ return the current snapshot field
    by session_id from cookies
    
    Arguments:
    - `session_id`: session id of user
    """
    try:
        user = Users.objects.get(session=session_id)
        return user.field_battle.snapshot
    except:
        return False

def get_user_by_session(session_id):
    """return objects user 
    
    Arguments:
    - `session_id`: session
    """
    try:
        return Users.objects.get(session=session_id)
    except:
        return False

def get_value_coordinata(session_id, coordinata):
    """ return value cell from database

    if user.status == 4, then user wait move
    if user.status == 3, then user go
    
    Arguments:
    - `session_id`: session id shooter
    - `coordinata`: coordinata
    """
    user = Users.objects.get(session = session_id)
    game = user.game
    for field in game.fields:
        if user.field_battle != field:
            coordict = field.snapshot
            other_user = Users.objects.get(field_battle=field)
            if coordict[coordinata] == u"0":
                coordict[coordinata] = u"1"
                user.status = 4
                user.save()
                other_user.status = 3
                other_user.save()
                field.snapshot = coordict
            if coordict[coordinata] == u"2":
                not_kill_flag = False
                x = coordinata[0]
                y = coordinata[1]
                graycells = []
                # for self cell
                cells = get_around_cells(int(x), int(y))
                for cell in cells:
                    if coordict[cell] == "1" or coordict[cell] == "0":
                        graycells.append(cell)
                # REFACTOR IT!
                # top cells
                # and yes, I know about range(x)!
                for i in [1, 2, 3]:
                    if not_kill_flag:
                        break
                    if coordict.has_key(str(int(x)-i)+y): 
                        if coordict[str(int(x)-i)+y] == "0" or coordict[str(int(x)-i)+y] == "1":
                            break
                        if coordict[str(int(x)-i)+y] == "2":
                            not_kill_flag = True
                            break
                        if coordict[str(int(x)-i)+y] == "3":
                            cells = get_around_cells((int(x)-i), int(y))
                            for cell in cells:
                                if coordict[cell] == "1" or coordict[cell] == "0":
                                    graycells.append(cell)
                # bottom cells
                for i in [1, 2, 3]:
                    if not_kill_flag:
                        break
                    if coordict.has_key(str(int(x)+i)+y): 
                        if coordict[str(int(x)+i)+y] == "0" or coordict[str(int(x)+i)+y] == "0":
                            break
                        if coordict[str(int(x)+i)+y] == "2":
                            not_kill_flag = True
                            break
                        if coordict[str(int(x)+i)+y] == "3":
                            cells = get_around_cells((int(x)+i), int(y))
                            for cell in cells:
                                if coordict[cell] == "1" or coordict[cell] == "0":
                                    graycells.append(cell)
                # left cells
                for i in [1, 2, 3]:
                    if not_kill_flag:
                        break
                    if coordict.has_key(x+str(int(y)-i)): 
                        if coordict[x+str(int(y)-i)] == "0" or coordict[x+str(int(y)-i)] == "1":
                            break
                        if coordict[x+str(int(y)-i)] == "2":
                            not_kill_flag = True
                            break
                        if coordict[x+str(int(y)-i)] ==  "3":
                            cells = get_around_cells(int(x), int(y)-i)
                            for cell in cells:
                                if coordict[cell] == "1" or coordict[cell] == "0":
                                    graycells.append(cell)
                # right cells
                for i in [1, 2, 3]:
                    if not_kill_flag:
                        break
                    if coordict.has_key(x+str(int(y)+i)): 
                        if coordict[x+str(int(y)+i)] == "0" or coordict[x+str(int(y)+i)] == "1":
                            break
                        if coordict[x+str(int(y)+i)] == "2":
                            not_kill_flag = True
                            break
                        if coordict[x+str(int(y)+i)] == "3":
                            cells = get_around_cells(int(x), int(y)+i)
                            for cell in cells:
                                if coordict[cell] == "1" or coordict[cell] == "0":
                                    graycells.append(cell)
                
                # get uniq cells
                graycells = list(set(graycells))

                # push results calculates in db
                if not not_kill_flag:
                    for i in graycells:
                        coordict[i] = u"1"
                coordict[coordinata] = u"3"
                field.snapshot = coordict
            field.save();

            # check that were kill all cells
            kill_cells = 0
            for key in coordict.keys():
                if coordict[key] == "3":
                    kill_cells += 1

            if kill_cells >= 20:
                user.status = 5
                user.save()
                other_user.status = 6
                other_user.save()
                game.status = 2
                game.time_end = datetime.datetime.now()
                game.save()
                # return u"4", means finish game
                return u"4"
            # graycells return in function get_field_opponent(session_id)
            return coordict[coordinata]

def get_field_opponent(session_id):
    """ return field by opponent
    
    Arguments:
    - `session_id`:
    """
    user = Users.objects.get(session=session_id)
    for u in Users.objects(game=user.game):
        if u.session != session_id:
            field = u.field_battle
            snapshot = field.snapshot
            visible_snapshot = {}
            for key, val in snapshot.iteritems():
                if val == u"2":
                    visible_snapshot[key] = u"0"
                else:
                    visible_snapshot[key] = val
            return visible_snapshot

#------------------------------------------------------------
# add and update database section
#------------------------------------------------------------
def add_user_in_db(session_id, username, game, field, status=0):
    """create user in database for registration in game
    
    Arguments:
    - `session`: uniq session 
    - `user`: name user from form
    - `game`: id game
    - `field`: id fields
    - `status`: status of user on site
    """
    # check session_id in database
    users = Users.objects(session=session_id) 
    if not users:
        new_user = Users(user_name=username, 
                         session=session_id,
                         game=game,
                         field_battle=field,
                     status=status)
        new_user.save()
    else:
        user = Users.objects.get(session=session_id)
        user.game = game
        user.user_name = username
        user.field_battle = field
        user.status = status
        user.save()
    return True

def add_new_field():
    """add new field in database
    """
    new_field = Fields()
    new_field.save()
    return new_field

def add_new_game(new_field):
    """add new game in database
    
    - `new_field`: object field
    """
    new_game = Games(fields=[new_field])
    new_game.save()
    return new_game

def add_field_in_game(user_id, field):
    """ add second field in create game other user
    
    Arguments:
    - `user_id`: first user
    - `field`: second field
    """
    first_user = Users.objects.get(id=user_id)
    game = Games.objects.get(id=first_user.game.id)
    game.fields.append(field)
    game.save(cascade=True)
    return game

def update_field(session_id, field_dict):
    """update data in field
    
    Arguments:
    - `session_id`: session current user
    - `field_dict`: new data in field
    """
    try:
        # if use:
        # user = Users.objects.get(session=session_id)
        # user.battle_field.snapshot = field_dict
        # then flask report about:
        # "FutureWarning: Cascading saves will default to off in 0.8, please  explicitly set `.save(cascade=True)`"
        # I rewrote the code ----->
        user = Users.objects.get(session=session_id)
        field = Fields.objects.get(id=user.field_battle.id)
        field.snapshot = field_dict
        field.save(cascade=True)
        return True
    except:
        print 'проверить utils.update_field'
        return False

def update_status_user(user_id, status):
    """ make update the status of user
    
    Arguments:
    - `user_id`: user in Users
    - `status`: status in user.status 
    """
    try:
        user = Users.objects.get(id=user_id)
        user.status = status
        user.save(cascade=True)
        return True
    except:
        return False

def update_user(**kwargs):
    """ update data for current user
    
    Arguments:
    - `*args`:
    """
    if  kwargs.has_key('session_id'):
        try:
            user = Users.objects.get(session=kwargs['session_id'])
        except:
            return False
        if kwargs.has_key('game'):
            user.game = kwargs['game']
        if kwargs.has_key('field'):
            field = user.field_battle
            field.delete()
            field.save()
            user.field_battle = kwargs['field']
        if kwargs.has_key('status'):
            if kwargs['status'] == 4:
                users = Users.objects(game=user.game)
                for u in users:
                    if u.session != user.session and u.status == 4:
                        u.status = 3
                        u.save()
                        game = u.game
                        game.status = 1
                        game.save()
            user.status = kwargs['status']
        user.save()
        return user.user_name
    else:
        return False
        

#------------------------------------------------------------
# delete database section
#------------------------------------------------------------

def drop_user(session_id):
    """delete user from db, clear game, delete field
    
    Arguments:
    - `session_id`:
    """
    try:
        user = Users.objects.get(session=session_id)
        field = user.field_battle
        game = user.game
        users = Users.objects(game=game)
        for u in users:
            if u != user:
                u.status = 7
            else:
                u.status = 0;
            u.save()
        user.delete()
        game.delete()
        field.delete()
        return True
    except:
        return False
