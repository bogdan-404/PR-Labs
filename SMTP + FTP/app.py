from flask import Flask, request, render_template, redirect, url_for
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from ftplib import FTP

app = Flask(__name__)


def send_email(destination_email, subject, email_text, file_link=""):
    sender_email = "cocostarcandrei84@gmail.com"
    sender_password = "wxxo mbqa nims qbqo"
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = destination_email
    message["Subject"] = subject
    if file_link:
        email_text += f"\n\nYou can download the file at: {file_link}"
    message.attach(MIMEText(email_text, "plain"))
    session = smtplib.SMTP("smtp.gmail.com", 587)
    session.starttls()
    session.login(sender_email, sender_password)
    session.sendmail(sender_email, destination_email, message.as_string())
    session.quit()


def upload_file_ftp(file_path):
    ftp_server = "138.68.98.108"
    ftp_user = "yourusername"
    ftp_password = "yourusername"
    with FTP(ftp_server) as ftp:
        ftp.login(user=ftp_user, passwd=ftp_password)
        with open(file_path, "rb") as file:
            ftp.storbinary(f"STOR {os.path.basename(file_path)}", file)
    return f"http://138.68.98.108/faf-212/bogdan/{os.path.basename(file_path)}"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/send_email", methods=["POST"])
def handle_send_email():
    destination_email = request.form["email"]
    subject = request.form["subject"]
    email_text = request.form["message"]
    file_link = ""
    if "file" in request.files:
        file = request.files["file"]
        if file.filename != "":
            file_path = os.path.join("uploads", file.filename)
            file.save(file_path)
            file_link = upload_file_ftp(file_path)
    send_email(destination_email, subject, email_text, file_link)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)

