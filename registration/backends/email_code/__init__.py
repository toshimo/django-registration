from django.conf import settings
from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site

from registration import signals
from registration.forms import EmailCodeRegistrationForm
from registration.models import RegistrationProfile, RegistrationCode
from registration.util import generate_unique_username
from registration.backends.email import EmailBackend


class EmailCodeBackend(EmailBackend):
    """
    A registration backend which follows a simple workflow:
    
    1. User signs up (require signup code), inactive account is created.
    
    2. Email is sent to user with activation link.
    
    3. User clicks activation link, account is now active.
    
    Using this backend requires that
    
    * ``registration`` be listed in the ``INSTALLED_APPS`` setting
      (since this backend makes use of models defined in this
      application).
    
    * The setting ``ACCOUNT_ACTIVATION_DAYS`` be supplied, specifying
      (as an integer) the number of days from registration during
      which a user may activate their account (after that period
      expires, activation will be disallowed).
    
    * The creation of the templates
      ``registration/activation_email_subject.txt`` and
      ``registration/activation_email.txt``, which will be used for
      the activation email. See the notes for this backends
      ``register`` method for details regarding these templates.
    
    Additionally, registration can be temporarily closed by adding the
    setting ``REGISTRATION_OPEN`` and setting it to
    ``False``. Omitting this setting, or setting it to ``True``, will
    be interpreted as meaning that registration is currently open and
    permitted.
    
    Internally, this is accomplished via storing an activation key in
    an instance of ``registration.models.RegistrationProfile``. See
    that model and its custom manager for full documentation of its
    fields and supported operations.
    
    """
    def register(self, request, **kwargs):
        """
        Given a username, email address and password, register a new
        user account, which will initially be inactive.
        
        Along with the new ``User`` object, a new
        ``registration.models.RegistrationProfile`` will be created,
        tied to that ``User``, containing the activation key which
        will be used for this account.
        
        An email will be sent to the supplied email address; this
        email should contain an activation link. The email will be
        rendered using two templates. See the documentation for
        ``RegistrationProfile.send_activation_email()`` for
        information about these templates and the contexts provided to
        them.
        
        After the ``User`` and ``RegistrationProfile`` are created and
        the activation email is sent, the signal
        ``registration.signals.user_registered`` will be sent, with
        the new ``User`` as the keyword argument ``user`` and the
        class of this backend as the sender.
        
        """
        signup_code_arg = kwargs.get("signup_code", None)
        if signup_code_arg:
            try:
                signup_code = RegistrationCode.objects.get(code=signup_code_arg)
                new_user = super(EmailCodeBackend, self).register(request, **kwargs)
                signup_code.use(new_user)
                return new_user
            except SignupCode.DoesNotExist:
                pass
        return False
    
    def get_form_class(self, request):
        """
        Return the default form class used for user registration.
        
        """
        # return RegistrationForm
        return EmailCodeRegistrationForm
    
