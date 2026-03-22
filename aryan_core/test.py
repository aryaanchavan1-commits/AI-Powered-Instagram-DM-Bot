import asyncio,aiohttp, time, uuid, json, threading, os
from aryan_core.sendmessage import mesj
from aryan_core.login import InstagramLogin
from aryan_core.ai import gpt4o
from aryan_core.tidb_connection import TiDBConnection

async def test(username, password,language,proxy,group_messages):
    timestamp = int(time.time())
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8","Host": "i.instagram.com","Priority": "u=3","User-Agent": "Instagram 342.0.0.33.103 Android (31/12; 454dpi; 1080x2254; Xiaomi/Redmi; Redmi Note 9 Pro; joyeuse; qcom; tr_TR; 627400398)","X-Bloks-Is-Layout-RTL": "false","X-Bloks-Is-Prism-Enabled": "true","X-Bloks-Prism-Button-Version": "CONTROL","X-Bloks-Prism-Colors-Enabled": "true","X-Bloks-Prism-Font-Enabled": "false","X-Bloks-Version-Id": "dummy","X-FB-Connection-Type": "WIFI","X-FB-HTTP-Engine": "Tigon-HUC-Fallback","X-FB-Network-Properties": "dummy","X-IG-Android-ID": "android-a19180f55839e822","X-IG-App-ID": "567067343352427","X-IG-App-Locale": "tr_TR","X-IG-Bandwidth-Speed-KBPS": "1934.000","X-IG-Bandwidth-TotalBytes-B": "1375348","X-IG-Bandwidth-TotalTime-MS": "785","X-IG-Capabilities": "3brTv10=","X-IG-CLIENT-ENDPOINT": "DirectThreadFragment:direct_thread","X-IG-Connection-Type": "WIFI","X-IG-Device-ID": "android-a19180f55839e822","X-IG-Device-Locale": "tr_TR","X-IG-Family-Device-ID": "dummy","X-IG-Mapped-Locale": "tr_TR","X-IG-Nav-Chain": "dummy","X-IG-SALT-IDS": "dummy","X-IG-SALT-LOGGER-IDS": "dummy","X-IG-Timezone-Offset": "10800","X-IG-WWW-Claim": "dummy","X-MID": "dummy","X-Pigeon-Rawclienttime": str(timestamp),"X-Pigeon-Session-Id": f"dummy-{uuid.uuid4()}"}

    # Initialize TiDB connection
    db = TiDBConnection()
    
    # Try to get auth from database
    mydata = {}
    auth_token = db.get_authorization(username)
    
    if auth_token is None:
        login_handler = InstagramLogin()
        result = login_handler.login(username, password)
        if result["success"]:
            auth_token = result["auth_token"]
            myuserid = str(result["user_id"])
            mydata = {'auth': auth_token, 'myuserid': myuserid}
            # Save to database
            db.save_authorization(username, auth_token)
        else:
            print(f"Login failed: {result.get('message')}")
            return False
    else:
        mydata = {'auth': auth_token, 'myuserid': username}

    headers["Authorization"] = f"{mydata.get('auth')}"
    session = aiohttp.ClientSession()
    if not proxy == None:
        proxy=f"http://{proxy}"
        
        

    async with session.get("https://i.instagram.com/api/v1/direct_v2/inbox/",proxy=proxy, headers=headers, params={"persistentBadging": "true", "use_unified_inbox": "true"})as re:
        res = await re.json()
        if not res.get('logout_reason') is None:
            login_handler = InstagramLogin()
            result = login_handler.login(username, password)
            if result["success"]:
                auth_token = result["auth_token"]
                myuserid = str(result["user_id"])
                mydata = {'auth': auth_token, 'myuserid': myuserid}
                # Save to database
                db.save_authorization(username, auth_token)
        if not res.get('is_spam') is None:
            print('your ip is stuck at rate limit try again after 50 seconds')
            time.sleep(50)

    if re.status == 200:
        data = await re.json()
        threads = data.get("inbox", {}).get("threads", [])

        for thread in threads:
            thread_id = thread.get('thread_id')
            items = thread.get("items", [])
            is_group = thread.get("is_group", False)  
            
            if is_group == True and group_messages == False:  
                print("group message is skipped (if you don't want it to be skipped, set group_messages in config.json to true)")
                await session.close()
                continue 
            if items:
                last_item = items[0]  
                item_id = last_item.get("item_id")
                text = last_item.get("text", None)
                sender = last_item.get("user_id", None)

                if text is None:
                    await session.close()
                    return False  

                my_user_id = mydata.get('myuserid', None)

                if str(sender) == str(my_user_id):
                    await session.close()
                    return None
                
                
                ai = await gpt4o(text,language)
                
                
                print(f"Message from {sender}: {text}")
                
                t = threading.Thread(target=mesj, args=(
                    str(mydata.get('auth')),
                    str(my_user_id),
                    "android-1",
                    str(ai),
                    [sender],
                    str(thread_id),
                    str(item_id)
                ))
                t.start()
                t.join()  
                print("message sent successfully")
                
            else:
                pass
    await session.close()
