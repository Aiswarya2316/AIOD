from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import *
from .forms import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.timezone import now




# Customer Registration
def customer_register(request):
    if request.method == "POST":
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer registered successfully!")
            return redirect("login")
    else:
        form = CustomerRegistrationForm()
    return render(request, "customer/register.html", {"form": form, "user_type": "Customer"})



# Seller Registration
def seller_register(request):
    if request.method == "POST":
        form = StafRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Seller registered successfully!")
            return redirect("login")
    else:
        form = StafRegistrationForm()
    return render(request, "staf/register.html", {"form": form, "user_type": "Seller"})



# Admin Registration
def admin_register(request):
    if request.method == "POST":
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Admin registered successfully!")
            return redirect("login")
    else:
        form = AdminRegistrationForm()
    return render(request, "admin/register.html", {"form": form, "user_type": "Admin"})



# --- User Login ---
def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = None
            redirect_url = "login"  # Default in case of failure

            if Customer.objects.filter(email=email, password=password).exists():
                user = Customer.objects.get(email=email)
                request.session["user_type"] = "Customer"
                redirect_url = "customerhome"
            elif Staf.objects.filter(email=email, password=password).exists():
                user = Staf.objects.get(email=email)
                request.session["user_type"] = "Staf"
                redirect_url = "stafhome"
            elif AdminReg.objects.filter(email=email, password=password).exists():
                user = AdminReg.objects.get(email=email)
                request.session["user_type"] = "Admin"
                redirect_url = "adminhome"

            if user:
                request.session["user_id"] = user.id
                messages.success(request, f"Welcome {user.name}!")
                return redirect(redirect_url)
            else:
                messages.error(request, "Invalid credentials")

    form = LoginForm()
    return render(request, "login.html", {"form": form})



# Logout View
def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect("home")



def home(request):
    return render(request,'home.html')

def customerhome(request):
    return render(request,'customer/customerhome.html')

def stafhome(request):
    return render(request,'staf/stafhome.html')


from django.shortcuts import render
from django.db.models import Sum, Count
from .models import Donation, Customer, Cause

def adminhome(request):
    total_donations = Donation.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_donors = Donation.objects.values('donor_email').distinct().count()
    total_causes = Cause.objects.count()
    total_customers = Customer.objects.count()

    donations = Donation.objects.all().order_by('-date')

    context = {
        'total_donations': total_donations,
        'total_donors': total_donors,
        'total_causes': total_causes,
        'total_customers': total_customers,
        'donations': donations,
    }

    return render(request, 'admin/adminhome.html', context)





from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Cause
from .forms import CategoryForm, CauseForm

# Category Views
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'staf/category_list.html', {'categories': categories})

def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'staf/category_form.html', {'form': form})

# Cause Views
def cause_list(request):
    causes = Cause.objects.all()
    return render(request, 'staf/cause_list.html', {'causes': causes})

def add_cause(request):
    if request.method == "POST":
        form = CauseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cause_list')
    else:
        form = CauseForm()
    return render(request, 'staf/cause_form.html', {'form': form})




from django.shortcuts import render, redirect
from .models import Donation, Cause, Customer
from .forms import DonationForm

def donate(request):
    if request.method == "POST":
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save()
            
            # Update raised_amount in the selected cause
            donation.cause.raised_amount += donation.amount
            donation.cause.save()

            return redirect('donation_success')  # Redirect to a success page
    else:
        form = DonationForm()

    return render(request, "customer/donate.html", {"form": form})

def donation_success(request):
    return render(request, "customer/donation_success.html")

def donation_history(request):
    donations = Donation.objects.all()  # Fetch all donations
    return render(request, "customer/donation_history.html", {"donations": donations})


from django.shortcuts import render
from .models import Donation

def donation_list(request):
    status = request.GET.get('status', 'all')

    if status == 'paid':
        donations = Donation.objects.filter(payment_status=True).order_by('-date')
    elif status == 'pending':
        donations = Donation.objects.filter(payment_status=False).order_by('-date')
    else:
        donations = Donation.objects.all().order_by('payment_status', '-date')

    return render(request, 'staf/donation_list.html', {'donations': donations, 'status': status})







import razorpay
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Donation

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def create_payment(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    
    # Create Razorpay Order
    order_data = {
        "amount": int(donation.amount * 100),  # Convert to paisa
        "currency": "INR",
        "payment_capture": "1",  # Auto capture payment
    }
    order = razorpay_client.order.create(order_data)
    
    # Save order ID in the model
    donation.razorpay_order_id = order["id"]
    donation.save()
    
    return JsonResponse({
        "order_id": order["id"],
        "amount": donation.amount,
        "currency": "INR",
        "key": settings.RAZORPAY_KEY_ID,
        "donor_name": donation.donor_name,
        "donor_email": donation.donor_email,
    })



from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def verify_payment(request):
    if request.method == "POST":
        data = json.loads(request.body)
        razorpay_order_id = data.get("order_id")
        razorpay_payment_id = data.get("payment_id")
        razorpay_signature = data.get("signature")

        try:
            # Verify payment signature
            params_dict = {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature
            }
            razorpay_client.utility.verify_payment_signature(params_dict)

            # Update donation status
            donation = Donation.objects.get(razorpay_order_id=razorpay_order_id)
            donation.payment_status = True
            donation.save()

            return JsonResponse({"success": True, "message": "Payment successful!"})

        except:
            return JsonResponse({"success": False, "message": "Payment verification failed."})







from django.shortcuts import render, get_object_or_404
from .models import Category, Cause

def cause_list(request, category_id=None):
    categories = Category.objects.all()
    if category_id:
        selected_category = get_object_or_404(Category, id=category_id)
        causes = Cause.objects.filter(category=selected_category)
    else:
        selected_category = None
        causes = Cause.objects.all()
    
    return render(request, 'customer/cause_list.html', {
        'categories': categories,
        'causes': causes,
        'selected_category': selected_category
    })




from django.shortcuts import render
from .models import Donation

def view_donations(request):
    donations = Donation.objects.all().order_by('-date')  # Fetch all donations in descending order

    context = {
        'donations': donations
    }
    return render(request, 'admin/donations.html', context)





from django.shortcuts import render
from .models import Customer

def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'admin/customers.html', {'customers': customers})




from django.shortcuts import render
from .models import Cause

def all_causes(request):
    causes = Cause.objects.all()
    return render(request, 'admin/causes_list.html', {'causes': causes})

