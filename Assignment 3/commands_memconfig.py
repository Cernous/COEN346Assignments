def readCommandsFile(commands_path:str):

    #Returns list of commands: ['Command name', 'First value', 'Second value (if applicable)']
    f = open(commands_path, 'r')
    commands = [s.strip() for s in f.read().splitlines()]

    for i, value in enumerate(commands):
        command = value.split(' ')
        if command[0] == 'Store':
            command[2] == int(command[2])
        
        commands[i] = command

    return commands

def readMemConfigFile(memconfig_path:str):
    f = open(memconfig_path, 'r')
    memconfig = [s.strip() for s in f.read().splitlines()]

    return int(memconfig[0])

# print(readMemConfigFile("Assignment 3/memconfig.txt"))