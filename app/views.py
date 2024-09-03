from django.shortcuts import render,redirect , get_object_or_404
from app.halper.AmzonScraper import amazon_scraper 
from app.halper.MyntraScraper import myntra_scraper
from django.core.files.storage import default_storage
from django.http import HttpResponse , FileResponse , HttpResponseNotFound , JsonResponse
import os
import pandas as pd
from django.conf import settings
import csv
import datetime
from django.http import Http404
import json
import time
from django.contrib import messages
from app.utils import sort_dataframe  # Import the function if it's in utils.py

 
CSV_DIR_PATH = os.path.join(settings.BASE_DIR, '/csv_folder')

def home(request):
    if request.method == 'POST':
        # Get data from POST request
        item_to_scrape = request.POST['item-to-scrape']
        data_number = request.POST['data-amount']
        platform = request.POST['website-selector']
        file_name = request.POST['your-file-name']

        # Debugging output to ensure values are being retrieved correctly
        print(f"Item to Scrape: {item_to_scrape}")
        print(f"Data Number: {data_number}")
        print(f"Platform: {platform}")
        print(f"File Name: {file_name}")

        # Check platform and call corresponding scraper
        if platform == 'Amazon':
            amazon_scraper(item_to_scrape, data_number, file_name)
            messages.success(request, 'Amazon Data Scraped Successfully')
        elif platform == 'Myntra':
            myntra_scraper(item_to_scrape, data_number, file_name)
            messages.success(request, 'Myntra Data Scraped Successfully')
        else:
            print("Invalid Platform")
            messages.error(request, 'Scraper is in Work in Progress')
            messages.error(request, 'Please select a valid platform')

        return redirect('result/')
    
    return render(request, 'home.html')

def contact(request):
    return render(request, 'contact.html')

def about(request):
    return render(request, 'about.html')

def result(request):
    csv_folder = 'csv_folder'
    
    # List all CSV files in the folder
    files = [f for f in os.listdir(csv_folder) if f.endswith('.csv')]
    
    if not files:
        raise Http404("No CSV files found.")
    
    # Get the most recent file based on modification time
    latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(csv_folder, f)))
    csv_path = os.path.join(csv_folder, latest_file)

    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_path)

    # Create a new column with HTML for images
    if 'Product Image URL' in df.columns:
        df['Image'] = df['Product Image URL'].apply(
            lambda url: f'<img src="{url}" alt="Product Image" style="max-width: 100px; max-height: 100px;">'
        )
        # Drop the 'Product Image URL' column as we don't want it in the table
        df = df.drop(columns=['Product Image URL'])
        # i want to add Index column (First Column)
        df.insert(0, 'Index', range(1, 1 + len(df)))    
    sort_option = request.GET.get('sort')

    sorted_df = sort_dataframe(df, sort_option)


    # Convert the DataFrame to an HTML table
    table_html = sorted_df.to_html(classes='table table-striped', index=False, escape=False)

    

    # Render the 'result.html' template with the table_html and latest_file context
    return render(request, 'result.html', {
        'table_html': table_html,
        'file_name': latest_file  
    })



def download_csv(request, filename):
    # Define the path to your CSV files
    file_path = os.path.join('csv_folder', filename)
    
    if not os.path.exists(file_path):
        # Return 404 if file not found
        return HttpResponse(status=404)
    
    # Serve the file
    response = FileResponse(open(file_path, 'rb'), as_attachment=True, content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

def history(request):
    # Define the path to the CSV folder
    csv_folder = 'csv_folder'
    csv_path = os.path.join(os.getcwd(), csv_folder)

    # Check if the directory exists
    if not os.path.isdir(csv_path):
        raise Http404("Directory not found.")

    # Get a list of all CSV files in the directory
    csv_files = [f for f in os.listdir(csv_path) if f.endswith('.csv')]

    return render(request, 'history.html', {
        'csv_files': csv_files
    })

def view_csv(request, file_name):

    csv_folder = 'csv_folder'
    csv_path = os.path.join(settings.BASE_DIR, csv_folder, file_name)  # Corrected path

    # Check if the file exists
    if not os.path.isfile(csv_path):
        raise Http404("File not found.")

    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_path)

    # Create a new column with HTML for images if applicable
    if 'Product Image URL' in df.columns:
        df['Image'] = df['Product Image URL'].apply(lambda url: f'<img src="{url}" alt="Product Image" style="max-width: 100px; max-height: 100px;">')
        df = df.drop(columns=['Product Image URL'])

    # Convert the DataFrame to an HTML table
    table_html = df.to_html(classes='table table-striped', index=False, escape=False)

    return render(request, 'view_csv.html', {
        'table_html': table_html,
        'file_name': file_name
    })





from django.shortcuts import render, redirect
from django.http import JsonResponse
import os
from django.conf import settings

def rename_file(request):
    if request.method == 'POST':
        old_name = request.POST.get('old_name')
        new_name = request.POST.get('new_name')
        file_extension = request.POST.get('file_extension')

        # Get the full path of the old and new file names
        old_file_path = os.path.join(settings.MEDIA_ROOT, old_name)
        new_file_path = os.path.join(settings.MEDIA_ROOT, new_name + file_extension)

        # Rename the file if the old file exists
        if os.path.exists(old_file_path):
            os.rename(old_file_path, new_file_path)
            return JsonResponse({'status': 'success', 'new_name': new_name + file_extension})
        else:
            return JsonResponse({'status': 'error', 'message': 'File not found.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})

def delete_file(request):
    if request.method == 'POST':
        file_name = request.POST.get('file_name')

        # Get the full path of the file to delete
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)

        # Delete the file if it exists
        if os.path.exists(file_path):
            os.remove(file_path)
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'File not found.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})

   
   