from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.views import (
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View

from ..forms import (
    CiudadanoLoginForm,
    CiudadanoPasswordResetForm,
    RegistroStep1Form,
    RegistroStep2Form,
)
from ..services.ciudadano_auth import (
    LOGIN_MAX_INTENTOS,
    RegistroCiudadanoCuentaExistenteError,
    RegistroCiudadanoIdentidadNoVerificadaError,
    RegistroCiudadanoLegajoYaVinculadoError,
    RegistroCiudadanoServicioNoDisponibleError,
    RegistroCiudadanoSesionInvalidaError,
    completar_registro_ciudadano,
    limpiar_login_fallido,
    login_bloqueado,
    preparar_registro_ciudadano,
    registrar_login_fallido,
)


def _get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def _get_safe_next(request):
    next_url = request.POST.get('next') or request.GET.get('next') or request.session.get('portal_next')
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return next_url
    return ''


class CiudadanoLoginView(View):
    template_name = 'portal/ciudadano/login.html'

    def get(self, request):
        if request.user.is_authenticated and request.user.groups.filter(name='Ciudadanos').exists():
            return redirect('portal:ciudadano_mi_perfil')
        next_url = _get_safe_next(request)
        if next_url:
            request.session['portal_next'] = next_url
        return render(request, self.template_name, {'form': CiudadanoLoginForm(), 'next': next_url})

    def post(self, request):
        ip = _get_client_ip(request)
        if login_bloqueado(ip):
            messages.error(request, 'Demasiados intentos fallidos. Intenta de nuevo en 5 minutos.')
            return render(request, self.template_name, {'form': CiudadanoLoginForm(), 'bloqueado': True, 'next': _get_safe_next(request)})

        form = CiudadanoLoginForm(request, data=request.POST)
        if form.is_valid():
            limpiar_login_fallido(ip)
            login(request, form.get_user())
            next_url = _get_safe_next(request)
            request.session.pop('portal_next', None)
            if next_url:
                return redirect(next_url)
            return redirect('portal:ciudadano_mi_perfil')

        registrar_login_fallido(ip)
        return render(request, self.template_name, {'form': form, 'next': _get_safe_next(request)})


class CiudadanoLogoutView(View):
    def post(self, request):
        logout(request)
        return redirect('portal:ciudadano_login')


class RegistroStep1View(View):
    template_name = 'portal/ciudadano/registro_step1.html'

    def get(self, request):
        next_url = _get_safe_next(request)
        if next_url:
            request.session['portal_next'] = next_url
        return render(request, self.template_name, {'form': RegistroStep1Form(), 'next': next_url})

    def post(self, request):
        next_url = _get_safe_next(request)
        if next_url:
            request.session['portal_next'] = next_url
        form = RegistroStep1Form(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {'form': form, 'next': next_url})

        try:
            request.session['registro_ciudadano'] = preparar_registro_ciudadano(
                dni=form.cleaned_data['dni'],
                genero=form.cleaned_data['genero'],
            )
        except RegistroCiudadanoCuentaExistenteError:
            messages.info(request, 'Ya tenes una cuenta registrada. Inicia sesion con tu DNI y contrasena.')
            return redirect('portal:ciudadano_login')
        except RegistroCiudadanoIdentidadNoVerificadaError:
            form.add_error('dni', 'No pudimos verificar tu identidad. Verifica los datos ingresados.')
            return render(request, self.template_name, {'form': form, 'next': next_url})
        except RegistroCiudadanoServicioNoDisponibleError:
            form.add_error(None, 'El servicio de verificacion no esta disponible. Intenta mas tarde.')
            return render(request, self.template_name, {'form': form, 'next': next_url})

        return redirect('portal:ciudadano_registro_step2')


class RegistroStep2View(View):
    template_name = 'portal/ciudadano/registro_step2.html'

    def get(self, request):
        datos = request.session.get('registro_ciudadano')
        if not datos:
            return redirect('portal:ciudadano_registro_step1')
        next_url = _get_safe_next(request)
        return render(request, self.template_name, {'form': RegistroStep2Form(), 'datos': datos, 'next': next_url})

    def post(self, request):
        datos = request.session.get('registro_ciudadano')
        if not datos:
            return redirect('portal:ciudadano_registro_step1')

        next_url = _get_safe_next(request)
        form = RegistroStep2Form(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {'form': form, 'datos': datos, 'next': next_url})

        try:
            user, ciudadano = completar_registro_ciudadano(
                datos_registro=datos,
                email=form.cleaned_data['email'],
                telefono=form.cleaned_data['telefono'],
                password=form.cleaned_data['password1'],
            )
        except RegistroCiudadanoSesionInvalidaError:
            return redirect('portal:ciudadano_registro_step1')
        except RegistroCiudadanoCuentaExistenteError:
            messages.error(request, 'Ya existe una cuenta con ese DNI.')
            return redirect('portal:ciudadano_login')
        except RegistroCiudadanoLegajoYaVinculadoError:
            messages.error(request, 'Este legajo ya tiene una cuenta asociada. Inicia sesion.')
            request.session.pop('registro_ciudadano', None)
            return redirect('portal:ciudadano_login')

        request.session.pop('registro_ciudadano', None)
        login(request, user)
        messages.success(request, f'Bienvenido/a, {ciudadano.nombre}. Tu cuenta fue creada correctamente.')
        request.session.pop('portal_next', None)
        if next_url:
            return redirect(next_url)
        return redirect('portal:ciudadano_mi_perfil')


class CiudadanoPasswordResetView(PasswordResetView):
    form_class = CiudadanoPasswordResetForm
    template_name = 'portal/ciudadano/password_reset.html'
    email_template_name = 'portal/ciudadano/email/password_reset_body.html'
    subject_template_name = 'portal/ciudadano/email/password_reset_subject.txt'
    success_url = reverse_lazy('portal:ciudadano_password_reset_done')


class CiudadanoPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'portal/ciudadano/password_reset_done.html'


class CiudadanoPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'portal/ciudadano/password_reset_confirm.html'
    success_url = reverse_lazy('portal:ciudadano_password_reset_complete')


class CiudadanoPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'portal/ciudadano/password_reset_complete.html'
