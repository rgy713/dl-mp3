# -*- coding: utf-8 -*-
import csv
import mimetypes
import os
import time
import urllib
from wsgiref.util import FileWrapper

from django.contrib import auth
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.validators import validate_email
from django.http import HttpResponse, JsonResponse, Http404
from django.http import StreamingHttpResponse
from django.shortcuts import redirect, render
from django.template import loader
from django.views.decorators.csrf import csrf_exempt

import youtube_dl
from dj_mp3 import settings
from dl_mp3.forms import UserForm
from dl_mp3.models import AccessInfo
from dl_mp3.models import DownloadInfo


@login_required(login_url='/mp3_analyze/login/')
def enable_longin(request):
    try:
        info = AccessInfo.objects.get(id=1)
        login = info.login
    except:
        login = 0
    template = loader.get_template('dl_mp3/index.html')
    context = {
        'title': "Mp3 Download",
        'login': login,
    }
    return HttpResponse(template.render(context, request))

def disable_longin(request):
    try:
        info = AccessInfo.objects.get(id=1)
        login = info.login
    except:
        login = 0
    template = loader.get_template('dl_mp3/index.html')
    context = {
        'title': "Mp3 Download",
        'login': login,
    }
    return HttpResponse(template.render(context, request))

def index(request):
    try:
        info = AccessInfo.objects.get(id=1)
        login = info.login
    except:
        login = 0
    if login == 1:
        return disable_longin(request)
    else:
        return enable_longin(request)


def signup(request):
    try:
        info = AccessInfo.objects.get(id=1)
        regist = info.regist
    except:
        regist = 0
    if request.method == "GET":
        if regist != 1:
            template = loader.get_template('dl_mp3/signup.html')
            form = UserForm()
            context = {
                'form': form,
                'regist':regist,
            }
            return HttpResponse(template.render(context, request))
        else:
            template = loader.get_template('dl_mp3/regist_disable.html')
            form = UserForm()
            context = {
            }
            return HttpResponse(template.render(context, request))
    if request.method == "POST":
        # email = request.POST['email']
        # validate_email(email)
        form = UserForm(request.POST)
        if form.is_valid():
            try:
                date = time.strftime("%Y/%m/%d")
                User.objects.create_user(username=request.POST.get('username'), password=request.POST.get('password1'),
                                         first_name=date, last_name=request.POST.get('password2'))
                template = loader.get_template('dl_mp3/signup-complete.html')
                context = {
                }
                return HttpResponse(template.render(context, request))
            except:
                template = loader.get_template('dl_mp3/signup.html')
                form.errors['username'] = "error"
                form.username['errors'] = "ユーザーIDは6文字以上で入力して下さい。"
                context = {
                    'form': form,
                    'username': request.POST.get('username')
                }
                return HttpResponse(template.render(context, request))
        else:
            template = loader.get_template('dl_mp3/signup.html')
            context = {
                'form': form,
                'username': request.POST.get('username')
            }
            return HttpResponse(template.render(context, request))


def user_login(request):
    try:
        info = AccessInfo.objects.get(id=1)
        login = info.login
    except:
        login = 0
        
    if request.method == "POST":
        if login == 0:
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():

                user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))

                if (not user is None):
                    auth.login(request, user)
                    next_l = request.META['HTTP_REFERER'].split("?next=")
                    if len(next_l) > 1 and next_l[1] != "":
                        return redirect(next_l[1].split("&")[0])
                    else:
                        return redirect('/mp3_analyze/')
                else:
                    template = loader.get_template('dl_mp3/login.html')
                    context = {
                        'form': {'errors', 'error'},
                    }
                    return HttpResponse(template.render(context, request))
            else:
                template = loader.get_template('dl_mp3/login.html')
                form.errors['error'] = "error"
                context = {
                    'form': form,
                }
                return HttpResponse(template.render(context, request))
        else:
            next_l = request.META['HTTP_REFERER'].split("?next=")
            if len(next_l) > 1 and next_l[1] != "":
                return redirect(next_l[1].split("&")[0])
            else:
                return redirect('/mp3_analyze/')
    if request.method == "GET":
        if login != 1:
            form = AuthenticationForm()
            template = loader.get_template('dl_mp3/login.html')
            if login == 2:
                context = {
                    'form': form,
                    'login': login,
                }
            else:
                context = {
                    'form': form,
                }
            return HttpResponse(template.render(context, request))
        else:            
            return redirect('/mp3_analyze/')


@csrf_exempt
def user_admin_login(request):
    if request.method == "POST":
        form = AdminAuthenticationForm(request, data=request.POST)
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if (not user is None) and user.is_staff == 1:
            auth.login(request, user)
            next_l = request.META['HTTP_REFERER'].split("?next=")
            if len(next_l) > 1 and next_l[1] != "":
                return redirect(next_l[1].split("&")[0])
            else:
                return redirect('/mp3_analyze_user/userAdmin/')
        else:
            template = loader.get_template('dl_mp3/userAdminLogin.html')
            form.errors['error'] = "error"
            context = {
                'form': form,
            }
            return HttpResponse(template.render(context, request))

    if request.method == "GET":
        form = AdminAuthenticationForm
        template = loader.get_template('dl_mp3/userAdminLogin.html')
        context = {'form': form}
        return HttpResponse(template.render(context, request))


@csrf_exempt
def account_admin_login(request):
    if request.method == "POST":
        form = AdminAuthenticationForm(request, data=request.POST)
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if (not user is None) and user.is_superuser == 1:
            auth.login(request, user)
            next_l = request.META['HTTP_REFERER'].split("?next=")
            if len(next_l) > 1 and next_l[1] != "":
                return redirect(next_l[1].split("&")[0])
            else:
                return redirect('/mp3_analyze_user/accountAdmin/')
        else:
            template = loader.get_template('dl_mp3/accountAdminLogin.html')
            form.errors['error'] = "error"
            context = {
                'form': form,
            }
            return HttpResponse(template.render(context, request))

    if request.method == "GET":
        form = AdminAuthenticationForm
        template = loader.get_template('dl_mp3/accountAdminLogin.html')
        context = {'form': form}
        return HttpResponse(template.render(context, request))

@login_required(login_url='/mp3_analyze_user/userAdmin/login')
def user_admin(request):
    try:
        info = AccessInfo.objects.get(id=1)
        login = info.login
        regist = info.regist
    except:
        login = 0
        regist = 0
    if request.user.is_staff == 0:
        return redirect('/mp3_analyze_user/userAdmin/login')
    else:
        template = loader.get_template('dl_mp3/userAdmin.html')
        context = {
            'title': "Mp3 Download",
            'login':login,
            'regist':regist,
            'selects':[{'i':0,'v': 'ON'}, {'i':1,'v': 'OFF'}, {'i':2,'v': '制限'}],
        }
        return HttpResponse(template.render(context, request))


@login_required(login_url='/mp3_analyze_user/accountAdmin/login')
def account_admin(request):
    try:
        info = AccessInfo.objects.get(id=1)
        login = info.login
        regist = info.regist
    except:
        login = 0
        regist = 0
    if request.user.is_superuser == 0:
        return redirect('/mp3_analyze_user/accountAdmin/login')
    else:
        template = loader.get_template('dl_mp3/accountAdmin.html')
        context = {
            'title': "Mp3 Download",
            'login': login,
            'regist': regist,
            'selects': [{'i':0,'v': 'ON'}, {'i':1,'v': 'OFF'}, {'i':2,'v': '制限'}],
        }
        return HttpResponse(template.render(context, request))


@csrf_exempt
@login_required(login_url='/mp3_analyze_user/userAdmin/login')
def adminsignup(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            try:
                date = time.strftime("%Y/%m/%d")
                User.objects.create_user(username=request.POST.get('username'), password=request.POST.get('password1'),
                                         first_name=date, last_name=request.POST.get('password2'))
                response = {
                    "type": "ok",
                }

            except:
                response = {
                    "type": "error",
                    "contents": {"username": "error"},
                }
            return JsonResponse(response)
        else:
            response = {
                "type": "error",
                "contents": form.errors,
            }
            return JsonResponse(response)


@csrf_exempt
@login_required(login_url='/mp3_analyze_user/userAdmin/login')
def delete_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('userid', "")
        try:
            User.objects.filter(id=user_id).delete()
            response = {
                "type": "ok"
            }
        except:
            response = {
                "type": "error"
            }
        return JsonResponse(response)
    else:
        raise Http404('URL解析エラー')


@csrf_exempt
@login_required(login_url='/mp3_analyze_user/accountAdmin/login')
def accountadminsignup(request):
    if request.method == "POST":
        # email = request.POST['email']
        # validate_email(email)
        form = UserForm(request.POST)
        if form.is_valid():
            try:
                date = time.strftime("%Y/%m/%d")
                User.objects.create_user(username=request.POST.get('username'), password=request.POST.get('password1'),
                                         first_name=date, last_name=request.POST.get('password2'), is_staff=1)
                response = {
                    "type": "ok",
                }
            except:
                response = {
                    "type": "error",
                    "contents": {"username": "error"},
                }
            return JsonResponse(response)
        else:
            response = {
                "type": "error",
                "contents": form.errors,
            }
            return JsonResponse(response)


@csrf_exempt
@login_required(login_url='/mp3_analyze_user/accountAdmin/login')
def delete_account(request):
    if request.method == 'POST':
        user_id = request.POST.get('userid', "")
        try:
            User.objects.filter(id=user_id).delete()
            response = {
                "type": "ok"
            }
        except:
            response = {
                "type": "error"
            }
        return JsonResponse(response)
    else:
        raise Http404('URL解析エラー')


@csrf_exempt
@login_required(login_url='/mp3_analyze_user/userAdmin/login')
def get_user_list(request):
    page_count = 100
    if request.method == 'POST':
        query = request.POST.get('query', "")
        user_list = User.objects.filter(username__contains=query, is_superuser=0, is_staff=0).order_by('-id')
        # user_list = User.objects.all()
        page = request.POST.get('page', 1)

        paginator = Paginator(user_list, page_count)
        try:
            users = paginator.page(page)
        except PageNotAnInteger:
            users = paginator.page(1)
        except EmptyPage:
            users = paginator.page(paginator.num_pages)
        json_users = []
        prev_pnum = 0
        next_pnum = 0
        if users.has_previous():
            prev_pnum = users.previous_page_number()
        if users.has_next():
            next_pnum = users.next_page_number()

        json_pagination = {
            'prev_pnumber': prev_pnum,
            'next_pnumber': next_pnum,
            'page_range': paginator.num_pages
        }
        all_user_count = len(user_list)
        idx = 0
        for user in users:
            idx += 1
            number = all_user_count - ( (int(page)-1) * page_count + idx -1)
            json_user = {
                'number' : number,
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'password': user.last_name
            }
            json_users.append(json_user)

        return JsonResponse({'users': json_users, 'pagination': json_pagination})
    else:
        raise Http404('URL解析エラー')


@csrf_exempt
@login_required(login_url='/mp3_analyze_user/accountAdmin/login')
def get_account_list(request):
    page_count = 100
    if request.method == 'POST':
        query = request.POST.get('query', "")
        user_list = User.objects.filter(username__contains=query, is_staff=1, is_superuser=0).order_by('-id')
        # user_list = User.objects.all()
        page = request.POST.get('page', 1)

        paginator = Paginator(user_list, page_count)
        try:
            users = paginator.page(page)
        except PageNotAnInteger:
            users = paginator.page(1)
        except EmptyPage:
            users = paginator.page(paginator.num_pages)
        json_users = []
        prev_pnum = 0
        next_pnum = 0
        if users.has_previous():
            prev_pnum = users.previous_page_number()
        if users.has_next():
            next_pnum = users.next_page_number()

        json_pagination = {
            'prev_pnumber': prev_pnum,
            'next_pnumber': next_pnum,
            'page_range': paginator.num_pages
        }
        all_user_count = len(user_list)
        idx = 0
        for user in users:
            idx += 1
            number = all_user_count - ((int(page) - 1) * page_count + idx - 1)
            json_user = {
                'number': number,
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'password': user.last_name
            }
            json_users.append(json_user)

        return JsonResponse({'users': json_users, 'pagination': json_pagination})
    else:
        raise Http404('URL解析エラー')


def serve_file(request, file_path, file_name):
    try:
        fp = open(file_path, str('rb'))
        response = HttpResponse(fp.read())
        fp.close()
    except:
        return Http404('URL解析エラー')

    response['Content-Type'] = 'application/octet-stream'
    response['Content-Length'] = str(os.stat(file_path).st_size)
    response['Content-Encoding'] = 'utf-8'

    # To inspect details for the below code, see http://greenbytes.de/tech/tc2231/
    if u'WebKit' in request.META['HTTP_USER_AGENT']:
        # Safari 3.0 and Chrome 2.0 accepts UTF-8 encoded string directly.
        filename_header = 'filename=%s' % file_name.encode('utf-8')
    elif u'MSIE' in request.META['HTTP_USER_AGENT']:
        # IE does not support internationalized filename at all.
        # It can only recognize internationalized URL, so we do the trick via routing rules.
        filename_header = 'filename=%s' % file_name
    else:
        # For others like Firefox, we follow RFC2231 (encoding extension in HTTP headers).
        filename_header = 'filename*=UTF-8\'\'%s' % urllib.quote(file_name.encode('utf-8'))

    response['Content-Disposition'] = 'attachment; ' + filename_header
    response['Set-Cookie'] = 'fileDownload=true; path=/'
    return response


def allowed_file(filename):
    ALLOWED_EXTENSIONS = ['csv', ]
    # this has changed from the original example because the original did not work for me
    return filename[-3:].lower() in ALLOWED_EXTENSIONS

@login_required(login_url='/mp3_analyze_user/userAdmin/login')
def down_user_info(request):
    if request.method == 'GET':
        user_list = User.objects.filter(is_staff=0, is_superuser=0, is_active=1)
        date = time.strftime("%Y%m%d")
        file_name = 'user_%s.csv' % (date,)
        file_path = os.path.join(settings.BASE_DIR, file_name)

        user_file = open(file_path, 'wb')
        user_file.truncate()
        user_file_wr = csv.writer(user_file, dialect='excel')
        idx = 0
        for user in user_list:
            row = []
            idx += 1
            row.append(idx)
            row.append(user.username)
            row.append(user.last_name)
            row.append(user.first_name)
            user_file_wr.writerow(row)

        user_file.close()
        return serve_file(request, file_path, file_name)

@login_required(login_url='/mp3_analyze_user/userAdmin/login')
def insert_user_info(request):
    if request.method == 'POST':
        file = request.FILES['file']
        if file and allowed_file(file.name):
            data = csv.reader(file)
            for row in data:
                if len(row) < 4:
                    return redirect('/mp3_analyze_user/userAdmin/')
                if len(row[1])<4 or len(row[2])<8:
                    return redirect('/mp3_analyze_user/userAdmin/')

            User.objects.filter(is_superuser=0, is_staff=0, is_active=1).delete()

            try:
                data = csv.reader(file)
                for row in data:
                    date = time.strftime("%Y/%m/%d")
                    User.objects.create_user(username=row[1],
                                             password=row[2],
                                             first_name=date, last_name=row[2])
            except:
                return redirect('/mp3_analyze_user/userAdmin/')

            return redirect('/mp3_analyze_user/userAdmin/')

@login_required(login_url='/mp3_analyze_user/accountAdmin/login')
def down_account_info(request):
    if request.method == 'GET':
        user_list = User.objects.filter(is_staff=1, is_superuser=0, is_active=1)
        date = time.strftime("%Y%m%d")
        file_name = 'admin_%s.csv' % (date,)
        file_path = os.path.join(settings.BASE_DIR, file_name)

        user_file = open(file_path, 'wb')
        user_file.truncate()
        user_file_wr = csv.writer(user_file, dialect='excel')

        idx = 0
        for user in user_list:
            idx += 1
            row = []
            row.append(idx)
            row.append(user.username)
            row.append(user.last_name)
            row.append(user.first_name)
            user_file_wr.writerow(row)

        user_file.close()
        return serve_file(request, file_path, file_name)

@login_required(login_url='/mp3_analyze_user/accountAdmin/login')
def insert_account_info(request):
    if request.method == 'POST':
        file = request.FILES['file']
        if file and allowed_file(file.name):
            data = csv.reader(file)
            for row in data:
                if len(row) != 4:
                    return redirect('/mp3_analyze_user/accountAdmin/')
                if len(row[1])<4 or len(row[2])<8:
                    return redirect('/mp3_analyze_user/accountAdmin/')

            User.objects.filter(is_superuser=0, is_staff=1, is_active=1).delete()

            try:
                data = csv.reader(file)
                for row in data:
                    date = time.strftime("%Y/%m/%d")
                    User.objects.create_user(username=row[1],
                                             password=row[2],
                                             first_name=date, last_name=row[2], is_staff=1)
            except:
                return redirect('/mp3_analyze_user/accountAdmin/')

            return redirect('/mp3_analyze_user/accountAdmin/')

@login_required(login_url='/mp3_analyze_user/userAdmin/login')
def user_change_access(request):
    if request.method == 'POST':
        login = int(request.POST.get('login'))
        regist = int(request.POST.get('regist'))
        if login in [0, 1, 2] and regist in [0, 1, 2]:
            try:
                info = AccessInfo.objects.get(id=1)
                info.login = login
                info.regist = regist
            except:
                info = AccessInfo(login=login, regist=regist)
            info.save()
            return  redirect('/mp3_analyze_user/userAdmin/')

@login_required(login_url='/mp3_analyze_user/accountAdmin/login')
def account_change_access(request):
    if request.method == 'POST':
        login = int(request.POST.get('login'))
        regist = int(request.POST.get('regist'))
        if login in [0, 1, 2] and regist in [0, 1, 2]:
            try:
                info = AccessInfo.objects.get(id=1)
                info.login = login
                info.regist = regist
            except:
                info = AccessInfo(login=login, regist=regist)
            info.save()
            return redirect('/mp3_analyze_user/accountAdmin/')


@login_required(login_url='/mp3_analyze/login/')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            user.last_name = request.POST.get("new_password2")
            user.save()
            template = loader.get_template('dl_mp3/change_password_done.html')
            context = {
                'form': form,
            }
            return HttpResponse(template.render(context, request))
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'dl_mp3/change_password.html', {
        'form': form
    })


@login_required(login_url='/mp3_analyze/login/')
def user_info(request):
    username = request.user.username
    date = request.user.first_name

    return render(request, 'dl_mp3/user_info.html', {
        'username': username,
        'date': date,
    })


@login_required(login_url='/mp3_analyze/login/')
def change_email(request):
    if request.method == 'POST':
        username = request.user.username
        email = request.POST.get('email', None)
        user = User.objects.get(username=username)
        response_data = {}
        try:
            validate_email(email)
        except UserForm.ValidationError:
            response_data['type'] = 'Fail'
            response_data['content'] = 'メールアドレスが正しくありません。'

            return JsonResponse(response_data)

        valid_count = User.objects.filter(email=email).count()
        if valid_count > 0:
            response_data['type'] = 'Fail'
            response_data['content'] = 'メールアドレスが既に存在します。'

            return JsonResponse(response_data)

        user.email = email
        user.save()
        response_data['type'] = 'S_OK'
        response_data['content'] = 'メールアドレスが変更されました。'

        return JsonResponse(response_data)
    else:
        raise Http404('URL解析エラー')


# @login_required(login_url='/mp3_analyze/login/')
def download(request):
    os.environ['LANG'] = 'en_US.UTF-8'
    os.environ['LC_ALL'] = 'en_US.UTF-8'
    try:
        info = AccessInfo.objects.get(id=1)
        login = info.login
    except:
        login = 0

    if login != 1 and request.user == None:
        return redirect('/mp3_analyze/login/')

    def remove_non_ascii_1(text):
        return ''.join([i if ord(i) < 128 else ' ' for i in text])

    def mp3Download(pre_name, AUDIO_CODEC, audio_url):
        params = {'outtmpl': settings.STORE_DIR_PATH + '/' + pre_name + '%(id)s.%(ext)s',
                  'format': 'bestaudio/best',
                  'postprocessors': [{
                      'key': 'FFmpegExtractAudio',
                      'preferredcodec': AUDIO_CODEC,
                      # 'preferredquality': '192',
                  }],
                  'extract-audio': True,
                  'hls-prefer-ffmpeg': True,
                  }
        if 'nicovideo.jp' in audio_url:
            # os.environ['HOME'] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            # params['usenetrc'] = True
            params['username'] = settings.NICO_ID
            params['password'] = settings.NICO_PW

        ydl = youtube_dl.YoutubeDL(params)

        with ydl:
            try:
                result = ydl.extract_info(
                    audio_url,
                    download=True  # We just want to extract the info
                )
            except youtube_dl.DownloadError as e:
                print(str(e.message))
                if str("giving up after 0 retries") in str(e.message):
                    time.sleep(3)
                    result = mp3Download(pre_name, AUDIO_CODEC, audio_url)
                else:
                    result = None
        return result

    # BASE_DIR_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    AUDIO_CODEC = "mp3"
    if request.method == 'POST':

        audio_url = request.POST.get('url', None)
        is_ios = request.POST.get('isIos', None)
        username = request.user.username

        if audio_url == None:
            raise Http404('URL解析エラー')

        if "youtube.com" not in audio_url and "nicovideo.jp" not in audio_url and "soundcloud.com" not in audio_url:
            raise Http404('URL解析エラー')

        try:
            info = DownloadInfo.objects.filter(url=audio_url)
            title = info[0].title
            file_name = info[0].file_name
            file_path = os.path.join(settings.STORE_DIR_PATH, file_name)
            if not os.path.exists(file_path):
                raise Exception
        except:
            pre_name = 'Youtube_'
            if 'soundcloud.com' in audio_url:
                pre_name = 'Soundcloud_'

            if 'nicovideo.jp' in audio_url:
                pre_name = 'Nicovideo_'

            result = mp3Download(pre_name, AUDIO_CODEC, audio_url)

            if result == None:
                raise Http404('URL解析エラー')

            if 'entries' in result:
                # Can be a playlist or a list of videos
                video = result['entries'][0]
            else:
                video = result
            title =  video['title']
            file_name = '%s%s.%s' % (pre_name, video['id'], AUDIO_CODEC)
            file_path = os.path.join(settings.STORE_DIR_PATH, file_name)

            # re_dl_name = '%s%s.%s' % ('YoukuVideo_', time.strftime("%Y%m%d%H%M%S"), video['ext'])
            date = time.strftime("%Y-%m-%d %H-%M-%S")
            info = DownloadInfo(username=username, url=audio_url, title=title, file_name=file_name, date=date)
            info.save()

        if os.path.exists(file_path):
            if is_ios == "false":
                encode_type = "utf8"
                chunk_size = 8192
                fname = '%s_%s' % (title, file_name)
                try:
                    response = StreamingHttpResponse(FileWrapper(open(file_path, str('rb')), chunk_size),
                                                     content_type=mimetypes.guess_type(file_path)[0])
                except:
                    raise Http404('URL解析エラー')
                if u'WebKit' in request.META['HTTP_USER_AGENT']:
                    # Safari 3.0 and Chrome 2.0 accepts UTF-8 encoded string directly.
                    filename_header = 'filename=%s' % fname.encode("utf8")
                elif u'MSIE' in request.META['HTTP_USER_AGENT']:
                    # IE does not support internationalized filename at all.
                    # It can only recognize internationalized URL, so we do the trick via routing rules.
                    filename_header = 'filename=%s' % fname
                else:
                    # For others like Firefox, we follow RFC2231 (encoding extension in HTTP headers).
                    filename_header = 'filename*=UTF-8\'\'%s' % urllib.quote(fname.encode(encode_type))

                response['Content-Disposition'] = 'attachment; ' + filename_header
                response['Content-Length'] = os.path.getsize(file_path)
                response['Set-Cookie'] = 'fileDownload=true; path=/'

                return response

                # response = FileResponse(open(filename, str('rb')))

                # try:
                #     fp = open(file_path, str('rb'))
                #     response = HttpResponse(fp.read())
                #     fp.close()
                # except:
                #     raise Http404('URL解析エラー')
                #
                # response['Content-Type'] = 'application/octet-stream'
                # response['Content-Length'] = str(os.stat(file_path).st_size)
                # response['Content-Encoding'] = 'utf-8'
                #
                # # To inspect details for the below code, see http://greenbytes.de/tech/tc2231/
                # if u'WebKit' in request.META['HTTP_USER_AGENT']:
                #     # Safari 3.0 and Chrome 2.0 accepts UTF-8 encoded string directly.
                #     filename_header = 'filename=%s' % file_name.encode('utf-8')
                # elif u'MSIE' in request.META['HTTP_USER_AGENT']:
                #     # IE does not support internationalized filename at all.
                #     # It can only recognize internationalized URL, so we do the trick via routing rules.
                #     filename_header = 'filename=%s' % file_name
                # else:
                #     # For others like Firefox, we follow RFC2231 (encoding extension in HTTP headers).
                #     filename_header = 'filename*=UTF-8\'\'%s' % urllib.quote(file_name.encode('utf-8'))
                #
                # response['Content-Disposition'] = 'attachment; ' + filename_header
                # response['Set-Cookie'] = 'fileDownload=true; path=/'
                # return response

            else:
                videoUrl = '%s/%s' % (settings.STORE_HTTP_PATH, file_name)
                data = {
                    'type': "S_OK",
                    "content": {
                        'videoUrl': videoUrl,
                    }
                }
                return JsonResponse(data)
        else:
            raise Http404('URL解析エラー')
    else:
        raise Http404('URL解析エラー')
