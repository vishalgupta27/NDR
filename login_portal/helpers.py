from django.core.mail import EmailMessage
from django.http import JsonResponse 
def send_email_with_attachment(subject, message, from_email, recipient_list, photo, file):
    email = EmailMessage(subject, message, from_email, recipient_list)
    email.attach_file(photo)
    email.attach_file(file)
    try:
        email.send()
        return JsonResponse({'status' : 200})
    except:
        print("Email not Sent")
        return JsonResponse({
            "status": 403,
            "success": False,
            "message": "Unable to send mail."
        })


from django.core.mail import EmailMessage
def send_email_with_multiple_attachments(from_email,to_email, file, photo):
    subject = 'Email with Multiple Attachments'
    body = 'Please find the attached files.'
    from_email = from_email
    to_email = to_email

    email = EmailMessage(subject, body, from_email, to_email)

    # Attach the files
    file_paths = [file, photo]
    for file_path in file_paths:
        print(file_path, "fjkddddddddddddddddddddddddddddddddddddddddddddddddd")
        with open(file_path, 'rb') as fileAttach:
            print("fjkddddddddddddddddddddddddddddddddddddddddddddddddd")   
            file_content = fileAttach.read()
            file_name = file_path.split('/')[-1]
            email.attach(file_name, file_content)

    # Send the email
    email.send()
