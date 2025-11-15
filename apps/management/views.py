from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import DietPlan, PackagePlan, WorkoutPlan
from .forms import DietPlanForm, PackagePlanForm, WorkoutPlanForm
from django.http import JsonResponse

from django.contrib import messages

def package_plans(request):
    if request.method == 'POST':
        form = PackagePlanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Package plan created successfully.')
            return redirect('package_plans')
    else:
        form = PackagePlanForm()
    plans = PackagePlan.objects.all()
    return render(request, 'management/PackagePlans/package_plans.html', {'form': form, 'plans': plans})

def edit_package_plan(request, pk):
    plan = get_object_or_404(PackagePlan, pk=pk)
    if request.method == 'POST':
        form = PackagePlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, 'Package plan updated successfully.')
            return redirect('package_plans')
    else:
        form = PackagePlanForm(instance=plan)
    return render(request, 'management/PackagePlans/edit_package_plan.html', {'form': form})

def delete_package_plan(request, pk):
    plan = get_object_or_404(PackagePlan, pk=pk)
    if request.method == 'POST':
        try:
            plan.delete()
            return JsonResponse({'status': 'success', 'message': 'Package plan deleted successfully.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

def diet_plans(request):
    if request.method == 'POST':
        form = DietPlanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Diet plan created successfully.')
            return redirect('diet_plans')
    else:
        form = DietPlanForm()
    plans = DietPlan.objects.all()
    return render(request, 'management/DietPlans/diet_plans.html', {'form': form, 'plans': plans})

def edit_diet_plan(request, pk):
    plan = get_object_or_404(DietPlan, pk=pk)
    if request.method == 'POST':
        form = DietPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, 'Diet plan updated successfully.')
            return redirect('diet_plans')
    else:
        form = DietPlanForm(instance=plan)
    return render(request, 'management/DietPlans/edit_diet_plan.html', {'form': form})

def delete_diet_plan(request, pk):
    plan = get_object_or_404(DietPlan, pk=pk)
    if request.method == 'POST':
        try:
            plan.delete()
            return JsonResponse({'status': 'success', 'message': 'Diet plan deleted successfully.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

def workout_plans(request):
    if request.method == 'POST':
        form = WorkoutPlanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Workout plan created successfully.')
            return redirect('workout_plans')
    else:
        form = WorkoutPlanForm()
    plans = WorkoutPlan.objects.all()
    return render(request, 'management/WorkoutPlans/workout_plans.html', {'form': form, 'plans': plans})