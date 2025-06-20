from django.shortcuts import render, redirect, get_object_or_404
from .forms import BookUploadForm
from .models import Book
import PyPDF2

def upload_book(request):
    if request.method == 'POST':
        form = BookUploadForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            pdf_file = request.FILES['pdf']
            reader = PyPDF2.PdfReader(pdf_file)
            text = "".join(page.extract_text() or '' for page in reader.pages)
            book.content = text
            book.save()
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookUploadForm()
    return render(request, 'upload.html', {'form': form})

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'detail.html', {'book': book})
