# -*- coding: utf-8 -*-
#------------------------------------------------------------
# views
#------------------------------------------------------------

import json

from flask import render_template, request, make_response, jsonify
from naval_battle import app
from naval_battle.utils2 import randstring
# TODO: after finish process develop replace on 
# 'from naval_battle.utils import *'
from naval_battle.utils import add_user_in_db, add_new_game, get_wait_users \
,add_new_field, get_user_id, get_begin_games, get_field_dictionary, update_field \
,add_field_in_game, get_user_status, drop_user, update_user \
,get_value_coordinata, get_field_opponent, get_user_by_session, get_opponent \
,get_fields_move_games, get_session_by_game, get_session_by_user_id, get_time_begin

@app.route("/", methods=['GET', 'POST'])
def main_page():
    """main page, install cookie for new users
    """
    current_page = u'Главная страница'
    users_wait = get_wait_users()
    if not request.cookies.has_key('session_id'):
        cookie_session = randstring()
        response = make_response(render_template('main_page.html', 
                                                 current_page=current_page,
                                                 users_wait=users_wait))
        response.set_cookie('session_id', cookie_session)
        return response
    else:
        return make_response(render_template('main_page.html', 
                                             current_page=current_page,
                                             users_wait=users_wait))
        

@app.route("/add_new_user/", methods=['GET', 'POST'])
def add_new_user():
    """registration user in database for game

    jsonify: 
     - `username` : username from form 
     - `user_id` : set user.id for uniq
     - `new_user`: `1` - this new user
                   `0` - this old user, dont hand
    """
    if request.method == 'POST':
        username = request.form.values()[0].encode('utf8')
        # check session
        if request.cookies.has_key('session_id'):
            cookie_session = request.cookies.get('session_id')
        else:
            cookie_session = randstring()
        user = get_user_by_session(cookie_session)
        # if user exist
        if user:
            # if already have a server
            if user.status == 0:
                return jsonify(new_user=0)
            # if game was finished
            if user.status == 5 or user.status == 6 or user.status == 7:
                field = add_new_field()
                game = add_new_game(field)
                if add_user_in_db(cookie_session, username, game, field):
                    return jsonify(username=username,
                                   user_id=get_user_id(cookie_session),
                                   user_status=0, 
                                   new_user=1)
            # if in game play now
            if user.status == 3 or user.status == 4:
                return jsonify(new_user=2)
        else:
            field = add_new_field()
            game = add_new_game(field)
            if add_user_in_db(cookie_session, username, game, field):
                return jsonify(username=username,
                               user_id=get_user_id(cookie_session),
                               user_status=0, 
                               new_user=1)

@app.route("/add_second_user/", methods=['GET', 'POST'])
def add_second_user():
    """registration second user for play
    """
    if request.method == 'POST': 
        wait_user = request.form['user_id'].encode('utf8')
        username = request.form['username'].encode('utf8')
        if request.cookies.has_key('session_id'):
            cookie_session = request.cookies.get('session_id')
        # TODO: this is bottleneck
        # add exception here!
        current_user = get_user_by_session(cookie_session)
        if current_user and str(current_user.id) == wait_user:
            return jsonify(result="0")
        field = add_new_field()
        game = add_field_in_game(wait_user, field)
        add_user = add_user_in_db(cookie_session, username, game, field, status=1)
        session_wait_user = get_session_by_user_id(wait_user)
        new_data_user = { 'session_id' : session_wait_user,
                          'status': 1 }
        update_status = update_user(**new_data_user)
        if add_user and update_status:
            return jsonify(result="1")
            

@app.route("/update_data_for_main_page/", methods=['GET', 'POST'])
def update_data_main_page():
    """return json with information about:

    - users who wait second player
    - games which does now

    the structure of dictionary is:
    { 'users':{ 'id1':'username1',
                'id2':'username2'},

      'games': { 'id':[user1, user2],
                 'id':[user1, user2]}}
    """
    if request.method == 'POST':
        current_user = "0"
        if request.cookies.has_key('session_id'):
            cookie_session = request.cookies.get('session_id')
            user_status = get_user_status(cookie_session)
            if user_status == 1:
                return jsonify(user_status=user_status)
            if user_status == 0:
                user = get_user_by_session(cookie_session)
                if user:
                    current_user = user.user_name
        users = get_wait_users()
        list_username = {}
        for user in users:
            list_username[str(user.id)] = user.user_name
        games = get_begin_games()
        return jsonify(users=list_username, games=games, current_user=current_user)

@app.route("/configure/", methods=['GET', 'POST'])
def configure():
    """the page for configure field battle
    """
    current_page = u'Настроить расположение фрегатов'
    response = make_response(render_template('configure.html', current_page=current_page))
    return response

@app.route("/send_state_field/", methods=['GET', 'POST'])
def send_state_field():
    """return the current snapshot field
    """
    if request.method == 'POST':
        if request.cookies.has_key('session_id'):
            cookie_session = request.cookies.get('session_id')
            field = get_field_dictionary(cookie_session)
            user_status = get_user_status(cookie_session)
            return jsonify(field=field,
                           status=user_status)

@app.route("/get_state_field/", methods=['GET', 'POST'])
def get_state_field():
    """get data about field from js
    """
    if request.method == 'POST':
        if request.cookies.has_key('session_id'):
            cookie_session = request.cookies.get('session_id')
            field = json.loads(request.form.keys()[0])
            if update_field(cookie_session, field):
                return jsonify(result='1')
            else:
                return jsonify(result='0')

@app.route("/get_names_players/", methods=['GET', 'POST'])
def get_names_players():
    """get names user and his opponent
    """
    if request.method == 'POST':
        if request.cookies.has_key('session_id'):
            cookie_session = request.cookies.get('session_id')
            username = get_user_by_session(cookie_session)
            opponent = get_opponent(cookie_session)
            return jsonify(username=username.user_name,
                           opponent=opponent.user_name)

@app.route("/all_cancel/", methods=['GET', 'POST'])
def all_cancel():
    """reset all data for current game by user
    """
    if request.method == 'POST':
        if request.cookies.has_key('session_id'):
            cookie_session = request.cookies.get('session_id')
            if drop_user(cookie_session):
                return jsonify(result=True)

@app.route("/reset_game/", methods=['GET', 'POST'])
def reset_game():
    """reset current games
    """
    if request.method == 'POST':
        if request.cookies.has_key('session_id'):
            cookie_session = request.cookies.get('session_id')
            field = add_new_field()
            game = add_new_game(field)
            new_data_user = { 'game': game,
                              'field': field,
                              'session_id': cookie_session,
                              'status': 0}
            username = update_user(**new_data_user)
            if username:
                return jsonify(username=username,
                           user_id=get_user_id(cookie_session),
                           user_status=0, 
                           new_user=1)

@app.route("/battle/", methods=['GET', 'POST'])            
def battle():
    """a page for configure field battle
    """
    current_page = u'Битва!'
    response = make_response(render_template('battle.html', current_page=current_page))
    return response

@app.route("/move_battle/", methods=['GET', 'POST'])            
def move_battle():
    """move to battle
    """
    if request.method == 'POST':
        if request.cookies.has_key('session_id'):
            cookie_session = request.cookies.get('session_id')
            new_data_user = {'session_id':cookie_session,
                             'status': 4 }
            update_user(**new_data_user)
            return jsonify(result=1)

@app.route("/go_move_battle/<id_game>/", methods=['GET'])            
def go_move_battle(id_game):
    """move to battle
    """
    current_page = u'Ход игры'
    response = make_response(render_template('move_game.html', 
                                             current_page=current_page,
                                             id_game=id_game))
    return response

    


@app.route("/check_shot/", methods=['GET', 'POST'])            
def check_shot():
    """check a shot and return result of shot
    """
    if request.method == 'POST':
        if request.cookies.has_key('session_id'):
            cookie_session = request.cookies.get('session_id')
            coordinata = request.form['coordinata'].encode('utf8')
            result = get_value_coordinata(cookie_session, coordinata)
            field_opponent = get_field_opponent(cookie_session)
            return jsonify(result=result,
                           coordinata=coordinata,
                           field_opponent=field_opponent)

@app.route("/get_field_second/", methods=['GET', 'POST'])            
def get_field_second():
    """return field by opponent
    """
    if request.method == 'POST':
        if request.cookies.has_key('session_id'):
            cookie_session = request.cookies.get('session_id')
            field_opponent = get_field_opponent(cookie_session)    
            return jsonify(field_opponent=field_opponent)

@app.route("/get_fields/", methods=['GET', 'POST'])            
def get_fields():
    """return fields of two plaing users
    """
    
    def return_data_field(cookie_session):
        """response for request
        
        Arguments:
        - `cookie_session`: session of user
        """
        
        months = { '01': 'января',
                   '02': 'февраля',
                   '03': 'марта',
                   '04': 'апреля',
                   '05': 'мая',
                   '06': 'июня',
                   '07': 'июля',
                   '08': 'августа',
                   '09': 'сентября',
                   '10': 'октября',
                   '11': 'ноября',
                   '12': 'декабря'
            }
        
        user = get_user_by_session(cookie_session)
        opponent = get_opponent(cookie_session)
        user_field_id = str(user.field_battle.id)
        opponent_field_id = str(opponent.field_battle.id)
        user_field, opponent_field = get_fields_move_games(user_field_id, opponent_field_id)
        game_status = user.game.status
        time_begin, game_duration = get_time_begin(cookie_session)
        # TODO: add data and time
        if user_field and opponent_field:
            return jsonify(user_field=user_field, 
                           opponent_field=opponent_field,
                           username=user.user_name, 
                           opponentname=opponent.user_name,
                           game_status=game_status,
                           time_begin=time_begin.strftime('%H:%M %d ') + months[time_begin.strftime('%m')]+ time_begin.strftime(' %Y') + 'г.',
                           game_duration = game_duration,
                           result="1")
        return False
    
    # return result
    if request.method == 'POST':
        if request.form['id_game'].encode('utf8'):
            cookie_session = get_session_by_game(request.form['id_game'].encode('utf8'))
            result = return_data_field(cookie_session)
            if result: 
                return result
            return jsonify(result="0")
        else:
            if request.cookies.has_key('session_id'):
                cookie_session = request.cookies.get('session_id')
                result = return_data_field(cookie_session)
                if result:
                    return result
                return jsonify(result="0")
            return jsonify(result="0")
        return jsonify(result="0")

        
@app.route("/move_game/", methods=['GET', 'POST'])
def move_game():
    """page for watch game
    """
    current_page = u'Ход игры'
    response = make_response(render_template('move_game.html', 
                                             current_page=current_page))
    return response

@app.route("/archive/")
def archive():
    """page with results old games
    """
    pass

