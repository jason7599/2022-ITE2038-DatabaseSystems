import pymysql;
import os;
from datetime import datetime, timedelta;

connection = pymysql.connect(host = "localhost",
                             user = "root",
                             password = "iaomai7599!@#",
                             database = "ourtube",
                             charset = "utf8mb4");

cursor = connection.cursor(pymysql.cursors.DictCursor);
cursor.execute("use ourtube;");

USERID = None;
ADMIN = False;

def clear(string = None):
    os.system("cls");
    if string: print(string);
    return;

def menu():

    clear();

    while True:

        if ADMIN:
            print();
            print("+-<WELCOME TO OURTUBE>----------------+");
            print("| Enter 1 to search for videos/users. |");
            print("| Enter 2 to check reports.           |");
            print("| Enter 3 to manage categories.       |");
            print("| Enter 4 to add a new admin account. |");
            print("| Enter 5 to log out.                 |");
            print("| Enter 6 to exit OurTube.            |");
            print("+-------------------------------------+");
            
            try: cmd = int(input("\nEnter: "));
            except: clear("Invalid command."); continue;

            if cmd == 1: search();
            elif cmd == 2: checkNewReports();
            elif cmd == 3: manageCategories();
            elif cmd == 4: adminSignUp();
            elif cmd == 5: logOut();
            elif cmd == 6: break;
            else: clear("Invalid command.");

        elif USERID:
            print();
            print("+-<MENU>------------------------------+");
            print("| Enter 1 to search for videos/users. |");
            print("| Enter 2 to check for notifications. |");
            print("| Enter 3 to upload a video.          |");
            print("| Enter 4 to manage your channel.     |");
            print("| Enter 5 to manage your account.     |");
            print("| Enter 6 to contact admins.          |");
            print("| Enter 7 to log out.                 |");
            print("| Enter 8 to exit OurTube.            |");
            print("+-------------------------------------+")

            try: cmd = int(input("\nEnter: "));
            except: clear("Invalid command."); continue;

            if cmd == 1: search();
            elif cmd == 2: checkNewNotifications();
            elif cmd == 3: uploadVideo();
            elif cmd == 4: manageChannel();
            elif cmd == 5: manageAccount();
            elif cmd == 6: listAdmins();
            elif cmd == 7: logOut();
            elif cmd == 8: break;
            else: clear("Invalid command.");

        else: # not logged in
            print();
            print("+-<WELCOME TO OURTUBE>----------------+");
            print("| Enter 1 to log in.                  |");
            print("| Enter 2 to sign up.                 |");
            print("| Enter 3 to search for videos/users. |");
            print("| Enter 4 to exit OurTube.            |");
            print("+-------------------------------------+");
            
            try: cmd = int(input("\nEnter: "));
            except: clear("Invalid command."); continue;

            if cmd == 1: logIn();
            elif cmd == 2: signUp();
            elif cmd == 3: search();
            elif cmd == 4: break;
            else: clear("Invalid command.");

    connection.close();

def logIn():
    global USERID;

    clear();

    while True:
        print("\n<LOG IN> Enter #EXIT to go back to the menu screen.");

        username = input("\nEnter your username: ");
        clear();

        if username == "#EXIT": return;
        if username == "#ADMIN": return adminLogIn();
        
        cursor.execute("""select userid, userpw from ouser where username = %s;""", username);
        res = cursor.fetchone();
        if res is None:
            print(f"User <{username}> does not exist. Please try again.");
            continue;

        password = input(f"Enter password for {username}: ");
        clear();

        if password == "#EXIT": return;

        if res["userpw"] == password:
            
            # check if banned
            cursor.execute("""select * 
                            from banneduserinfo 
                            where userid = %s and (expiretime is null or expiretime > now())
                            limit 1;"""
                            , res["userid"]);
            bannedInfo = cursor.fetchone();

            if bannedInfo:
                if bannedInfo["expiretime"]: 
                    print(f"Account {username} has been banned until {str(bannedInfo['expiretime'])}.");
                else: # perma ban
                    print(f"Account {username} has been banned permanently.");
                    
                print(f"Reason for this ban: {bannedInfo['reason']}");

                cursor.execute("select adminname from oadmin where adminid = %s;", bannedInfo["adminid"]);
                adminName = cursor.fetchone()["adminname"];

                print(f"This ban was carried out by admin {adminName}.");
                return;

            print(f"\nSuccessfully logged in. Welcome {username}!");
            USERID = int(res["userid"]);
            return;

        print("Invalid password. Please try again.");

def logOut():
    global USERID;
    global ADMIN;

    USERID = None;
    ADMIN = False;

    clear("Successfully logged out.");

    return;

def adminLogIn():
    global ADMIN;
    global USERID;

    clear();

    name = input();
    pw = input();

    cursor.execute("select adminid from oadmin where adminname = %s and adminpw = %s;", (name, pw));
    res = cursor.fetchone();

    clear();

    if res:
        ADMIN = True;
        USERID = res["adminid"];
        print("ACCESS GRANTED: ENTERING ADMIN MODE");
    else: print("ACCESS DENIED");
  
def signUp():

    clear();

    while True:
        print("\n<SIGN UP> Enter #EXIT to go back to the menu screen.");

        username = input("\nEnter your username: ");
        clear();

        if username == "#EXIT":return;

        cursor.execute("select exists(select username from ouser where username = %s) as chck;", username);
        if cursor.fetchone()["chck"]:
            print(f"Username <{username}> already taken. Please try another username.");
            continue;

        password = input("Enter your password: ");
        clear();

        if password == "#EXIT": return;

        cursor.execute("insert into ouser (username, userpw) values (%s, %s);", (username, password));
        connection.commit();

        print("Successfully created account.");

        return;

def adminSignUp():

    clear();

    while True:
        print("\n<CREATE NEW ADMIN ACCOUNT> Enter #EXIT to go back.");

        name = input("\nEnter the name for this admin: ");
        clear();

        if name == "#EXIT": return;

        cursor.execute("select exists(select adminname from oadmin where adminname = %s) as chck;", name);
        if cursor.fetchone()["chck"]:
            print(f"Admin name <{name}> already taken.");
            continue;

        password = input(f"Enter password for admin <{name}>: ");
        clear();

        if password == "#EXIT": return;

        cursor.execute("insert into oadmin (adminname, adminpw) values (%s, %s);", (name, password));
        connection.commit();

        print("Successfully created admin account.");

        return;

# int
def selectCategory(allowNonLeafNodes = False, header = "<SELECT CATEGORY>", parentID = None, path = "Categories"):

    clear();

    categoryName = "ROOT";

    if not parentID: # init
        cursor.execute("select * from category where subcategoryof is null;");
    else:
        cursor.execute("select categoryname from category where categoryid = %s;", parentID);
        categoryName = cursor.fetchone()["categoryname"];
        cursor.execute("select * from category where subcategoryof = %s;", parentID);

    res = cursor.fetchall(); # get child categories of parent

    while True:
        print(header);
        print('\n',path,'\n');

        if len(res): # non leaf category
            index = 1;
            for row in res:
                print(f"{index :<4}{row['categoryname']}");
                index += 1;
            print("\nEnter index of a category to view.");

        # can select any category in create mode
        # in select mode, can only choose from leaf categories
        if allowNonLeafNodes or not len(res):
            print(f"Enter 0 to select this category ({categoryName})");

        if parentID:
            print("Enter -1 to go back a page.");

        else: print("Enter -1 to exit.");

        cmd = int(input("\nEnter: "));

        if cmd == -1:
            clear();
            return 0;

        if cmd == 0:
            clear(); 
            if not allowNonLeafNodes and len(res):
                print("You must select from leaf categories.");
                continue;
                
            return parentID;

        newParentID = res[cmd - 1]["categoryid"];
        newPath = path + "> " + res[cmd - 1]["categoryname"];

        temp = selectCategory(allowNonLeafNodes, header, newParentID, newPath);

        if temp: return temp; # selected

# list of categoryids(ints)
def getAllLeafCategoriesOf(parentID):

    if parentID is None: # start from root
        cursor.execute("""select categoryid
                          from category
                          where subcategoryof is null;""");
    
    else: cursor.execute("""select categoryid 
                            from category 
                            where subcategoryof = %s;"""
                            , parentID);

    children = cursor.fetchall();

    # leaf
    if not children: return [parentID];

    # non leaf
    res = [];
    for child in children:
        res.extend(getAllLeafCategoriesOf(child["categoryid"]));
    
    return res;

def search():

    clear();

    while True:
        print();
        print("+-<SEARCH>------------------------+");
        print("| Enter 1 to search videos.       |");
        print("| Enter 2 to search users.        |");
        print("| Enter 3 to exit search.         |");
        print("+---------------------------------+");

        try: cmd = int(input("\nEnter: "));
        except:
            clear("Invalid command.");
            continue;

        if cmd == 1:

            clear();

            while True:
                print();
                print("+-<SEARCH VIDEOS>----------------------------+");
                print("| Enter title to search.                     |");
                print("| Enter * to list all videos.                |");
                print("| Enter #CAT to search videos by category.   |");
                if USERID and not ADMIN:
                    print("| Enter #REC for video recommendations.      |");
                print("| Enter #ADV to enter advanced search mode.  |");
                print("| Enter #EXIT to go back to the search menu. |");
                print("+--------------------------------------------+");

                cmd = input("\nEnter: ");
                clear();

                if cmd == "#EXIT": break;

                elif cmd == "#CAT":

                    # can select non leaf categories
                    category = selectCategory(True);
                    if category == 0: continue; # cancel

                    if not category: cmd = "*"; # redirect to search all

                    else: # remove [ and ]
                        subCategories = str(getAllLeafCategoriesOf(category))[1:-1];

                        query = f"""select videoid, title, uploader, username, uploadtime, viewcount
                                    from video, ouser
                                    where uploader = userid and categoryof in ({subCategories})
                                    order by viewcount desc;""";

                        cursor.execute("select categoryname from category where categoryid = %s;", category);
                        categoryName = cursor.fetchone()["categoryname"];

                        listVideos(query, (), "view", f"Videos under category {categoryName}:");

                        continue;

                if cmd == "*":
                    listVideos("""select videoid, title, uploader, username, uploadtime, viewcount
                        from video, ouser 
                        where uploader = userid
                        order by viewcount desc;""", (), "view", "List of all videos:");

                elif cmd == "#REC" and USERID and not ADMIN: recommendVideos();
                elif cmd == "#ADV": advancedVideoSearch();

                else: listVideos("""select videoid, title, uploader, username, uploadtime, viewcount
                        from video, ouser
                        where uploader = userid and title like %s
                        order by viewcount desc""", f"%{cmd}%", "view", f"Video search result for {cmd}:");

        elif cmd == 2:

            clear();
            
            while True:
                print();
                print("+-<SEARCH USERS>-----------------------------+");
                print("| Enter username to search.                  |");
                print("| Enter * to list all users.                 |");
                print("| Enter #EXIT to go back to the search menu. |");
                print("+--------------------------------------------+");

                cmd = input("\nEnter: ");

                if cmd == "#EXIT":
                    clear();
                    break;
                
                if cmd == '*':
                    listUsers("""select userid, username, subcount 
                        from ouser 
                        order by subCount desc, username;""", (), "List of all users:");
                else:
                    listUsers("""select userid, username, subcount 
                        from ouser 
                        where username like %s 
                        order by subCount desc, username;""", "%"+cmd+"%", f"User search result for {cmd}:");

        elif cmd == 3: 
            clear();
            return;

        else: clear("Invalid command.");

def advancedVideoSearch():

    clear();

    searchKey = None;
    categoryID = None;
    categoryName = "All";
    after = None;
    before = None;
    sortBy = None;
    desc = None;
    hideAlreadySeen = False;

    while True:
        # uploadtime range, category, sort by (title, uploadtime, viewcount)

        header="\n+-<SEARCH PARAMETERS>-----------------------+\n";
        header+=f"| Search key: {searchKey if searchKey else 'None' :<29} |\n";
        header+=f"| Under category: {categoryName :<25} |\n";
        header+=f"| Uploaded between: {(after if after else '____-__-__') + ' ~ ' + (before if before else '____-__-__') :<23} |\n";
        header+=f"| Sort by: {sortBy + (' desc' if desc else ' asc') if sortBy else 'None' :<32} |\n";
        header+=f"| Hide already seen videos: {str(hideAlreadySeen) :<15} |\n";
        header+= "+-------------------------------------------+";

        print(header, '\n');

        print( "+-------------------------------------------+");
        print( "| Enter 1 to change the search key.         |");
        print( "| Enter 2 to change the category.           |");
        print( "| Enter 3 to change the upload period.      |");
        print( "| Enter 4 to change the sorting criteria.   |");
        print(f"| Enter 5 to {('un-' if hideAlreadySeen else '') + 'hide already seen videos.' :<30} |");
        print( "| Enter 6 to execute search.                |");
        print( "| Enter 7 to exit advanced search.          |");
        print( "+-------------------------------------------+");

        try: cmd = int(input("\nEnter: "));
        except:
            clear("Invalid command.");
            continue;
        
        if cmd == 1:
            clear();
            key = input("\nEnter search key, or blank to set none: ");
            if len(key): searchKey = key;
            else: searchKey = None;
            clear();
            continue;

        elif cmd == 2:
            cat = selectCategory(True);
            if cat == 0: continue; # cancelled 
            if cat is None:
                categoryID = None;
                categoryName = "All";
                continue;

            cursor.execute("select categoryname from category where categoryid = %s;", cat);
            categoryName = cursor.fetchone()["categoryname"];
            categoryID = cat;

            continue;
        
        elif cmd == 3:
            clear("\nEnter in format of 'yyyy-mm-dd', or blank to set none.\n");
            af = input("Search videos uploaded after: ")
            if len(af): after = af;
            else: after = None;

            clear("\nEnter in format of 'yyyy-mm-dd', or blank to set none.\n");
            bf = input("Search videos uploaded before: ")
            if len(bf): before = bf;
            else: before = None;

            clear();
            continue;

        elif cmd == 4:
            clear();

            while True:
                print();
                print("+-<SET SORTING CRITERIA>----------+");
                print("| Enter 1 to sort by title.       |");
                print("| Enter 2 to sort by view count.  |");
                print("| Enter 3 to sort by upload time. |");
                print("| Enter 4 to set none.            |");
                print("+---------------------------------+");

                try: cmdd = int(input("\nEnter: "));
                except:
                    clear("Invalid command.");
                    continue;

                if cmdd == 1: sortBy = "title";
                elif cmdd == 2: sortBy = "viewcount";
                elif cmdd == 3: sortBy = "uploadtime";
                elif cmdd == 4:
                    sortBy = None;
                    break;
                else:
                    clear("Invalid command.");
                    continue;

                while True:
                    clear();
                    print("+-<SET SORTING CRITERIA>---------------+");
                    print("| Enter 1 to sort in ascending order.  |");
                    print("| Enter 2 to sort in descending order. |");
                    print("+--------------------------------------+");

                    try: cmdd = int(input("\nEnter: "));
                    except:
                        clear("Invalid command.");
                        continue;

                    if 0 < cmdd < 3:
                        desc = cmdd == 2;
                        break;
                    else:
                        clear("Invalid command.");
                        continue;

                break;

            clear();
            continue;

        elif cmd == 5:
            clear();
            if not USERID or ADMIN:
                print("This feature is for users of OurTube only.");
                continue;

            hideAlreadySeen = not hideAlreadySeen;
            continue;

        # execute
        elif cmd == 6:

            query = """select videoid, title, uploader, username, uploadtime, viewcount
                        from video, ouser
                        where uploader = userid
                        """;
            keys = ();

            if searchKey:
                query += "and title like %s ";
                keys = f"%{searchKey}%";
      
            if categoryID:
                categories = str(getAllLeafCategoriesOf(categoryID))[1:-1];
                query += f"and categoryof in ({categories}) ";
 
            if before or after:
                if after: query += f"and '{after}' <= uploadtime ";
                if before: query += f"and uploadtime <= '{before + ' 23:59:59'}' ";

            if hideAlreadySeen:
                query += f"""and videoid not in (
                                    select vidid
                                    from viewed
                                    where viewer = {USERID})"""

            query += "\n";

            if sortBy: 
                query += f"order by {sortBy}";
                if desc: query += " desc";
            
            query += ";";

            listVideos(query, keys, "view", header);

        elif cmd == 7:
            clear();
            return;

        else: clear("Invalid command.");

def recommendVideos():

    clear();

    while True:

        print();
        print( "+-<VIDEO RECOMMENDATIONS>-------------------+");
        print( "| Enter 1 for personalized recommendations. |");
        print( "| Enter 2 to list trending videos.          |");
        print( "| Enter 3 to go back to the search menu.    |");
        print( "+-------------------------------------------+");

        try: cmd = int(input("\nEnter: "));
        except:
            clear("Invalid command.");
            continue;

        clear();

        # personalized
        if cmd == 1:

            while True:

                cursor.execute("""select * from (
                                    select viewer, categoryid, (sum(rated)+1)*sum(tally) as score
                                    from viewed, video, category
                                    where viewer = %s and vidid = videoid and categoryof = categoryid
                                    group by viewer, categoryid
                                    order by score desc
                                    limit 5) temp
                                where score > 0;""", USERID);
                scoreBoard = cursor.fetchall();

                length = len(scoreBoard);

                if not length:
                    print("Sorry, we couldn't quite grasp which categories you prefer.");
                    print("Try leaving likes on videos you enjoy for better results.");
                    break;

                exitFlag = False;

                while True:

                    print("Based on your like history, we think you enjoy these categories:\n");

                    catIDs = [0 for i in range(length)];
                    catNames = ["" for i in range(length)];

                    print("+-<SCOREBOARD>-------------------------------------+");
                    for i in range(length):
                        catIDs[i] = scoreBoard[i]["categoryid"];
                        cursor.execute("select categoryname from category where categoryid = %s;", catIDs[i]);
                        catNames[i] = cursor.fetchone()['categoryname'];

                        print(f"| {i + 1}. {catNames[i] :<10} {'score: ' + str(scoreBoard[i]['score']) :>34} |");
                    print("+--------------------------------------------------+");
                    
                    print("+--------------------------------------------------+");
                    print("| Enter #BROWSE to browse from these categories.   |");
                    print("| Enter #REF to refresh the scoreboard.            |");
                    print("| Enter #EXIT to go back.                          |");
                    print("|                                                  |");
                    print("| * Videos you've already seen will not be shown.  |");
                    print("+--------------------------------------------------+");

                    cmdd = input("\nEnter: ");
                    clear();

                    if cmdd == "#BROWSE":
                        listVideos(f"""select videoid, title, uploader, username, uploadtime, viewcount
                                        from video, ouser
                                        where uploader = userid and categoryof in ({str(catIDs)[1:-1]})
                                        and videoid not in (
                                                select vidid
                                                from viewed
                                                where viewer = {USERID}
                                            )
                                        order by viewcount desc;""" , ()
                                        , "view", "Videos just for you:");


                    elif cmdd == "#EXIT":
                        exitFlag = True;
                        break;
                    
                    elif cmdd == "#REF": break;

                if exitFlag: break;

        # trending videos
        elif cmd == 2:
            while True:
                print();
                print("+-<TRENDING VIDEOS>--------------------------------+");
                print("| Enter 1 to list trending videos of today.        |");
                print("| Enter 2 to list trending videos of the week.     |");
                print("| Enter 3 to list trending videos of the month.    |");
                print("| Enter 4 to list trending videos of the year.     |");
                print("| Enter 5 to list trending videos of all time.     |");
                print("| Enter 6 to go back.                              |");
                print("+--------------------------------------------------+");

                try: cmdd = int(input("\nEnter: "));
                except: 
                    clear("Invalid command.");
                    continue;
                clear();

                if cmdd == 6: break;

                query = """select videoid, title, uploader, username, uploadtime, viewcount
                        from video, ouser """;

                today = datetime.today().date();
                after = None;
                header = "Trending videos of ";
                # today
                if cmdd == 1:
                    after = today;
                    header += "today:";
                # the week
                elif cmdd == 2:
                    after = today - timedelta(days= datetime.weekday(today));
                    header += "the week:";
                # the month
                elif cmdd == 3:
                    after = today.replace(day = 1);
                    header += "the month:";
                # the year
                elif cmdd == 4:
                    after = today.replace(month = 1, day = 1);
                    header += "the year:";
                # all time: no need to reference viewed, just order by viewcount;
                elif cmdd == 5:
                    header += "all time:";
                else: 
                    print("Invalid command.");
                    continue;
                    
                if after: query += f""", (select vidid, sum(tally) as k
                                        from viewed
                                        where lastviewed >= '{str(after)}'
                                        group by vidid) temp """;

                query += "where uploader = userid ";
                if after: query += "and videoid = vidid order by k desc;";
                else: query += "order by viewcount;";

                listVideos(query, (), "view", header);

        elif cmd == 3: return;

def listUsers(query, keys, header):
    
    clear();

    index = 0;
    update = False;

    while True:

        cursor.execute(query, keys);    
        res = cursor.fetchall();
        size = len(res);

        if size == 0: 
            clear("\nNo results.");
            return update;

        while True:
            print(header);

            print(f"\nPage {index // 20 + 1} of {(size - 1) // 20 + 1} [{size} result(s)]");
            print("+-----------------------------------------------------+");
            for n in range(20):
                if index + n == size: break;
                name = res[index + n]["username"];
                subCount = res[index + n]["subcount"];
                print(f"| {index + n + 1 :<4}{name :<20}{subCount :>15} subscribers |");
            print("+-----------------------------------------------------+\n");
            
            print("+-----------------------------------------------------+");
            print("| Enter an index of a user to view their user info.   |");
            if index != 0:
                print("| Enter #PREV to view the previous page.              |");
            if index + 20 < size:
                print("| Enter #NEXT to view the next page.                  |");
            if size > 20:
                print("| Enter #(pagenum) to jump to that page.              |");
            print("| Enter #EXIT to exit.                                |");
            print("+-----------------------------------------------------+");

            cmd = input("\nEnter: ");
            clear();

            if cmd == "#EXIT": return update;

            if cmd == "#PREV" and index != 0: 
                index -= 20;
                continue;

            if cmd == "#NEXT" and index + 20 < size: 
                index += 20;
                continue;
            
            if cmd[0] == '#':
                try: index = (int(cmd[1:]) - 1) * 20;
                except: print("Invalid page number.");
                continue;

            try: cmd = int(cmd);
            except:
                print("Invalid command.");
                continue;
            
            if cmd <= 0 or cmd > size: 
                clear("Invalid index.");
                continue;
            
            # caller: manageChannel -> list subscribed channels
            # if update at viewAccount, must update list(res) as well
            if viewAccount(res[cmd-1]["userid"]):
                update = True;
                break; # refresh

# boolean
def listVideos(query, keys, mode, header):

    clear();

    index = 0;
    update = False;

    while True:

        cursor.execute(query, keys);
        res = cursor.fetchall();
        size = len(res);

        if size == 0:
            print("\nNo results.");
            return;

        while True:
            print(header);

            print(f"\nPage {index // 10 + 1} of {(size - 1) // 10 + 1} [{size} result(s)]");
            print("+-----------------------------------------------------------------------+"); # 71 + 2
            for n in range(10):
                if index + n == size: break;

                title = res[index + n]["title"];
                viewCount = res[index + n]["viewcount"];
                uploader = res[index + n]["username"];
                uploadTime = res[index + n]["uploadtime"];

                cursor.execute("""select categoryname
                                from category, video
                                where videoid = %s and categoryof = categoryid;"""
                                , res[index + n]["videoid"]);
                category = cursor.fetchone()["categoryname"];

                print(f"| {index + n + 1 :<4}{title :<65} |");
                print(f"| {'Category: ' + category + ', ' + str(viewCount) :>63} views |"); 
                print(f"| {'uploaded at ' + str(uploadTime) + ' by ' + uploader :>69} |");
                print("+-----------------------------------------------------------------------+");

            print();
            print("+-----------------------------------------------------------------------+");
            if mode != "restrict":
                print("| Enter an index of a video to select.                                  |");
            if mode == "manage":
                print("| Enter #NEW to upload a new video.                                     |");
            if index != 0:
                print("| Enter #PREV to view the previous page.                                |");
            if index + 10 < size:
                print("| Enter #NEXT to view the next page.                                    |");
            if size > 10:
                print("| Enter #(pagenum) to jump to that page.                                |");
            print("| Enter #EXIT to exit.                                                  |");
            print("+-----------------------------------------------------------------------+");


            cmd = input("\nEnter: ");
            clear();

            if mode == "manage" and cmd == "#NEW":
                if uploadVideo():
                    update = True;
                    break;

            if cmd == "#EXIT": return update;

            if cmd == "#PREV": 
                index -= 10;
                continue;

            if cmd == "#NEXT": 
                index += 10;
                continue;

            if cmd[0] == '#':
                try: index = (int(cmd[1:]) - 1) * 10;
                except: print("Invalid page number.");
                continue;

            if mode != "restrict":

                try: cmd = int(cmd);
                except:
                    print("Invalid command.");
                    continue;

                if cmd <= 0 or cmd > size: 
                    print("Invalid index.");
                    continue;

                videoID = res[cmd-1]["videoid"];

                if mode == "view": 
                    if viewVideo(videoID):
                        if ADMIN: update = True;
                        break; # re-query, since incremented viewcount

                # delete video from playlist
                if mode == "delete":
                    cursor.execute("""delete 
                                    from listcontains 
                                    where listid = %s and vidid = %s;"""
                                    , (keys, videoID));
                    connection.commit();
                    update = True;
                    break;

                # rename or delete video
                if mode == "manage":
                    if manageVideo(videoID):
                        update = True;
                        break;

# boolean
def viewAccount(userID): # channel info

    if ADMIN: return administrateAccount(userID);

    clear();

    update = False;

    cursor.execute("select * from ouser where userid = %s;", userID);
    info = cursor.fetchone();
    username = info["username"];
    subCount = info["subcount"];

    cursor.execute("""select count(*) as count 
                    from ouser as s, ouser as p, subscribes as sub
                    where s.userid = %s and s.userid = subscriber and publisher = p.userid""", userID);

    subscribedToHowMany = cursor.fetchone()["count"];
    cursor.execute("select count(*) as count from video where uploader = %s;", userID);
    howManyVideos = cursor.fetchone()["count"];
    cursor.execute("select * from subscribes where subscriber = %s and publisher = %s;", (USERID, userID));
    isSubscribed = cursor.fetchone() is not None;

    cursor.execute("""select exists (
                        select userid
                        from banneduserinfo
                        where userid = %s and (expiretime is null or expiretime > now())
                        ) as chck;"""
                        , userID);
    banned = cursor.fetchone()["chck"];

    while True:

        header = "\n+-<" + username + ">" + "-" * (49 - len(username)) + "+";
        if banned:
            header+= "\n|                                                    |";
            header+= "\n|           THIS USER IS CURRENTLY BANNED.           |";
        header+= "\n|                                                    |";
        header+=f"\n|   {str(subCount) + ' subscribers':<49}|";
        header+=f"\n|   Subscribed to {str(subscribedToHowMany) + ' users' :<35}|"
        header+=f"\n|   Uploaded {str(howManyVideos) + ' videos' :<40}|";
        header+= "\n|                                                    |"
        if isSubscribed:
            header+= "\n|   You are subscribed to this user.                 |";
            header+= "\n|                                                    |";
        header+= "\n+----------------------------------------------------+"

        while True:

            print(header);
            
            print("+-<ACTIONS>------------------------------------------+");
            if not isSubscribed:
                print("| Enter 1 to subscribe to this user.                 |");
            else:
                print("| Enter 1 to unsubscribe from this user.             |");
            print("| Enter 2 to list this user's videos.                |");
            print("| Enter 3 to report this user.                       |");
            print("| Enter 4 to go back.                                |");
            print("+----------------------------------------------------+");

            try: cmd = int(input("\nEnter: "));
            except:
                clear("Invalid Input.");
                continue;
            clear();

            # subscribe
            if cmd == 1:

                if USERID is None:
                    print("\nYou should be logged in to subscribe.");
                    continue;

                if USERID == userID: 
                    print("\nYou can't subscribe to yourself.");
                    continue;

                # subscribe
                if not isSubscribed:
                    cursor.execute("insert into subscribes (subscriber, publisher) values (%s, %s);", (USERID, userID));
                    cursor.execute("update ouser set subcount = subcount + 1 where userid = %s;", userID);
                    subCount += 1;
                    print("\nSuccessfully subscribed to",username);
                
                # unsubscribe
                else:
                    cursor.execute("delete from subscribes where subscriber = %s and publisher = %s;", (USERID, userID));
                    cursor.execute("update ouser set subcount = subcount - 1 where userid = %s;", userID);
                    subCount -= 1;
                    print("\nSuccessfully unsubscribed from", username);

                connection.commit();
                update = not update;
                isSubscribed = not isSubscribed;
                break; # update header

            elif cmd == 2:
                if howManyVideos == 0:
                    print("\nThis user hasn't uploaded any videos.");
                    continue;

                listVideos("""select videoid, title, username, viewcount, uploadtime
                                from video, ouser
                                where uploader = %s and uploader = userid
                                order by uploadtime desc""", userID, "view", f"Video(s) by {username}:");

            # report this user
            elif cmd == 3: reportUser(userID);

            # notify caller functions (listUsrs)
            # about whether an update has happened (subbing, unsubbing)
            elif cmd == 4: return update;

def reportUser(userID):

    clear();

    if USERID is None:
        print("You must be logged in to file a report.");
        return;

    cursor.execute("""select exists(
                            select *
                            from userreport 
                            where complainant = %s and defendant = %s) as chck;"""
                            , (USERID, userID));

    if cursor.fetchone()["chck"]:
        print("You have already filed a report on this user.");
        return;

    cursor.execute("select username from ouser where userid = %s;", userID);
    username = cursor.fetchone()["username"];
    
    print(f"<REPORT USER> - {username} Enter #EXIT to go back.");

    reason = input("\nReason for your report (OPTIONAL): ");
    clear();

    if reason == "#EXIT": return;

    if len(reason):
        cursor.execute("""insert into userreport (complainant, defendant, reason) 
                                            values (%s, %s, %s);""",
                                            (USERID, userID, reason));
    else:
        cursor.execute("""insert into userreport (complainant, defendant) 
                                            values (%s, %s);""",
                                            (USERID, userID));

    connection.commit();
    print("Successfully reported user.");
    return;

# boolean
def uploadVideo():

    clear();

    while True:

        print("\n<UPLOAD VIDEO> Enter #EXIT to go back to the menu screen.");

        title = input("\nEnter the title for your video: ");

        if title == "#EXIT":
            clear();
            return False;

        cursor.execute("select exists(select * from video where uploader = %s and title = %s) as chck;", (USERID, title));
        if cursor.fetchone()["chck"]:
            clear();
            print(f"You already have a video titled \"{title}\".");
            continue;

        length = input("Enter the length of this video (in format of hh:mm:ss): ");

        category = selectCategory();
        if category == 0:
            clear(); # cancel
            return False;
        
        cursor.execute("insert into video (title, uploader, length, categoryof) values (%s, %s, %s, %s);", (title, USERID, length, category));
        connection.commit();

        clear();
        print(f"\nSuccessfully uploaded \"{title}\".");
        return True;

# void
def manageChannel(): # manage subscription list, videos, playlists

    clear();

    while True:

        cursor.execute("select * from ouser where userid = %s;", USERID);
        info = cursor.fetchone();
        username = info["username"];
        subCount = info["subcount"];
        cursor.execute("""select count(*) as count 
                        from ouser as s, ouser as p, subscribes as sub
                        where s.userid = %s and s.userid = subscriber and publisher = p.userid""", USERID);
        subscribedToHowMany = cursor.fetchone()["count"];
        cursor.execute("select count(*) as count from video where uploader = %s;", USERID);
        howManyVideos = cursor.fetchone()["count"];

        header = "\n+-<" + username + ">" + "-" * (49 - len(username)) + "+";
        header+= "\n|                                                    |";
        header+=f"\n|   UserID: {USERID :<41}|";
        header+=f"\n|   {str(subCount) + ' subscribers':<49}|";
        header+=f"\n|   Subscribed to {str(subscribedToHowMany) + ' users' :<35}|"
        header+=f"\n|   Uploaded {str(howManyVideos) + ' videos' :<40}|";
        header+= "\n|                                                    |"
        header+= "\n+----------------------------------------------------+"

        while True:

            print(header);

            print("+-<ACTIONS>------------------------------------------+");
            print("| Enter 1 to manage your subscription list.          |");
            print("| Enter 2 to manage your videos.                     |");
            print("| Enter 3 to manage your playlists.                  |");
            print("| Enter 4 to manage comments you left.               |");
            print("| Enter 5 to go back.                                |");
            print("+----------------------------------------------------+");

            try: cmd = int(input("\nEnter: "));
            except: 
                clear("Invalid input.");
                continue;
            clear();

            # manage subscription list
            if cmd == 1:
                if listUsers("""select userid, username, subcount 
                                    from ouser, subscribes
                                    where subscriber = %s and publisher = userid;"""
                                    , USERID, "You are subscribed to: "):
                                    break; # user might unsub to some, refresh info
            
            # manage videos 
            elif cmd == 2:
                    if listVideos("""select videoid, title, uploader, username, uploadtime, length, viewcount, likes, dislikes
                                    from video, ouser 
                                    where uploader = %s and uploader = userid
                                    order by uploadtime desc;""", USERID, "manage", "Manage videos:"):
                                    break; # user might delete some vids

            # manage playlists
            elif cmd == 3: listPlaylists("select * from playlist where creator = %s;", USERID, "manage");

            elif cmd == 4: listCommentsByUser(USERID);

            elif cmd == 5: return;

# boolean
def createPlaylist():

    clear();

    while True:
        print("\n<CREATE PLAYLIST> Enter #EXIT to go back.");

        title = input("\nEnter the title for this playlist: ");
        clear();

        if title == "#EXIT": return False;

        cursor.execute("""select exists(
                                select playlistid
                                from playlist
                                where creator = %s and listname = %s
                        ) as chck;""", (USERID, title));

        if cursor.fetchone()["chck"]:
            print(f"You already have a playlist <{title}>. Please try again.");
            continue;
        
        cursor.execute("insert into playlist (listname, creator) values (%s, %s);", (title, USERID));
        connection.commit();

        print(f"Successfully created playlist <{title}>. ");
        return True;

# boolean
def managePlaylist(playlistID):
    
    clear();

    update = False;

    cursor.execute("""select listname, username
                    from playlist, ouser 
                    where playlistid = %s and creator = userid;""",
                     playlistID);
    
    info = cursor.fetchone();

    creator = info["username"];
    listName = info["listname"];

    while True:
        # vidCount will change after deleting vids
        cursor.execute("""select count(*) as count 
                            from listcontains
                            where listid = %s;""", playlistID);
        videoCount = cursor.fetchone()["count"];

        while True:

            print( "\n+-<" + listName + ">" + "-" * (49 - len(listName)) + "+");
            print( "|                                                    |");
            print(f"|  Created by {creator :<38} |");
            print(f"|  Contains {str(videoCount) + ' videos' :<40} |");
            print( "|                                                    |");
            print( "+----------------------------------------------------+\n");

            print( "+----------------------------------------------------+");
            print( "| Enter 1 to view this playlist.                     |");
            print( "| Enter 2 to rename this playlist.                   |");
            print( "| Enter 3 to remove videos from this playlist.       |");
            print( "| Enter 4 to delete this playlist.                   |");
            print( "| Enter 5 to go back.                                |");
            print( "+----------------------------------------------------+");

            try: cmd = int(input("\nEnter: "));
            except:
                clear("Invalid command.");
                continue;
            clear();

            if cmd == 1:
                listVideos("""select videoid, title, viewcount, uploadtime, username
                            from listcontains, video, ouser
                            where listid = %s and vidid = videoid and uploader = userid"""
                            , playlistID, "view", f"Video(s) in playlist {listName}:");

            # rename playlist
            elif cmd == 2:
                
                while True:
                    print("<RENAME PLAYLIST> Enter #EXIT to go back.");
                    
                    newName = input("\nEnter a new name for this playlist: ");
                    clear();

                    if newName == "#EXIT": break;

                    cursor.execute("""select exists(
                                        select listname 
                                        from playlist 
                                        where creator = %s and listname = %s) as chck;""",
                                        (USERID, newName));

                    if cursor.fetchone()["chck"]:
                        print(f"You already have a playlist <{newName}>.");
                        continue;
                    
                    cursor.execute("update playlist set listname = %s where playlistid = %s;", (newName, playlistID));
                    connection.commit();

                    listName = newName;
                    update = True;
 
                    print("Successfully renamed playlist.");

                    break;

            # remove videos from this playlist
            elif cmd == 3:
                if listVideos("""select videoid, title, viewcount, uploadtime, username
                            from listcontains, video, ouser
                            where listid = %s and vidid = videoid and uploader = userid"""
                            , playlistID, "delete", f"Remove video(s) from playlist {listName}:"):
                    break; # update vidcount

            # delete this playlist
            elif cmd == 4:
                if input(f"\nAre you sure you want to delete this playlist? (y / n): ") == 'y':

                    cursor.execute("delete from playlist where playlistid = %s;", playlistID);
                    connection.commit();

                    clear(f"Successfully deleted playlist <{listName}>.");

                    return True; 

            elif cmd == 5: return update;

def listPlaylists(query, keys, mode, option = None):

    clear();

    index = 0;

    while True:

        cursor.execute(query, keys);
        res = cursor.fetchall();
        size = len(res);

        if size == 0:
            if input("You don't have any playlists. Would you like to create one? (y / n): ") == 'y' and createPlaylist():
                continue; # new playlist, refresh list
            else:
                clear();
                return;

        while True:
            print(f"\nPage {index // 20 + 1} of {(size - 1) // 20 + 1} [{size} result(s)]");
            print("+-----------------------------------------------------+");
            for n in range(20):
                if index + n == size: break;
                name = res[index + n]["listname"];
                
                cursor.execute("""select count(*) as count
                                from listcontains
                                where listid = %s;""", res[index + n]["playlistid"]);
                videoCount = cursor.fetchone()["count"];

                print(f"| {index + n + 1 :<4}{name :<20}{str(videoCount) + ' videos' :>27} |");
            print("+-----------------------------------------------------+\n");
            
            print("+-----------------------------------------------------+");
            print("| Enter an index of a playlist to select.             |");
            print("| Enter #NEW to create a new playlist.                |");
            if index != 0:
                print("| Enter #PREV to view the previous page.              |");
            if index + 20 < size:
                print("| Enter #NEXT to view the next page.                  |");
            if size > 20:
                print("| Enter #(pagenum) to jump to that page.              |");
            print("| Enter #EXIT to exit.                                |");
            print("+-----------------------------------------------------+");

            cmd = input("\nEnter: ");
            clear();

            if cmd == "#EXIT": return;

            if cmd == "#PREV": 
                index -= 20;
                continue;

            if cmd == "#NEXT": 
                index += 20;
                continue;
            
            if cmd == "#NEW":
                if createPlaylist(): break;
                continue;
            
            if cmd[0] == '#':
                try: index = (int(cmd[1:]) - 1) * 20;
                except: print("Invalid page number.");
                continue;

            try: cmd = int(cmd);
            except: 
                print("Invalid command.");
                continue;

            if cmd <= 0 or cmd > size: 
                print("Invalid index.");
                continue;

            playlistID = res[cmd - 1]["playlistid"];
            playlistName = res[cmd - 1]["listname"];
            
            # insert video to playlist
            if mode == "add":
                cursor.execute("""select exists(select * 
                                                from listcontains 
                                                where listid = %s and vidid = %s) as chck;""",
                                                (playlistID, option));
                if cursor.fetchone()["chck"]:
                    print(f"This video already exists in <{playlistName}>.");
                    continue;

                cursor.execute("insert into listcontains (listid, vidid) values (%s, %s);", (playlistID, option));
                connection.commit();

                print(f"Successfully added video to <{playlistName}>!");
                break; # refresh list

            elif mode == "manage":
                if(managePlaylist(playlistID)): break;

            elif mode == "view": 
                listVideos("""select videoid, title, viewcount, uploadtime, username
                        from listcontains, video, ouser
                        where listid = %s and vidid = videoid and uploader = userid"""
                        , playlistID, "view", f"Video(s) in playlist {playlistName}:");

# void
def manageAccount(): # change username & password, delete account

    clear();

    cursor.execute("select userpw from ouser where userid = %s;", USERID);
    password = cursor.fetchone()["userpw"];

    if input("\nEnter your password: ") != password:
        clear("Invalid password.");
        return;

    clear();

    while True:
        print();
        print("+-<MANAGE ACCOUNT>-----------------+");
        print("| Enter 1 to change your username. |");
        print("| Enter 2 to change your password. |");
        print("| Enter 3 to delete your account.  |");
        print("| Enter 4 to exit.                 |");
        print("+----------------------------------+");

        try: cmd = int(input("\nEnter: "));
        except: 
            clear("Invalid command.");
            continue;
        clear();


        if cmd == 1:

            while True:
                print("\n<CHANGE USERNAME> Enter #EXIT to exit.");

                newUsername = input("\nEnter new username: ");
                clear();

                if newUsername == "#EXIT": break;

                cursor.execute("select username from ouser where username = %s;", newUsername);
                if cursor.fetchone() is not None:
                    print(f"Username <{newUsername}> already taken. Please try another username.");
                    continue;
                    
                cursor.execute("update ouser set username = %s where userid = %s;", (newUsername, USERID));
                connection.commit();

                print("Username successfully changed.");
                break;
        
        elif cmd == 2:
            newPassword = input("Enter new password: ");

            cursor.execute("update ouser set userpw = %s where userid = %s;", (newPassword, USERID));
            connection.commit();

            clear("Password successfully changed.");

        elif cmd == 3:
            if deleteAccount(USERID):
                return;

        elif cmd == 4: return;
        else: print("Invalid command.");

# boolean
def deleteAccount(userID):
    global USERID;

    clear();

    if input("Are you sure you want to delete this account? (y/n): ") == "y":
        # decrement subCount of every publisher this user had been subscribed to 
        cursor.execute("""update ouser 
                            set subcount = subcount - 1
                            where userid in (
                            select publisher
                            from subscribes
                            where subscriber = %s
                            );""", userID);

        cursor.execute("""update video 
                            set likes = likes - 1
                            where videoid in (
                            select vidid
                            from viewed
                            where viewer = %s and rated = 1
                            );""", userID);

        cursor.execute("""update video 
                            set dislikes = dislikes - 1
                            where videoid in (
                            select vidid
                            from viewed
                            where viewer = %s and rated = -1
                            );""", userID);

        cursor.execute("delete from ouser where userid = %s;", userID);
        connection.commit();

        if not ADMIN: USERID = None;

        print("Successfully deleted account.");
        return True;
    
    return False;

# bool
def viewVideo(videoID): 

    if ADMIN: return administrateVideo(videoID);

    clear();

    cursor.execute("select * from censoredvideoinfo where vidid = %s;", videoID);
    censorInfo = cursor.fetchone();

    # check if censored
    if censorInfo:
        cursor.execute("select adminname from oadmin where adminid = %s;", censorInfo["adminid"]);
        adminName = cursor.fetchone()["adminname"];
        print(f"This video has been censored by admin {adminName} at {censorInfo['censortime']}.");
        print(f"Reason: {censorInfo['reason']}");
        return False;

    cursor.execute("select * from video where videoid = %s;", videoID);
    videoInfo = cursor.fetchone();

    title = videoInfo["title"];
    length = videoInfo["length"];
    viewCount = videoInfo["viewcount"];
    likes = videoInfo["likes"];
    dislikes = videoInfo["dislikes"];
    uploaderID = videoInfo["uploader"];
    uploadTime = videoInfo["uploadtime"];

    cursor.execute("select username from ouser where userid = %s;", uploaderID);
    uploader = cursor.fetchone()["username"];

    cursor.execute("""select categoryname 
                        from category, video
                        where videoid = %s and categoryof = categoryid;"""
                        , videoID);
    category = cursor.fetchone()["categoryname"];

    rated = 0;
    viewCount += 1; # increment viewcount
    cursor.execute("update video set viewcount = viewcount + 1 where videoid = %s", videoID);

    if USERID is not None and USERID != uploaderID: # logged in, and not watching one's own video

        cursor.execute("select * from viewed where viewer = %s and vidid = %s;", (USERID, videoID));
        viewedInfo = cursor.fetchone();

        if viewedInfo is None: # first time viewing this video
            cursor.execute("insert into viewed (viewer, vidid) values (%s, %s)", (USERID, videoID));

        else: 
            rated = viewedInfo["rated"];
            cursor.execute("""update viewed 
                            set tally = tally + 1, lastviewed = now()
                            where viewer = %s and vidid = %s""", (USERID, videoID));

        connection.commit();
    
    cursor.execute("select count(*) from ocomment where vidid = %s;", videoID);
    commentCount = cursor.fetchone()["count(*)"];


    while True:

        header="\n+---------------------------------------------------------------+\n";
        header+= "|                                                               |\n";
        header+= "|                            | \                                |\n";
        header+= "|                            |   \                              |\n";
        header+= "|                            |     \                            |\n";
        header+= "|                            |     /                            |\n";
        header+= "|                            |   /                              |\n";
        header+= "|                            | /                                |\n";
        header+= "|                                                               |\n";
        header+= "+==============O------------------------------------------------+\n";
        header+=f"| || {str(length // 4).split('.')[0] + ' / ' + str(length) :<58} |\n";
        header+= "+---------------------------------------------------------------+\n";
        header+=f"| {'[' + title + '] by ' + uploader:<61} |\n";
        header+=f"| {str(viewCount) + ' views / ' + str(likes) + ' likes / ' + str(dislikes) + ' dislikes / ' + str(commentCount) + ' comments' :<61} |\n";
        header+=f"| {'uploaded at ' + str(uploadTime):<61} |\n";
        header+=f"| category: {category :<51} |\n";
        header+= "+---------------------------------------------------------------+\n\n";

        header+= "+-<ACTIONS>-----------------------------------------------------+\n";
        header+=f"| Enter 1 to {('un-' if rated == 1 else '') + 'like this video.' :<50} |\n";
        header+=f"| Enter 2 to {('un-' if rated == -1 else '') + 'dislike this video.' :<50} |\n";
        header+= "| Enter 3 to view / add comments.                               |\n";
        header+=f"| Enter 4 to view {(uploader + ''''s user info. ''') :<45} |\n";
        header+= "| Enter 5 to add this video to your playlist.                   |\n";
        header+= "| Enter 6 to report this video.                                 |\n";
        header+= "| Enter 7 to go back.                                           |\n";
        header+= "+---------------------------------------------------------------+\n";

        while True:
            print(header);

            try: cmd = int(input("Enter: "));
            except:
                clear("Invalid command.");
                continue;
            clear();

            if cmd == 1:

                if USERID is None:
                    print("You must be logged in to leave a like.");
                    continue;

                if rated == 1: # un-like;
                    cursor.execute("update video set likes = likes - 1 where videoid = %s;", videoID);
                    cursor.execute("update viewed set rated = 0 where viewer = %s and vidid = %s;", (USERID, videoID));
                    rated = 0;
                    likes -= 1;
                    
                elif rated == -1: # un-dislike and like
                    cursor.execute("update video set likes = likes + 1, dislikes = dislikes - 1 where videoid = %s;", videoID);
                    cursor.execute("update viewed set rated = 1 where viewer = %s and vidid = %s;", (USERID, videoID));
                    rated = 1;
                    dislikes -= 1;
                    likes += 1;

                else: # like
                    cursor.execute("update video set likes = likes + 1 where videoid = %s;", videoID);
                    cursor.execute("update viewed set rated = 1 where viewer = %s and vidid = %s;", (USERID, videoID));
                    rated = 1;
                    likes += 1;    
                
                connection.commit();

                break; # refresh info
            
            elif cmd == 2:

                clear();

                if USERID is None:
                    print("You must be logged in to leave a dislike.");
                    continue;

                if rated == -1: # un-dislike;
                    cursor.execute("update video set dislikes = dislikes - 1 where videoid = %s;", videoID);
                    cursor.execute("update viewed set rated = 0 where viewer = %s and vidid = %s;", (USERID, videoID));
                    rated = 0;
                    dislikes -= 1;
                    
                elif rated == 1: # un-like and dislike
                    cursor.execute("update video set likes = likes - 1, dislikes = dislikes + 1 where videoid = %s;", videoID);
                    cursor.execute("update viewed set rated = -1 where viewer = %s and vidid = %s;", (USERID, videoID));
                    rated = -1;
                    likes -= 1;
                    dislikes += 1;

                else: # dislike
                    cursor.execute("update video set dislikes = dislikes + 1 where videoid = %s;", videoID);
                    cursor.execute("update viewed set rated = -1 where viewer = %s and vidid = %s;", (USERID, videoID));       
                    rated = -1;
                    dislikes +=1;
                
                connection.commit();

                break; # refresh info
            
            # comments on this video
            elif cmd == 3:
                delta = listCommentsOnVideo(videoID);
                if delta: 
                    commentCount += delta;
                    break;

            # view channel info
            elif cmd == 4: viewAccount(uploaderID);

            # add this video to playlist
            elif cmd == 5:
                if USERID is None:
                    print("You must be logged in to create a playlist.");
                    continue;

                listPlaylists("select * from playlist where creator = %s;", USERID, "add", videoID);

            # report this video
            elif cmd == 6: reportVideo(videoID);

            elif cmd == 7: return True;

# boolean
def addComment(videoID):

    clear();

    while True:
        print();
        print("<COMMENT> Enter #EXIT to go back.");

        comment = input("\nYour comment: ");

        if comment == "#EXIT": 
            clear();
            return False;
        
        cursor.execute("""insert into ocomment (commenter, vidid, content) 
                        values (%s, %s, %s);""", (USERID, videoID, comment));
        connection.commit();

        clear();
        print(f"Successfully left comment.");
        return True;

# int
def listCommentsOnVideo(videoID):

    clear();

    index = 0;
    delta = 0; # return change in comment count

    cursor.execute("select title from video where videoid = %s;", videoID);
    title = cursor.fetchone()["title"];

    while True:

        cursor.execute("select * from ocomment where vidid = %s order by commenttime desc;", videoID);
        res = cursor.fetchall();
        size = len(res);

        while True:

            print(f"\nComments on <{title}>:\n");

            if size:
                print(f"Page {index // 10 + 1} of {(size - 1) // 10 + 1} [{size} result(s)]");
                print("+-----------------------------------------------------------------------+"); # 71 + 2
                for n in range(10):
                    if index + n == size: break;

                    cursor.execute("select username from ouser where userid = %s;",res[index + n]["commenter"]);

                    commenter = cursor.fetchone()["username"]; 
                    content = res[index + n]["content"];
                    commentTime = res[index + n]["commenttime"];

                    print(f"| {index + n + 1 :<4}{content[:65] :<65} |");
                    content = content[65:];
                    while len(content):
                        print(f"|     {content[:65] :<65} |");
                        content = content[65:];

                    print(f"| {'by ' + commenter +', at ' + str(commentTime) :>69} |");
                    print( "+-----------------------------------------------------------------------+");
            else:
                print("+-----------------------------------------------------------------------+"); # 71 + 2
                print("|                   No comments on this video yet.                      |");
                print("+-----------------------------------------------------------------------+"); 

            print();
            print("+-----------------------------------------------------------------------+");
            if USERID:
                print("| Enter #NEW to leave a comment.                                        |");
            if index != 0:
                print("| Enter #PREV to view the previous page.                                |");
            if index + 10 < size:
                print("| Enter #NEXT to view the next page.                                    |");
            if size > 10:
                print("| Enter #(pagenum) to jump to that page.                                |");
            print("| Enter #EXIT to exit.                                                  |");
            print("+-----------------------------------------------------------------------+");


            cmd = input("\nEnter: ");
            clear();

            if cmd == "#EXIT": return delta;

            if cmd == "#PREV": 
                index -= 10;
                continue;

            if cmd == "#NEXT": 
                index += 10;
                continue;

            if cmd == "#NEW":
                if addComment(videoID):
                    delta += 1;
                    break; # refresh list

                continue;

            if cmd[0] == '#':
                try: index = (int(cmd[1:]) - 1) * 10;
                except: print("Invalid page number.");
                continue;

# void
def listCommentsByUser(userID):

    clear();

    index = 0;

    cursor.execute("select username from ouser where userid = %s;", userID);
    commenter = cursor.fetchone()["username"];

    while True:

        cursor.execute("select * from ocomment where commenter = %s order by commenttime desc;", userID);
        res = cursor.fetchall();
        size = len(res);

        if size == 0:
            clear();
            print(f"{commenter} hasn't left any comments.");
            return;

        while True:

            print(f"\nComments by <{commenter}>:");

            print(f"\nPage {index // 10 + 1} of {(size - 1) // 10 + 1} [{size} result(s)]");
            print("+-----------------------------------------------------------------------+"); # 71 + 2
            for n in range(10):
                if index + n == size: break;

                cursor.execute("select title from video where videoid = %s;",res[index + n]["vidid"]);
                title = cursor.fetchone()["title"];

                content = res[index + n]["content"];
                commentTime = res[index + n]["commenttime"];

                print(f"| {index + n + 1 :<4}{content[:65] :<65} |");
                content = content[65:];
                while len(content):
                    print(f"|     {content[:65] :<65} |");
                    content = content[65:];

                print(f"| {'on ' + title +', at ' + str(commentTime) :>69} |");
                print( "+-----------------------------------------------------------------------+");

            print();
            print("+-----------------------------------------------------------------------+");
            if ADMIN or userID == USERID:
                print("| Enter an index of a comment to manage.                                |");
            if index != 0:
                print("| Enter #PREV to view the previous page.                                |");
            if index + 10 < size:
                print("| Enter #NEXT to view the next page.                                    |");
            if size > 10:
                print("| Enter #(pagenum) to jump to that page.                                |");
            print("| Enter #EXIT to exit.                                                  |");
            print("+-----------------------------------------------------------------------+");


            cmd = input("\nEnter: ");

            if cmd == "#EXIT":
                clear();
                return;

            if cmd == "#PREV": 
                index -= 10;
                clear();
                continue;

            if cmd == "#NEXT": 
                index += 10;
                clear();
                continue;

            if cmd[0] == '#':
                index = (int(cmd[1:]) - 1) * 10;
                clear();
                continue;
            
            if ADMIN or userID == USERID:
                try: cmd = int(cmd);
                except: clear("Invalid command.");

                if manageComment(res[cmd - 1]["commentid"]):
                    break; #delete

def manageComment(commentID): #delete

    clear();

    cursor.execute("select * from ocomment where commentid = %s;", commentID);
    commentInfo = cursor.fetchone();

    cursor.execute("select username from ouser where userid = %s;", commentInfo["commenter"]);
    commenter = cursor.fetchone()["username"];

    cursor.execute("select title from video where videoid = %s;", commentInfo["vidid"]);
    title = cursor.fetchone()["title"];

    content = commentInfo["content"];
    commentTime = commentInfo["commenttime"];

    update = False;

    while True:

        print(f"Comment by <{commenter}>:\n");

        print("+-----------------------------------------------------------------------+");
        print(f"| {content[:69] :<69} |");
        content = content[69:];
        while len(content):
            print(f"| {content[:69] :<69} |");
            content = content[69:];
        print(f"| {'on ' + title +', at ' + str(commentTime) :>69} |");
        print("+-----------------------------------------------------------------------+\n");

        print("+-<ACTIONS>-------------------------------------------------------------+");
        print("| Enter 1 to delete this comment.                                       |");
        print("| Enter 2 to go back.                                                   |");
        print("+-----------------------------------------------------------------------+");

        try: cmd = int(input("\nEnter: "));
        except:
            clear("Invalid command.");
            continue;
        clear();

        # delete
        if cmd == 1:
            if input("Are you sure you want to delete this comment? (y / n): ") == 'y':
                cursor.execute("delete from ocomment where commentid = %s;", commentID);
                connection.commit();

                clear("Successfully deleted comment.");
                return True;
            
            continue;

        elif cmd == 2: return update;

def reportVideo(videoID):
    
    clear();

    if USERID is None:
        print("You must be logged in to file a report.");
        return;

    cursor.execute("""select exists(
                            select *
                            from videoreport 
                            where complainant = %s and vidid = %s) as chck;"""
                            , (USERID, videoID));

    if cursor.fetchone()["chck"]:
        print("You have already filed a report on this video.");
        return;

    cursor.execute("select title from video where videoid = %s;", videoID);
    title = cursor.fetchone()["title"];
    
    print(f"<REPORT VIDEO> - [{title}] Enter #EXIT to go back.");

    reason = input("\nReason for your report (OPTIONAL): ");

    if reason == "#EXIT":
        clear();
        return;

    if len(reason):
        cursor.execute("""insert into videoreport (complainant, vidid, reason) 
                                            values (%s, %s, %s);""",
                                            (USERID, videoID, reason));
    else:
        cursor.execute("""insert into videoreport (complainant, vidid) 
                                            values (%s, %s);""",
                                            (USERID, videoID));

    connection.commit();
    clear();
    print("Successfully reported video.");
    return;

def manageVideo(videoID): # rename, delete, re-categorize video

    clear();
    
    cursor.execute("select * from video where videoid = %s;", videoID);
    videoInfo = cursor.fetchone();

    title = videoInfo["title"];
    uploadTime = videoInfo["uploadtime"];
    uploaderID = videoInfo["uploader"];

    cursor.execute("select username from ouser where userid = %s;", uploaderID);
    uploader = cursor.fetchone()["username"];

    cursor.execute("""select categoryname 
                    from category
                    where categoryid = %s""", videoInfo["categoryof"]);
    category = cursor.fetchone()["categoryname"];

    update = False;

    while True:

        print();
        print( "+-<" + title + ">" + "-" * (40 - len(title)) + "+");
        print( "|                                           |");
        print(f"|   uploaded by: {uploader :<26} |");
        print(f"|   uploaded at: {str(uploadTime) :<26} |");
        print(f"|   category: {category :<29} |");
        print( "|                                           |");
        print( "+-------------------------------------------+\n");

        print( "+-<ACTIONS>---------------------------------+");
        print( "| Enter 1 to view this video.               |");
        print( "| Enter 2 to rename this video.             |");
        print( "| Enter 3 to re-categorize this video.      |");
        print( "| Enter 4 to delete this video.             |");
        print( "| Enter 5 to go back.                       |");
        print( "+-------------------------------------------+");
        
        try: cmd = int(input("\nEnter: "));
        except:
            clear("Invalid command.");
            continue;
        clear();
        
        # view video
        if cmd == 1:
            if viewVideo(videoID):
                update = True; # new viewcount
            
        # rename video
        elif cmd == 2:
            while True:
                print("\n<RENAME VIDEO> Enter #EXIT to go back.");

                newTitle = input("\nEnter a new title for this video: ");
                clear();

                if newTitle == "#EXIT": break;

                cursor.execute("""select exists(
                                        select *
                                        from video
                                        where uploader = %s and title = %s)
                                as chck;""", (USERID, newTitle));
                if cursor.fetchone()["chck"]:
                    print(f"You already have a video titled \"{newTitle}\".");
                    continue;
                
                cursor.execute("update video set title = %s where videoid = %s;", (newTitle, videoID));
                connection.commit();

                title = newTitle;
                update = True;

                print("Successfully renamed video.");
                break;
        
        # re-categorize
        elif cmd == 3:

            newCategory = selectCategory();

            # update
            if newCategory != 0 and newCategory != videoInfo["categoryof"]:
                cursor.execute("update video set categoryof = %s where videoid = %s;", (newCategory, videoID));
                connection.commit();

                cursor.execute("select categoryname from category where categoryid = %s;", newCategory);
                category = cursor.fetchone()["categoryname"];

                print(f"Successfully re-categorized video <{title}>.");
                update = True;
            
        # delete video
        elif cmd == 4:
            if deleteVideo(videoID):
                return True;

        # go back
        elif cmd == 5: return update;

def deleteVideo(videoID):

    cursor.execute("select title from video where videoid = %s;",videoID);
    title = cursor.fetchone()["title"];

    clear();

    if input(f"\nAre you sure you want to delete this video? (y / n): ") == 'y':
        cursor.execute("delete from video where videoid = %s;", videoID);

        connection.commit();
        clear(f"Successfully deleted video <{title}>.");
        return True; 
    
    return False;

def listAdmins():

    clear();

    cursor.execute("select adminname, adminid from oadmin;");
    res = cursor.fetchall();
    
    size = len(res);

    if not size: 
        print("NO ADMINS??");
        return;

    index = 0;

    while True:
        print("Admins of OurTube");

        print(f"\nPage {index // 20 + 1} of {(size - 1) // 20 + 1} [{size} result(s)]");
        print("+----------------------------------------+");
        for n in range(20):
            if index + n == size: break;
            name = res[index + n]["adminname"];
            print(f"| {index + n + 1 :<4}{name :<35}|");
        print("+----------------------------------------+\n");
        
        print("+----------------------------------------+");
        print("| Enter an index of an admin to contact. |");
        if index != 0:
            print("| Enter #PREV to view the previous page. |");
        if index + 20 < size:
            print("| Enter #NEXT to view the next page.     |");
        if size > 20:
            print("| Enter #(pagenum) to jump to that page. |");
        print("| Enter #EXIT to exit.                   |");
        print("+----------------------------------------+");

        cmd = input("\nEnter: ");
        clear();

        if cmd == "#EXIT": return;

        if cmd == "#PREV" and index != 0: 
            index -= 20;
            continue;

        if cmd == "#NEXT" and index + 20 < size: 
            index += 20;
            continue;
        
        if cmd[0] == '#':
            try: index = (int(cmd[1:]) - 1) * 20;
            except: print("Invalid page number.");
            continue;

        try: cmd = int(cmd);
        except:
            print("Invalid command.");
            continue;
        
        if cmd <= 0 or cmd > size: 
            clear("Invalid index.");
            continue;
        
        exchangeMessagesWith(res[cmd-1]["adminid"]);

def exchangeMessagesWith(id):

    clear();

    name = None;
    if ADMIN:
        cursor.execute("select username from ouser where userid = %s;", id);
        name = cursor.fetchone()["username"];
    else:
        cursor.execute("select adminname from oadmin where adminid = %s;", id);
        name = cursor.fetchone()["adminname"];

    keys = None;
    if ADMIN: keys = (id, USERID);
    else: keys = (USERID, id);

    index = 0;

    while True:

        cursor.execute("""select *
                            from uamessage
                            where userid = %s and adminid = %s
                            order by timesent desc;"""
                            , keys);
        res = cursor.fetchall();
        size = len(res);

        while True:

            print(f"\nMessages with <{name}>:\n");

            if size:
                print(f"Page {index // 10 + 1} of {(size - 1) // 10 + 1} [{size} result(s)]");
                print("+-----------------------------------------------------------------------+"); # 71 + 2
                for n in range(10):
                    if index + n == size: break;

                    message = res[index + n]["message"];
                    timeSent = res[index + n]["timesent"];
                    fromUser = res[index + n]["fromuser"];

                    if ADMIN == fromUser:
                        print(f"| {name + ' sent:' :<69} |");
                    else:
                        print("| You sent:                                                             |");

                    print(f"|    {message[:63] :<63}    |");
                    message = message[63:];
                    while len(message):
                        print(f"|    {message[:63] :<63}    |");
                        message = message[63:];

                    print(f"| {'at ' + str(timeSent) :>69} |");
                    print( "+-----------------------------------------------------------------------+");
            else:
                print("+-----------------------------------------------------------------------+"); # 71 + 2
                print("|                           No message history.                         |");
                print("+-----------------------------------------------------------------------+"); 

            print();
            print("+-----------------------------------------------------------------------+");
            print("| Enter #NEW to send a message.                                         |");
            if index != 0:
                print("| Enter #PREV to view the previous page.                                |");
            if index + 10 < size:
                print("| Enter #NEXT to view the next page.                                    |");
            if size > 10:
                print("| Enter #(pagenum) to jump to that page.                                |");
            print("| Enter #EXIT to exit.                                                  |");
            print("+-----------------------------------------------------------------------+");


            cmd = input("\nEnter: ");
            clear();

            if cmd == "#EXIT": return;

            if cmd == "#PREV": 
                index -= 10;
                continue;

            if cmd == "#NEXT": 
                index += 10;
                continue;

            if cmd == "#NEW":
                print("\n<SEND MESSAGE> Enter #EXIT to go back.");

                message = input("\nEnter: ");
                clear();

                if message == "#EXIT": continue;

                cursor.execute("""insert into uamessage (userid, adminid, message, fromuser)
                                        values (%s, %s, %s, %s);""", keys + (message, not ADMIN));
                connection.commit();

                print("Successfully sent message.");
                break;

            if cmd[0] == '#':
                try: index = (int(cmd[1:]) - 1) * 10;
                except: print("Invalid page number.");
                continue;

# void
def checkNewNotifications():
    
    clear();
    cursor.execute("select lastchecked from ouser where userid = %s;", USERID);
    lastChecked = cursor.fetchone()["lastchecked"];
    # check for new uploads, new comments, new  messages
    cursor.execute("""select * from (
                            select videoid as id, uploadtime as notiftime, 'video' as notiftype
                            from video
                            where uploader in (
                                    select publisher
                                    from subscribes
                                    where subscriber = %s)
                        union
                            select commentid as id, commenttime as notiftime, 'comment' as notiftype
                            from ocomment, video
                            where vidid = videoid and uploader = %s and commenter != uploader
                        union
                            select messageid as id, timesent as notiftime, 'message' as notiftype
                            from uamessage
                            where not fromuser and userid = %s
                        ) temp
                    where notiftime > %s
                    order by notiftime desc;"""
                , (USERID, USERID, USERID, lastChecked));

    res = cursor.fetchall(); # {'id': 6889, 'notiftime': datetime(2022, 11, 26, 21, 59, 55), 'notiftype': 'video'}
    size = len(res);

    cursor.execute("update ouser set lastchecked = now() where userid = %s;", USERID);
    connection.commit();

    if size == 0:
        print(f"No new notifications since {lastChecked}.");
        return;

    index = 0;
    
    while True:
        print(f"\nYou have {size} notification(s) since {lastChecked}.");
        print(f"\nPage {index // 10 + 1} of {(size - 1) // 10 + 1} [{size} result(s)]");
        print("+-----------------------------------------------------------------------------+");
        for n in range(10):
            if index + n == size: break;

            ntype = res[index + n]["notiftype"];
            id = res[index + n]["id"];
            time = res[index + n]['notiftime'];
            text = None;
            # commenter = None;

            # new video from subscribed channel
            if ntype == "video":
                cursor.execute("""select username, title
                                  from ouser, video
                                  where videoid = %s and uploader = userid;"""
                                  , id);
                videoInfo = cursor.fetchone();
                uploader = videoInfo["username"];
                text = videoInfo["title"];

                if len(text) > 72: text = text[:69] + "..."; 

                print(f"| {index + n + 1 :<3}New video from {uploader + ':':<57} |");

            # new comment on my video
            elif ntype == "comment":
                cursor.execute("""select username, title
                                 from ouser, ocomment, video
                                 where commentid = %s and commenter = userid and vidid = videoid;"""
                                 ,id);
                commentInfo = cursor.fetchone();
                commenter = commentInfo["username"];
                text = commentInfo["title"];

                print(f"| {index + n + 1 :<3}{commenter + ' has commented on your video: ':<72} |");
            
            elif ntype == "message":
                cursor.execute("select * from uamessage where messageid = %s;", id);
                messageInfo = cursor.fetchone();

                text = messageInfo["message"];
                if len(text) > 72: text = text[:69] + '...';

                cursor.execute("select adminname from oadmin where adminid = %s;", messageInfo["adminid"]);
                admin = cursor.fetchone()["adminname"];

                print(f"| {index + n + 1 :<3}New Message from admin {admin + ':':<49} |");

            print(f"|    {text :<72} |");
            print(f"|    {'at ' + str(time) :<72} |");
            print("+-----------------------------------------------------------------------------+");

        print();
        print("+-----------------------------------------------------------------------------+");
        print("| Enter an index of a notification for details.                               |");
        if index != 0:
            print("| Enter #PREV to view the previous page.                                      |");
        if index + 10 < size:
            print("| Enter #NEXT to view the next page.                                          |");
        if size > 10:
            print("| Enter #(pagenum) to jump to that page.                                      |");
        print("| Enter #EXIT to exit.                                                        |");
        print("+-----------------------------------------------------------------------------+");

        cmd = input("\nEnter: ");
        clear();

        if cmd == "#EXIT": return;

        elif cmd == "#PREV" and index != 0: 
            index -= 10;
            continue;

        elif cmd == "#NEXT" and index + 10 < size: 
            index += 10;
            continue;
        
        elif cmd[0] == '#':
            try: index = (int(cmd[1:]) - 1) * 20;
            except: print("Invalid page number.");
            continue;

        try: cmd = int(cmd);
        except:
            print("Invalid command."); 
            continue;

        if cmd <= 0 or cmd > size: 
            print("Invalid index.");
            continue;

        selected = res[cmd - 1];

        if selected["notiftype"] == "video":
            viewVideo(selected["id"]);

        elif selected["notiftype"] == "comment":
            cursor.execute("select vidid from ocomment where commentid = %s;", selected["id"]);
            listCommentsOnVideo(cursor.fetchone()["vidid"]);

        elif selected["notiftype"] == "message":
            cursor.execute("select adminid from uamessage where messageid = %s;", selected["id"]);
            exchangeMessagesWith(cursor.fetchone()["adminid"]);

# boolean
def administrateAccount(userID):

    clear();

    cursor.execute("select * from ouser where userid = %s;", userID);
    info = cursor.fetchone();
    username = info["username"];
    subCount = info["subcount"];

    cursor.execute("""select count(*) as count 
                    from ouser as s, ouser as p, subscribes as sub
                    where s.userid = %s and s.userid = subscriber and publisher = p.userid""", userID);

    subscribedToHowMany = cursor.fetchone()["count"];

    cursor.execute("""select count(*) as count
                    from userreport
                    where defendant = %s;""", userID);
    userReportCount = cursor.fetchone()["count"];

    cursor.execute("select count(*) as count from banneduserinfo where userid = %s;", userID);
    bannedCount = cursor.fetchone()["count"];

    cursor.execute("""select count(*) as count
                    from videoreport, video
                    where uploader = %s and videoid = vidid;""", userID);
    videoReportCount = cursor.fetchone()["count"];

    while True:

        cursor.execute("select count(*) as count from video where uploader = %s;", userID);
        howManyVideos = cursor.fetchone()["count"];

        cursor.execute("""select expiretime
                            from banneduserinfo
                            where userid = %s and (expiretime is null or expiretime > now())"""
                            , userID);
        banned = cursor.fetchone();

        header = "\n+-<" + username + ">" + "-" * (49 - len(username)) + "+";
        header+= "\n|                                                    |";
        header+=f"\n|   UserID: {userID :<41}|";
        header+=f"\n|   {str(subCount) + ' subscribers':<49}|";
        header+=f"\n|   Subscribed to {str(subscribedToHowMany) + ' users' :<35}|"
        header+=f"\n|   Uploaded {str(howManyVideos) + ' videos' :<40}|";
        header+= "\n|                                                    |"
        header+=f"\n|   This user has been reported {str(userReportCount + videoReportCount) + ' times:':<20} |";
        header+=f"\n|       {str(userReportCount) + ' user reports':<44} |";
        header+=f"\n|       {str(videoReportCount) + ' video reports':<44} |";
        header+= "\n|                                                    |"
        if banned:
            if banned["expiretime"]:
                header+=f"\n|   This user is banned until {str(banned['expiretime'])}    |";
            else:
                header+=f"\n|   This user is banned permanently.                 |";

        header+=f"\n|   This user has {str(bannedCount) + ' bans on record.' :<34} |";
        header+= "\n|                                                    |"
        header+= "\n+----------------------------------------------------+"

        while True:

            print(header);
            
            print("+-<ACTIONS>------------------------------------------+");
            print("| Enter 1 to list this user's videos.                |");
            print("| Enter 2 to list this user's view history.          |");
            print("| Enter 3 to list reports against this user.         |");
            print("| Enter 4 to list comments by this user.             |");
            print("| Enter 5 to message this user.                      |");
            if not banned:
                print("| Enter 6 to ban this user.                          |");
            else:
                print("| Enter 6 to un-ban this user.                       |");
            print("| Enter 7 to remove this user from OurTube.          |");
            print("| Enter 8 to go back.                                |");
            print("+----------------------------------------------------+");

            try: cmd = int(input("\nEnter: "));
            except:
                clear("Invalid command.");
                continue;

            # list user's videos
            if cmd == 1:
                if howManyVideos == 0:
                    clear("\nThis user hasn't uploaded any videos.");
                    continue;
                
                if listVideos("""select videoid, title, username, viewcount, uploadtime
                                from video, ouser
                                where uploader = %s and uploader = userid
                                order by uploadtime desc""", userID, "view", f"Video(s) by {username}:"):
                                break;

            # view history
            elif cmd == 2:
                listVideos("""select videoid, title, username, viewcount, uploadtime
                                from video, ouser, viewed
                                where viewer = %s and vidid = videoid and uploader = userid
                                order by lastviewed desc;"""
                                , userID, "restrict", f"{username + ''''s'''} view history");

            # list reports against this user
            elif cmd == 3:
                cursor.execute("""select * from (
                                        select complainant, vidid as id, reason, reporttime, 'video' as reporttype
                                        from videoreport, video
                                        where uploader = %s and vidid = videoid
                                    union
                                        select complainant, defendant as id, reason, reporttime, 'user' as reporttype
                                        from userreport
                                        where defendant = %s
                                    ) temp
                                order by reporttime desc;"""
                                ,(userID, userID));
                res = cursor.fetchall();

                listReports(res, f"Reports against user {username}:");

            elif cmd == 4: listCommentsByUser(userID);
            elif cmd == 5: exchangeMessagesWith(userID);
            elif cmd == 6:
                temp = banOrUnbanUser(userID);
                if temp:
                    if temp == 1:
                        bannedCount += 1;
                    break;

            elif cmd == 7:
                if deleteAccount(userID):
                    return True;

            elif cmd == 8:
                clear();
                return False;

            else: clear("Invalid command.");

# int. -1 for unban, 0 for cancel, 1 for ban
def banOrUnbanUser(userID): # and unban

    clear();

    cursor.execute("select username from ouser where userid = %s;", userID);
    username = cursor.fetchone()["username"];

    cursor.execute("""select expiretime, userbanid 
                        from banneduserinfo
                        where userid = %s and (expiretime is null or expiretime > now())
                    """, userID);
    res = cursor.fetchone();

    if res:
        banID = res["userbanid"];
        if input(f"Unban user {username}? (y / n): ") == 'y':
            cursor.execute("""update banneduserinfo
                                set expiretime = now()
                                where userbanid = %s;"""
                                ,banID);
            connection.commit();
            clear(f"Successfully unbanned user {username}.");
            return -1;

        clear();
        return 0;
        
    print(f"<BAN USER {username}> Enter #EXIT to go back.");

    reason = input("\nReason for this ban: ");

    if reason == "#EXIT":
        clear();
        return 0;

    print("\nEnter the duration for this ban, in format of 'days hours minutes seconds', or blank for a permanent ban.");

    duration = input("\nEnter: ");
    if duration == "#EXIT":
        clear();
        return 0;

    now = datetime.now();

    clear(f"Successfully banned user {username}.");

    if len(duration):
        days, hours, minutes, seconds = map(int, duration.split());
        expiretime = now + timedelta(days = days, hours = hours, minutes = minutes, seconds = seconds);
        expiretime = str(expiretime).split('.')[0];
        
        cursor.execute("""insert into banneduserinfo (userid, adminid, bantime, expiretime, reason)
                                        values (%s, %s, %s, %s, %s);""",
                                        (userID, USERID, now, expiretime, reason));
        print(f"This ban will expire at {str(expiretime)}.");
    
    else:
        cursor.execute("""insert into banneduserinfo (userid, adminid, bantime, reason)
                                values (%s, %s, %s, %s);""",
                                (userID, USERID, now, reason));

    connection.commit();
    return 1;

def listReports(reports, header = None):

    clear();

    size = len(reports);

    if not size:
        print("No results.");
        return;

    index = 0;

    while True:

        if header: print(header);
        print(f"\nPage {index // 10 + 1} of {(size - 1) // 10 + 1} [{size} result(s)]");
        print("+-----------------------------------------------------------------------------+");
        for n in range(10):
            if index + n == size: break;

            cur = reports[index + n];
            cursor.execute("select username from ouser where userid = %s;", cur["complainant"]);
            complainant = cursor.fetchone()["username"];
            reportType = cur["reporttype"];
            reason = cur["reason"];

            if reportType == "message":
                print(f"| {index + n + 1 :<3}{'User ' + complainant + ' has sent you a message:' :<72} |");
                print(f"|    {reason:72} |");

            else:
                if not reason: reason = "Not given";
                against = "";

                if reportType == "video":
                    cursor.execute("""select username
                                    from ouser, video
                                    where videoid = %s and uploader = userid;""", cur["id"])
                    uploader = cursor.fetchone()["username"];
                    cursor.execute("select title from video where videoid = %s;", cur["id"]);
                    against = "[" + cursor.fetchone()["title"] + "] by " + uploader;

                elif reportType == "user":
                    cursor.execute("select username from ouser where userid = %s;", cur["id"]);
                    against = cursor.fetchone()["username"];

                print(f"| {index + n + 1 :<3}{'User ' + complainant + ' reported ' + reportType + ': ' + against :<72} |");
                print(f"|    Reason: {reason:<64} |");
                
            print(f"|    At {str(cur['reporttime']):<69} |");
            print("+-----------------------------------------------------------------------------+");

        print();
        print("+-----------------------------------------------------------------------------+");
        print("| Enter index of a report for details.                                        |");
        if index != 0:
            print("| Enter #PREV to view the previous page.                                      |");
        if index + 10 < size:
            print("| Enter #NEXT to view the next page.                                          |");
        if size > 10:
            print("| Enter #(pagenum) to jump to that page.                                      |");
        print("| Enter #EXIT to exit.                                                        |");
        print("+-----------------------------------------------------------------------------+");

        cmd = input("\nEnter: ");
        clear();

        if cmd == "#EXIT": return;

        elif cmd == "#PREV" and index != 0: 
            index -= 10;
            continue;

        elif cmd == "#NEXT" and index + 10 < size: 
            index += 10;
            continue;
        
        elif cmd[0] == '#' and size > 10:
            try: index = (int(cmd[1:]) - 1) * 20;
            except: print("Invalid page number.");
            continue;

        try: cmd = int(cmd);
        except:
            print("Invalid command.");
            continue;

        if cmd <= 0 or cmd > size: 
            print("Invalid index.");
            continue;

        selectedType = reports[cmd - 1]["reporttype"];
        selectedID = reports[cmd - 1]["id"];

        if selectedType == "user": administrateAccount(selectedID);
        elif selectedType == "video": administrateVideo(selectedID);
        elif selectedType == "message": exchangeMessagesWith(selectedID);

def checkNewReports():

    clear();
    cursor.execute("select lastchecked from oadmin where adminid = %s;", USERID);
    lastChecked = cursor.fetchone()["lastchecked"];

    cursor.execute("update oadmin set lastchecked = now() where adminid = %s;", USERID);
    connection.commit();

    cursor.execute("""select * from (
                                select complainant, vidid as id, reason, reporttime, 'video' as reporttype
                                from videoreport
                            union
                                select complainant, defendant as id, reason, reporttime, 'user' as reporttype
                                from userreport
                            union
                                select userid as complainant, userid as id, message as reason, timesent as reporttime, 'message' as reporttype
                                from uamessage 
                                where adminid = %s and fromuser
                            ) temp
                    where reporttime > %s
                    order by reporttime desc;""", (USERID, lastChecked));

    res = cursor.fetchall(); 

    if not len(res):
        print(f"No new reports since {lastChecked}.");
        return;
    
    listReports(res, f"{len(res)} new report(s) since {str(lastChecked)}.");
    
    return;

def administrateVideo(videoID):

    clear();

    cursor.execute("select * from video where videoid = %s;", videoID);
    videoInfo = cursor.fetchone();

    title = videoInfo["title"];
    uploadTime = videoInfo["uploadtime"];
    uploaderID = videoInfo["uploader"];

    cursor.execute("select username from ouser where userid = %s;", uploaderID);
    uploader = cursor.fetchone()["username"];

    cursor.execute("""select categoryname 
                    from category
                    where categoryid = %s""", videoInfo["categoryof"]);
    category = cursor.fetchone()["categoryname"];

    cursor.execute("""select count(*) as count
                    from videoreport
                    where vidid = %s;""", videoID);
    reportCount = cursor.fetchone()["count"];

    cursor.execute("""select exists(
                            select vidid 
                            from censoredvideoinfo
                            where vidid = %s)
                        as chck;""", videoID);
    censored = cursor.fetchone()["chck"];

    while True:

        print();
        print( "+-<" + title + ">" + "-" * (40 - len(title)) + "+");
        print( "|                                           |");
        if censored:
            print(f"|           THIS VIDEO IS CENSORED          |");
        print( "|                                           |");
        print(f"|   videoID: {videoID :<30} |");
        print(f"|   uploaded by: {uploader :<26} |");
        print(f"|   uploaded at: {str(uploadTime) :<26} |");
        print(f"|   category: {category :<29} |");
        print( "|                                           |");
        print(f"|   This video has been reported {str(reportCount) + ' times':<10} |");
        print( "|                                           |");
        print( "+-------------------------------------------+\n");

        print( "+-<ACTIONS>---------------------------------+");
        print(f"| Enter 1 to {('un-' if censored else '') + 'censor this video.' :<30} |");
        print( "| Enter 2 to list reports on this video.    |");
        print( "| Enter 3 to remove this video completely.  |");
        print( "| Enter 4 to go back.                       |");
        print( "+-------------------------------------------+");
        
        try: cmd = int(input("\nEnter: "));
        except:
            clear("Invalid command.");
            continue;
        clear();
        
        if cmd == 1:
            if censorOrUncensorVideo(videoID):
                censored = not censored;

        # list reports on this video
        elif cmd == 2:
            if not reportCount:
                print("No reports on this video.");
                continue;

            cursor.execute("""select complainant, vidid as id, reason, reporttime, 'video' as reporttype
                              from videoreport
                              where vidid = %s
                              order by reporttime desc;"""
                              , videoID);
            res = cursor.fetchall();

            listReports(res, f"Reports on <{title}>:");

        elif cmd == 3:
            print("\n<DELETE VIDEO> Enter #EXIT to go back.");

            reason = input("\nReason for this action: ");
            clear();

            if reason == "#EXIT": continue;

            if deleteVideo(videoID):
                cursor.execute("""insert into uamessage (adminid, userid, message, fromuser)
                values (%s, %s, %s, false);""", (USERID, uploaderID, 
                f"We decided to delete your video {title} because: {reason}"));

                return True;

        elif cmd == 4: return False;
        else: print("Invalid command.");

# boolean
def censorOrUncensorVideo(videoID):

    clear();

    cursor.execute("select * from censoredvideoinfo where vidid = %s;", videoID);
    censorInfo = cursor.fetchone();

    cursor.execute("select uploader, title from video where videoid = %s;", videoID);
    videoInfo = cursor.fetchone();
    uploader = videoInfo["uploader"];
    title = videoInfo["title"];

    # uncensor
    if censorInfo:
        if input(f"Uncensor video {title}? (y / n): ") == 'y':

            cursor.execute("delete from censoredvideoinfo where vidid = %s;", videoID);
            cursor.execute("""insert into uamessage (adminid, userid, message, fromuser)
                                values (%s, %s, %s, false);""", 
                                (USERID, uploader, f"Your video '{title}' has been uncensored."));
            connection.commit();
            clear(f"Successfully uncensored video {title}.");
            return True;

        clear();
        return False;

    # censor
    print(f"<CENSOR VIDEO {title}> Enter #EXIT to go back.");

    reason = input("\nReason for this censor: ");
    clear();

    if reason == "#EXIT": return False;

    cursor.execute("""insert into censoredvideoinfo (vidid, adminid, reason)
                    values (%s, %s, %s);""", (videoID, USERID, reason));
    cursor.execute("""insert into uamessage (adminid, userid, message, fromuser)
                        values (%s, %s, %s, false);""", 
                        (USERID, uploader, 
    f"Your video '{title}' has been censored because: {reason} You can contact me if you feel this censorship is unjust."));
    
    connection.commit();
    print(f"Successfully censored video {title}.");
    return True;

def manageCategories():

    clear();

    while True:
        print()
        print("+-<MANAGE CATEGORIES>---------------------+");
        print("| Enter 1 to view the category tree.      |");
        print("| Enter 2 to manage a category.           |");
        print("| Enter 3 to go back.                     |");
        print("+-----------------------------------------+");

        try: cmd = int(input("\nEnter: "));
        except:
            clear("Invalid command.");
            continue;
        clear();

        if cmd == 1: printCategoryTree();

        elif cmd == 2: 
            categoryID = selectCategory(True);
            if categoryID == 0: continue; # cancel
            manageCategory(categoryID);

        elif cmd == 3: return;

def manageCategory(categoryID):

    clear();

    name = "ROOT";
    parentName = "NONE";
    subCategories = getAllLeafCategoriesOf(categoryID);
    subCategoryCount = 0;

    if subCategories[0] != categoryID:
        subCategoryCount = len(subCategories);

    if categoryID: # not root
        cursor.execute("select * from category where categoryid = %s;", categoryID);
        categoryInfo = cursor.fetchone();

        name = categoryInfo["categoryname"];
        
        parentName = "ROOT";
        if categoryInfo["subcategoryof"]:
            cursor.execute("select categoryname from category where categoryid = %s;", categoryInfo["subcategoryof"]);
            parentName = cursor.fetchone()["categoryname"];


    while True:
        print();
        print( "+-<" + name + ">" + "-" * (31 - len(name)) + "+");
        print( "|                                  |");
        print(f"|   Category ID: {categoryID if categoryID else 'NONE':<17} |");
        print(f"|   Subcategory of: {parentName :<14} |");
        if subCategoryCount:
            print(f"|   Has {str(subCategoryCount) + ' child categories' :<26} |");
        else:
            print( "|   This is a Leaf Category.       |");
        print( "|                                  |");
        print( "+----------------------------------+");

        print( "+-<ACTIONS>------------------------+");
        print( "| Enter 1 to rename this category. |");
        print( "| Enter 2 to add child categories. |");
        print( "| Enter 3 to delete this category. |");
        print( "| Enter 4 to go back.              |");
        print( "+----------------------------------+");

        try: cmd = int(input("\nEnter: "));
        except: 
            clear("Invalid command.");
            continue;
        clear();

        if cmd == 1:

            if not categoryID:
                print("Cannot rename ROOT.");
                continue;

            while True:
                print("\n<RENAME CATEGORY> Enter #EXIT to go back.");

                newName = input(f"\nEnter new name for category {name}: ");
                clear();

                if newName == "#EXIT": break;

                cursor.execute("select subcategoryof from category where categoryname = %s;", newName);
                dup = cursor.fetchone();

                if dup:
                    pName = "ROOT";
                    if dup["subcategoryof"]: # is not none
                        cursor.execute("select categoryname from category where categoryid = %s;", dup["subcategoryof"]);
                        pName = cursor.fetchone()["categoryname"];
                    print(f"Category {newName} already exists under {pName}.");
                    continue;

                cursor.execute("update category set categoryname = %s where categoryid = %s;", (newName, categoryID));
                connection.commit();

                print(f"Successfully renamed category {name} to {newName}.");
                name = newName;
                break;

        # add children
        elif cmd == 2:

            exitFlag = False;
            newChildren = [];

            while True:

                print(f"INSERT INTO CATEGORY {name}:\n");

                if len(newChildren):
                    for i in range(len(newChildren)):
                        print(f"{i + 1}. {newChildren[i]}");
                    print();

                print("Enter name of child category to insert.");
                print("Enter #COMMIT to commit these changes.");
                print("Enter #EXIT to cancel and go back.");

                childName = input("\nEnter: ");
                clear();

                if childName == "#EXIT":
                    exitFlag = True;
                    break;

                if childName == "#COMMIT": break;

                cursor.execute("select subcategoryof from category where categoryname = %s;", childName);
                dup = cursor.fetchone();

                if childName in newChildren: continue;

                if dup:
                    pName = "ROOT";
                    if dup["subcategoryof"]: # is not none
                        cursor.execute("select categoryname from category where categoryid = %s;", dup["subcategoryof"]);
                        pName = cursor.fetchone()["categoryname"];
                    print(f"{childName} already exists under category {pName}.\n");
                    continue;
                
                newChildren.append(childName);
            
            # commit changes if any
            if not exitFlag and len(newChildren):
                # no recategorizatons needed
                if subCategoryCount: # if not leaf

                    if categoryID:
                        for child in newChildren:
                            cursor.execute("""insert into category (categoryname, subcategoryof)
                                                values (%s, %s);""", (child, categoryID));
                    else:
                        for child in newChildren:
                            cursor.execute("""insert into category (categoryname)
                                                value (%s);""", child);

                else:
                    # leaf category becomes a non leaf category
                    # videos with this category needs to be updated
                    # and send notifications
                    newChildrenIDs = [];

                    for child in newChildren:
                        cursor.execute("""insert into category (categoryname, subcategoryof)
                                        values (%s, %s);""", (child, categoryID));
                        cursor.execute("select last_insert_id() as id;");
                        newChildrenIDs.append(cursor.fetchone()["id"]);

                    # recategorize randomly
                    affectedVideoCount = cursor.execute(f"""update video
                            set categoryof = elt(floor(rand() * {len(newChildrenIDs)})+1, {str(newChildrenIDs)[1:-1]})
                            where categoryof = {categoryID};""");
                    print(f"{affectedVideoCount} video(s) have been recategorized.");

                connection.commit();

                subCategories = getAllLeafCategoriesOf(categoryID);
                subCategoryCount += len(newChildren);
                print("Successfully committed changes.");

        # delete
        elif cmd == 3:
            if not categoryID: # ROOT
                print("Cannot delete ROOT.");
                continue;

            cursor.execute(f"select count(*) as count from video where categoryof in ({str(subCategories)[1:-1]});");
            affectedVideoCount = cursor.fetchone()["count"];

            if affectedVideoCount:
                print(f"{affectedVideoCount} videos are under category {name}. You must specify which category these videos will be moved to.");

                if input("\nAre you sure you want to delete this category? (y / n): ") != 'y': continue;

                newCategory = selectCategory(False, f"<SELECT NEW CATEGORY TO REPLACE {name}>");

                if newCategory == 0: continue;

                if newCategory == categoryID:
                    print("Cannot replace category with itself.");
                    continue;
                
                if newCategory in subCategories:
                    print(f"This category is under {name}.");
                    continue;

                cursor.execute(f"""update video
                                    set categoryof = {newCategory}
                                    where categoryof in ({str(subCategories)[1:-1]});""");

            else:
                if input("\nAre you sure you want to delete this category? (y / n): ") != 'y':
                    continue;

            cursor.execute("delete from category where categoryid = %s;", categoryID);

            connection.commit();
            clear(f"Successfully deleted {name}. {affectedVideoCount} video(s) have been recategorized.");
            return;

        elif cmd == 4: return;


def printCategoryTree(categoryID = None, depth = 0):

    if not categoryID: # init
        clear("");
        cursor.execute("select * from category where subcategoryof is null;");
    else: cursor.execute("select * from category where subcategoryof = %s;", categoryID);

    res = cursor.fetchall();
    if not len(res): return;

    for row in res:
        print("--" * depth + row["categoryname"]);
        printCategoryTree(row["categoryid"], depth + 1);


menu();
