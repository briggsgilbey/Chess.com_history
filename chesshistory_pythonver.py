#Goals
#Collect all of my game data (Done)
#Sort the games for my colour piece to list my colour piece and my elo (Done)
#Sort data into tables (Done)
#Plot elo data as a graph, using my game number/ date as the y axis (Done).




import requests
import json
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import chess.pgn, chess.polyglot
import io
import numpy as np
import re


me = "https://api.chess.com/pub/player/bigbadbege"
allgames = "https://api.chess.com/pub/player/bigbadbege/games/live/600/0"
url = "https://api.chess.com/pub/player/bigbadbege/games/2025/03"
headers = {'User-Agent':'header'}
username = input("Please enter your chess.com username")
df = pd.DataFrame()
i = 0

def month_and_year_data(df, i):
    archive_list = "https://api.chess.com/pub/player/" + username + "/games/archives"
    retrieve_data(df, i, archive_list)




def retrieve_data(df, i, archive_list):
    response = requests.get(url=archive_list, headers=headers)
    data = response.json()
    
    if i < len(data["archives"]):
        response2 = requests.get(url=data["archives"][i], headers=headers)
        data2 = response2.json()
        games = data2["games"]
        i = i + 1
          

    games_pgn=[]
    for game in games:
        pgn = (game['pgn'])
        pgn = io.StringIO(pgn)
        game = chess.pgn.read_game(pgn)
        games_pgn.append(game)

    games_list=[]
    for x in games_pgn:
        time_control = (x.headers['TimeControl'])
        if time_control == "600": 
            moves = (x.mainline_moves())
            moves = [str(y) for y in moves]


            white = (x.headers['White'])
            if white.lower() == username.lower():
                piece_colour = "white"
                elo = "WhiteElo"
                
            else:
                piece_colour = "black"
                elo = "BlackElo"

            eco = re.split("/(?=[/])|(?<=[/])",(x.headers['ECOUrl']))
            eco = eco[5]
            if len(re.split("/(?=[-])|(?<=[-])", eco)) >= 3:
                eco = eco.split("-")
                opening_name = eco[0] + " " + eco[1] + " " + eco[2] 
            elif len(re.split("\w[-]", eco)) == 2: 
                eco = eco.split("-")
                opening_name = eco[0] + " " + eco[1]
            else:
                opening_name = eco[0]
                #could rename this to "Non Standard Opening"

            if len(moves)>1:
            
                if piece_colour == "white":
                    first_move = re.split("\w[0-9]", moves[0], maxsplit=1)
                    move_made = re.split("\w[0-9]", moves[1], maxsplit=1)
                    response = move_made[1]
                
                else:
                    first_move = re.split("\w[0-9]", moves[1], maxsplit=1)
                    if len(moves) >= 3:
                        move_made = re.split("\w[0-9]", moves[2], maxsplit=1)
                        response = move_made[1]
                    else:
                        response = ""
                
            else:
                response = ""   
            
            
            game = {"Date": (x.headers["Date"]), "player_white": white, "player_black": (x.headers['Black']), 
                    "Piece_Colour": piece_colour, "Result": (x.headers['Result']), "Termination": (x.headers["Termination"]),
                    "Moves": moves, "First_move": first_move[1], "Response":response, "Opening": opening_name, "Elo":(x.headers[elo])}
        games_list.append(game)
    games_df = pd.DataFrame(games_list)


    if i == len(data["archives"]):
        multiple_months(df, games_df, True, i)

        
    else:
        multiple_months(df, games_df, False, i)



def multiple_months(df, dfs, end, i):
    df = pd.concat([df, dfs], ignore_index = True)

    if end == True:
        ignored_colums(df)
        
        
    else:
        month_and_year_data(df, i)



def ignored_colums(df):
    df = df.drop(["player_white", "player_black","Moves"], axis =1)    
    print("Dropped columns")
    elo_change(df)

def elo_change(df):
    df['Elo'] = df['Elo'].dropna().astype(int)
    df['Elo_Change'] = df.Elo - df.Elo.shift()
    df['Elo_Change'] = df['Elo_Change'].dropna().astype(int)
    #df = df.applymap(lambda x: "+"+ int(df['Elo_Change']) if df['Elo_Change']> 0 else x)
    #df.style.format(lambda x:   'NaN' if np.isnan(x) else '{:+g}'.format(x))
    show_result(df)

def show_result(df):
    conditions = \
    [(df["Piece_Colour"] == "white") & (df["Result"] == "1-0"),
    (df["Piece_Colour"] == "white") & (df["Result"] == "0-1"),
    (df["Piece_Colour"] == "white") & (df["Result"] == "1/2-1/2"),
    (df["Piece_Colour"] == "black") & (df["Result"] == "0-1"),
    (df["Piece_Colour"] == "black") & (df["Result"] == "1-0"),
    (df["Piece_Colour"] == "black") & (df["Result"] == "1/2-1/2")]

    values = ["Win", "Loss","Draw", "Win", "Loss", "Draw"]
    df['My_Result'] = np.select(conditions, values, default=np.str_)
    print("Win/Loss/Draws added")
    export_data(df)
    #plot_elo(df)


def export_data(df):
    print("Exporting Data")
    df.to_csv('Chess_Data.csv')
    quit()
   


   

#next, plot data using matplotlib
def plot_elo(df):
    print("Plotting chart")
    #plt.bar(df.index.values, df['Elo'])
    plt.plot(df.index.values, df['Elo'])
    plt.ylabel("Elo")
    plt.xlabel("Game Number")
    plt.ylim(600,2000)      
    plt.show()
    quit()

month_and_year_data(df, i)

'''


