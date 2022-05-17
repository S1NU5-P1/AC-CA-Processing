import os
import pyaudio

import ac_ca_processing as ac
from rich import print
from rich.prompt import Prompt as prompt
import threading


def cls():
	os.system('cls' if os.name == 'nt' else 'clear')


def main():
	port = 2137
	ip = "192.168.0.18"
	audio_setup = (1024, pyaudio.paInt16, 2, 44100)
	user_choice = ''
	while user_choice != 'q':
		cls()
		print(f"IP:PORT\n\t{ip}:{port}")
		print(audio_setup_to_string(audio_setup), "\n")
		print("Wybierz opcję:",
			  "(0) Tryb Setup (podaj wszystko i połącz)",
			  "(1) Podaj parametry audio",
			  "(2) Podaj parametry przesyłu (port i adres hosta)",
			  "(3) Rozpocznij połączenie", 
			  "\[q - wyjście]", sep="\n\t")
		user_choice = input("> ")
		match user_choice:
			case '0':
				audio_setup = get_audio_parameters(audio_setup)
				ip, port = get_transmission_parameters(ip, port)
				begin_transmission(port, ip, audio_setup)
			case '1':
				audio_setup = get_audio_parameters(audio_setup)
			case '2':
				ip, port = get_transmission_parameters(ip, port)
			case '3':
				begin_transmission(port, ip, audio_setup)
			case _:
				continue

def audio_setup_to_string(audio_setup: tuple[int, int, int, int]):
	chunk, input_format, channel_number, rate = audio_setup
	return f"Rozdzielczość: {chunk}\n" +\
		   f"Format wejściowy: {input_format}\n" +\
		   f"Liczba kanałów: {channel_number}\n" +\
		   f"Próbkowanie: {rate}"

def get_audio_parameters(audio_setup: tuple[int, int, int, int]):
	chunk, input_format, channel_number, rate = audio_setup
	chunk = int(prompt.ask("Podaj rozdzielczość", default=str(chunk)))

	audio_input_formats = [pyaudio.paInt8, pyaudio.paInt16, pyaudio.paInt24, pyaudio.paInt32]
	print(f"Podaj format wejściowy:",
		   "(1) Int8",
		   "(2) Int16",
		   "(3) Int24",
		   "(4) Int32", sep="\n")
	input_format = int(prompt.ask("", default=str(audio_input_formats.index(input_format)+1)))
	input_format = audio_input_formats[input_format-1]
	
	channel_number = int(prompt.ask(
		"Wprowadź liczbę kanałów",
		choices=["1", "2"],
		default=str(channel_number)))

	rate = int(prompt.ask("Podaj częstotliwość próbkowania", default=str(rate)))

	return (chunk, input_format, channel_number, rate)


def get_transmission_parameters(ip, port):
	ip   = prompt.ask("Podaj adres ip", default=ip)
	port = int(prompt.ask("Podaj port", default=str(port)))
	return (ip, port)


def begin_transmission(port, ip, audio_setup: tuple[int, int, int, int]):
	sender_thread = threading.Thread(target=ac.send_audio, args=(audio_setup, (ip, port)))
	receiver_thread = threading.Thread(target=ac.receive_audio, args=(audio_setup, port))

	try:
		print("[ Wciśnij Ctrl+C by przerwać ]")
		receiver_thread.start()
		input("Naciśnij enter aby rozpocząć połączenie")
		sender_thread.start()
	except KeyboardInterrupt:
		input("Przerwano połączenie. Naciśnij dowolny klawisz, by kontynuować...")


if __name__ == '__main__':
	main()
