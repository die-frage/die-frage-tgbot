# 1. Проект "Die Frage"
Телеграмм чат-бот приложение для прохождения опросов

# 2. Описание

Бот обладает функционалом по приему кода опроса, регистрации пользователей и реализации самого процесса опроса.

## Сценарий

### 1. Начало диалога  

1.1 Пользователь начинает диалог с ботом, отправив команду /start.  
1.2 Бот приветствует пользователя и предлагает ввести код опроса через кнопку "Ввести код".  
1.3 Если пользователь открывает бота через специальную ссылку с кодом опроса, бот переходит к шагу 3.  

### 2. Ввод кода опроса  

2.1 Пользователь вводит код опроса.  
2.2 Бот отправляет запрос на сервер для получения информации об опросе.  
2.3 Если опрос найден (код 200), переход к шагу 3.  
2.4 Если опрос не найден, бот отправляет уведомление: " Опрос не найден, введите другой код!", и возвращает пользователя к шагу 1.  

### 3. Регистрация пользователя  

3.1. Бот отправляет сообщение о начале регистрации.  
3.2. Если опрос анонимный - шаг 3.4.  
3.3. Если опрос не анонимный:  
- Бот запрашивает у пользователя ввести ФИО.  
- Бот запрашивает у пользователя ввести почту.  
- Бот запрашивает у пользователя ввести номер группы.  

3.4. После ввода данных, бот запрашивает подтверждение, "Данные правильные?", и отправляет две кнопки "ДА" и "НЕТ".  
3.5. Если пользователь нажимает на кнопку "ДА", то сервер регистрирует пользователя на опрос.  
3.6. При успешной регистрации выводится сообщение "Регистрация прошла успешно!".  
3.7. Если пользователь нажимает на кнопку "НЕТ", то переход к шагу 3.   

### 4. Прохождение опроса  

В процессе.


# 1. Project "Die Frage"

Telegram Chat-Bot Application for Survey Participation

# 2. Description

The bot has functionality for accepting a survey code, registering users, and carrying out the survey process.

## Scenario

### 1. Starting the Dialogue

1.1 The user starts the dialogue with the bot by sending the /start command.
1.2 The bot greets the user and offers to enter the survey code via the “Enter Code” button.
1.3 If the user opens the bot through a special link with the survey code, the bot proceeds directly to Step 3.

### 2. Entering the Survey Code

2.1 The user enters the survey code.
2.2 The bot sends a request to the server to retrieve information about the survey.
2.3 If the survey is found (HTTP code 200), proceed to Step 3.
2.4 If the survey is not found, the bot sends a notification: “Survey not found, please enter another code!” and returns the user to Step 1.

### 3. User Registration

3.1 The bot sends a message about starting the registration process.
3.2 If the survey is anonymous, proceed to Step 3.4.
3.3 If the survey is not anonymous:
	•	The bot asks the user to enter their full name.
	•	The bot asks the user to enter their email address.
	•	The bot asks the user to enter their group number.
3.4 After entering the data, the bot asks for confirmation: “Are the details correct?” and provides two buttons: “YES” and “NO.”
3.5 If the user clicks “YES,” the server registers the user for the survey.
3.6 Upon successful registration, the bot displays the message: “Registration completed successfully!”
3.7 If the user clicks “NO,” return to Step 3.

### 4. Completing the Survey

In progress.
