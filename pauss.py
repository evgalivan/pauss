# Программа автоматизации управления для снятия переодических спектров газов и газовых смесей (ПАУСС)
# 
# Алгоритм с точки зрения наблюдателя:
# 0. Предварительная подготовка установки, пневматической схемы, баллонов и спектрометра.
# 1. Запуск программы ПАУСС.
# 2. Активирует прогрев в терминале.
# 3. Ждет, пока прогревается прибор и прочее.
# 4. Подача нулевого газа или иные манипуляции с пневматикой.
# 5. Активирует начало измерений.
# 6. Имеет возможность принудительно завершить испытаения.
#
# Алгоритм работы программы:
# Шаг 1. Отобразить преветствие в терминал.
# Шаг 2. Скопировать файл GASpec.ini,  с нужными конфигурациями для старта работы GASpec
# Шаг 3. Задать вопрос оператору о начале запуска программы GASpec.
# Шаг 4. Запуск программы GASpec (C:\Infraspek\FSpec\FSpec.exe /mod=GASpec)
# Шаг 5. Задать вопрос оператору о начале измерений
# Шаг 6. Скопировать последовательность файлов control.ini для измерения нулевого газа, затем для измерения пробы.
# Шаг 7. Задать вопрос оператору о завершении измерения
# Шаг 8. Скопировать последовательность файлов control.ini для завершения работы программы GASpec

from time import sleep
import subprocess
import datetime

Path_GASpec_ini = 'C:\Infraspek\FSpec\GASpec\GASpec.ini'
Path_Control_ini = 'C:\Infraspek\FSpec\GASpec\Control.ini'
Path_Status_ini = 'C:\Infraspek\FSpec\GASpec\Status.ini'
Path_Timer_exe = 'FreeTimerPortable\FreeTimer.exe'

# именование номеров строк в соотвествии с содержением внутри GASpec.ini
Index_control_mode = 2
Index_continue_sampling_mode = 11
Index_continue_sampling_type = 14
Index_timeout_continue_sampling = 17
Index_timeout_pos = 26
Index_inverse_opto = 34
Index_vision_spectrs = 36
Index_heght_cuvette = 44

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

# возможные статусы GASpec
status_warm = 1 # 000001	Прогрев
status_ready = 2 # 000010	Прибор готов к работе
status_meas = 6 # 000110	Измерение
status_error_1 = 8 # 001000\001010	Ошибка
status_error_2 = 10 # 001000\001010	Ошибка
status_meas_pos = 22 # 010110	Измерение спектра сравнения
status_wait_pos = 38 # 100110	Ожидание спектра сравнения

# возможные ошибки GASpec
error_loop_recall = -2 # -2:  Превышено число циклов ожидания переключения ПОС
error_timeout_switch = -5 # -5:  Превышен таймаут ожидания переключения ПОС
error_test_speed = -9 # -9:  Не пройден стартовый тест скорости
error_test_refsig = -10 # -10: Не пройден стартовый тест рефсигнала
error_metod_mis = -11 # -11: отсутствие файла метода или невозможность его загрузки

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

def get_status():
    Statusini = read_Statusini()
    value = Statusini[Index_Status].split('=')
    return int(value[1])

def get_error():
    Statusini = read_Statusini()
    value = Statusini[Index_Error].split('=')
    return int(value[1])

def print_time():
    now = datetime.datetime.now()
    print(now.strftime("%d-%m-%Y %H:%M:%S"), end = ': ')

def start_config_GASpec(GASpecini):
    # Редактирование файла GASpec.ini
    # Устанавливаю Режим управления из файлов ini
    GASpecini[Index_control_mode] = 'Режим управления=1\n' # 0 - оператор, 1 - ini-файл
    # Устанавливаю Режим непрерывного измерения на непрерывное
    GASpecini[Index_continue_sampling_mode] = 'Режим непрерывного измерения=1\n' # 0 - единичное, 1 - непрерывное.
    # Устанавливаю Тип непрерывного измерения на заданный интервал
    GASpecini[Index_continue_sampling_type] = 'Тип непрерывного измерения=0\n' # 0 - постоянно, 1 - в заданном интервале времени.
    # Устанавливаю длительность интервала на 0 минут
    GASpecini[Index_timeout_continue_sampling] = 'Длительность непрерывного измерения=0\n' # Длительность непрерывного измерения в минутах.
    # Устанавливаю таймер ожидания ПОС на 60 секунд
    GASpecini[Index_timeout_pos] = 'Таймаут ожидания пос=60\n' # Таймаут ожидания пос в секундах
    # Включаю режим отображения спектров
    GASpecini[Index_vision_spectrs] = 'Отображать спектры=1\n' # 0 - не отображать, 1 - отображать
    # Задаем толщину (длину) кюветы
    GASpecini[Index_heght_cuvette] = 'Толщина кюветы=4.8\n' # 0 - не отображать, 1 - отображать
    # Вношу изменения в файл
    write_GASpecini(GASpecini)

def reset_config_GASpec(GASpecini):
    # Редактирование файла GASpec.ini
    # Устанавливаю Режим управления из файлов ini
    GASpecini[Index_control_mode] = 'Режим управления=0\n' # 0 - оператор, 1 - ini-файл
    # Устанавливаю Режим управления из файлов ini
    GASpecini[Index_inverse_opto] = 'Инверсия оптопары=1\n' # 0 - оператор, 1 - ini-файл
    # Вношу изменения в файл
    write_GASpecini(GASpecini)

def start_congig_Control(Controlini):
    # Редактирование файла config.ini
    # Даю команду остановка измерения
    Controlini[Index_Command] = 'Command=2\n' # 1 - запуск измерения, 2 - остановка измерения, 3 - выключение ПК, 4 - выключение GASpec
    # Выбираю измерение образца сравнения
    Controlini[Index_POS] = 'POS=0\n' # 1 - образец сравнения, 0 - проба
    # Устанавливаю время гоности СС в 0
    Controlini[Index_ComparisonSpectrumPeriod] = 'ComparisonSpectrumPeriod=7200\n' # Время, в течение которого изменения спектра сравнения не критичны для точности анализа, сек
    # Промежуток времени между началом смежных измерений 60 секунд
    Controlini[Index_MeasurementFrequency] = 'MeasurementFrequency=0\n' # Промежуток времени между началом смежных измерений, сек
    # Время для обновления пробы 5 сек
    Controlini[Index_PumpingDuration] = 'PumpingDuration=0\n' # Время, необходимое для обновления пробы, сек
    # Время прогрева 0 сек (0 мин)
    Controlini[Index_WarmTime] = 'WarmTime=0\n' # Время, необходимое для прогрева спектрометра, сек
    # Интервал создания отчетов через 60 сек
    Controlini[Index_ReportCreateInterval] = 'ReportCreateInterval=60\n' # Интервал создания отчетов, минимум 60 сек, сек
    # Вношу изменения в файл
    write_Controlini(Controlini)

def measurement(flag):
    count_none_status = 0 # завожу счетчик для принудительного выхода
    Flag_pos = flag # флаг ПОС: 0 - спектр сравнения есть, 1 - спектр сравнения измеряется
    odd = True # для ошибки GASpec
    while True:
        status = get_status()
        Controlini = read_Controlini()
        # Редактирование файла config.ini
        if status == status_ready:  # если прибор готов, то запускаю измерения
            print_time()
            print('Прибор готов, начинаю измерения')

            # Даю команду запуск измерения
            Controlini[Index_Command] = 'Command=1\n' # 1 - запуск измерения, 2 - остановка измерения, 3 - выключение ПК, 4 - выключение GASpec
            # Вношу изменения в файл
            write_Controlini(Controlini)

        elif status == status_meas: # если измерение, то убираю запрос на измерение спектра сравнения
            print_time()
            print('Идет измерение')

            if Flag_pos == 1:
                # Выбираю измерение пробы
                Controlini[Index_POS] = 'POS=0\n' # 1 - образец сравнения, 0 - проба
                # Устанавливаю время гоности СС в 7200 (2 часа)
                Controlini[Index_ComparisonSpectrumPeriod] = 'ComparisonSpectrumPeriod=7200\n' # Время, в течение которого изменения спектра сравнения не критичны для точности анализа, сек
                # Вношу изменения в файл
                write_Controlini(Controlini)
                # Снимаю флаг POS
                Flag_pos = 0

        elif status == status_error_1 or status == status_error_2: # если ошибка, то выясняю, что делать
            error = get_error()
            if error == error_loop_recall:
                print_time()
                print("Превышено число циклов ожидания переключения ПОС")

                # Даю команду остановка
                Controlini[Index_Command] = 'Command=2\n' # 1 - запуск измерения, 2 - остановка измерения, 3 - выключение ПК, 4 - выключение GASpec
                # Вношу изменения в файл
                write_Controlini(Controlini)

            elif error == error_timeout_switch:
                print_time()
                print("Превышен таймаут ожидания переключения ПОС")

                # Даю команду остановка
                Controlini[Index_Command] = 'Command=2\n' # 1 - запуск измерения, 2 - остановка измерения, 3 - выключение ПК, 4 - выключение GASpec
                # Вношу изменения в файл
                write_Controlini(Controlini)

            elif error == error_test_speed:
                print_time()
                print("Не пройден стартовый тест скорости")
                break

            elif error == error_test_refsig:
                print_time()
                print("Не пройден стартовый тест рефсигнала")
                break

            elif error == error_metod_mis:
                print_time()
                print("отсутствие файла метода или невозможность его загрузки")
                break

            else:
                print_time()
                print("Ошибка программы GASpec")
                if odd == True:
                    # Даю команду остановка
                    Controlini[Index_Command] = 'Command=1\n' # 1 - запуск измерения, 2 - остановка измерения, 3 - выключение ПК, 4 - выключение GASpec
                    # Вношу изменения в файл
                    write_Controlini(Controlini)
                    odd = False
                else:
                    # Даю команду остановка
                    Controlini[Index_Command] = 'Command=2\n' # 1 - запуск измерения, 2 - остановка измерения, 3 - выключение ПК, 4 - выключение GASpec
                    # Вношу изменения в файл
                    write_Controlini(Controlini)
                    odd = True
                sleep(3)

        elif status == status_meas_pos: # если измерение спектра сравнения, то выдаю статус
            print_time()
            print('Идет измерение спектра сравнения')

        elif status == status_wait_pos: # если ожидание спектра сравнения, то выставляю его измерение
            print_time()
            print('Ожидание спектра сравнения')

            if Flag_pos == 0:

                # Выбираю измерение образца сравнения
                Controlini[Index_Command] = 'Command=2\n' # 1 - образец сравнения, 0 - проба
                # Вношу изменения в файл
                write_Controlini(Controlini)

                # Жду введение команды оператором
                print('Загрузите в кювету образец сравнения и введите команду (без ковычек) "измерить пос":', end=' ')
                s = input()

                if s == 'измерить пос' or s == 'Измерить пос' or s == 'Измерить ПОС' or s == 'Измерить Пос' or s == 'ИЗМЕРИТЬ ПОС':
                    # Выбираю измерение образца сравнения
                    Controlini[Index_POS] = 'POS=1\n' # 1 - образец сравнения, 0 - проба
                    # Устанавливаю время гоности СС в 0
                    Controlini[Index_ComparisonSpectrumPeriod] = 'ComparisonSpectrumPeriod=0\n' # Время, в течение которого изменения спектра сравнения не критичны для точности анализа, сек
                    # Вношу изменения в файл
                    write_Controlini(Controlini)

                    Flag_pos = 1

                else :
                    print('Команда на измерение пос введена не верна.\nПроверьте, что у вас включен русский язык.')
        elif status == status_warm: # если прогрев, то выдаю статус
            print_time()
            print('Идет прогрев')

        else: # если статус отличен от известных, то предупреждение
            print_time()
            print('неизвестное состояние')

            count_none_status += 1
            if count_none_status > 20:
                print ('Превышено ожидание получение статуса программы GASpec')
                break

        sleep(1)

def end_of_measurement(Controlini):
    # Редактирование файла config.ini
    # Даю команду запуск измерения
    Controlini[Index_Command] = 'Command=2\n' # 1 - запуск измерения, 2 - остановка измерения, 3 - выключение ПК, 4 - выключение GASpec
    # Вношу изменения в файл
    write_Controlini(Controlini)
    # жду обработки команды GASpec
    while get_status() == status_meas or get_status() == status_meas_pos:
        sleep(1)
    # Даю команду остановка измерения
    Controlini[Index_Command] = 'Command=4\n' # 1 - запуск измерения, 2 - остановка измерения, 3 - выключение ПК, 4 - выключение GASpec
    # Вношу изменения в файл
    write_Controlini(Controlini)


# Шаг 1. Отобразить преветствие в терминал.
print('Привет, тебя приветствует программа ПАУСС версия 2.34, которая поможет тебе с GASpec.')
print('Теперь я автоматическая ^-^')
print('***************************************************************************************************')

# print('Прежде, чем запускать GASpec необходимо подождать прогревания прибора. Если же прибор предварительно прогрет, то просто закрой окно с таймером.')
# P = subprocess.Popen([Path_Timer_exe, '/START',  '/TITLE', 'Прогрев кюветы', '/TIME', '01:00:00'])
# P.wait();

CheatFlag = 0
Flag_pos = 0 # Flag_pos для измерения спектра сравнения
GASpecini = read_GASpecini()
Controlini = ['[commands]\n', '', '', '[parameters]\n', '', '', '', '', '']
Controlini = read_Controlini()

# Шаг 3. Задать вопрос оператору о начале запуска программы GASpec.
print('д - запустить GASpec и начать измерения\nп - продолжить измерения без запуска GASpec\nн - выйти из программы ПАУСС')
print('Запустить программу GASpec [д/п/н]:', end=' ')
s = input()

# Шаг 4. Запуск программы GASpec (C:\Infraspek\FSpec\FSpec.exe /mod=GASpec)
if s == 'д' or s == 'Д':
    print('Программа GASpec скоро будет запущена')
    start_congig_Control(Controlini)
    start_config_GASpec(GASpecini)
    subprocess.Popen(['C:\Infraspek\FSpec\FSpec.exe', '/mod=GASpec'])

    while Flag_pos == 0:
        print('Загрузите в кювету образец сравнения и введите команду (без ковычек) "измерить пос":', end=' ')

        s = input()
        if s == 'измерить пос' or s == 'Измерить пос' or s == 'Измерить ПОС' or s == 'Измерить Пос' or s == 'ИЗМЕРИТЬ ПОС':
            # Выбираю измерение образца сравнения
            Controlini[Index_POS] = 'POS=1\n' # 1 - образец сравнения, 0 - проба
            # Устанавливаю время гоности СС в 0
            Controlini[Index_ComparisonSpectrumPeriod] = 'ComparisonSpectrumPeriod=0\n' # Время, в течение которого изменения спектра сравнения не критичны для точности анализа, сек
            # Вношу изменения в файл
            write_Controlini(Controlini)

            Flag_pos = 1

        elif s == 'чит' or s == 'ЧИТ' or s == 'Чит':
            print('Будь как дома, путник. Я ни в чем не откажу.')
            Flag_pos = 1
            CheatFlag = 1

        else :
            print('Команда на измерение пос введена не верна.\nПроверьте, что у вас включен русский язык.')

        sleep(1)

    if CheatFlag == 1:
        Flag_pos = 0

    status = get_status()
    # ждем пока стутус прибора не станет "Готов"
    while status != status_ready:
        status = get_status()
        if status == status_error_1 or status == status_error_2:
            break
        sleep(1)

elif s == 'п' or s == 'П':
    print('Продолжаю работать с GASpec')
    status = get_status()
    if status == status_meas_pos:
        Flag_pos = 1

else:
    reset_config_GASpec(GASpecini)
    exit()

# Шаг 5. Скопировать последовательность файлов control.ini для измерения нулевого газа, затем для измерения пробы.
measurement(Flag_pos)

# Шаг 6. Завершении измерения
print('Завершаю работу программы GASpec')
Controlini = read_Controlini()
end_of_measurement(Controlini)

print('Всего доброго!')

input("Нажмите любую клавишу...")
