from kicktippbb import main

arguments_login = {
    '--deadline': None,
    '--dry-run': False,
    '--get-login-token': True,
    '--list-predictors': False,
    '--matchday': None,
    '--override-bets': False,
    '--predictor': None,
    '--use-login-token': None,
    'COMMUNITY': ['ludewigs']
}

arguments = {
    '--deadline': None,
    '--dry-run': False,
    '--get-login-token': False,
    '--list-predictors': False,
    '--matchday': None,
    '--override-bets': True,
    '--predictor': 'SimplePredictor',
    '--use-login-token': 'a29ydy55cmFybyU0MGdtYWlsLmNvbToxNjk5NDMzNTMxODU3OjgzNWEzYmVkMTFhM2RiM2RkZGEwODk1YThjYzA0NmEz',
    'COMMUNITY': ['ludewigs']
}

if __name__ == '__main__':
    main(arguments)