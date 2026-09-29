import random
import json
import os

SQUARES = ["11","12","13","21","22","23","31","32","33"]
PATH = os.path.expanduser("~/.basix/patterns.json")

if os.path.exists(PATH):
    with open(PATH, "r") as patterns:
        base = json.load(patterns)
else:
    base = {sq:[0,0] for sq in SQUARES}

MAX_BIAS = 2

#finds biggest value in each sq
max_hn = max(1, max(v[0] for v in base.values()))
max_wn = max(1, max(v[1] for v in base.values()))

#tunes each sq in choices to have a bias based on previous games. Gives a max value of MAX_BIAS
choices = [[sq,
            round(MAX_BIAS * base[sq][0] / max_hn, 2),
            round(MAX_BIAS * base[sq][1] / max_wn, 2)]
           for sq in SQUARES]
#choices = [["square",HN(hot number),WN(wanted number)]]

player_choices = []
computer_choices = []

def print_board():
    print()
    for r in "123":
        cells = []
        for c in "123":
            sq = r + c
            if sq in player_choices:
                cells.append("X")
            elif sq in computer_choices:
                cells.append("O")
            else:
                cells.append(sq)  # empty squares show their number so you know what to type
        print(" " + "|".join(f"{cell:^4}" for cell in cells))
        if r != "3":
            print(" " + "----+----+----")
    print()

def ask_player():
    while True:
        move = input("Your move (row+column, e.g. 22):\n>>>").strip()
        if find(move, choices) != -1:
            return move
        print("Invalid or already taken square. Pick one of the numbers shown on the board.")

def check_win(user_choices):
    backslash = ["11","22","33"]
    slash= ["31","22","13"]
    count_1=count_2=count_3=count21=count22=count23=backs=slas=0
    for x in user_choices:
        if x[0] == "1":
            count_1+=1
        if x[0] == "2":
            count_2+=1
        if x[0] == "3":
            count_3+=1
        if x[1] == "1":
            count21+=1
        if x[1] == "2":
            count22+=1
        if x[1] == "3":
            count23+=1
        if x in backslash:
            backs+=1
        if x in slash:
            slas+=1
    if any(var == 3 for var in (count_1,count_2,count_3,count21,count22,count23,backs,slas)):
        return True
    return False

def find(square,choices):
    for i in range(len(choices)):
        if square in choices[i]:
            return i
    return -1

def find_affected(square,chosen,user):
    backslash = ["11","33"]
    slash= ["31","13"]
    affected = []
    count_1=count_2=count_3=count21=count22=count23=backs=slas=0
    for x in range(1,4): #horizontal
        affected.append(square[0]+str(x))
    for x in range(1,4): #vertical
        affected.append(str(x)+square[1])
    if square in backslash:
        for x in range(1,4):
            affected.append(str(x)+str(x))
    elif square in slash:
        for x in range(1,4):
            affected.append(str(x)+str(4-x))
    elif square == "22":
        for x in range(1,4):
            affected.append(str(x)+str(x))
        for x in range(1,4):
            affected.append(str(x)+str(4-x))
    while square in affected:
        affected.remove(square)
    for x in chosen:
        if x[0] == "1":
            count_1+=1
        if x[0] == "2":
            count_2+=1
        if x[0] == "3":
            count_3+=1
        if x[1] == "1":
            count21+=1
        if x[1] == "2":
            count22+=1
        if x[1] == "3":
            count23+=1
        if x in backslash or x == "22":
            backs+=1
        if x in slash or x == "22":
            slas+=1
    if user=="computer":
        for i in range(2):
            if count_1 == 2:
                for x in range(1,4):
                    affected.append(str(1)+str(x))
            if count_2 == 2:
                for x in range(1,4):
                    affected.append(str(2)+str(x))
            if count_3 == 2:
                for x in range(1,4):
                    affected.append(str(3)+str(x))
            if count21 == 2:
                for x in range(1,4):
                    affected.append(str(x)+str(1))
            if count22 == 2:
                for x in range(1,4):
                    affected.append(str(x)+str(2))
            if count23 == 2:
                for x in range(1,4):
                    affected.append(str(x)+str(3))
            if backs == 2:
                for x in range(1,4):
                    affected.append(str(x)+str(x))
            if slas == 2:
                for x in range(1,4):
                    affected.append(str(x)+str(4-x))
    else:
        if count_1 == 2:
            for x in range(1,4):
                affected.append(str(1)+str(x))
        if count_2 == 2:
            for x in range(1,4):
                affected.append(str(2)+str(x))
        if count_3 == 2:
            for x in range(1,4):
                affected.append(str(3)+str(x))
        if count21 == 2:
            for x in range(1,4):
                affected.append(str(x)+str(1))
        if count22 == 2:
            for x in range(1,4):
                affected.append(str(x)+str(2))
        if count23 == 2:
            for x in range(1,4):
                affected.append(str(x)+str(3))
        if backs == 2:
            for x in range(1,4):
                affected.append(str(x)+str(x))
        if slas == 2:
            for x in range(1,4):
                affected.append(str(x)+str(4-x))
    return affected

def learn(won):
    if won == "computer":
        for sq in computer_choices:
            base[sq][1]+=1
    else:
        for sq in player_choices:
            base[sq][0]+=1
    os.makedirs(os.path.dirname(PATH), exist_ok=True)
    with open(PATH,"w") as patterns:
        json.dump(base,patterns)

print("Tic Tac Toe: you are X, the computer is O.")
print("Type the number of a free square to play there (row first, then column).")
print_board()

while True:
    #player's turn
    player = ask_player()
    player_choices.append(player)
    if check_win(player_choices):
        print_board()
        print("You won.")
        learn("player")
        break
    affected = find_affected(player,player_choices,"p")
    for square in affected:
        pos=find(square,choices)
        if pos != -1:
            choices[pos][1]=choices[pos][1]+1
    choices.pop(find(player,choices))

    #tie check: must happen after the player's square is removed
    if len(choices)==0:
        print_board()
        print("Tie.")
        break

    #computer's turn
    max_hn=max_wn=0
    same_hn=[]
    same_wn=[]
    for x in range(len(choices)):
        if choices[x][1]>max_hn:
            max_hn=choices[x][1]
        if choices[x][2]>max_wn:
            max_wn=choices[x][2]
    for x in range(len(choices)):
        if choices[x][1]==max_hn:
            same_hn.append(x)
        if choices[x][2]==max_wn:
            same_wn.append(x)
    max_hn_pos=same_hn[random.randint(0,len(same_hn)-1)]
    max_wn_pos=same_wn[random.randint(0,len(same_wn)-1)]
    if max_hn>max_wn:
        computer = choices[max_hn_pos][0]
    else:
        computer = choices[max_wn_pos][0]
    computer_choices.append(computer)
    affected = find_affected(computer,computer_choices,"computer")
    for square in affected:
        pos=find(square,choices)
        if pos != -1:
            choices[pos][2]=choices[pos][2]+1
    choices.pop(find(computer,choices))
    print("Computer's choice:",computer)
    print_board()
    if check_win(computer_choices):
        print("Computer won.")
        learn("computer")
        break
