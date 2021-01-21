from django.views import View
from django.views.generic import CreateView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from .forms import CreationForm, ContactForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy("login")  # где login — это параметр "name" в path()
    template_name = "signup.html"


# from django.core.mail import send_mail
#
# send_mail(
#     'Тема письма',
#     'Текст письма.',
#     'from@example.com',  # Это поле "От кого"
#     ['to@example.com'],  # Это поле "Кому" (можно указать список адресов)
#     fail_silently=False,  # Сообщать об ошибках («молчать ли об ошибках?»)
# )


def user_contact(request):
    # проверим, пришёл ли к нам POST-запрос или какой-то другой:
    if request.method == 'POST':
        # создаём объект формы класса ContactForm и передаём в него полученные данные
        form = ContactForm(request.POST)
        # проверяем данные на валидность:
        # ... здесь код валидации ...

        if form.is_valid():
            # обрабатываем данные формы, используя значения словаря form.cleaned_data
            # возвращаем результат
            # Функция redirect перенаправляет пользователя
            # на другую страницу сайта, чтобы защититься
            # от повторного заполнения формы, если посетитель
            # сайта случайно перезагрузит страницу
            return redirect('/thank-you/')

        # если не сработало условие if form.is_valid() и данные не прошли валидацию
        # сработает следующий блок кода,
        # иначе команда return прервала бы дальнейшее исполнение функции

        # вернём пользователю страницу с HTML-формой и передадим полученный объект формы на страницу,
        # чтобы вернуть информацию об ошибке

        # заодно автоматически заполним прошедшими валидацию данными все поля,
        # чтобы не заставлять пользователя второй раз заполнять их
        return render(request, 'contact.html', {'form': form})

    form = ContactForm()
    return render(request, 'contact.html', {'form': form})
