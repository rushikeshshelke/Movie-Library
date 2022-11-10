import uuid
import datetime
import functools

from flask import (
    Blueprint,
    render_template,
    current_app,
    session,
    redirect,
    request,
    url_for,
    abort,
    flash
)
from moviewatchlist.commonLibs.forms import (
    MovieForm,
    ExtendedMovieForm,
    RegisterForm,
    LoginForm
)
from moviewatchlist.models.models import Movie, User
from dataclasses import asdict
from moviewatchlist.commonLibs.globalVariables import GlobalVariables
from passlib.hash import pbkdf2_sha256

pages = Blueprint("movieLibrary",__name__,template_folder="../templates")

def login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args, **kwargs):
        if session.get("email") == None:
            return redirect(url_for(".login"))
        
        return route(*args, **kwargs)
    
    return route_wrapper

@pages.route("/")
@login_required
def index():
    user_data = current_app.db.user.find_one({"email":session["email"]})
    user = User(**user_data)

    movie_data = current_app.db.movie.find({"_id": {"$in":user.movies}})
    movies = [Movie(**movie) for movie in movie_data]
    return render_template(
        "index.html",
        title="Movie Watchlist",
        movies_data=movies
    )

@pages.route("/register",methods=["GET","POST"])
def register():

    if session.get("email"):
        return redirect(url_for(".index"))
    
    form = RegisterForm()

    if form.validate_on_submit():
        user = User(
            _id = uuid.uuid4().hex,
            email = form.email.data,
            password = pbkdf2_sha256.hash(form.password.data)
        )

        existingUser = current_app.db.user.find_one({"email":form.email.data})

        if existingUser:
            flash("User alreay exists... Try to login", "danger")
            return redirect(url_for('.login'))

        current_app.db.user.insert_one(asdict(user))

        flash("User registered successfully", "success")

        return redirect(url_for(".login"))
    
    return render_template(
        "register.html",
        title="Movie Watchlist - Register",
        form=form
    )

@pages.route("/login",methods=["GET","POST"])
def login():
    
    if session.get("email"):
        return redirect(url_for(".index"))

    form = LoginForm()

    if form.validate_on_submit():
        user_data = current_app.db.user.find_one({"email":form.email.data})
        
        if not user_data:
            flash("Invalid login credentials", category="danger")
            return redirect(url_for(".login"))
        
        user = User(**user_data)

        if user and pbkdf2_sha256.verify(form.password.data,user.password):
            session["user_id"] = user._id
            session["email"] = user.email

            return redirect(url_for(".index"))
        
        flash("Invalid login credentials", category="danger")
     
    return render_template(
        "login.html",
        title="Movie Watchlist - Login",
        form=form
    )

@pages.route("/logout",methods=["GET"])
def logout():
    currentTheme = session.get("theme")
    session.clear()
    session["theme"] = currentTheme
    return redirect(url_for('.login'))

@pages.route("/add",methods=["GET","POST"])
@login_required
def addMovie():

    form = MovieForm()

    if form.validate_on_submit():
        movies = Movie(
            _id= uuid.uuid4().hex,
            title= form.title.data,
            director= form.director.data,
            year= form.year.data
        )
    
        current_app.db.movie.insert_one(asdict(movies))
        current_app.db.user.update_one(
            {"_id":session["user_id"]},{"$push":{"movies":movies._id}}
        )

        return redirect(url_for(".index"))

    return render_template(
        "new_movie.html",
        title="Movies Watchlist - Add Movie",
        form=form
        )

@pages.route("/edit/<string:_id>", methods=["GET","POST"])
@login_required
def editMovie(_id: str):
    movie_data = current_app.db.movie.find_one({"_id": _id})
    movie = Movie(**movie_data)
    form = ExtendedMovieForm(obj=movie)

    if form.validate_on_submit():
        movie.cast = form.cast.data
        movie.series = form.series.data
        movie.tags = form.tags.data
        movie.description = form.description.data
        movie.video_link = form.video_link.data
    
        current_app.db.movie.update_one({"_id":_id}, {"$set": asdict(movie)})

        return redirect(url_for(".movie",_id=movie._id))
    
    return render_template("movie_form.html", movie=movie, form=form)


@pages.route("/movie/<string:_id>", methods=["GET"])
def movie(_id: str):
    movie_data = current_app.db.movie.find_one({"_id": _id})

    GlobalVariables.LOGGER.info("Movie data : {}".format(movie_data))
    
    if not movie_data:
        abort(404)
    
    movie = Movie(**movie_data)

    GlobalVariables.LOGGER.info("Movie data : {}".format(movie))

    return render_template("movie_details.html",movie=movie)

@pages.route("/movie/<string:_id>/rate",methods=["GET"])
@login_required
def rateMovie(_id: str):
    rating = int(request.args.get("rating"))

    current_app.db.movie.update_one({"_id": _id}, {"$set": {"rating":rating}})

    return redirect(url_for(".movie", _id=_id))

@pages.route("/movie/<string:_id>/watch", methods=["GET"])
@login_required
def watchToday(_id: str):

    current_app.db.movie.update_one(
        {"_id": _id},
        {"$set": {"last_watched": datetime.datetime.today()}}
        )
    
    return redirect(url_for(".movie", _id=_id))

@pages.route("/toggle-theme",methods=["GET"])
def toggleTheme():

    currentTheme = session.get("theme")
    if currentTheme == "dark":
        session["theme"] = "light"
    else:
        session["theme"] = "dark"
    
    return redirect(request.args.get("current_page"))