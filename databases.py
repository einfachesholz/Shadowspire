import bcrypt # for hashing passwords
from supabase import create_client# for communicating with our superbase database

#constants we will need to setup the database connection
URL = ""
API_KEY = ""

#sets up our database connection
supabase = create_client(URL, API_KEY)

def sign_up(username, password, email):
    #we hash the password first to store     
    hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=5))
    data = {
        "username": username,
        "password": hash.decode('utf-8'), #converts bytes to characters
        "emailaddress": email
    } 
    #adds new record to the accounts databases   
    try:              
        response = supabase.table("accounts").insert(data).execute()
    except:
        return 'invalid connection'

def upsert_highscore(userid, high_score):
    #this function will either update highscore or add a new record to the leaderboard database
    check = supabase.table("leaderboard").select('userid').eq('userid', userid).execute()
    if check.data: #check.data will either be empty or have a value if the account is already in the leaderboard database
        response = (
            supabase.table("leaderboard")
            .update({'highscore': high_score})
            .eq('userid', userid) #WHERE SQL equivelent
            .execute() # executes the command
        #updates highscore 
        )
    else:
        data = {
            'userid': userid,
            'highscore': high_score
        }
        #adds new record to the leaderboard databases
        response = supabase.table("leaderboard").insert(data).execute()

def retrieve_password(username):
    #we retrieve the player's password from the accounts database
    try:
        password_data = supabase.table("accounts").select('password').eq('username', username).execute()
    except:
        return "invalid connection"
    return (password_data.data[0]['password'])

def retrieve_userdata(username):
    #retrieves the relevant data for the accounts record based on the username
    user_data = []
    #user_data will store the relevant account details such as userid
    
    userid_data = supabase.table("accounts").select('userid').eq('username', username).execute()
    #retrieves the matching userid
    userid = userid_data.data[0]['userid']
    #retreieves the player's highscore
    high_score = retrieve_highscore(userid)

    user_data.append(username)
    user_data.append(userid)
    user_data.append(high_score)

    return user_data

def check_valid_username(username):
    try:
        response = supabase.table("accounts").select('username').eq('username', username).execute()
    except:
        return "Invalid connection"

    if response.data:
        #if response.data has a value, the username is not valid
        return True
    #otherwise the username is valid
    return False

def retrieve_highscore(userid):
    #retrieves the highscore for a user 
    highscore_data = supabase.table("leaderboard").select('highscore').eq('userid', userid).execute()
    try:
        #there is already an entry for the given userid in the leaderboard database
        return (highscore_data.data[0]['highscore'])
    except:
        #there isn't an entry for the given userid, this is the first time the player is playing
        return (0)
    
def retrieve_leaderboard_data():
    rankings = []
    response = (
        #gets the top 5 accounts based on high-score
        supabase.table('leaderboard')
        .select('userid', 'highscore')
        .order('highscore', desc=True)
        .limit(5)
        .execute()
    )

    for data in response.data:
        #response.data contains arrays with a userid highscore pair
        username = supabase.table('accounts').select('username').eq('userid', data['userid']).execute() #gets the username from userid
        rankings.append([username.data[0]['username'], data['highscore']]) #adds username highscore pair to the rankings list

    return (rankings)

def check_connection():
    #checks for a valid internet connection
    try:
        response = supabase.table("accounts").select('username').execute()
        return True
    except:
        return False

