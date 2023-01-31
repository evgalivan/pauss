# Программа автоматизации управления для снятия переодических спектров газов и газовых смесей (ПАУСС)
# 
# Алгоритм с точки зрения наблюдателя:
# 0. Предварительная подготовка установки, пневматической схемы, баллонов и спектрометра.
# 1. Запуск программы ПАУСС.
# 2. Активирует прогрев в терминале.
# 3. Ждет, пока прогревается прибор и прочее.
# 4. Подача нулевого газа или иные манипуляции с пневматикой.
# 5. Активирует измерение нулевого газа в терминале.
# 5. Ждет окончания измерения нулевой смеси.
# 6. Подает измеряемый газ или иные манипуляции с пневматикой.
# 7. Активирует измерение желаемых газов.
# 8. Имеет возможность принудительно завершить испытаения.
#
# Алгоритм работы программы:
# Шаг 1. Отобразить преветствие в терминал.
# Шаг 2. Скопировать файл GASpec.ini,  с нужными конфигурациями для старта работы GASpec
# Шаг 3. Задать вопрос оператору о начале запуска программы GASpec.
# Шаг 4. Запуск программы GASpec (C:\Infraspek\FSpec\FSpec.exe /mod=GASpec)
# Шаг 5. Задать вопрос оператору о начале измерения нулевого газа.
# Шаг 6. Скопировать последовательность файлов control.ini для измерения нулевого газа.
# Шаг 7. Задать вопрос оператору о начале измерения желаемого газа.
# Шаг 8. Скопировать последовательность файлов control.ini для измерения желаемого газа.
# Шаг 9. Задать вопрос оператору о завершении измерения
# Шаг 10. Скопировать последовательность файлов control.ini для завершения работы программы GASpec

from time import sleep
import subprocess

Path_GASpec_ini = 'C:\Infraspek\FSpec\GASpec\GASpec.ini'
Path_Control_ini = 'C:\Infraspek\FSpec\GASpec\Control.ini'
Path_Status_ini = 'C:\Infraspek\FSpec\GASpec\Status.ini'
Path_Timer_exe = 'FreeTimerPortable\FreeTimer.exe'

# именование номеров строк в соотвествии с содержением внутри GASpec.ini
Index_control_mode = 2
Index_continue_sampling_mode = 11
Index_timeout_pos = 26
Index_vision_spectrs = 36

# именование номеров строк в соотвествии с содержением внутри Control.ini
Index_Command = 1
Index_POS = 2
Index_ComparisonSpectrumPeriod = 4
Index_MeasurementFrequency = 5
Index_PumpingDuration = 6
Index_WarmTime = 7
Index_ReportCreateInterval = 8

# именование номеров строк в соотвествии с содержением внутри Status.ini
Index_Status = 1
Index_Warning = 2
Index_Error = 3

#Читает файл GASpec.ini по пути Path_GASpec_ini и возвращает список всех строк файла
def read_GASpecini():
    with open(Path_GASpec_ini, 'r') as file:
        text = file.readlines()
    return text

#Читает файл Control.ini по пути Path_Control_ini и возвращает список всех строк файла
def read_Controlini():
    with open(Path_Control_ini, 'r') as file:
        text = file.readlines()
    return text

#Читает файл Status.ini по пути Path_Status_ini и возвращает список всех строк файла
def read_Statusini():
    with open(Path_Status_ini, 'r') as file:
        text = file.readlines()
    return text

# Запись в файл GASpec.ini по пути Path_GASpec_ini список новых строк text
def write_GASpecini(text):
    with open(Path_GASpec_ini, 'w') as file:
        for line in text:
            file.writelines(line)

# Запись в файл Control.ini по пути Path_Control_ini список новых строк text
def write_Controlini(text):
    with open(Path_Control_ini, 'w') as file:
        for line in text:
            file.writelines(line)

def start_config(GASpecini, Controlini):
    # Редактирование файла GASpec.ini
    # Устанавливаю Режим управления из файлов ini
    GASpecini[Index_control_mode] = 'Режим управления=1\n' # 0 - оператор, 1 - ini-файл
    # Устанавливаю Режим непрерывного измерения на непрерывное
    GASpecini[Index_continue_sampling_mode] = 'Режим непрерывного измерения=1\n' # 0 - единичное, 1 - непрерывное.
    # Устанавливаю таймер ожидания ПОС на 60 секунд
    GASpecini[Index_timeout_pos] = 'Таймаут ожидания пос=60\n' # Таймаут ожидания пос в секундах
    # Включаю режим отображения спектров
    GASpecini[Index_vision_spectrs] = 'Отображать спектры=0\n' # 0 - отображать, 1 - не отображать
    # Вношу изменения в файл
    write_GASpecini(GASpecini)

    # Редактирование файла config.ini
    # Даю команду остановка измерения
    Controlini[Index_Command] = 'Command=2\n' # 1 - запуск измерения, 2 - остановка измерения, 3 - выключение ПК, 4 - выключение GASpec
    # Выбираю измерение образца сравнения
    Controlini[Index_POS] = 'POS=1\n' # 1 - образец сравнения, 0 - проба
    # Устанавливаю время гоности СС в 0
    Controlini[Index_ComparisonSpectrumPeriod] = 'ComparisonSpectrumPeriod=0\n' # Время, в течение которого изменения спектра сравнения не критичны для точности анализа, сек
    # Промежуток времени между началом смежных измерений 60 секунд
    Controlini[Index_MeasurementFrequency] = 'MeasurementFrequency=0\n' # Промежуток времени между началом смежных измерений, сек
    # Время для обновления пробы 5 сек
    Controlini[Index_PumpingDuration] = 'PumpingDuration=0\n' # Время, необходимое для обновления пробы, сек
    # Время прогрева 10 мин (600 сек)
    Controlini[Index_WarmTime] = 'WarmTime=600\n' # Время, необходимое для прогрева спектрометра, сек
    # Интервал создания отчетов через 60 сек
    Controlini[Index_ReportCreateInterval] = 'ReportCreateInterval=60\n' # Интервал создания отчетов, минимум 60 сек, сек
    # Вношу изменения в файл
    write_Controlini(Controlini)

def measurement_zero_gas(Controlini):
    # Редактирование файла config.ini
    # Даю команду запуск измерения
    Controlini[Index_Command] = 'Command=1\n' # 1 - запуск измерения, 2 - остановка измерения, 3 - выключение ПК, 4 - выключение GASpec
    # Выбираю измерение образца сравнения
    Controlini[Index_POS] = 'POS=1\n' # 1 - образец сравнения, 0 - проба
    # Устанавливаю время гоности СС в 0
    Controlini[Index_ComparisonSpectrumPeriod] = 'ComparisonSpectrumPeriod=0\n' # Время, в течение которого изменения спектра сравнения не критичны для точности анализа, сек
    # Вношу изменения в файл
    write_Controlini(Controlini)
    # жду 10 секунд обработки команды GASpec
    sleep(10)
    # Устанавливаю время гоности СС в 0
    Controlini[Index_ComparisonSpectrumPeriod] = 'ComparisonSpectrumPeriod=36000\n' # Время, в течение которого изменения спектра сравнения не критичны для точности анализа, сек
    # Вношу изменения в файл
    write_Controlini(Controlini)

def measurement_probe(Controlini):
    # Редактирование файла config.ini
    # Даю команду остановка измерения
    Controlini[Index_Command] = 'Command=2\n' # 1 - запуск измерения, 2 - остановка измерения, 3 - выключение ПК, 4 - выключение GASpec
    # Выбираю измерение пробы
    Controlini[Index_POS] = 'POS=0\n' # 1 - образец сравнения, 0 - проба
    # Вношу изменения в файл
    write_Controlini(Controlini)
    # жду 10 секунд обработки команды GASpec
    sleep(10)
    # Даю команду запуск измерения
    Controlini[Index_Command] = 'Command=1\n' # 1 - запуск измерения, 2 - остановка измерения, 3 - выключение ПК, 4 - выключение GASpec
    # Вношу изменения в файл
    write_Controlini(Controlini)

def end_of_measurement(Controlini):
    # Редактирование файла config.ini
    # Даю команду запуск измерения
    Controlini[Index_Command] = 'Command=2\n' # 1 - запуск измерения, 2 - остановка измерения, 3 - выключение ПК, 4 - выключение GASpec
    # Вношу изменения в файл
    write_Controlini(Controlini)
    # жду 3 секунд обработки команды GASpec
    sleep(3)
    # Даю команду остановка измерения
    Controlini[Index_Command] = 'Command=4\n' # 1 - запуск измерения, 2 - остановка измерения, 3 - выключение ПК, 4 - выключение GASpec
    # Вношу изменения в файл
    write_Controlini(Controlini)
    # жду 3 секунд обработки команды GASpec
    sleep(3)
    # Даю команду запуск измерения
    Controlini[Index_Command] = 'Command=2\n' # 1 - запуск измерения, 2 - остановка измерения, 3 - выключение ПК, 4 - выключение GASpec
    # Вношу изменения в файл
    write_Controlini(Controlini)

# Шаг 1. Отобразить преветствие в терминал.
print('Привет, тебя приветсвует программа ПАУСС версия 1.0, которая поможет тебе с GASpec.')
print('***************************************************************************************************')
# Шаг 2. Скопировать файл GASpec.ini, control.ini с нужными конфигурациями для старта работы GASpec

GASpecini = read_GASpecini()
Controlini = read_Controlini()
count = len(Controlini)

#дописываю в конец списка Controlini несколько пустых элементов, если их еще не было
if count < (Index_ReportCreateInterval + 1):
    while (Index_ReportCreateInterval + 1) - count > 0:
        Controlini.append('\n')
        count += 1


start_config(GASpecini, Controlini)

GASpecini = read_GASpecini()

# Шаг 3. Задать вопрос оператору о начале запуска программы GASpec.
print('Запустить программу GASpec [y/n]:', end=' ')
s = input()

# Шаг 4. Запуск программы GASpec (C:\Infraspek\FSpec\FSpec.exe /mod=GASpec)
if s == 'y' or s == 'Y':
    print('Программа GASpec запущена. Теперь нужно подождать, пока прогреется прибор')
    subprocess.Popen(['C:\Infraspek\FSpec\FSpec.exe', '/mod=GASpec'])
    P = subprocess.Popen([Path_Timer_exe, '/START',  '/TITLE', 'Прогрев кюветы', '/TIME', '00:05:00'])
    P.wait();
else:
    exit()


# Шаг 5. Задать вопрос оператору о начале измерения нулевого газа.
print('Начать измерения спектра сравнения [y/n]:', end=' ')
s = input()

# Шаг 6. Скопировать последовательность файлов control.ini для измерения нулевого газа.
if s == 'y' or s == 'Y':
    print('Начаты измерения спетра сравнения')
    Controlini = read_Controlini()
    measurement_zero_gas(Controlini)
else:
    exit()

# Шаг 7. Задать вопрос оператору о начале измерения желаемого газа.
print('Начать измерения пробы [y/n]:', end=' ')
s = input()

# Шаг 8. Скопировать последовательность файлов control.ini для измерения желаемого газа.
if s == 'y' or s == 'Y':
    print('Начаты измерения пробы')
    Controlini = read_Controlini()
    measurement_probe(Controlini)
else:
    exit()

# Шаг 9. Задать вопрос оператору о завершении измерения
print('Хотите завершить измерения [y/n]:', end=' ')
s = input()
print('Завершаю работу программы')
Controlini = read_Controlini()
end_of_measurement(Controlini)

print('Всего доброго!')