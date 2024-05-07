def migrate_concelhos():

    
    for concelho in concelhos:
        concelho = concelho.strip()
        if concelho:
            concelho = concelho.title()
            concelho = concelho.replace(' De ', ' de ')
            concelho = concelho.replace(' Do ', ' do ')
            concelho = concelho.replace(' Da ', ' da