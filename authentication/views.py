import django
from django.utils.encoding import force_str
django.utils.encoding.force_text = force_str

from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login, logout
from login import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes


from .tokens import generate_token
from django.core.mail import EmailMessage, send_mail

def home(request):
    return render(request, 'authentication/index.html')
    
def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        # validating the user inputs

        if User.objects.filter(username = username):
            messages.error(request, "Username already exists!, Please try another one")
            return redirect('home')

        if User.objects.filter(email = email):
            messages.error(request, "Email already registered!")
            return redirect('home')
        
        if len(username)> 10:
            messages.error(request, "your username should not contain more than 10 characters!")

        if pass1 != pass2:
            messages.error(request, "Passwords didn't match.")

        if not username.isalnum():
            messages.error(request, "Username must be alpha-numeric")




        my_user = User.objects.create_user(username, email, pass1)
        my_user.first_name = fname
        my_user.last_name = lname
        my_user.is_active = False

        my_user.save()

        messages.success(request, "your account has been successfully created")

        # welcome email
        subject = "Welcome to ConnectWithBhagi"
        message = "Hello " + my_user.first_name + "!!\n" + "welcome to ConnectWithBhagi\nThank you for visiting our website \nWe have also sent you a confirmation email, Please confirm your email address to activate your account\n\n Thanking you,\n Bhagirath!"
        from_email = settings.EMAIL_HOST_USER
        to_list = [my_user.email]
        send_mail(subject, message, from_email, to_list, fail_silently = True)


        # email address confirmation
        current_site = get_current_site(request)
        email_subject = "Confirm Your email @ GFG - Django Login!!"
        message2 = render_to_string('email_confirmation.html',{
            'name': my_user.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(my_user.pk)),
            'token': generate_token.make_token(my_user)
        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [my_user.email],

        )
        email.fail_silently = True
        email.send()



        return redirect("signin")




    return render(request, 'authentication/signup.html')

def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        pass1 =request.POST['pass1']

        user = authenticate(username = username, password = pass1)

        if user is not None:
            login(request,user)
            fname = user.first_name
            return render (request, 'authentication/index.html',{'fname': fname})


        else:
            messages.error(request,  "Wrong Credentials")
            return redirect('home')


    return render(request, 'authentication/signin.html')

def signout(request):
    logout( request)
    messages.success(request,"Sussessfully Logged out!")
    return redirect('home')


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        my_user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        my_user = None

    if my_user is not None and generate_token.check_token(my_user, token):
        my_user.is_active = True
        my_user.save()
        login(request, my_user)
        return redirect('home')
    else:
        return render(request, 'activation_failed.html')



