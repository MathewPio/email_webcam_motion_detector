import smtplib
import filetype
from email.message import EmailMessage

SENDER = "oseghaleokononfua@gmail.com"
PASSWORD = "apniqkhftfrlcnzg"
RECEIVER = "oseghaleokononfua@gmail.com"

def send_email(image_path):
    email_message = EmailMessage()
    email_message["subject"] = "New customer showed up!"
    email_message.set_content("Hey, We just saw a new customer!")
    
    with open(image_path, "rb") as file:
        content = file.read()

    kind = filetype.guess(content)
    
    if kind:
        email_message.add_attachment(
            content,
            maintype="image",
            subtype=kind.extension
        )
        
    gmail = smtplib.SMTP("smtp.gmail.com", 587)
    gmail.ehlo()
    gmail.starttls()
    gmail.login(SENDER, PASSWORD)
    gmail.sendmail(SENDER, RECEIVER, email_message.as_string())
    gmail.quit()
            
   
if __name__ == "__main__":
    send_email(image_path="images/14.png")
   