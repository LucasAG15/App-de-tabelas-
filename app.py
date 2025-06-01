
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm
import os
import matplotlib.pyplot as plt
import uuid
import matplotlib
matplotlib.use('Agg')  # Configura o backend para não interativo


app = Flask(__name__)
app.config['SECRET_KEY'] = 'segredo-supersecreto'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

GRAPH_FOLDER = os.path.join("static", "graphs")
app.config["GRAPH_FOLDER"] = GRAPH_FOLDER

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Usuário registrado com sucesso!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login inválido!', 'danger')
    return render_template('login.html', form=form)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('create_graph.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/create_graph", methods=["GET", "POST"])
@login_required
def create_graph():
    if request.method == "POST":
        tipo = request.form["tipo"]
        titulo = request.form["titulo"]
        labels = request.form.get("labels").split(",")
        valores = list(map(int, request.form.get("valores").split(",")))

        # Gerar gráfico
        plt.clf()
        if tipo == "pizza":
            plt.pie(valores, labels=labels, autopct="%1.1f%%")
        elif tipo == "barra":
            plt.bar(labels, valores)
        elif tipo == "linha":
            plt.plot(labels, valores)

        plt.title(titulo)

        # Salvar imagem
        nome_arquivo = f"{uuid.uuid4().hex}.png"
        caminho = os.path.join(app.config["GRAPH_FOLDER"], nome_arquivo)
        plt.savefig(caminho)

        # Redirecionar para a página de exibição do gráfico
        return redirect(url_for("ver_grafico", nome=nome_arquivo, titulo=titulo))

    return render_template("create_graph.html")


@app.route("/ver_grafico")
@login_required
def ver_grafico():
    nome = request.args.get("nome")
    titulo = request.args.get("titulo")
    return render_template("view_graph.html", nome=nome, titulo=titulo)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
