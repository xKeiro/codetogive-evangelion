from flask import Flask  # type: ignore
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask import make_response

import util
from data_manager import language_handler
from data_manager import user_handler
from data_manager import work_motivation_handler

app = Flask(__name__)
app.secret_key = ("b'o\xa7\xd9\xddj\xb0n\x92qt\xcc\x13\x113\x1ci'")

@app.context_processor
def inject_dict_for_all_templates():
    text = language_handler.get_texts_in_language(request.cookies.get("language", "hu"))
    return dict(text=text)


@app.route('/')
def index():
    resp = make_response(render_template("index.jinja2"))
    # resp.set_cookie('language', 'hu')
    return resp


# region -------------------------------AUTHENTICATION-----------------------------------------
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        expected_fields = ["username", "password", "email", "last_name", "first_name", "birthday"]
        fields = request.form.to_dict();
        fields = {key: fields[key] for key in fields if key in expected_fields}
        fields["password"] = util.hash_password(fields["password"])
        try:
            user_handler.add_new_user(fields)
        except:
            return render_template("authentication/register.jinja2", matching_username=True)
        session["username"] = fields["username"]
        return redirect(url_for('index'))
    return render_template("authentication/register.jinja2", matching_username=False)


@app.route('/login', methods=["GET", "POST"])
def login():
    login_attempt_failed = False
    if request.method == "POST":
        expected_fields = ["username", "password"]
        fields = request.form.to_dict();
        fields = {key: fields[key] for key in fields if key in expected_fields}
        try:
            hashed_password = user_handler.get_user_password_by_username(fields["username"])
            is_valid_login = util.check_password(fields["password"], hashed_password)
            if is_valid_login:
                session["username"] = fields["username"]
                return redirect(url_for("index"))
        except:
            login_attempt_failed = True
    return render_template("authentication/login.jinja2", login_attempt_failed=login_attempt_failed)


@app.route('/logout')
@util.login_required
def logout():
    session.pop("username")
    return redirect(request.referrer)


# endregion


@app.route('/test/work-motivation')
@util.login_required
def work_motivation():
    questions = work_motivation_handler.get_questions()
    return render_template('tests/work_motivation.jinja2', questions=questions)


@app.route('/api/work-motivation', methods=["POST"])
@util.login_required
@util.json_response
def api_work_motivation_submit():
    answers = request.json
    work_motivation_handler.submit_answer(answers, session["username"])
    return {"status": "success"}
