from flask import Flask, render_template, request, redirect, session
from config import get_db_connection

from routes.dashboard import dashboard_bp
from routes.inventory import inventory_bp
from routes.inventory_report import inventory_report_bp
from routes.distribution import distribution_bp
from routes.forecast import forecast_bp
from routes.medicine_request import medicine_request_bp
from routes.distribution_report import distribution_report_bp
from routes.received_report import received_report_bp
from routes.expiry_wastage_report import expiry_wastage_report_bp
from routes.activity_log import activity_log_bp
from routes.settings import settings_bp

from datetime import timedelta


app = Flask(__name__)

app.secret_key = "meditrack_secret_key_2026"
app.permanent_session_lifetime = timedelta(hours=24)


# ==============================
# REGISTER BLUEPRINTS
# ==============================

app.register_blueprint(dashboard_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(inventory_report_bp)
app.register_blueprint(distribution_bp)
app.register_blueprint(forecast_bp)
app.register_blueprint(medicine_request_bp)
app.register_blueprint(distribution_report_bp)
app.register_blueprint(received_report_bp)
app.register_blueprint(expiry_wastage_report_bp)
app.register_blueprint(activity_log_bp)
app.register_blueprint(settings_bp)


# ==============================
# LANDING PAGE
# ==============================

@app.route("/")
def landing():
    return render_template("landing.html")


# ==============================
# LOGIN PAGE
# ==============================

@app.route("/login", methods=["GET", "POST"])
def login():

    # Kapag binuksan lang ang /login sa browser,
    # ipapakita muna ang login page.
    if request.method == "GET":
        return render_template("login.html")

    # Kapag nag-submit ng login form,
    # dito iche-check ang account.
    employee_id = request.form["user_id"]
    password = request.form["password"]

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM users
        WHERE employee_id = %s
        AND password = %s
        AND status = 'Active'
    """, (employee_id, password))

    user = cursor.fetchone()

    cursor.close()
    db.close()

    if user:
        session.permanent = True
        session["user_id"] = user["id"]
        session["employee_id"] = user["employee_id"]
        session["full_name"] = user["full_name"]
        session["role"] = user["role"]

        return redirect("/dashboard")

    return render_template(
        "login.html",
        error="Invalid Employee ID or Password"
    )


# ==============================
# LOGOUT
# ==============================

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ==============================
# RUN APP
# ==============================

if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True)