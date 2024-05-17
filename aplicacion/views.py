from django.shortcuts import render, redirect
from aplicacion.forms import RegisterForm, CodeForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from aplicacion.forms import VerificationForm
from . import models
from . import utils
import TFM.settings
import qrcode, hashlib
import base64, pyotp
import secrets
import datetime
import hashlib

MAX_ATTEMPTS = 3
TEMP_USER_ID = 1


# Create your views here.
def initial_menu(request):
    if not request.user.is_anonymous:        
        if request.user.verified:
            return redirect('/home')
    return render(request, 'initial_menu.html')

def register(request):
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            
            username = form.cleaned_data.get('username')
            password:str = form.cleaned_data.get('password1')
            # Send mail to verify if the mail is valid.
            email = form.cleaned_data.get('email')
            
            
            sec_code = secrets.token_hex(16)  # Genera un token hexadecimal de 16 bytes (32 caracteres)
            hash_sec_code = hashlib.sha256(bytes(sec_code, 'utf-8'))
            utils.enviarcorreo(email, 'Verification account', f'Remember the code and follow the next link to verify the mail\nCode: {sec_code}', None)
            
            date = datetime.datetime.now()
            margen = datetime.timedelta(minutes=2)
            
            password, iv = utils.cifrar(TFM.settings.Key, bytes(password, 'utf-8'))
            user = models.TemporalUser(username = username, password = password, email = email, iv=iv)
            user.save()
            
            token = models.Token(token=hash_sec_code.hexdigest(), temp_user_id = user.id, date = date+margen)
            token.save()
            
            request.session['id'] = user.id
            
            #login(request,user)
            return redirect('verification')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})

@require_http_methods(["GET", "POST"])
def verification(request):
    user_id = request.session['id']
    
    if request.method == 'GET':
        #Create new form
        form = VerificationForm()
        request.session['login_attempts'] = 0
        return render(request, 'registration/post_verification.html', {'form': form})
    elif request.method == 'POST':
        form = VerificationForm(request.POST)
        print(form)
        code_sec = form.cleaned_data.get('secuence')
        if not code_sec:
            error = 'The secuence is not found'
            return render(request, 'registration/delete_data.html', {'error': error})
        if not user_id:
            error = 'The user is not found'
            return render(request, 'registration/delete_data.html', {'error': error})
        token = models.Token.objects.get(temp_user_id = user_id)
        if token.token != hashlib.sha256(bytes(code_sec, 'utf-8')).hexdigest():
            request.session['login_attempts'] += 1
            if(request.session['login_attempts'] >= 3):
                models.Token.objects.get(temp_user_id = user_id).delete()
                models.TemporalUser.objects.get(id = user_id).delete()
                del request.session['id']
                error = 'The maximum number of attempts is reached. The verification is not fulfilled and your information has been removed.'
                return render(request, 'registration/delete_data.html', {'error': error})
            else:
                attempts = 3 - request.session['login_attempts']
                form.add_error('secuence', f'Incorrect secuence. You have {attempts} attempts left.')
                return render(request, 'registration/post_verification.html', {'form': form})
        else:
            if datetime.datetime.now() > token.date:
                models.Token.objects.get(temp_user_id = user_id).delete()
                models.TemporalUser.objects.get(id = user_id).delete()    
                del request.session['id']
                error = 'The validation of the token has expired. Please, try again using another secuence.'
                return render(request, 'registration/delete_data.html', {'error': error})
        
            else:
                
                temp_user = models.TemporalUser.objects.get(id = user_id)
                password = utils.descifrar(temp_user.password, TFM.settings.Key, temp_user.iv)
                user = models.CustomUser(username = temp_user.username, email = temp_user.email)
                user.set_password(password)
                user.save()
                del request.session['id']
                models.Token.objects.get(temp_user_id = user_id).delete()
                temp_user.delete()
                error = 'The verification process is completed successfully. You are going to be redirect to the initial menu to perform the log in.'
                return render(request, 'registration/delete_data.html', {'error': error})

        

    
@login_required
def postlogin(request):
    base_key = f'{request.user.username}'.encode()
    key = hashlib.sha256(base_key).hexdigest().encode()
    #key = b'Myrandomkey'
    if request.method == 'GET':
        if 'login_attempts' in request.session:
            del request.session['login_attempts']
        usuario = request.user
        email = usuario.email
        
        # Qr code generation step 
        uri = pyotp.totp.TOTP(base64.b32encode(key)).provisioning_uri(name= request.user.username, issuer_name='LessonMaster')     
        qrcode.make(uri).save(f'aplicacion/static/qrcode/qr_{usuario.username}.png')

        utils.enviarcorreo(email, 'No-replay', 'Hello', f'aplicacion/static/qrcode/qr_{usuario.username}.png')
        return render(request, 'registration/postlogin.html', {'form': CodeForm(request.POST)})
      
    else:
               
        form = CodeForm(request.POST)
        # verificación del código y reenvio a la página correspondiente.
        if form.is_valid():
            code = form.data.get('fcode')
            totp = pyotp.TOTP(base64.b32encode(key))
            
            if totp.verify(code):
                if 'login_attempts' in request.session:
                    del request.session['login_attempts']
                
                usuario = models.CustomUser.objects.get(username = request.user.username)
                usuario.verified = True
                usuario.save()
                return redirect('/home')
            else:
                if 'login_attempts' in request.session:
                    request.session['login_attempts'] += 1
                else:
                    request.session['login_attempts'] = 1
                
                if request.session['login_attempts'] >= MAX_ATTEMPTS:
                    del request.session['login_attempts']
                    return redirect('/')
                else:
                    return render(request, 'registration/postlogin.html', {'form': CodeForm(request.POST)})

        return render(request, 'registration/postlogin.html', {'form': CodeForm(request.POST)})

def home(request:object):
    if not request.user.is_anonymous:        
        if request.user.verified: 
            return render(request, 'home.html')
    else:
        return redirect('/accounts/login/?next=/postlogin')
                     

def logout_extension(request):
    usuario = models.CustomUser.objects.get(username = request.user.username)
    usuario.verified = False
    # print(usuario.verified)
    usuario.save() 
    return redirect('/accounts/logout/?next=/')




    
