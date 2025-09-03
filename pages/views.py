from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView
from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Product
from .utils import ImageLocalStorage
# Create your views here.
class HomePageView(TemplateView):
    template_name = 'pages/home.html'
    pass
class AboutPageView(TemplateView):
 template_name = 'pages/about.html'

 def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context.update({
    "title": "About us - Online Store",
    "subtitle": "About us",
    "description": "This is an about page ...",
    "author": "Developed by: Santiago",
    })
    return context


class ProductIndexView(View):
    template_name = 'products/index.html'
    def get(self, request):
        viewData = {}
        viewData["title"] = "Products - Online Store"
        viewData["subtitle"] = "List of products"
        viewData["products"] = Product.objects.all()
        return render(request, self.template_name, viewData)

class ProductShowView(View):
    template_name = 'products/show.html'
    
    def get(self, request, id):
        viewData = {}
        try:
            product = get_object_or_404(Product, id=id)
            viewData["title"] = product.name + " - Online Store"
            viewData["subtitle"] = product.name + " - Product information"
            viewData["product"] = product
            viewData["price"] = product.price
            viewData["comment_form"] = CommentForm()
            return render(request, self.template_name, viewData)
        except (ValueError, IndexError):
            return HttpResponseRedirect(reverse('home'))
    
    def post(self, request, id):
        viewData = {}
        try:
            product = get_object_or_404(Product, id=id)
            comment_form = CommentForm(request.POST)
            
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.product = product
                comment.save()
                return HttpResponseRedirect(reverse('show', kwargs={'id': id}))
            else:
                viewData["title"] = product.name + " - Online Store"
                viewData["subtitle"] = product.name + " - Product information"
                viewData["product"] = product
                viewData["price"] = product.price
                viewData["comment_form"] = comment_form
                return render(request, self.template_name, viewData)
        except (ValueError, IndexError):
            return HttpResponseRedirect(reverse('home'))


from django import forms
from django.shortcuts import render, redirect
from .models import Product, Comment

class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ['name', 'price'] 
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError("Price must be greater than zero.")
        return price

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['description']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter your comment...'})
        }

class ProductCreateView(View):
    template_name = 'products/create.html'
    def get(self, request):
        form = ProductForm()
        viewData = {}
        viewData["title"] = "Create product"
        viewData["form"] = form
        return render(request, self.template_name, viewData)

    def post(self, request):
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'products/success.html', {"title": "Product Created"})
        else:
            viewData = {}
            viewData["title"] = "Create product"
            viewData["form"] = form
            return render(request, self.template_name, viewData)

class ProductListView(ListView):
 model = Product
 template_name = 'product_list.html'
 context_object_name = 'products' # This will allow you to loop through 'products' in your template

def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = 'Products - Online Store'
    context['subtitle'] = 'List of products'
    return context             


class CartView(View):
    template_name = 'cart/index.html'

    def get(self, request):
        # Simulated database for products
        products = {}
        products[121] = {'name': 'Tv samsung', 'price': '1000'}
        products[11] = {'name': 'Iphone', 'price': '2000'}
        # Get cart products from session
        cart_products = {}
        cart_product_data = request.session.get('cart_product_data', {})
        for key, product in products.items():
            if str(key) in cart_product_data.keys():
                cart_products[key] = product
        # Prepare data for the view
        view_data = {
            'title': 'Cart - Online Store',
            'subtitle': 'Shopping Cart',
            'products': products,
            'cart_products': cart_products
        }
        return render(request, self.template_name, view_data)

    def post(self, request, product_id):
        # Get cart products from session and add the new product
        cart_product_data = request.session.get('cart_product_data', {})
        cart_product_data[product_id] = product_id
        request.session['cart_product_data'] = cart_product_data
        return redirect('cart_index')

class CartRemoveAllView(View):
    def post(self, request):
        # Remove all products from cart in session
        if 'cart_product_data' in request.session:
            del request.session['cart_product_data']
            return redirect('cart_index')

# With DI
def ImageViewFactory(image_storage):
    class ImageView(View):
        template_name = 'images/index.html'

        def get(self, request):
            image_url = request.session.get('image_url', '')
            return render(request, self.template_name, {'image_url': image_url})

        def post(self, request):
            image_url = image_storage.store(request)
            request.session['image_url'] = image_url
            return redirect('image_index')
    return ImageView       

# No DI
class ImageViewNoDI(View):
    template_name = 'images/index.html'
    def get(self, request):
        image_url = request.session.get('image_url', '')
        return render(request, self.template_name, {'image_url': image_url})
    def post(self, request):    # No DI
        image_storage = ImageLocalStorage()
        image_url = image_storage.store(request)
        request.session['image_url'] = image_url
        return redirect('image_index')