from django.shortcuts import render, redirect, get_object_or_404
from .models import PackagePlan
from .forms import PackagePlanForm

def package_plans(request):
    if request.method == 'POST':
        form = PackagePlanForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('package_plans')
    else:
        form = PackagePlanForm()
    plans = PackagePlan.objects.all()
    return render(request, 'management/package_plans.html', {'form': form, 'plans': plans})

def edit_package_plan(request, pk):
    plan = get_object_or_404(PackagePlan, pk=pk)
    if request.method == 'POST':
        form = PackagePlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            return redirect('package_plans')
    else:
        form = PackagePlanForm(instance=plan)
    return render(request, 'management/edit_package_plan.html', {'form': form})

def delete_package_plan(request, pk):
    plan = get_object_or_404(PackagePlan, pk=pk)
    plan.delete()
    return redirect('package_plans')

def diet_plans(request):
    return render(request, 'management/diet_plans.html')

def workout_plans(request):
    return render(request, 'management/workout_plans.html')