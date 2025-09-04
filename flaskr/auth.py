import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Nome do usuario e obrigatorio'
        elif not password:
            error = 'Senha e obrigatorio'
        
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"Usuario {username} ja esta registrado."
            else:
                return redirect(url_for("auth.login"))
            
        flash(error)
    
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone() # fetchnone retorna apenas um resultado da busca do banco de dados. Se retornar nada, user armazenará None. (ao invés de um objeto db)

        if user is None:
            error = 'Nome de usuario incorreto.'
        elif not check_password_hash(user['password'], password):
            error = 'Senha incorreta.'
        
        if error is None:
            session.clear()
            session['user_id'] = user['id'] # armazena o id do usuario em um cookie no navegador (de forma segura) para que a informação já exista quando outras requisições forem feitas
            return redirect(url_for('index'))
        
        flash(error)
    
    return render_template('auth/login.html')

@bp.before_app_request # isso indica que essa função vai rodar antes de qualquer função de outra view rodar
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Essa função vai pegar outra função (a que está sendo enviada por parâmetro) e ENROLAR a função dentro dela, vai "encapsular" a função enviada
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:   #ver função load_logged_user
            return redirect(url_for('auth.login'))
        
        return view(**kwargs) #se tiver um usuário, retorna a função que foi chamada inicialmente, a que foi "enrolada/wrapped" pela login_required

    return wrapped_view #login_required retorna wrapped_view, que vai primeiro verificar se o usuário está logado para então devolver a função/view que foi enrolada/wrapped