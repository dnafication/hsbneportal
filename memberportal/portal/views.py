from django.contrib.auth import login, authenticate
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse, HttpResponseServerError
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import *


def log_admin_action(admin_user, member_id, action="unknown", description="none"):
    """
    Called to log admin action to the DB.
    :param admin_user: user object of logged in admin performing the request.
    :param member_id: id number of member action is being performed on.
    :param action: brief description of the action being taken.
    :param description: either a brief description of why or the raw request params.
    :return:
    """

    if "csrfmiddlewaretoken" in description:
        import re
        description = re.sub(r"csrfmiddlewaretoken=[a-zA-Z0-9]*&", '', description)

    member = User.objects.get(pk=member_id)
    AdminLog(log_user=admin_user, action=action, log_member=member, description=description).save()


def signup(request):
    """
    The signup view.
    :param request:
    :return:
    """

    # if the user has submitted a form process it
    if request.method == 'POST':
        # make a new instance of both forms
        user_form = SignUpForm(request.POST)
        profile_form = AddProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            # if both forms are valid save them
            new_user = user_form.save()
            profile = profile_form.save(commit=False)

            # this check is needed sometimes, don't ask why
            if profile.user_id is None:
                profile.user_id = new_user.id
            profile.save()

            # for convenience, we should now log the user in
            username = user_form.cleaned_data.get('username')
            raw_password = user_form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)

            return redirect('/')

    else:
        # make a new instance for both forms and render the template
        user_form = SignUpForm()
        profile_form = AddProfileForm()

    return render(request, 'registration/signup.html', {'user_form': user_form, 'profile_form': profile_form})


def signin(request):
    """
    The sign in view.
    :param request:
    :return:
    """
    return render(request, 'registration/login.html')


def loggedout(request):
    """
    The view to show the logged out page.
    :param request:
    :return:
    """
    return render(request, 'loggedout.html')


def home(request):
    """
    The home page view.
    :param request:
    :return:
    """
    return render(request, 'home.html')


@login_required()
def profile(request):
    """
    The profile view.
    :param request:
    :return:
    """
    return render(request, 'profile.html')


@login_required()
def member_list(request):
    """
    The list all members view. Used to manage all members.
    :param request:
    :return:
    """
    # make sure the user is a staff member
    if request.user.is_staff:
        # extract the values we need for each member
        members = User.objects.values('id', 'username', 'email', 'first_name', 'last_name',
                                      'profile__member_type__name',
                                      'profile__state__name', 'profile__cause1__name', 'profile__cause2__name',
                                      'profile__cause3__name', 'profile__state')

        return render(request, 'memberlist.html', {'members': members})

    else:
        # if the user isn't authorised let them know
        return HttpResponseForbidden("403 Access Forbidden")


# def save_admin_edit_member_form(request, form, template_name, member_id):
#     """
#     Part of the process for our ajax requests for the member list.
#     :param request:
#     :param form:
#     :param template_name:
#     :param member_id:
#     :return:
#     """
#     data = dict()
#     if request.method == 'POST':
#         if form.is_valid():
#             # if it's a valid form submission then save and log it
#             form.save()
#             data['form_is_valid'] = True
#             log_admin_action(request.user, member_id, "edited member profile", str(request.body))
#
#         else:
#             # if it's not valid don't save or log it
#             data['form_is_valid'] = False
#
#     # render the form and return it
#     data['html_form'] = render_to_string(template_name, {'form': form, 'member_id': member_id}, request=request)
#     return JsonResponse(data)


@login_required()
def admin_edit_member(request, member_id):
    """
    Part of the process for our ajax requests for the member list.
    :param request:
    :param member_id:
    :return:
    """
    user = get_object_or_404(Profile, user=member_id)
    if request.method == 'POST':
        # if it's a form submission pass it to the form
        form = AdminEditProfileForm(request.POST, instance=user)

    else:
        # otherwise make generate one
        form = AdminEditProfileForm(instance=user)

    # call the function above to process/render the form
    #return save_admin_edit_member_form(request, form, 'partial_admin_edit_member.html', member_id)

    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            # if it's a valid form submission then save and log it
            form.save()
            data['form_is_valid'] = True
            log_admin_action(request.user, member_id, "edited member profile", str(request.body))

        else:
            # if it's not valid don't save or log it
            data['form_is_valid'] = False

    # render the form and return it
    data['html_form'] = render_to_string('partial_admin_edit_member.html', {'form': form, 'member_id': member_id},
                                         request=request)
    return JsonResponse(data)


@login_required()
def edit_profile(request):
    """
    The edit user profile view.
    :param request:
    :return:
    """
    if request.method == 'POST':
        user_form = EditUserForm(request.POST, instance=request.user)
        if user_form.is_valid():
            # if it was a form submission save it
            user_form.save()
            return HttpResponseRedirect('%s' % (reverse('profile')))
        else:
            # otherwise return form with errors
            return render(request, 'edit_profile.html', {'user_form': user_form})

    else:
        # if it's not a form submission, return an empty form
        user_form = EditUserForm(instance=request.user)
        return render(request, 'edit_profile.html', {'user_form': user_form})


@login_required()
def edit_causes(request):
    """
    The edit causes view.
    :param request:
    :return:
    """
    if request.method == 'POST':
        user = Profile.objects.get(user=request.user)
        form = EditCausesForm(request.POST, instance=user)
        if form.is_valid():
            # if it was a form submission save it
            form.save()
            return HttpResponseRedirect('%s' % (reverse('edit_causes')))
        else:
            # otherwise return form with errors
            return render(request, 'edit_causes.html', {'form': form})

    else:
        # if it's not a form submission, return an empty form
        user = Profile.objects.get(user=request.user)
        form = EditCausesForm(instance=user)
        return render(request, 'edit_causes.html', {'form': form})


@login_required()
def set_state(request, member_id, state):
    """
    Sets the active/inactive (access disabled/enabled) state for members.
    :param request:
    :param member_id:
    :param state:
    :return:
    """

    # grab the user object and save the state
    user = User.objects.get(id=member_id)
    user.profile.state = MemberState.objects.get(pk=state)
    user.profile.save()

    # verify if the state was actually saved correctly
    if User.objects.get(id=member_id).profile.state == MemberState.objects.get(pk=state):
        return JsonResponse({"success": True})
    else:
        # if the response is not 200 the frontend will show an error
        return HttpResponseServerError("error processing request")


@login_required()
def manage_causes(request):
    if request.method == 'POST':
        form = CauseForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("manage_causes"))

    else:
        form = CauseForm()

    causes = Causes.objects.all()

    return render(request, 'manage_causes.html', {"form": form, "causes": causes})


@login_required()
def edit_cause(request, cause_id):
    """
    The edit cause (admin) view.
    :param request:
    :param cause_id: cause id to edit
    :return:
    """
    if request.method == 'POST':
        form = CauseForm(request.POST, instance=Causes.objects.get(pk=cause_id))
        if form.is_valid():
            # if it was a form submission save it
            form.save()
            return HttpResponseRedirect('%s' % (reverse('manage_causes')))
        else:
            # otherwise return form with errors
            return render(request, 'edit_cause.html', {'form': form})

    else:
        # if it's not a form submission, return an empty form
        form = CauseForm(instance=Causes.objects.get(pk=cause_id))
        return render(request, 'edit_cause.html', {'form': form})


@login_required()
def delete_cause(request, cause_id):
    Causes.objects.get(pk=cause_id).delete()
    return HttpResponseRedirect('%s' % (reverse('manage_causes')))


@login_required()
def access_permissions(request):
    return render(request, 'access_permissions.html', {"form": "form"})


def manage_doors(request):
    if request.method == 'POST':
        form = DoorForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("manage_doors"))

    else:
        form = DoorForm()

    doors = Doors.objects.all()
    return render(request, 'manage_doors.html', {"form": form, "doors": doors})


@login_required()
def edit_door(request, door_id):
    if request.method == 'POST':
        form = DoorForm(request.POST, instance=Doors.objects.get(pk=door_id))
        if form.is_valid():
            # if it was a form submission save it
            form.save()
            return HttpResponseRedirect('%s' % (reverse('manage_doors')))
        else:
            # otherwise return form with errors
            return render(request, 'edit_cause.html', {'form': form})

    else:
        # if it's not a form submission, return an empty form
        form = DoorForm(instance=Doors.objects.get(pk=door_id))
        return render(request, 'edit_door.html', {'form': form})


@login_required()
def delete_door(request, door_id):
    Doors.objects.get(pk=door_id).delete()
    return HttpResponseRedirect('%s' % (reverse('manage_doors')))


@login_required()
def admin_edit_access(request, member_id):
    user = get_object_or_404(Profile, user=member_id)
    doors = Doors.objects.all()
    data = dict()

    # render the form and return it
    data['html_form'] = render_to_string('partial_admin_edit_access.html', {'member_id': member_id, 'doors': doors},
                                         request=request)
    return JsonResponse(data)