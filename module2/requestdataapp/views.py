from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.core.files.storage import FileSystemStorage

def process_get_view(request: HttpRequest) -> HttpResponse:
    a = request.GET.get("a", "")
    b = request.GET.get("b", "")
    result = a + b
    context = {
            "a": a,
            "b": b,
            "result": result,
    }
    return render(request, "requestdataapp/request-query-params.html", context=context)

def user_form(request: HttpRequest) -> HttpResponse:
    return render(request, "requestdataapp/user-bio-form.html")

def handle_file_upload(request: HttpRequest) -> HttpResponse:
    if request.method == "POST" and request.FILES.get("myfile"):
        myfile = request.FILES["myfile"] # Считываем файл
        if myfile.size > 1048576:
            raise MemoryError
        fs = FileSystemStorage() # Сохраняем файл
        filename = fs.save(myfile.name, myfile) # Имя файла и сам файл
        print("saved file", filename)
    return render(request, "requestdataapp/file-upload.html")