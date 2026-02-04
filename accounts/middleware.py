from django.http import JsonResponse
from django.utils.timezone import now
from user_agents import parse
from accounts.models import UserSession, IPActivity, BlacklistedIP

class DeviceTrackingMiddleware:
    '''
    Tracks authenticated users’ sessions with real device intelligence:
    - IP address
    - Full user agent
    - Device type
    - Operating system
    - Browser
    '''

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            ip = self.get_client_ip(request)
            raw_user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')

            # Parse user agent real library
            ua = parse(raw_user_agent)

            device_type = self.get_device_type(ua)
            os_name = f'{ua.os.family} {ua.os.version_string}'.strip()
            browser = f'{ua.browser.family} {ua.browser.version_string}'.strip()

            # Update or create a session for this IP + user_agent
            UserSession.objects.update_or_create(
                user=request.user,
                ip_address=ip,
                user_agent=raw_user_agent,
                defaults={
                    'device_type': device_type,
                    'os': os_name,
                    'browser': browser,
                    'is_active': True,
                }
            )

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')

    def get_device_type(self, ua):
        if ua.is_mobile:
            return 'Mobile'
        elif ua.is_tablet:
            return 'Tablet'
        elif ua.is_pc:
            return 'Desktop'
        elif ua.is_bot:
            return 'Bot'
        return 'Unknown'




class IPActivityLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self.get_client_ip(request)
        endpoint = request.path
        method = request.method

        # Log or update activity BEFORE response
        try:
            activity, created = IPActivity.objects.get_or_create(
                ip_address=ip,
                endpoint=endpoint,
                method=method,
                defaults={
                    'user': request.user if request.user.is_authenticated else None
                }
            )

            if not created:
                activity.request_count += 1
                activity.last_seen = now()
                activity.save(update_fields=['request_count', 'last_seen'])

        except Exception:
            pass

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')



class IPBlacklistMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self.get_client_ip(request)

        if ip and BlacklistedIP.objects.filter(
            ip_address = ip,
            is_active = True
        ).exists():
            return JsonResponse({'detail': 'Access Denied'}, status=403)
        return self.get_response(request)
            
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDEDED_FOR')

        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')