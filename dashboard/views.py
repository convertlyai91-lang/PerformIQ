from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Employee
import pandas as pd
import csv
import io
import os
import joblib
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

@login_required
def dashboard(request):
    employees = Employee.objects.all()
    total = employees.count()
    if total > 0:
        avg_score = round(sum(e.performance_rating for e in employees) / total, 2)
        top = list(employees.order_by('-performance_rating')[:10])
        lowest = min(e.performance_rating for e in employees)
        highest = max(e.performance_rating for e in employees)
    else:
        avg_score = 0
        top = []
        lowest = 0
        highest = 0
    context = {
        'total': total,
        'avg_score': avg_score,
        'top_employees': top,
        'lowest': lowest,
        'highest': highest,
    }
    return render(request, 'dashboard.html', context)

@login_required
def employee_list(request):
    employees = Employee.objects.all()
    query = request.GET.get('search', '')
    dept = request.GET.get('department', '')
    if query:
        employees = employees.filter(name__icontains=query)
    if dept:
        employees = employees.filter(department__icontains=dept)
    return render(request, 'employee_list.html', {'employees': employees})

@login_required
def add_employee(request):
    if request.method == 'POST':
        Employee.objects.create(
            employee_id=request.POST['employee_id'],
            name=request.POST['name'],
            department=request.POST['department'],
            position=request.POST['position'],
            attendance=request.POST['attendance'],
            performance_rating=request.POST['performance_rating'],
            experience=request.POST['experience'],
            salary=request.POST['salary'],
            project_completion_rate=request.POST['project_completion_rate'],
        )
        return redirect('employee_list')
    return render(request, 'add_employee.html')

@login_required
def edit_employee(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        emp.name = request.POST['name']
        emp.department = request.POST['department']
        emp.position = request.POST['position']
        emp.attendance = request.POST['attendance']
        emp.performance_rating = request.POST['performance_rating']
        emp.experience = request.POST['experience']
        emp.salary = request.POST['salary']
        emp.project_completion_rate = request.POST['project_completion_rate']
        emp.save()
        return redirect('employee_list')
    return render(request, 'edit_employee.html', {'emp': emp})

@login_required
def delete_employee(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    emp.delete()
    return redirect('employee_list')

@login_required
def import_csv(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        file = request.FILES['csv_file']
        decoded = file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(decoded))
        for row in reader:
            Employee.objects.get_or_create(
                employee_id=row['employee_id'],
                defaults={
                    'name': row['name'],
                    'department': row['department'],
                    'position': row['position'],
                    'attendance': row['attendance'],
                    'performance_rating': row['performance_rating'],
                    'experience': row['experience'],
                    'salary': row['salary'],
                    'project_completion_rate': row['project_completion_rate'],
                }
            )
    return redirect('employee_list')

@login_required
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="employees.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID','Name','Department','Position','Attendance','Rating','Experience','Salary','Completion Rate'])
    for e in Employee.objects.all():
        writer.writerow([e.employee_id, e.name, e.department, e.position,
                         e.attendance, e.performance_rating, e.experience,
                         e.salary, e.project_completion_rate])
    return response

@login_required
def export_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="employees.pdf"'
    p = canvas.Canvas(response, pagesize=letter)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(200, 750, "Employee Performance Report")
    p.setFont("Helvetica", 10)
    y = 720
    for e in Employee.objects.all():
        p.drawString(50, y, f"{e.name} | {e.department} | Rating: {e.performance_rating}")
        y -= 20
        if y < 50:
            p.showPage()
            y = 750
    p.save()
    return response


    

@login_required
def predict(request):
    result = None
    error = None
    if request.method == 'POST':
        try:
            model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ml_model.pkl')
            model = joblib.load(model_path)
            age = int(request.POST.get('age', 0))
            department = int(request.POST.get('department', 0))
            no_of_trainings = int(request.POST.get('no_of_trainings', 0))
            previous_year_rating = float(request.POST.get('previous_year_rating', 0))
            length_of_service = int(request.POST.get('length_of_service', 0))
            kpis_met = int(request.POST.get('kpis_met', 0))
            awards_won = int(request.POST.get('awards_won', 0))
            features = [[age, department, no_of_trainings, previous_year_rating,
                        length_of_service, kpis_met, awards_won]]
            prediction = model.predict(features)[0]
            result = round(float(prediction), 2)
        except Exception as e:
            error = str(e)
    return render(request, 'predict.html', {'result': result, 'error': error})

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})
