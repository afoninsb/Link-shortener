#!/bin/sh
echo "##### НАЧИНАЕМ РАБОТУ #####"
echo "### 1. Выполняем миграции ###"
sudo docker-compose exec web alembic upgrade head
echo "!!! Миграции выполнены"
echo " "
echo "??? 2. Будем выполнять тесты сейчас? ('Д/н' или 'Y/n' ) "
read yesno
if [ "$yesno" = "д" ] || [ "$yesno" = "y" ] || [ "$yesno" = "" ] || [ "$yesno" = "Y" ] || [ "$yesno" = "Д" ]
then
	echo "### Выполняем тесты ###"
	sudo docker-compose exec web python -m pytest ./tests -ra -q
	echo " "
	echo "!!! Тесты завершены"
else
	echo "Когда решите провести тестирование, отправьте команду:"
	echo "sudo docker-compose exec web python -m pytest ./tests -ra -q"
fi
echo " "
echo "##### РАБОТА ЗАВЕРШЕНА #####"
