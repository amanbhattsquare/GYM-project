from django.shortcuts import render, redirect, get_object_or_404
from .models import Gym, SubscriptionPlan
from django.contrib.auth.models import User

def gym_list(request):
    gyms = Gym.objects.all()
    return render(request, 'superadmin/gym_list.html', {'gyms': gyms})

def add_gym(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        contact_person = request.POST.get('contact_person')
        website = request.POST.get('website')
        gstin = request.POST.get('gstin')
        notes = request.POST.get('notes')
        username = request.POST.get('username')
        password = request.POST.get('password')
        logo = request.FILES.get('logo')
        subscription_plan_id = request.POST.get('subscription_plan')
        status = request.POST.get('status')
        domain_url = request.POST.get('domain_url')
        timezone = request.POST.get('timezone')

        if User.objects.filter(username=username).exists():
            error_message = "Username already exists. Please choose a different one."
            subscription_plans = SubscriptionPlan.objects.all()
            return render(request, 'superadmin/add_gym.html', {
                'subscription_plans': subscription_plans,
                'error_message': error_message,
                'form_data': request.POST
            })

        # Create a new user
        user = User.objects.create_user(username=username, password=password)

        subscription_plan = get_object_or_404(SubscriptionPlan, id=subscription_plan_id)

        # Create a new gym and associate it with the user
        Gym.objects.create(
            user=user, 
            name=name, 
            address=address, 
            phone_number=phone_number, 
            email=email,
            contact_person=contact_person,
            website=website,
            gstin=gstin,
            notes=notes,
            logo=logo,
            subscription_plan=subscription_plan,
            status=status,
            domain_url=domain_url,
            timezone=timezone
        )
        
        return redirect('superadmin:gym_list')
    
    subscription_plans = SubscriptionPlan.objects.all()
    return render(request, 'superadmin/add_gym.html', {'subscription_plans': subscription_plans})

def update_gym(request, gym_id):
    gym = get_object_or_404(Gym, id=gym_id)
    if request.method == 'POST':
        gym.name = request.POST.get('name')
        gym.address = request.POST.get('address')
        gym.phone_number = request.POST.get('phone_number')
        gym.email = request.POST.get('email')
        gym.contact_person = request.POST.get('contact_person')
        gym.website = request.POST.get('website')
        gym.gstin = request.POST.get('gstin')
        gym.notes = request.POST.get('notes')
        if request.FILES.get('logo'):
            gym.logo = request.FILES.get('logo')
        
        subscription_plan_id = request.POST.get('subscription_plan')
        if subscription_plan_id:
            gym.subscription_plan = get_object_or_404(SubscriptionPlan, id=subscription_plan_id)
        
        gym.status = request.POST.get('status')
        gym.domain_url = request.POST.get('domain_url')
        gym.timezone = request.POST.get('timezone')

        gym.save()
        return redirect('superadmin:gym_list')
    
    subscription_plans = SubscriptionPlan.objects.all()
    return render(request, 'superadmin/update_gym.html', {'gym': gym, 'subscription_plans': subscription_plans})

def delete_gym(request, gym_id):
    gym = get_object_or_404(Gym, id=gym_id)
    gym.delete()
    return redirect('superadmin:gym_list')