from email.message import EmailMessage
import os, ssl, smtplib

email_sender = os.environ["Email_from"]
email_password = os.environ["Email_password"]
em = EmailMessage()

def send_email(**email):
  try:
    em['sender'] = email_sender
    em['to'] = email["receiver"]
    em['subject'] = email["subject"]
    em.set_content(email["body"])
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
      smtp.login(email_sender, email_password)
      smtp.sendmail(email_sender, email["receiver"], em.as_string())
      smtp.quit()
      del em["To"]
  except:
    print("email not sent")
