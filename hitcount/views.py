import warnings
from collections import namedtuple
from django.http import Http404, JsonResponse, HttpResponseBadRequest
from django.conf import settings
from django.views.generic import View, DetailView
from hitcount.utils import get_ip
from hitcount.models import Hit, BlacklistIP, BlacklistUserAgent
from hitcount.utils import RemovedInHitCount13Warning, get_hitcount_model


class HitCountMixin(object):

    @classmethod
    def hit_count(self, request, hitcount):
        UpdateHitCountResponse = namedtuple('UpdateHitCountResponse',
            'hit_counted hit_message')
        if request.session.session_key is None:
            request.session.save()
        user = request.user
        try:
            is_authenticated_user = user.is_authenticated()
        except:
            is_authenticated_user = user.is_authenticated
        session_key = request.session.session_key
        ip = get_ip(request)
        domain = request.get_host()
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]
        hits_per_ip_limit = getattr(settings, 'HITCOUNT_HITS_PER_IP_LIMIT', 0)
        exclude_user_group = getattr(settings,
            'HITCOUNT_EXCLUDE_USER_GROUP', None)
        if BlacklistIP.objects.filter(ip__exact=ip):
            return UpdateHitCountResponse(False,
                'Not counted: user IP has been blacklisted')
        if BlacklistUserAgent.objects.filter(user_agent__exact=user_agent):
            return UpdateHitCountResponse(False,
                'Not counted: user agent has been blacklisted')
        if exclude_user_group and is_authenticated_user:
            if user.groups.filter(name__in=exclude_user_group):
                return UpdateHitCountResponse(False,
                    'Not counted: user excluded by group')
        qs = Hit.objects.filter_active()
        if hits_per_ip_limit:
            if qs.filter(ip__exact=ip).count() >= hits_per_ip_limit:
                return UpdateHitCountResponse(False,
                    'Not counted: hits per IP address limit reached')
        hit = Hit(session=session_key, hitcount=hitcount, ip=get_ip(request
            ), domain=request.get_host(), user_agent=request.META.get(
            'HTTP_USER_AGENT', '')[:255])
        if is_authenticated_user:
            if not qs.filter(user=user, hitcount=hitcount):
                hit.user = user
                hit.domain = domain
                hit.save()
                response = UpdateHitCountResponse(True,
                    'Hit counted: user authentication')
            else:
                response = UpdateHitCountResponse(False,
                    'Not counted: authenticated user has active hit')
        elif not qs.filter(session=session_key, hitcount=hitcount):
            hit.domain = domain
            hit.save()
            response = UpdateHitCountResponse(True, 'Hit counted: session key')
        else:
            response = UpdateHitCountResponse(False,
                'Not counted: session key has active hit')
        return response


class HitCountJSONView(View, HitCountMixin):

    def dispatch(self, request, *args, **kwargs):
        if not request.is_ajax():
            raise Http404()
        return super(HitCountJSONView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        msg = 'Hits counted via POST only.'
        return JsonResponse({'success': False, 'error_message': msg})

    def post(self, request, *args, **kwargs):
        hitcount_pk = request.POST.get('hitcountPK')
        try:
            hitcount = get_hitcount_model().objects.get(pk=hitcount_pk)
        except:
            return HttpResponseBadRequest('HitCount object_pk not working')
        hit_count_response = self.hit_count(request, hitcount)
        return JsonResponse(hit_count_response._asdict())


class HitCountDetailView(DetailView, HitCountMixin):
    count_hit = False

    def get_context_data(self, **kwargs):
        context = super(HitCountDetailView, self).get_context_data(**kwargs)
        if self.object:
            hit_count = get_hitcount_model().objects.get_for_object(self.object
                )
            hits = hit_count.hits
            context['hitcount'] = {'pk': hit_count.pk}
            if self.count_hit:
                hit_count_response = self.hit_count(self.request, hit_count)
                if hit_count_response.hit_counted:
                    hits = hits + 1
                context['hitcount']['hit_counted'
                    ] = hit_count_response.hit_counted
                context['hitcount']['hit_message'
                    ] = hit_count_response.hit_message
            context['hitcount']['total_hits'] = hits
        return context


def _update_hit_count(request, hitcount):
    warnings.warn(
        'hitcount.views._update_hit_count is deprecated. Use hitcount.views.HitCountMixin.hit_count() instead.'
        , RemovedInHitCount13Warning)
    return HitCountMixin.hit_count(request, hitcount)


def update_hit_count_ajax(request, *args, **kwargs):
    warnings.warn(
        'hitcount.views.update_hit_count_ajax is deprecated. Use hitcount.views.HitCountJSONView instead.'
        , RemovedInHitCount13Warning)
    view = HitCountJSONView.as_view()
    return view(request, *args, **kwargs)
