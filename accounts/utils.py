import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import qrcode
#from io import StringIO
from django.core.files.base import ContentFile
###############
from rest_framework.views import exception_handler
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    if isinstance(exc, NotAuthenticated):
        return Response({"message": "token auth required"}, status=200)

    # else
    # default case
    return exception_handler(exc, context)
################

#mail_content = '''Hello,
#This is a simple mail. There is only text, no attachments are there The mail is sent using Python SMTP library.
#Thank You'''
#The mail addresses and password
#sender_address = 'drake.augurs@gmail.com'
#sender_pass = 'Augurs@9848'
#sender_pass = 'cmbltdegazabdqjv'

#receiver_address = 'deepak.narayanan@yahoo.com'
#Setup the MIME
#message = MIMEMultipart()
#message['From'] = sender_address
#message['To'] = receiver_address
#message['Subject'] = 'A test mail sent by Python. It has an attachment.'   #The subject line
#The body and the attachments for the mail
#message.attach(MIMEText(mail_content, 'plain'))
#Create SMTP session for sending the mail
#session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
#session.starttls() #enable security
#session.login(sender_address, sender_pass) #login with mail_id and password
#text = message.as_string()
#session.sendmail(sender_address, receiver_address, text)
#session.quit()
#print('Mail Sent')


def generate_qr(data,save_path):


    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    #qr.add_data('{username : Deepak}')
    qr.add_data(data)

    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    #img.save("/home/owner/Desktop/some_file.png")
    img.save(save_path)
    with open(save_path,'rb') as f:
        data = f.read()




    return data


'''



class RefreshToken(BlacklistMixin, Token):
    token_type = "refresh"
    lifetime = api_settings.REFRESH_TOKEN_LIFETIME
    no_copy_claims = (
        api_settings.TOKEN_TYPE_CLAIM,
        "exp",
        # Both of these claims are included even though they may be the same.
        # It seems possible that a third party token might have a custom or
        # namespaced JTI claim as well as a default "jti" claim.  In that case,
        # we wouldn't want to copy either one.
        api_settings.JTI_CLAIM,
        "jti",
    )
    access_token_class = AccessToken

    @property
    def access_token(self):
        """
        Returns an access token created from this refresh token.  Copies all
        claims present in this refresh token to the new access token except
        those claims listed in the `no_copy_claims` attribute.
        """
        access = self.access_token_class()

        # Use instantiation time of refresh token as relative timestamp for
        # access token "exp" claim.  This ensures that both a refresh and
        # access token expire relative to the same time if they are created as
        # a pair.
        access.set_exp(from_time=self.current_time)

        no_copy = self.no_copy_claims
        for claim, value in self.payload.items():
            if claim in no_copy:
                continue
            access[claim] = value

        return access


class UntypedToken(Token):
    token_type = "untyped"
    lifetime = timedelta(seconds=0)

    def verify_token_type(self):
        """
        Untyped tokens do not verify the "token_type" claim.  This is useful
        when performing general validation of a token's signature and other
        properties which do not relate to the token's intended use.
        """
        pass
Footer'''
