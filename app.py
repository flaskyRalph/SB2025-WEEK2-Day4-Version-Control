from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_bootstrap import Bootstrap5

app = Flask(__name__)
bootstrap = Bootstrap5(app)

# Database configurations
app.config['SECRET_KEY'] = "Do_not_expose"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Define PostgreSQL User model
class Users(db.Model):
    userID: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    Fname: Mapped[str] = mapped_column(nullable=False)
    Lname: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True, nullable=False)


class Log(db.Model):
    logID: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    action: Mapped[str] = mapped_column(nullable=False)
    timestamp: Mapped[DateTime] = mapped_column(DateTime, default=db.func.now())
    userID: Mapped[int] = mapped_column(nullable=True)


def log_action(action, user_id=None):
    log_entry = Log(action=action, userID=user_id)
    db.session.add(log_entry)
    db.session.commit()


@app.route('/')
def homePage():
    users = Users.query.all()
    return render_template('index.html', users=users)


@app.route('/create', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        Fname = request.form['Fname']
        Lname = request.form['Lname']
        email = request.form['email']
        
        if Users.query.filter_by(email=email).first():
            flash("Email already exists!", "danger")
            return redirect(url_for('create_user'))
        
        new_user = Users(Fname=Fname, Lname=Lname, email=email)
        db.session.add(new_user)
        db.session.commit()
        log_action(f"Created user {Fname.title()} {Lname.title()}", new_user.userID)
        
        flash("User created successfully!", "success")
        return redirect(url_for('homePage'))
    
    return render_template('create.html')


@app.route('/logs')
def view_logs():
    logs = Log.query.all()
    return render_template('logs.html', logs=logs)


if __name__ == '__main__':
    app.run(debug=True)
