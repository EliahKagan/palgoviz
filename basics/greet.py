#!/usr/bin/env python

"""Hello world example."""


def hello(name, lang='en'):
    """Greet the user."""
    if lang == 'en': 
        print(f'Hello, {name}!')  # fstring demonstration
    elif lang == 'es':
        print(f'¡Hola, {name}!')  # fstring demonstration en español
    else:
        raise ValueError(f'{lang} is an unrecognized language code')


def run():
    """Run as a script."""
    print('¿Como se llama usted?')
    name = input()
    hello(name, 'es')


if __name__ == '__main__':  # If we are running this module as a script.
    run()
